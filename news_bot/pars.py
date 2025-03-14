import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def clean_url(url):
    """
    Очищает URL, оставляя только доменное имя.
    Например: https://kommersant.ru/doc/7553098 -> kommersant.ru
    """
    parsed_url = urlparse(url)
    return parsed_url.netloc  # Возвращает только доменное имя

def parse_rbc():
    """Получить новости с RBC."""
    url = 'https://www.rbc.ru'
    print(f"Fetching from {url}...")

    try:
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")

        soup = BeautifulSoup(response.content, 'html.parser')
        rbc_items = []

        for item in soup.select('div.q-item.js-rm-central-column-item.js-load-item')[:10]:
            title_element = item.find("span", class_='q-item__title js-rm-central-column-item-text')
            link_element = item.find("a", class_='q-item__link', href=True)

            if title_element and link_element:
                title = title_element.text.strip()
                full_link = link_element['href'].strip()
                clean_link = clean_url(full_link)  # Очищенная ссылка
                print(f"Found news: {title} - {clean_link}")
                rbc_items.append({'title': title, 'link': clean_link})

        return rbc_items

    except Exception as e:
        print(f"Error parsing RBC: {e}")
        return []


def parse_kommersant():
    """Получить новости с Kommersant."""
    url = 'https://www.kommersant.ru'
    print(f"Fetching from {url}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')
        kom_items = []

        for item in soup.select('.uho__link')[:10]:
            title = item.text.strip()
            full_link = url + item['href']
            clean_link = clean_url(full_link)  # Очищенная ссылка
            print(f"Found news: {title} - {clean_link}")
            kom_items.append({'title': title, 'link': clean_link})

        return kom_items

    except Exception as e:
        print(f"Error parsing Kommersant: {e}")
        return []


def parse_ria():
    """Получить новости с Ria.ru."""
    url = 'https://ria.ru'
    print(f"Fetching from {url}...")

    try:
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")

        soup = BeautifulSoup(response.content, 'html.parser')
        ria_items = []

        for post in soup.find_all('div', class_="cell-list__item m-no-image")[:10]:
            title_element = post.find("a", class_='cell-list__item-link')
            if title_element:
                title = title_element.text.strip()
                full_link = title_element['href'].strip()
                clean_link = clean_url(full_link)  # Очищенная ссылка
                print(f"Found news: {title} - {clean_link}")
                ria_items.append({'title': title, 'link': clean_link})

        return ria_items

    except Exception as e:
        print(f"Error parsing RIA: {e}")
        return []


def parse_cnn():
    """Получить новости с CNN."""
    url = 'https://edition.cnn.com'
    print(f"Fetching from {url}...")

    try:
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")

        soup = BeautifulSoup(response.content, 'html.parser')
        cnn_items = []

        for container in soup.select('.container__item')[:10]:
            title_element = container.find(['span', 'a'], class_='container__headline-text')
            link_element = container.find('a', href=True)

            if title_element and link_element:
                title = title_element.text.strip()
                full_link = 'https://edition.cnn.com' + link_element['href']
                clean_link = clean_url(full_link)  # Очищенная ссылка
                print(f"Found news: {title} - {clean_link}")
                cnn_items.append({'title': title, 'link': clean_link})

        return cnn_items

    except Exception as e:
        print(f"Error parsing CNN: {e}")
        return []