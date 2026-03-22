import asyncio
from playwright.async_api import async_playwright

# -------------------------------------------------------------------------------------
# IMPORTANT NOTE ON ANTI-BOT PROTECTIONS:
# Many law firms (e.g. Nishimura, Mori Hamada) use Cloudflare or Imperva to block bots.
# If you get '403 Forbidden' or empty results, change headless=True to headless=False
# in the scrape_all_firms launcher, or use a package like 'playwright-stealth'.
# -------------------------------------------------------------------------------------

# ======= 1. NISHIMURA & ASAHI =======
async def scrape_nishimura(query: str, p) -> list:
    results = []
    try:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 1. Open the main Knowledge search page
        await page.goto("https://www.nishimura.com/ja/knowledge", timeout=20000)
        
        # 2. Wait for the keyword input box and fill it
        search_input_selector = 'input[id^="edit-search-keywords-all"]'
        await page.wait_for_selector(search_input_selector, timeout=10000)
        await page.fill(search_input_selector, query)
        
        # 3. Press Enter to submit the search form and wait for the page to navigate
        async with page.expect_navigation(timeout=20000):
            await page.press(search_input_selector, 'Enter')
        
        # 4. Wait for the result elements to load on the new page
        await page.wait_for_selector('a:has(h3)', timeout=15000)
        
        # Await the list completely before slicing the top 3 items
        items = (await page.query_selector_all('a:has(h3)'))[:3]
        
        for item in items:
            title_el = await item.query_selector('h3')
            title = await title_el.inner_text() if title_el else "No Title"
            
            link = await item.get_attribute('href')
            if link and link.startswith('/'): link = f"https://www.nishimura.com{link}"
            
            summary_paras = await item.query_selector_all('dd p')
            summary = " | ".join([await p.inner_text() for p in summary_paras]) if summary_paras else "Details available on site"
            
            results.append({"firm": "Nishimura & Asahi", "title": title.strip(), "summary": summary.strip(), "link": link})
        await browser.close()
    except Exception as e: print(f"[Nishimura] Error: {e}")
    return results

# ======= 2. MORI HAMADA & MATSUMOTO =======
async def scrape_mhm(query: str, p) -> list:
    results = []
    try:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.morihamada.com/en/search/?q={query}", timeout=15000)
        # TODO: Find Mori Hamada's search result CSS
        # await page.wait_for_selector('.result-item', timeout=5000)
        await browser.close()
    except Exception as e: print(f"[MHM] Error: {e}")
    return results

# ======= 3. NAGASHIMA OHNO & TSUNEMATSU =======
async def scrape_not(query: str, p) -> list:
    results = []
    try:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.nagashima.com/?s={query}", timeout=15000)
        # TODO: Implement CSS query
        await browser.close()
    except Exception as e: print(f"[NO&T] Error: {e}")
    return results

# ======= 4. ATSUMI & SAKAI =======
async def scrape_atsumi(query: str, p) -> list:
    results = []
    try:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.aplawjapan.com/search?q={query}", timeout=15000)
        # TODO
        await browser.close()
    except Exception as e: print(f"[Atsumi] Error: {e}")
    return results

# ======= 5. ANDERSON MORI & TOMOTSUNE =======
async def scrape_amt(query: str, p) -> list:
    results = []
    try:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.amt-law.com/search/?q={query}", timeout=15000)
        # TODO
        await browser.close()
    except Exception as e: print(f"[AMT] Error: {e}")
    return results

# ======= 6. CITY-YUWA PARTNERS =======
async def scrape_cityyuwa(query: str, p) -> list:
    results = []
    try:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.city-yuwa.com/?s={query}", timeout=15000)
        await browser.close()
    except Exception as e: print(f"[City-Yuwa] Error: {e}")
    return results

# ======= 7. HAYABUSA ASUKA =======
async def scrape_hayabusa(query: str, p) -> list:
    results = []
    try:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.halaw.jp/?s={query}", timeout=15000)
        await browser.close()
    except Exception as e: print(f"[Hayabusa] Error: {e}")
    return results

# ======= 8. KITAHAMA PARTNERS =======
async def scrape_kitahama(query: str, p) -> list:
    results = []
    try:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.kitahama.or.jp/?s={query}", timeout=15000)
        await browser.close()
    except Exception as e: print(f"[Kitahama] Error: {e}")
    return results

# ======= 9. MIURA & PARTNERS =======
async def scrape_miura(query: str, p) -> list:
    results = []
    try:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.miura-partners.com/?s={query}", timeout=15000)
        await browser.close()
    except Exception as e: print(f"[Miura] Error: {e}")
    return results

# ======= 10. USHIJIMA & PARTNERS =======
async def scrape_ushijima(query: str, p) -> list:
    results = []
    try:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.ushijima-law.gr.jp/?s={query}", timeout=15000)
        await browser.close()
    except Exception as e: print(f"[Ushijima] Error: {e}")
    return results

# ======= 11. MOMO-O, MATSUO & NAMBA =======
async def scrape_mmn(query: str, p) -> list:
    results = []
    try:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.mmn-law.gr.jp/search?q={query}", timeout=15000)
        await browser.close()
    except Exception as e: print(f"[MMN] Error: {e}")
    return results

# ======= 12. ONE ASIA LAWYERS =======
async def scrape_oneasia(query: str, p) -> list:
    results = []
    try:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://oneasia.legal/?s={query}", timeout=15000)
        await browser.close()
    except Exception as e: print(f"[One Asia] Error: {e}")
    return results

# ======= 13. AUTHENSE LAW OFFICES =======
async def scrape_authense(query: str, p) -> list:
    results = []
    try:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.authense.jp/?s={query}", timeout=15000)
        await browser.close()
    except Exception as e: print(f"[Authense] Error: {e}")
    return results

# ======= 14. SPRING LAW =======
async def scrape_spring(query: str, p) -> list:
    results = []
    try:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://spring-partners.com/?s={query}", timeout=15000)
        await browser.close()
    except Exception as e: print(f"[Spring] Error: {e}")
    return results

# ==========================================================
# MASTER LAUNCHER: Runs all 14 scrapers simultaneously
# ==========================================================
async def scrape_all_firms(query: str) -> list:
    print(f"Executing Master Scraper across 14 firms for query: '{query}'")
    
    async with async_playwright() as p:
        # We start the tasks concurrently
        tasks = [
            scrape_nishimura(query, p),
            scrape_mhm(query, p),
            scrape_not(query, p),
            scrape_atsumi(query, p),
            scrape_amt(query, p),
            scrape_cityyuwa(query, p),
            scrape_hayabusa(query, p),
            scrape_kitahama(query, p),
            scrape_miura(query, p),
            scrape_ushijima(query, p),
            scrape_mmn(query, p),
            scrape_oneasia(query, p),
            scrape_authense(query, p),
            scrape_spring(query, p)
        ]
        
        results_lists = await asyncio.gather(*tasks)
        
        # Merge the parallel results into a single flat list
        flattened_results = []
        for firm_data in results_lists:
            flattened_results.extend(firm_data)
            
        return flattened_results
