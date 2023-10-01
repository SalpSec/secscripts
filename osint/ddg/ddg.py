from bs4 import BeautifulSoup
import requests
import urllib3 as urllib
from urllib.parse import quote, urlparse, unquote_plus
import sys

urllib.disable_warnings()

BASE_URI="https://html.duckduckgo.com/html/"
USER_AGENT="Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0"
PROXY={"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
PAGES=10

def query_ddg(data: dict) -> BeautifulSoup | None:
    headers = {
        'User-Agent': USER_AGENT,
        'Origin': 'https://html.duckduckgo.com',
        'Referer': 'https://html.duckduckgo.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'DNT': '1',
        }
    cookies = {
        'kl': 'wt-wt',
    }
    response = requests.post(BASE_URI, headers=headers, data=data, cookies=cookies, proxies=PROXY, verify=False)
    parsed = BeautifulSoup(response.text, 'html.parser')
    return parsed

def get_result_links(parsed_data: BeautifulSoup) -> list[tuple[str, str]]:
    for topic in parsed_data.find_all('div', {'id': 'links', 'class': 'results'}):
        for result in topic.find_all('h2', {'class': 'result__title'}):
            for a in result.find_all('a'):
                href = a.get("href")
                if "duckduckgo.com" in href:
                    print(href)
                    ddg_url =urlparse(href)
                    ddg_query = ddg_url.query
                    url = unquote_plus(ddg_query.split("=")[1]).split("&")[0]
                else:
                    url = href
                title = a.get_text()
                yield (url, title)

def get_next_page(parsed_data: BeautifulSoup) -> BeautifulSoup | None:
    next_page = None
    div = parsed_data.find('div', {'class': 'nav-link'})
    if div:
        form = div.find('form', {'action': '/html/'})
        if form:
            data = {
                'q': form.find('input', {'name': 'q'}).get('value'),
                's': form.find('input', {'name': 's'}).get('value'),
                'nextParams': form.find('input', {'name': 'nextParams'}).get('value'),
                'v': form.find('input', {'name': 'v'}).get('value'),
                'o': form.find('input', {'name': 'o'}).get('value'),
                'dc': form.find('input', {'name': 'dc'}).get('value'),
                'api': form.find('input', {'name': 'api'}).get('value'),
                'vqd': form.find('input', {'name': 'vqd'}).get('value'),
                'kl': form.find('input', {'name': 'kl'}).get('value'),
            }
            next_page = query_ddg(data)
    return next_page


def get_results(query, pages=PAGES):
    curr_page = 1
    result = query_ddg({'q': query, 'b':'', 'kl': '', 'df': ''})
    while result is not None and curr_page <= pages:
        for url, title in get_result_links(result):
            yield (url, title)
        result = get_next_page(result)
        curr_page += 1

if __name__ == '__main__':
    query = " ".join(sys.argv[1:])
    print(f"[ddg] Searching ddg for '{query}' using the call {BASE_URI}:")
    for url, title in get_results(query):
        print(f"{url} | {title}")
