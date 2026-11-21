p='templates/marania_invoice_app/trend_analytics.html'
s=open(p,encoding='utf-8').read()

color_map = {
    '<!-- Filters -->': 'bg-secondary',
    '<!-- Business KPI Overview -->': 'bg-primary',
    '<!-- Monthly Best-Performing Product Analysis -->': 'bg-info text-dark',
    '<!-- Customer Concentration -->': 'bg-warning text-dark',
    '<!-- Precautionary Measures & Predictive Analysis -->': 'bg-danger',
    '<!-- Business Action Recommendations -->': 'bg-success',
    '<!-- Product Trends': 'bg-primary',
    '<!-- Product \\u00d7 Specification Matrix -->': 'bg-secondary text-white',
    '<!-- Customer Performance -->': 'bg-warning text-dark',
    '<!-- Recommendations -->': 'bg-success',
    '<!-- Data Quality -->': 'bg-dark',
    '<!-- Detailed Orders Table -->': 'bg-dark',
}

for comment, color in color_map.items():
    idx = s.find(comment)
    if idx == -1:
        print('MISSING comment:', comment)
        continue
    # find the card-header after this comment
    hdr = s.find('card-header bg-dark text-white', idx)
    if hdr == -1 or hdr - idx > 300:
        print('no header near:', comment)
        continue
    s = s[:hdr] + f'card-header {color} d-flex justify-content-between align-items-center' + s[hdr+len('card-header bg-dark text-white d-flex justify-content-between align-items-center'):] if 'd-flex justify-content-between align-items-center' in s[hdr:hdr+80] else s[:hdr] + f'card-header {color}' + s[hdr+len('card-header bg-dark text-white'):]
    print('OK:', comment, '->', color)

open(p,'w',encoding='utf-8').write(s)
print('done')
PY