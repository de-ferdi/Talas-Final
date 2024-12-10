import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from crawler_tribun import crawl_tribun
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Load JSON file
with open('news_websites_general.json') as json_file:
    websites = json.load(json_file)['websites']

def get_soup(url):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

def parse_article(link, website):
    try:
        soup = get_soup(link)
        content_div = soup.find(class_=website['content_class'])
        content = ' '.join(p.get_text(strip=True) for p in content_div.find_all('p')) if content_div else 'No content found'
        if(website['name'] == "Antara"):
            content = content_div.get_text(strip=True)
        return content
    except Exception as e:
        print(f"Error parsing article {link}: {e}")
        return 'No content found'

def parse_page(url, website):
    soup = get_soup(url)
    news_data = []
    articles = soup.find_all(website['article_tag'], class_=website['article_class'])
    print(f"Found {len(articles)} articles on page: {url}")

    for article in articles:
        title_tag = article.find(class_=website.get('title_class', None))
        if title_tag:
            title = title_tag.get_text(strip=True)
        else:
            title_tag = article.find('a')
            title = title_tag['title'] if 'title' in title_tag.attrs else title_tag.get_text(strip=True)

        link_tag = article.find('a')
        link = link_tag['href'] if link_tag else 'No link found'

        if not link.startswith('http'):
            link = 'No link found'

        date_tag = article.find(class_=website['date_class'])
        date = date_tag.get_text(strip=True) if date_tag else 'No date found'

        image_tag = article.find('img')
        print(image_tag)
        if website['name'] == "Antara":
            image = image_tag['data-src'] if image_tag else 'No image found'
        else:
            image = image_tag['src'] if image_tag else 'No image found'

        content = parse_article(link, website) if link != 'No link found' else 'No content found'
        if not content:
            content = "No content found"

        if link == 'No link found' and image == 'No image found' and content == 'No content found':
            print(f"Skipping article with title '{title}' due to missing data.")
            continue
        
        news_data.append({
            'title': title,
            'link': link,
            "image": image,
            'date': date,
            'content': content,
            'is_fake': 0,
            'media_bias': website['platform']
        })

    return news_data

def get_all_articles(base_url, website, max_pages=1):
    articles = []
    next_page = base_url
    print(base_url)
    current_page = 1

    while next_page and current_page <= max_pages:
        print(f"Crawling page {current_page}")
        articles.extend(parse_page(next_page, website))
        soup = get_soup(next_page)
        if website['name'] == 'Antara':
            next_page = f"{base_url}/{current_page + 1}"
        elif website['name'] == 'Suara':
            next_page = f"{base_url}?page={current_page + 1}"
        elif website['name'] == 'Detik':
            next_page = f"{base_url}/{current_page + 1}"
        elif website['name'] == 'Tribunnews':
            break
        else:
            next_button = soup.find(class_=website['next_page'])
            next_page = next_button["href"] if next_button else None
        current_page += 1
        time.sleep(2)
    return articles

def crawlerGeneral():
    all_news = []
    #tribun_data = crawl_tribun()
    #all_news = all_news + tribun_data

    for website in websites:
        try:
            base_url = website['url']
            scraped_news = get_all_articles(base_url, website)
            print(f"Scraped {len(scraped_news)} articles from {website['name']}")
            all_news.extend(scraped_news)
            time.sleep(2) 
        except requests.HTTPError as e:
            print(f"Failed to scrape {website['name']}: {e}")

    print(f"Total articles collected: {len(all_news)}")
    return all_news

if __name__ == "__main__":
    crawlerGeneral()
