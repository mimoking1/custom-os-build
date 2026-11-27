import os, sys, hashlib
from mediafire.client import MediaFireClient
iso = sys.argv[1]
email = 'qusa48@mail.instinct.com'
pw = os.environ['MF_PW']
c = MediaFireClient()
c.login(email=email, password=pw, app_id='42511')
print('logged in')
name = os.path.basename(iso)
c.upload_file(iso, 'mf:/')
print('upload call returned')
f = c.get_resource_by_path('/' + name)
key = f['quickkey']
links = c.api.file_get_links(quickkey=key, link_type='normal_download')
print('LINK', links['links'][0]['normal_download'])
print('SIZE', f.get('size'), 'HASH', f.get('hash'))
