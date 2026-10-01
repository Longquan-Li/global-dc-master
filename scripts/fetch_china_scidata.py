from pathlib import Path
import re, json, urllib.parse
import requests

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"raw"/"china_scidata"
OUT.mkdir(parents=True, exist_ok=True)

doi="https://doi.org/10.57760/sciencedb.32970"
r=requests.get(doi,timeout=90,headers={"User-Agent":"global-dc-facility-database/0.1"})
r.raise_for_status()
(OUT/"landing.html").write_text(r.text,encoding="utf-8",errors="ignore")
base=r.url

hrefs=re.findall(r'href=["\']([^"\']+)["\']',r.text,re.I)
cands=[]
for h in hrefs:
    u=urllib.parse.urljoin(base,h)
    lo=u.lower()
    if any(x in lo for x in [".csv",".zip",".xlsx",".xls",".geojson",".json"]) or "download" in lo:
        cands.append(u)

manifest=[]
for i,u in enumerate(dict.fromkeys(cands),1):
    try:
        rr=requests.get(u,timeout=120,headers={"User-Agent":"global-dc-facility-database/0.1"})
        ct=rr.headers.get("content-type","")
        cd=rr.headers.get("content-disposition","")
        name=None
        m=re.search(r'filename\*?=(?:UTF-8\'\')?["\']?([^;"\']+)',cd,re.I)
        if m: name=urllib.parse.unquote(m.group(1))
        if not name:
            path=urllib.parse.urlparse(rr.url).path
            name=Path(path).name or f"candidate_{i}"
        if rr.ok and len(rr.content)>500 and ("html" not in ct.lower() or any(name.lower().endswith(x) for x in [".csv",".zip",".xlsx",".xls",".geojson",".json"])):
            p=OUT/name
            if p.exists(): p=OUT/f"{i}_{name}"
            p.write_bytes(rr.content)
            manifest.append({"url":u,"resolved":rr.url,"file":p.name,"bytes":len(rr.content),"content_type":ct})
    except Exception as e:
        manifest.append({"url":u,"error":str(e)})

(OUT/"download_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"landing":base,"candidate_links":len(cands),"downloaded":sum("file" in x for x in manifest)},indent=2))
