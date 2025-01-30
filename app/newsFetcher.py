import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import feedparser
from sqlalchemy.exc import IntegrityError
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import fromstring
from app.database_manager import DatabaseManager, News
from dotenv import load_dotenv
import cloudscraper
from app.time_conf import format_and_validate_date_time
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
            pub_date = item.find("pubDate").text
            media_content = item.find("{http://search.yahoo.com/mrss/}content")
            image_url = media_content.attrib.get('url') if media_content is not None else None

            news_item = {
                "link": link,
                "headline": title,
                "image_url": image_url,
                "publish_date": format_and_validate_date_time(pub_date),
                "site_name": "Bianet",
                "ziman": "kur"
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
                'publish_date': format_and_validate_date_time(pub_date),
                'site_name': 'Diyarname',
                "ziman": "kur"
            })
        return data

    @staticmethod
    def scrape_and_feed_ajansa_welat(url, lang):
        rss_response = requests.get(url)
        rss_root = ET.fromstring(rss_response.content)
        news_items = []

        for item in rss_root.findall(".//item"):
            title = item.find("title").text
            link = item.find("link").text
            pub_date = item.find("pubDate").text

            # Create a base news dictionary
            news_item = {
                "headline": title,
                "link": link,
                "publish_date": format_and_validate_date_time(pub_date),
                "image_url": None,  # To be filled later via scraping
                'site_name': 'Ajansa Welat',
                "ziman": "kur" if lang == 'kur' else "zza",
                
            }
            news_items.append(news_item)

        # Step 2: Scrape the site for image URLs
        page_url =  'https://ajansawelat.com/' if lang == "kur" else 'https://ajansawelat.com/ki'
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
            print(news_item)
        
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
                'publish_date': format_and_validate_date_time(date),
                'site_name': 'Xwebûn',
                "ziman": "kur"
            })
        return data
    @staticmethod
    def rojavatv_rss():
        rss_url = "https://rojavatv.net/rss"
        feed = feedparser.parse(rss_url)
        data = []
        for entry in feed.entries:
            content_html = entry.get("content", [{}])[0].get("value", "")
            soup = BeautifulSoup(content_html, "html.parser")
            img_tag = soup.find("img")
            image_url = ""
            if img_tag:
                image_url = img_tag["src"]
            else:
                image_url = None
            data.append({
                'link': entry.link,
                'headline': entry.title,
                'image_url': image_url,
                'publish_date': format_and_validate_date_time(entry.published) if 'published' in entry else datetime.now().isoformat(),
                'site_name': "Rojava Tv",
                "ziman": "kur"
            })
        return data
    def channel8_rss():
        rss_url = "https://channel8.com/kurmanci/feed"
        feed = feedparser.parse(rss_url)
        scraper = cloudscraper.create_scraper()
        data = []
        image_url = ""
        for entry in feed.entries:
            response = scraper.get(entry.link)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                thumbnail_div = soup.find('div', class_='thumbnail-stretch-area')
                if thumbnail_div:
                    img_tag = thumbnail_div.find('img')
                    image_url = img_tag['src'] if img_tag else None
            data.append({
                'link': entry.link,
                'headline': entry.title,
                'image_url': image_url,
                'publish_date': format_and_validate_date_time(entry.published) if 'published' in entry else datetime.now().isoformat(),
                'site_name': "Channel 8",
                "ziman": "kur"
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
                'publish_date': format_and_validate_date_time(entry.published) if 'published' in entry else datetime.now().isoformat(),
                'site_name': site_name,
                "ziman": "kur"
            })
        return data
    def fetch_zazaki_news_rss(feed_url, site_name):
        feed = feedparser.parse(feed_url)
        data = []

        if feed.bozo:
            root = fromstring(feed.bozo_exception.args[0].decode("utf-8"))
            items = root.findall(".//item")
            entries = [{
                "link": i.findtext("link"),
                "headline": i.findtext("title", "No Title"),
                "image_url": (i.find("enclosure").get("url") if i.find("enclosure") is not None else None),
                "publish_date": format_and_validate_date_time(i.findtext("pubDate")),
                "site_name": site_name,
                "ziman": "zza"
            } for i in items]
            data.extend(entries)
        else:
            data = [{
                "link": e.link,
                "headline": e.title,
                "image_url": next((l.href for l in e.links if l.rel == "enclosure" and "image" in l.type), None) if "links" in e else None,
                "publish_date": format_and_validate_date_time(e.published) if "published" in e else datetime.now().isoformat(),
                "site_name": site_name,
                "ziman": "zza"
            } for e in feed.entries[:14]]

        return data


    def fetch_and_save_allNews():
        saving = ""
        try:
            diyarname_data = NewsFetcher.diyarname_rss()
            bianet_data = NewsFetcher.fetch_bianet_rss()
            ajansa_welat_kur = NewsFetcher.scrape_and_feed_ajansa_welat('https://ajansawelat.com/feed/', lang= "kur")
            ajansa_welat_za = NewsFetcher.scrape_and_feed_ajansa_welat('https://ajansawelat.com/ki/feed/', lang= "zza")
            xwebun_data = NewsFetcher.scrape_xwebun()
            nuhev_data = NewsFetcher.fetch_rss('https://www.nuhev.com/feed/', 'Nuhev')
            zazaki_news_data = NewsFetcher.fetch_zazaki_news_rss('https://www.zazakinews.com/rss/tum-mansetler', 'Zazakî News')
            rojavatv_data = NewsFetcher.rojavatv_rss()
            channel8_data = NewsFetcher.channel8_rss()
            all_news = diyarname_data + bianet_data + ajansa_welat_kur + ajansa_welat_za+ xwebun_data + nuhev_data+ zazaki_news_data + rojavatv_data + channel8_data
            saving = db_manager.save_news(all_news)
        except Exception as e:
            print(f"Error during scraping or saving: {e}")
        return saving