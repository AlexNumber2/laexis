import os
import re
try:
    from bs4 import BeautifulSoup
except ImportError:
    import subprocess
    subprocess.check_call(["pip", "install", "beautifulsoup4"])
    from bs4 import BeautifulSoup

def analyze(filename):
    print(f"\n=== {filename} ===")
    filepath = f"C:\\Users\\Alex\\.gemini\\antigravity\\brain\\a67276d9-1f6d-48dc-9cdc-583101eccf49\\{filename}"
    if not os.path.exists(filepath):
        print("File not found.")
        return
        
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    # Try finding common article wrappers
    articles = soup.find_all(['article', 'li', 'div'], class_=re.compile(r'post|item|article|news|topic|list', re.I))
    for i, a in enumerate(articles[:5]):
        link = a.find('a')
        
        # Try finding a title element
        title_el = a.find(['h2', 'h3', 'h4', 'div', 'p', 'span'], class_=re.compile(r'title|heading|text|name', re.I))
        title = title_el.text.strip() if title_el else (link.text.strip() if link else a.text.strip()[:50])
        
        url = link['href'] if link and link.has_attr('href') else 'No URL'
        print(f"[{i}] {a.name}.{'.'.join(a.get('class', []))} -> Title: {title[:60]} | Link: {url}")

for f in ["cityyuwa_dump.html", "miura_dump.html", "oneasia_dump.html"]:
    analyze(f)
