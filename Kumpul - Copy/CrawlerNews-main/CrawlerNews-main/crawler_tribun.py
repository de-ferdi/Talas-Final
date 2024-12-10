from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

def scrape_tribun_news(url):
    driver = webdriver.Chrome()
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, 'animate-pulse'))
        )
        
        content = driver.page_source
        soup = BeautifulSoup(content, 'html.parser')
        
        articles = soup.find_all('li', class_="p1520 art-list pos_rel")
        news_data = []

        for article in articles:
            title_tag = article.find('h1') or article.find('h2') or article.find('h3') or article.find('h4')
            title = title_tag.get_text(strip=True) if title_tag else 'No Title'
            date_tag = article.find('time')
            date = date_tag.get_text(strip=True) if date_tag else 'No date found'

            link_tag = article.find('a')
            link = link_tag['href'] if link_tag else 'No link found'

            image_div = article.find('div', class_="fr mt5 pos_rel")
            image_tag = image_div.find('img') if image_div else None
            image = image_tag['src'] if image_tag else "No image found"

            # Parse konten artikel jika link valid
            if link != 'No link found':
                driver.get(link)
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                article_content = driver.page_source
                article_soup = BeautifulSoup(article_content, 'html.parser')
                content_paragraphs = article_soup.find(class_="side-article txt-article multi-fontsize").find_all("p")
                content = " ".join(p.get_text() for p in content_paragraphs)
            else:
                content = "No content found"

            # Simpan data jika valid
            if link != "#" and content != "No content found":
                news_data.append({
                    'title': title,
                    'content': content,
                    'date': date,
                    'link': link,
                    'image': image,
                    'is_fake': 0,
                    'media_bias': "tribun"
                })

    finally:
        driver.quit()

    return news_data

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def crawl_tribun():
    url = "https://www.tribunnews.com/nasional/politik"
    article_data = scrape_tribun_news(url)
    save_to_json(article_data, 'tribun_news.json')
    print(article_data)
    return article_data

if __name__ == "__main__":
    crawl_tribun()
