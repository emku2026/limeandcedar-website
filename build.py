"""Build the static site: python3 build.py

Pages live in pages/*.html. Each starts with a header block:
    <!--
    title: Page title for Google (about 60 characters)
    description: Page description for Google (about 155 characters)
    path: car-shipping.html
    priority: 0.8
    -->
then the page body (everything between the site header and footer).
{{QUOTE_FORM}} in a page is replaced with the quote form; {{BRAND}}, {{PHONE}} etc. with the values below.
The output (*.html, sitemap.xml) is written next to this file, ready for GitHub Pages.
"""

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SITE = "https://limeandcedar.com/"
BRAND = "Lime & Cedar"
BRAND_LONG = "Lime & Cedar Auto Transport"
LEGAL = "Lime and Cedar LLC"
PHONE = "(909) 323-0321"
PHONE_TEL = "+19093230321"
EMAIL = "limencedar@gmail.com"
MC, USDOT = "1543888", "4056326"
QUOTE_URL = "https://sign.limeandcedar.com/quote"
GA_ID = "G-53QSEQHHPS"  # Google Analytics 4, property limeandcedar.com

NAV = [("car-shipping.html", "Car Shipping"), ("motorcycle-shipping.html", "Motorcycles"),
       ("enclosed-car-shipping.html", "Enclosed"), ("heavy-equipment-shipping.html", "Heavy Equipment"),
       ("routes.html", "Routes")]

ORG = {
    "@type": "Organization", "@id": SITE + "#org", "name": BRAND_LONG, "legalName": LEGAL, "url": SITE,
    "logo": SITE + "img/logo-full.jpg", "telephone": "+1-909-323-0321", "email": EMAIL, "areaServed": "US",
    "identifier": [{"@type": "PropertyValue", "propertyID": "MC", "value": MC},
                   {"@type": "PropertyValue", "propertyID": "USDOT", "value": USDOT}],
    "sameAs": ["https://www.facebook.com/limeandcedar"],
}

QUOTE_FORM = """
<form class="quote" id="quote" action="{QUOTE_URL}" method="post" novalidate>
  <h2>Get a free quote</h2>
  <p class="quote__sub">Takes 1 minute. No obligation.</p>
  <div class="row">
    <label>Pickup ZIP code<input name="pickup" required inputmode="numeric" maxlength="5" pattern="[0-9]{{5}}" placeholder="95112" data-zip><small class="zip-city" aria-live="polite"></small></label>
    <label>Delivery ZIP code<input name="delivery" required inputmode="numeric" maxlength="5" pattern="[0-9]{{5}}" placeholder="78701" data-zip><small class="zip-city" aria-live="polite"></small></label>
  </div>
  <div class="row">
    <label>Vehicle<input name="vehicle" required placeholder="2021 Toyota Camry"></label>
    <label>Type
      <select name="vehicle_type">{TYPE_OPTIONS}</select>
    </label>
  </div>
  <div class="row">
    <label>Trailer
      <select name="trailer"><option value="open">Open (most popular)</option><option value="enclosed"{ENCLOSED}>Enclosed</option></select>
    </label>
    <label>Runs?
      <select name="running"><option value="yes">Yes, it runs</option><option value="no">No / inoperable</option></select>
    </label>
  </div>
  <div class="row">
    <label>First available date<input type="date" name="date"></label>
    <label>Your price <span class="hint">(optional)</span><input name="target_price" inputmode="decimal" placeholder="$"></label>
  </div>
  <div class="row">
    <label>Your name<input name="name" autocomplete="name" required></label>
    <label>Phone<input type="tel" name="phone" autocomplete="tel" required placeholder="(555) 123-4567"></label>
  </div>
  <label>Email<input type="email" name="email" autocomplete="email" required></label>
  <input type="hidden" name="pickup_city" value="">
  <input type="hidden" name="delivery_city" value="">
  <input type="hidden" name="page" value="">
  <input class="hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
  <button class="btn btn--wide" type="submit">Get my quote</button>
  <p class="fine">Don't know the ZIP? Search “ZIP code” + the address in Google. Have a budget in mind? Put it in “Your price” — we'll tell you honestly if a carrier will take it. By sending this form you agree that we may call, text or email you about this shipment. We never sell or share your info.</p>
  <p class="quote__ok" hidden>✓ Got it! A dispatcher will call or text you shortly with your price.</p>
  <p class="quote__err" hidden>Something went wrong. Please call us at <a href="tel:{PHONE_TEL}">{PHONE}</a>.</p>
</form>
"""

