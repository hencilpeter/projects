p='templates/marania_invoice_app/trend_analytics.html'
s=open(p,encoding='utf-8').read()
# Change remaining 'card-body collapse show' (without ta-collapse) to collapsed
s=s.replace('class="card-body collapse show"', 'class="card-body collapse ta-collapse"', 0)  # all
# Also remove 'show' from any remaining 'collapse show' card-body
s=s.replace('class="card-body collapse show ta-collapse"', 'class="card-body collapse ta-collapse"')
open(p,'w',encoding='utf-8').write(s)
print('done')
PY