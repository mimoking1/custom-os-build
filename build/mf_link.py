import os
from mediafire.client import MediaFireClient
c = MediaFireClient()
c.login(email='qusa48@mail.instinct.com', password=os.environ['MF_PW'], app_id='42511')
for it in c.get_folder_contents_iter('mf:/'):
    d = dict(it) if hasattr(it, 'keys') else {}
    if d.get('type') == 'file' or 'quickkey' in d:
        r = c.api.file_get_links(quick_key=d['quickkey'], link_type='normal_download')
        print('FILE', d.get('filename'), 'SIZE', d.get('size'), 'HASH', d.get('hash'), 'LINK', r['links'][0]['normal_download'])