HEAVY_FORM = """
<form class="quote" id="quote" action="{QUOTE_URL}" method="post" novalidate>
  <h2>Heavy equipment quote</h2>
  <p class="quote__sub">Free, no obligation. The more you tell us, the faster the price.</p>
  <div class="row">
    <label>Pickup ZIP code<input name="pickup" required inputmode="numeric" maxlength="5" pattern="[0-9]{{5}}" placeholder="93721" data-zip><small class="zip-city" aria-live="polite"></small></label>
    <label>Delivery ZIP code<input name="delivery" required inputmode="numeric" maxlength="5" pattern="[0-9]{{5}}" placeholder="85001" data-zip><small class="zip-city" aria-live="polite"></small></label>
  </div>
  <div class="row">
    <label>Equipment type
      <select name="equipment_type">
        <option>Excavator</option><option>Tractor</option><option>Skid steer / Loader</option><option>Backhoe</option>
        <option>Dozer</option><option>Forklift</option><option>Combine / Farm equipment</option><option>Boat on trailer</option>
        <option>Trailer / RV</option><option>Other</option>
      </select>
    </label>
    <label>Year, make, model<input name="vehicle" required placeholder="2018 CAT 320"></label>
  </div>
  <div class="row">
    <label>Size L × W × H <span class="hint">(if known)</span><input name="dimensions" placeholder="31 × 10 × 10 ft"></label>
    <label>Weight <span class="hint">(if known)</span><input name="weight" placeholder="50,000 lb"></label>
  </div>
  <div class="row">
    <label>Runs?
      <select name="running"><option value="yes">Yes, it runs</option><option value="no">No / inoperable</option></select>
    </label>
    <label>Loading at pickup
      <select name="loading"><option>Drives on (ramps)</option><option>Forklift / crane on site</option><option>Needs loading help</option><option>Not sure</option></select>
    </label>
  </div>
  <label>Auction or listing link <span class="hint">(optional)</span><input name="auction_link" type="url" placeholder="https://"></label>
  <div class="row">
    <label>First available date<input type="date" name="date"></label>
    <label>Your price <span class="hint">(optional)</span><input name="target_price" inputmode="decimal" placeholder="$"></label>
  </div>
  <div class="row">
    <label>Your name<input name="name" autocomplete="name" required></label>
    <label>Phone<input type="tel" name="phone" autocomplete="tel" required placeholder="(555) 123-4567"></label>
  </div>
  <label>Email<input type="email" name="email" autocomplete="email" required></label>
  <input type="hidden" name="kind" value="heavy">
  <input type="hidden" name="pickup_city" value="">
  <input type="hidden" name="delivery_city" value="">
  <input type="hidden" name="page" value="">
  <input class="hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
  <button class="btn btn--wide" type="submit">Get my quote</button>
  <p class="fine">Don't know the size or weight? Give us the exact model or the listing link — we'll look up the specs. By sending this form you agree that we may call, text or email you about this shipment. We never sell or share your info.</p>
  <p class="quote__ok" hidden>✓ Got it! A dispatcher will call or text you shortly about your equipment.</p>
  <p class="quote__err" hidden>Something went wrong. Please call us at <a href="tel:{PHONE_TEL}">{PHONE}</a>.</p>
</form>
"""

LAYOUT = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
{head_index}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND_LONG}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}img/logo-full.jpg">
<link rel="icon" href="/img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<link rel="stylesheet" href="/css/site.css">
<script type="application/ld+json">{schema}</script>
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA_ID}');</script>
</head>
<body>
<header class="top">
  <div class="wrap top__in">
    <a class="brand" href="/" aria-label="{BRAND_LONG} home">
      <img src="/img/logo-mark.png" srcset="/img/logo-mark@2x.png 2x" alt="" width="44" height="44">
      <span><b>{BRAND}</b><small>Auto Transport</small></span>
    </a>
    <nav class="nav" aria-label="Main">{nav}</nav>
    <a class="phone" href="tel:{PHONE_TEL}">{PHONE}</a>
    <a class="btn btn--sm" href="{quote_link}">Free Quote</a>
  </div>
