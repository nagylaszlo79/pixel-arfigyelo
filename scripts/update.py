
import json
import re
import datetime
import urllib.request
import pathlib
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.blocks = []
        self.script = False
        self.href = None
        self.text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self.script = True
            self.blocks.append("")
        if tag == "a":
            self.href = a.get("href")
            self.text = []

    def handle_data(self, data):
        if self.script and self.blocks:
            self.blocks[-1] += data
        if self.href:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "script":
            self.script = False
        if tag == "a" and self.href:
            self.links.append((self.href, " ".join(self.text)))
            self.href = None

def walk(obj):
    if isinstance(obj, list):
        for value in obj:
            yield from walk(value)
    elif isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk(value)

def storage_of(name):
    m = re.search(r"\b(256|512|1024)\s*(?:GB|G|TB)?\b", name, re.I)
    return int(m.group(1)) if m else None

def correct_model(name):
    return (
        bool(re.search(r"pixel[\s-]*10[\s-]*pro\b", name, re.I))
        and not bool(re.search(r"\b(XL|Fold|10a)\b", name, re.I))
    )

def add_offer(store, country, name, url, price=None,
              currency=None, condition="unknown", note=""):
    storage = storage_of(name)
    if not correct_model(name) or not storage:
        return
    if not url.startswith(("https://", "http://")):
        return
    key = (store, url, storage)
    if key in seen:
        return
    seen.add(key)
    offers.append({
        "id": "auto-" + str(len(offers)),
        "store": store,
        "country": country,
        "condition": condition,
        "storage": storage,
        "price": price,
        "currency": currency,
        "shipping": 0,
        "shippingKnown": False,
        "warranty": "Nem ellenőrzött",
        "notes": note or "Ár, állapot és garancia ellenőrzendő",
        "url": url,
        "date": NOW,
        "automatic": True
    })

sources = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
offers = []
errors = []
seen = set()

for source in sources:
    try:
        req = urllib.request.Request(
            source["url"],
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=25) as response:
            html = response.read(2000000).decode("utf-8", "replace")

        parser = PageParser()
        parser.feed(html)

        for block in parser.blocks:
            try:
                nodes = list(walk(json.loads(block)))
            except (ValueError, TypeError):
                continue

            for node in nodes:
                types = node.get("@type", [])
                if isinstance(types, str):
                    types = [types]
                if "Product" not in types:
                    continue

                name = str(node.get("name", ""))
                raw_offers = node.get("offers", [])
                if isinstance(raw_offers, dict):
                    raw_offers = [raw_offers]

                for offer in raw_offers:
                    if not isinstance(offer, dict):
                        continue
                    raw_price = offer.get("price", offer.get("lowPrice"))
                    try:
                        price = float(str(raw_price).replace(",", "."))
                        if price <= 0:
                            price = None
                    except (ValueError, TypeError):
                        price = None

                    currency = offer.get("priceCurrency")
                    if currency not in ("HUF", "EUR", "PLN"):
                        price = None
                        currency = None

                    raw_condition = str(offer.get("itemCondition", "")).lower()
                    condition = (
                        "new" if "newcondition" in raw_condition
                        else "used" if "usedcondition" in raw_condition
                        else "unknown"
                    )
                    if condition == "used":
                        continue

                    link = urljoin(source["url"], str(offer.get("url") or source["url"]))
                    add_offer(source["name"], source["country"],
                              name, link, price, currency, condition,
                              "Strukturált termékadat; szállítás és garancia ellenőrzendő")

        for href, label in parser.links:
            name = re.sub(r"\s+", " ", label).strip()
            link = urljoin(source["url"], href)
            if urlparse(link).netloc != urlparse(source["url"]).netloc:
                continue
            add_offer(source["name"], source["country"],
                      name, link, note="Hivatkozásból felismert jelölt; ár és új állapot nem igazolt")

        if not any(o["store"] == source["name"] for o in offers):
            errors.append(source["name"] + ": nincs felismerhető ajánlat")

    except Exception as exc:
        errors.append(source["name"] + ": " + str(exc)[:180])

output = {
    "updatedAt": NOW,
    "offers": offers,
    "errors": errors
}
(ROOT / "offers.json").write_text(
    json.dumps(output, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print(f"{len(offers)} jelölt, {len(errors)} figyelmeztetés")
