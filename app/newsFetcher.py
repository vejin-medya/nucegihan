import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import feedparser
from sqlalchemy.exc import IntegrityError
import xml.etree.ElementTree as ET
from app.database_manager import DatabaseManager, News
from dotenv import load_dotenv
load_dotenv()
db_url = os.getenv('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

db_manager = DatabaseManager(db_url)
class NewsFetcher:
    @staticmethod
    def fetch_bianet_rss():
        rss_url = "https://bianet.org/rss/kurdi"
        response = requests.get(rss_url)
        root = ET.fromstring(response.content)
        news_items = []

        for item in root.findall(".//item"):
            title = item.find("title").text
            link = item.find("link").text
            description = item.find("description").text
            pub_date = item.find("pubDate").text
            media_content = item.find("{http://search.yahoo.com/mrss/}content")
            image_url = media_content.attrib.get('url') if media_content is not None else None

            news_item = {
                "link": link,
                "headline": title,
                "image_url": image_url,
                "publish_date": pub_date,
                "site_name": "Bianet"
            }

            news_items.append(news_item)

        return news_items

    @staticmethod
    def diyarname_rss():
        rss_url = "https://diyarname.com/rss_news.php"
        response = requests.get(rss_url)
        response.encoding = 'utf-8'
        root = ET.fromstring(response.content)
        channel = root.find("channel")
        data = []
        for item in channel.findall("item")[:40]:
            title = item.find("title").text
            link = item.find("link").text
            pub_date = item.find("pubDate").text
            thumbnail = item.find("thumbnail").attrib.get("url", "")
            data.append({
                'link': link,
                'headline': title,
                'image_url': thumbnail,
                'publish_date': pub_date,
                'site_name': 'Diyarname'
            })
        return data

    @staticmethod
    def scrape_and_feed_ajansa_wela():
        # Step 1: Fetch and parse RSS feed
        rss_url = "https://ajansawelat.com/feed/"
        rss_response = requests.get(rss_url)
        rss_root = ET.fromstring(rss_response.content)
        news_items = []

        for item in rss_root.findall(".//item"):
            title = item.find("title").text
            link = item.find("link").text
            pub_date = item.find("pubDate").text

            # Create a base news dictionary
            news_item = {
                "title": title,
                "link": link,
                "published": pub_date,
                "image_url": None,  # To be filled later via scraping
            }
            news_items.append(news_item)

        # Step 2: Scrape the site for image URLs
        page_url = 'https://ajansawelat.com/'
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Map links to images from scraping
        scraped_articles = soup.find_all('div', class_="jeg_post")
        scraped_images = {}

        for article in scraped_articles:
            tag = article.find('h2', class_='jeg_post_title')
            if tag:
                link = tag.find('a')['href']
                image = article.find('img')
                if image and image.get('data-src'):
                    image_url = image['data-src'].replace("75x75", "350x350")
                    scraped_images[link] = image_url

        # Step 3: Combine RSS data with scraped images
        for news_item in news_items:
            if news_item['link'] in scraped_images:
                news_item['image_url'] = scraped_images[news_item['link']]

        
        return news_items

    @staticmethod
    def scrape_xwebun():
        url = 'https://xwebun2.org/cat/hemu/'
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        data = []
        articles = soup.find('div', class_="td-main-content-wrap td-container-wrap").find('div', class_='td_block_inner td-mc1-wrap')
        tags = articles.find_all('div', class_='td_module_flex td_module_flex_1 td_module_wrap td-animation-stack td-cpt-post')

        for item in tags:
            title_tag = item.find('h3', class_='entry-title')
            image_span = item.find('span', class_='entry-thumb')
            date_tag = item.find('time', class_='entry-date')

            title = title_tag.text if title_tag else None
            link = title_tag.a['href'] if title_tag and title_tag.a else None
            image_style = image_span.get('style', '') if image_span else None
            date = date_tag['datetime'] if date_tag else None

            if image_style:
                start = image_style.find("url('") + len("url('")
                end = image_style.find("')", start)
                image_url = image_style[start:end]
            else:
                image_url = None
            data.append({
                'link': link,
                'headline': title,
                'image_url': image_url,
                'publish_date': date,
                'site_name': 'Xwebûn'
            })
        return data

    @staticmethod
    def fetch_rss(feed_url, site_name):
        feed = feedparser.parse(feed_url)
        data = []
        for entry in feed.entries:
            data.append({
                'link': entry.link,
                'headline': entry.title,
                'image_url': entry.get('media_content', [{'url': ''}])[0]['url'],
                'publish_date': entry.published if 'published' in entry else datetime.now().isoformat(),
                'site_name': site_name
            })
        return data

    def fetch_and_save_allNews():
        saving = ""
        try:
            diyarname_data = NewsFetcher.diyarname_rss()
            bianet_data = NewsFetcher.fetch_bianet_rss()
            ajansa_welat_data = NewsFetcher.scrape_and_feed_ajansa_wela()
            xwebun_data = NewsFetcher.scrape_xwebun()
            nuhev_data = NewsFetcher.fetch_rss('https://www.nuhev.com/feed/', 'Nuhev')
            all_news = diyarname_data + bianet_data + ajansa_welat_data + xwebun_data + nuhev_data
            saving = db_manager.save_news(all_news)
        except Exception as e:
            print(f"Error during scraping or saving: {e}")
        return saving