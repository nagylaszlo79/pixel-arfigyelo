import json, re, datetime, urllib.request, pathlib
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]
class JSONLD(HTMLParser):
 def __init__(self): super().__init__(); self.inside=False; self.blocks=[]
 def handle_starttag(self,tag,attrs):
  if tag=='script' and dict(attrs).get('type','').lower()=='application/ld+json': self.inside=True; self.blocks.append('')
 def handle_endtag(self,tag):
  if tag=='script': self.inside=False
 def handle_data(self,data):
  if self.inside: self.blocks[-1]+=data

def walk(x):
 if isinstance(x,list):
  for v in x: yield from walk(v)
 elif isinstance(x,dict):
  yield x
  for v in x.values(): yield from walk(v)

sources=json.loads((ROOT/'sources.json').read_text(encoding='utf8'))
items=[]; errors=[]
for s in sources:
 try:
  req=urllib.request.Request(s['url'],headers={'User-Agent':'Mozilla/5.0 (compatible; PersonalPriceTracker/1.0)'})
  with urllib.request.urlopen(req,timeout=18) as r: html=r.read(1500000).decode('utf8','replace')
  p=JSONLD(); p.feed(html)
  found=0
  for block in p.blocks:
   try: nodes=list(walk(json.loads(block)))
   except Exception: continue
   for node in nodes:
    typ=node.get('@type',[]); typ=[typ] if isinstance(typ,str) else typ
    if 'Product' not in typ: continue
    name=str(node.get('name',''))
    if not re.search(r'pixel\s*10\s*pro\b',name,re.I) or re.search(r'\b(?:xl|fold|10a)\b',name,re.I):continue
    if not re.search(r'\b(?:256|512|1024)\s*(?:gb|g|tb)?\b',name,re.I):continue
    storage=int(re.search(r'\b(256|512|1024)\b',name).group(1))
    for offer in (node.get('offers') if isinstance(node.get('offers'),list) else [node.get('offers')]):
     if not isinstance(offer,dict):continue
     price=offer.get('price') or offer.get('lowPrice'); currency=offer.get('priceCurrency')
     if not price or currency not in ('HUF','EUR','PLN'):continue
     condition=str(offer.get('itemCondition','')).lower()
     if condition and 'newcondition' not in condition:continue
     # If condition is absent, newness cannot be established.
     verified_new='newcondition' in condition
     try: amount=float(str(price).replace(',','.'))
     except ValueError:continue
     if amount<=0:continue
     items.append(dict(id='auto-'+str(len(items)),store=s['name'],country=s['country'],condition='new' if verified_new else 'unknown',storage=storage,price=amount,currency=currency,shipping=0,shippingKnown=False,warranty='Nem ellenőrzött',notes='Automatikusan kinyert adat; szállítás, készlet és garancia ellenőrzendő',url=s['url'],date=datetime.datetime.now(datetime.timezone.utc).isoformat(),automatic=True))
     found+=1
  if not found:errors.append(s['name']+': nem találtam megfelelő strukturált termékadatot')
 except Exception as exc:errors.append(s['name']+': '+str(exc)[:180])
output={'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'offers':items,'errors':errors}
(ROOT/'offers.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf8')
print(f'{len(items)} találat, {len(errors)} figyelmeztetés')
