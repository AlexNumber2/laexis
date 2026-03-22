from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# =========================
# 各律所数据抓取
# =========================

def fetch_nishimura():
    url = "https://www.nishimura.com/en/knowledge"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []

    for a in soup.select("a"):
        title = a.get_text(strip=True)
        link = a.get("href")

        if title and link and "/en/knowledge/" in link:
            if not link.startswith("http"):
                link = "https://www.nishimura.com" + link

            results.append({
                "title": title,
                "summary": title[:120],
                "url": link,
                "law_firm": "Nishimura & Asahi"
            })

    return results


def search_aplaw(keyword):
    url = f"https://www.aplawjapan.com/search?q={keyword}"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []

    for a in soup.select("a"):
        title = a.get_text(strip=True)
        link = a.get("href")

        if title and link and "/en/" in link:
            results.append({
                "title": title,
                "summary": title[:120],
                "url": link,
                "law_firm": "Atsumi & Sakai"
            })

    return results


def search_amt(keyword):
    url = f"https://www.amt-law.com/search/?q={keyword}"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []

    for a in soup.select("a"):
        title = a.get_text(strip=True)
        link = a.get("href")

        if title and link and "/en/" in link:
            if not link.startswith("http"):
                link = "https://www.amt-law.com" + link

            results.append({
                "title": title,
                "summary": title[:120],
                "url": link,
                "law_firm": "Anderson Mori & Tomotsune"
            })

    return results


# =========================
# 统一搜索接口
# =========================

@app.get("/search")
def search(q: str):
    results = []

    # 1. Nishimura（本地过滤）
    data1 = fetch_nishimura()
    for item in data1:
        if q.lower() in item["title"].lower():
            results.append(item)

    # 2. APLaw（远程搜索）
    results += search_aplaw(q)

    # 3. AMT（远程搜索）
    results += search_amt(q)

    return results