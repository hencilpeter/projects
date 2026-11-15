import os, zipfile
from django.test import RequestFactory
from django.contrib.auth.models import User
from marania_invoice_app import views
rf = RequestFactory()
req = rf.get('/backup-export-all/', {'format': 'json'})
req.session = {}
req.user = User(username='t', is_staff=True)
resp = views.backup_export_all(req)
print('status', resp.status_code)
print('content-type', resp.get('Content-Type'))
# find the zip file
import glob
zips = sorted(glob.glob(os.path.join('media', 'marania_backup_*.zip')), key=os.path.getmtime)
print('latest zip:', zips[-1] if zips else None)
if zips:
    z = zips[-1]
    with zipfile.ZipFile(z) as zf:
        names = zf.namelist()
        print('file count:', len(names))
        print('first few:', names[:5])
        print('has AdHocColourConfiguration:', any('AdHocColourConfiguration' in n for n in names))
    # save zip name for import test
    open('last_zip.txt','w').write(z)
PY