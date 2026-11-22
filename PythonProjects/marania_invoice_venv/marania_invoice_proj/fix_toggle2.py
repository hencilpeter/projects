p='templates/marania_invoice_app/trend_analytics.html'
s=open(p,encoding='utf-8').read()

# Filters header
old_f='''<div class="card-header bg-white text-dark border-start border-4 border-secondary d-flex justify-content-between align-items-center flex-wrap" style="cursor:pointer;">'''
new_f='''<div class="card-header bg-white text-dark border-start border-4 border-secondary d-flex justify-content-between align-items-center flex-wrap" data-bs-toggle="collapse" data-bs-target="#filterBody" style="cursor:pointer;">'''
assert old_f in s
s=s.replace(old_f,new_f,1)

# Monthly Best header (find by title)
import re
i=s.find('Monthly Best-Performing Product Analysis</h5>')
hdr=s.rfind('<div class="card-header', 0, i)
old_hdr=s[hdr:hdr+120]
# extract up to the closing >
end=s.find('>', hdr)+1
header=s[hdr:end]
assert 'data-bs-toggle' not in header
# find body id after
body_match=re.search(r'<div class="card-body collapse[^"]*" id="([^"]+)"', s[end:end+400])
print('Monthly Best body id:', body_match.group(1) if body_match else None)
if body_match:
    body_id=body_match.group(1)
    s=s[:end-1]+f' data-bs-toggle="collapse" data-bs-target="#{body_id}" style="cursor:pointer;">'+s[end:]
    # remove the original >
    # Actually we inserted before >, need to remove duplicate. Let me redo carefully.
print('done partial')

open(p,'w',encoding='utf-8').write(s)
PY