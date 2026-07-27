import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


SITES = [
    ("СКБ Контур", "https://kontur.ru"),
    ("Saby", "https://saby.ru"),
    ("Битрикс24", "https://www.bitrix24.ru"),
    ("amoCRM", "https://www.amocrm.ru"),
    ("Mindbox", "https://mindbox.ru"),
    ("Calltouch", "https://www.calltouch.ru"),
    ("UIS", "https://www.uiscom.ru"),
    ("MANGO OFFICE", "https://www.mango-office.ru"),
    ("Roistat", "https://roistat.com/ru"),
    ("Carrot quest", "https://www.carrotquest.io"),
    ("Envybox", "https://envybox.io"),
    ("Jivo", "https://www.jivo.ru"),
    ("Usedesk", "https://usedesk.ru"),
    ("Naumen", "https://www.naumen.ru"),
    ("Directum", "https://www.directum.ru"),
    ("ELMA365", "https://elma365.com/ru"),
    ("Planfix", "https://planfix.ru"),
    ("Kaiten", "https://kaiten.ru"),
    ("WEEEK", "https://weeek.net/ru"),
    ("Pyrus", "https://pyrus.com/ru"),
    ("Selectel", "https://selectel.ru"),
    ("Cloud.ru", "https://cloud.ru"),
    ("Timeweb Cloud", "https://timeweb.cloud"),
    ("MTS Link", "https://mts-link.ru"),
    ("Webinar", "https://webinar.ru"),
    ("Teachbase", "https://teachbase.ru"),
    ("Unisender", "https://www.unisender.com/ru"),
    ("Sendsay", "https://sendsay.ru"),
    ("DashaMail", "https://dashamail.ru"),
    ("Altcraft", "https://altcraft.com/ru"),
    ("retailCRM", "https://www.retailcrm.ru"),
    ("МойСклад", "https://www.moysklad.ru"),
    ("Мегаплан", "https://megaplan.ru"),
    ("Huntflow", "https://huntflow.ru"),
    ("Поток", "https://potok.io"),
    ("FriendWork", "https://friend.work"),
    ("Skillaz", "https://skillaz.ru"),
    ("ЭкспаСофт", "https://expasoft.com"),
    ("Pressfeed", "https://pressfeed.ru"),
    ("Workspace", "https://workspace.ru"),
    ("Kokoc Group", "https://kokoc.com"),
    ("Комплето", "https://completo.ru"),
    ("TexTerra", "https://texterra.ru"),
    ("AGIMA", "https://www.agima.ru"),
    ("КРОК", "https://www.croc.ru"),
    ("Первый Бит", "https://www.1cbit.ru"),
    ("КОРУС Консалтинг", "https://korusconsulting.ru"),
    ("Инфосистемы Джет", "https://www.jetinfo.ru"),
    ("iSpring", "https://www.ispring.ru"),
    ("Контур Толк", "https://kontur.ru/talk"),
]

COMMON_PATHS = (
    "", "/contacts", "/company/contacts", "/about/contacts", "/rekvizity",
)
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b")
BAD_PARTS = ("example.", "wixpress", "sentry", "cloudflare", "schema.org")
BAD_TLDS = (".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif")


def clean_email(value):
    value = value.strip(" \t\r\n<>.,;:'\"()[]{}")
    low = value.lower()
    return value if not any(x in low for x in BAD_PARTS) and not low.endswith(BAD_TLDS) else None


def fetch(session, url):
    try:
        r = session.get(url, timeout=5, allow_redirects=True)
        if r.ok and "text/html" in r.headers.get("content-type", ""):
            return r
    except requests.RequestException:
        pass
    return None


def main():
    def collect(item):
        idx, (name, base) = item
        session = requests.Session()
        session.headers["User-Agent"] = "Mozilla/5.0 (compatible; public-contact-research/1.0)"
        seen = set()
        found = {}
        title = ""
        for path in COMMON_PATHS:
            url = urljoin(base.rstrip("/") + "/", path.lstrip("/"))
            if url in seen:
                continue
            seen.add(url)
            r = fetch(session, url)
            if not r:
                continue
            if not title:
                soup = BeautifulSoup(r.text, "html.parser")
                title = soup.title.get_text(" ", strip=True) if soup.title else ""
            for raw in EMAIL_RE.findall(r.text.replace("&#64;", "@")):
                email = clean_email(raw)
                if email:
                    found.setdefault(email.lower(), r.url)
        host = urlparse(base).hostname.removeprefix("www.")
        preferred = [(e, s) for e, s in found.items() if e.rsplit("@", 1)[-1].endswith(host)]
        chosen = (preferred or list(found.items()))[:3]
        pairs = "; ".join(f"{email} [{src}]" for email, src in chosen)
        return idx, f"{idx:02d}\t{name}\t{base}\t{title[:100]}\t{pairs}"

    results = []
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(collect, item) for item in enumerate(SITES, 1)]
        for future in as_completed(futures):
            results.append(future.result())
    for _, line in sorted(results):
        print(line)


if __name__ == "__main__":
    sys.exit(main())
