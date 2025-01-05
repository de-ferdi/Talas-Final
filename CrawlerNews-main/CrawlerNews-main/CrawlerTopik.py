import json
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Load JSON file
with open('news_websites_topik.json') as json_file:
    websites = json.load(json_file)['websites']

def get_soup(url):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

def parse_article(link, website):
    try:
        soup = get_soup(link)
        content_div = soup.find(class_=website['content_class'])
        if content_div:
            if website['name'] == 'Antara':
                my4_divs = content_div.find_all('div', class_='my-4')
                if my4_divs:
                    content = ' '.join(div.get_text(strip=True) for div in my4_divs)
                else:
                    content = ' '.join(p.get_text(strip=True) for p in content_div.find_all('p'))
            else:
                content = ' '.join(p.get_text(strip=True) for p in content_div.find_all('p'))
        else:
            content = 'No content found'
        return content
    except Exception as e:
        print(f"Error parsing article {link}: {e}")
        return 'No content found'


def parse_page(url, website):
    news_data = []

    if website['name'] == 'CNN Indonesia':
        driver = webdriver.Chrome()
        driver.get(url)
        print(url)

        try:
            WebDriverWait(driver, 20).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, 'animate-pulse'))
            )
            
            content = driver.page_source
            soup = BeautifulSoup(content, 'html.parser')
            
            articles = soup.find_all('article')
            
            for article in articles:
                title = article.find('h2').get_text(strip=True) if article.find('h2') else 'No Title found'
                date_tag = article.find('span', class_='text-xs text-cnn_black_light3')
                date = date_tag.get_text(strip=True) if date_tag else 'No date found'

                link_tag = article.find('a')
                link = link_tag['href'] if link_tag else 'No link found'

                if link and not link.startswith(('http://', 'https://')):
                    link = urljoin(url, link)

                image_tag = article.find('img')
                image = image_tag['src'] if image_tag else 'No image found'
                content = parse_article(link, website) if link != 'No link found' else 'No content found'
                if not content:
                    content = "No content found"

                if title == 'No Title found' and image == 'No image found' and content == 'No content found':
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
        
        finally:
            driver.quit()

    else:
        soup = get_soup(url)
        articles = soup.find_all(website['article_tag'], class_=website['article_class'])
        print(f"Found {len(articles)} articles on page: {url}")
        
        for article in articles:
            title_tag = article.find(class_=website.get('title_class', None))
            if title_tag:
                title = title_tag.get_text(strip=True)
            else:
                title_tag = article.find('a')
                if title_tag:
                    title = title_tag['title'] if 'title' in title_tag.attrs else title_tag.get_text(strip=True)
                else:
                    title = 'No title found'
            link_tag = article.find('a')
            link = link_tag['href'] if link_tag else 'No link found'

            date_tag = article.find(class_=website['date_class'])
            date = date_tag.get_text(strip=True) if date_tag else 'No date found'

            image_tag = article.find('img')
            if(website['name'] == 'Antara'):
                image = image_tag['data-src'] if image_tag else 'No image found'
            elif(website['name'] == 'Detik'):
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
            print(f"Appended article: {title}")

    return news_data

def get_all_articles(base_url, website, max_pages=2):
    articles = []
    next_page = base_url
    current_page = 1

    while next_page and current_page <= max_pages:
        print(f"Crawling page {current_page}")
        articles.extend(parse_page(next_page, website))
        if website['name'] in ['Antara', 'Suara', 'Detik']:
            next_page = f"{base_url}&page={current_page + 1}"
        else:
            soup = get_soup(next_page)
            next_button = soup.find(class_=website['next_page'])
            next_page = next_button["href"] if next_button else None
        current_page += 1
        time.sleep(2)
    return articles

def crawlerWithTopik(topik):
    topik = topik.replace(" ", "+")
    all_news = []
    for website in websites:
        try:
            base_url = website['url'] + topik
            print(f"Base URL: {base_url}")
            scraped_news = get_all_articles(base_url, website)
            print(f"Scraped {len(scraped_news)} articles from {website['name']}")
            all_news.extend(scraped_news)
            time.sleep(2)
        except requests.HTTPError as e:
            print(f"Failed to scrape {website['name']}: {e}")

    print(f"Total articles collected: {len(all_news)}")
    return all_news

if __name__ == "__main__":
    topik = input("Masukkan Topik: ")
    crawlerWithTopik(topik)