</header>
<main>
{body}
</main>
<footer class="foot">
  <div class="wrap foot__in">
    <div>
      <b>{BRAND_LONG}</b>
      <p>Operated by {LEGAL}, a licensed auto transport broker.<br>MC-{MC} · USDOT {USDOT}<br>
      <a href="https://safer.fmcsa.dot.gov/query.asp?searchtype=ANY&amp;query_type=queryCarrierSnapshot&amp;query_param=MC_MX&amp;query_string={MC}" target="_blank" rel="noopener">Verify on FMCSA ↗</a></p>
    </div>
    <div>
      <a href="tel:{PHONE_TEL}">{PHONE}</a><br>
      <a href="mailto:{EMAIL}">{EMAIL}</a><br><br>
      <a href="/about.html">About us</a><br>
      <a href="/privacy.html">Privacy Policy</a>
    </div>
    <div>
      <a href="/car-shipping.html">Car Shipping</a><br>
      <a href="/motorcycle-shipping.html">Motorcycle Shipping</a><br>
      <a href="/enclosed-car-shipping.html">Enclosed Transport</a><br>
      <a href="/heavy-equipment-shipping.html">Heavy Equipment</a><br>
      <a href="/routes.html">Popular Routes</a>
    </div>
  </div>
  <p class="wrap foot__copy">© {year} {LEGAL}</p>
</footer>
<a class="callbar" href="tel:{PHONE_TEL}">📞 Call {PHONE}</a>
<script src="/js/quote.js" defer></script>
</body>
</html>
"""

CONSTANTS = dict(SITE=SITE, BRAND=BRAND, BRAND_LONG=BRAND_LONG, LEGAL=LEGAL, PHONE=PHONE, PHONE_TEL=PHONE_TEL,
                 EMAIL=EMAIL, MC=MC, USDOT=USDOT, QUOTE_URL=QUOTE_URL, GA_ID=GA_ID)


def fill(text, **extra):
    values = dict(CONSTANTS, **extra)
    return re.sub(r"\{\{(\w+)\}\}", lambda m: str(values[m.group(1)]), text)


def quote_form(vehicle="Car", enclosed=False):
    types = ["Car", "SUV", "Pickup", "Van", "Motorcycle", "Other"]
    options = "".join(f"<option{' selected' if t == vehicle else ''}>{t}</option>" for t in types)
    return QUOTE_FORM.format(TYPE_OPTIONS=options, ENCLOSED=" selected" if enclosed else "", **CONSTANTS)


def faq_schema(body):
    """FAQPage schema from the <details><summary>Q</summary><p>A</p></details> blocks of a page."""
    pairs = re.findall(r"<details><summary>(.*?)</summary>\s*<p>(.*?)</p></details>", body, re.S)
    if not pairs:
        return None
    strip = lambda s: re.sub(r"<[^>]+>", "", s).strip()
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}}
        for q, a in pairs]}


def build():
    sitemap = []
    for src in sorted((ROOT / "pages").glob("*.html")):
        raw = src.read_text()
        head, body = re.match(r"\s*<!--(.*?)-->(.*)", raw, re.S).groups()
        meta = dict(line.split(":", 1) for line in head.strip().splitlines())
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        path = meta["path"]
        url = SITE if path == "index.html" else SITE + path
        body = body.replace("{{HEAVY_FORM}}", HEAVY_FORM.format(**CONSTANTS))
        body = body.replace("{{QUOTE_FORM}}", quote_form(meta.get("vehicle", "Car"), meta.get("trailer") == "enclosed"))
        body = fill(body)
        graph = [ORG]
        if path != "index.html":
            graph.append({"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
                {"@type": "ListItem", "position": 2, "name": meta.get("crumb", meta["title"].split("|")[0].strip()), "item": url}]})
        if meta.get("service"):
            graph.append({"@type": "Service", "serviceType": meta["service"], "provider": {"@id": SITE + "#org"},
                          "areaServed": "US", "url": url})
        faq = faq_schema(body)
        if faq:
            graph.append(faq)
        current = ' aria-current="page"'
        nav = "".join(f'<a href="/{href}"{current if href == path else ""}>{label}</a>' for href, label in NAV)
        head_index = ('<meta name="robots" content="noindex">' if meta.get("priority") == "none"
                      else f'<link rel="canonical" href="{url}">')
        html = LAYOUT.format(head_index=head_index, title=meta["title"], description=meta["description"], url=url, body=body.strip(),
                             schema=json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False),
                             nav=nav, quote_link="#quote", year=date.today().year, **CONSTANTS)
        (ROOT / path).write_text(html)
        if meta.get("priority") != "none":
            sitemap.append((url, meta.get("priority", "0.6")))
    today = date.today().isoformat()
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{today}</lastmod><priority>{p}</priority></url>\n" for u, p in sitemap)
        + "</urlset>\n")
    print("built", len(sitemap), "pages")


if __name__ == "__main__":
    build()
