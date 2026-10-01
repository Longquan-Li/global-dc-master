from pathlib import Path
import json, time, requests

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "raw" / "japan_dc_watch" / "facilities.json"
out = ROOT / "raw" / "japan_dc_watch" / "facility_details.json"

obj = json.loads(p.read_text(encoding="utf-8"))
details = []
for i, item in enumerate(obj.get("items", []), 1):
    slug = item["slug"]
    url = f"https://japandatacenter.org/api/v1/facilities/{slug}"
    r = requests.get(url, timeout=60, headers={"User-Agent":"global-dc-facility-database/0.1"})
    r.raise_for_status()
    details.append(r.json())
    print(i, slug)
    time.sleep(0.05)
out.write_text(json.dumps(details, ensure_ascii=False, indent=2), encoding="utf-8")
print("wrote", len(details), "detail records")