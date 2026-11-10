"""Content-addressed Drive upload with download SHA verification and safe retry."""
import hashlib, json, os, mimetypes, uuid
from urllib import request,parse
from pathlib import Path
class Drive:
 def __init__(self,config):
  import google.auth.transport.requests
  from google.oauth2 import service_account
  from google.oauth2.credentials import Credentials
  self.transport=google.auth.transport.requests.Request
  if os.getenv('DRIVE_OAUTH_JSON'):
   c=json.loads(os.environ['DRIVE_OAUTH_JSON'])
   self.creds=Credentials(token=None,refresh_token=c['refresh_token'],token_uri='https://oauth2.googleapis.com/token',client_id=c['client_id'],client_secret=c['client_secret'],scopes=['https://www.googleapis.com/auth/drive.file'])
  else:
   self.creds=service_account.Credentials.from_service_account_info(json.loads(os.environ['DRIVE_SERVICE_ACCOUNT_JSON']),scopes=['https://www.googleapis.com/auth/drive.file'])
 def call(self,url,body=None,headers=None,method=None):
  # google-auth's transport uses requests, installed transitively via google-auth[requests].
  if not self.creds.valid:self.creds.refresh(self.transport())
  req=request.Request(url,data=body,headers={'Authorization':'Bearer '+self.creds.token,**(headers or {})},method=method)
  with request.urlopen(req,timeout=90) as res:return res.read()
 def put_verified(self,path,parent,name):
  path=Path(path);data=path.read_bytes();digest=hashlib.sha256(data).hexdigest()
  query=f"'{parent}' in parents and trashed=false and appProperties has {{ key='factory_sha256' and value='{digest}' }}"
  result=json.loads(self.call('https://www.googleapis.com/drive/v3/files?'+parse.urlencode({'q':query,'fields':'files(id,name)','supportsAllDrives':'true','includeItemsFromAllDrives':'true'})))
  matches=[f for f in result.get('files',[]) if f['name']==name]
  if matches:file_id=matches[0]['id']
  else:
   boundary='factory_'+uuid.uuid4().hex
   meta=json.dumps({'name':name,'parents':[parent],'appProperties':{'factory_sha256':digest}}).encode()
   mime=mimetypes.guess_type(name)[0] or 'application/octet-stream'
   body=b'--'+boundary.encode()+b'\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'+meta+b'\r\n--'+boundary.encode()+b'\r\nContent-Type: '+mime.encode()+b'\r\n\r\n'+data+b'\r\n--'+boundary.encode()+b'--\r\n'
   res=json.loads(self.call('https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true',body,{'Content-Type':'multipart/related; boundary='+boundary},'POST'))
   file_id=res['id']
  downloaded=self.call('https://www.googleapis.com/drive/v3/files/'+file_id+'?alt=media&supportsAllDrives=true')
  if hashlib.sha256(downloaded).hexdigest()!=digest:raise ValueError('Drive download integrity mismatch')
  return {'name':name,'drive_file_id':file_id,'sha256':digest,'download_verified':True,'bytes':len(data)}
