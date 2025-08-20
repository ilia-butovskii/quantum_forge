#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для скачивания и очистки текстов с фандом-сайтов
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urljoin, urlparse
import time
from tqdm import tqdm
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FandomScraper:
    def __init__(self, base_url, output_dir="knowledge_base"):
        """
        Инициализация скрапера
        
        Args:
            base_url (str): Базовый URL фандом-сайта (например, "https://starwars.fandom.com")
            output_dir (str): Папка для сохранения результатов
        """
        self.base_url = base_url.rstrip('/')
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Создаем папку для результатов
        os.makedirs(output_dir, exist_ok=True)
        
    def clean_text(self, text):
        """
        Очистка текста от лишних символов и форматирования
        """
        # Удаляем множественные пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text)
        # Удаляем специальные символы
        text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)\[\]]', '', text)
        # Удаляем лишние пробелы в начале и конце
        text = text.strip()
        return text
    
    def extract_content(self, soup):
        """
        Извлечение основного контента со страницы
        """
        # Удаляем ненужные элементы
        for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Удаляем элементы навигации и меню
        for element in soup.find_all(class_=re.compile(r'(nav|menu|sidebar|breadcrumb|toc)')):
            element.decompose()
        
        # Ищем основной контент
        content_selectors = [
            '.mw-parser-output',
            '.content',
            '.main-content',
            '#content',
            'article',
            '.article-content'
        ]
        
        content = None
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                break
        
        if not content:
            # Если не нашли по селекторам, берем body
            content = soup.find('body')
        
        if content:
            # Извлекаем текст
            text = content.get_text(separator=' ', strip=True)
            return self.clean_text(text)
        
        return ""
    
    def get_page_title(self, soup):
        """
        Извлечение заголовка страницы
        """
        title = soup.find('title')
        if title:
            return title.get_text().strip()
        return "Untitled"
    
    def scrape_page(self, url):
        """
        Скачивание и обработка одной страницы
        """
        try:
            logger.info(f"Скачиваю страницу: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = self.get_page_title(soup)
            content = self.extract_content(soup)
            
            return {
                'url': url,
                'title': title,
                'content': content
            }
            
        except Exception as e:
            logger.error(f"Ошибка при скачивании {url}: {e}")
            return None
    
    def save_page(self, page_data, filename=None):
        """
        Сохранение страницы в файл
        """
        if not page_data or not page_data['content']:
            return None
        
        if not filename:
            # Создаем имя файла из заголовка
            filename = re.sub(r'[^\w\s-]', '', page_data['title'])
            filename = re.sub(r'[-\s]+', '-', filename)
            filename = filename.strip('-')[:100]  # Ограничиваем длину
            filename = f"{filename}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Заголовок: {page_data['title']}\n")
                f.write(f"URL: {page_data['url']}\n")
                f.write("=" * 50 + "\n\n")
                f.write(page_data['content'])
            
            logger.info(f"Сохранен файл: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении файла {filepath}: {e}")
            return None
    
    def scrape_pages(self, urls):
        """
        Скачивание множества страниц
        """
        results = []
        
        for url in tqdm(urls, desc="Скачивание страниц"):
            page_data = self.scrape_page(url)
            if page_data:
                filepath = self.save_page(page_data)
                if filepath:
                    results.append({
                        'url': page_data['url'],
                        'title': page_data['title'],
                        'filepath': filepath
                    })
            
            # Небольшая задержка между запросами
            time.sleep(1)
        
        return results

def main():
    """
    Основная функция для демонстрации работы скрапера
    """
    # Пример использования для Star Wars
    base_url = "https://starwars.fandom.com"
    
    # Список ключевых страниц Star Wars (пример)
    star_wars_pages = [
        "https://starwars.fandom.com/wiki/Darth_Vader",
        "https://starwars.fandom.com/wiki/Luke_Skywalker",
        "https://starwars.fandom.com/wiki/Death_Star",
        "https://starwars.fandom.com/wiki/The_Force",
        "https://starwars.fandom.com/wiki/Lightsaber",
        "https://starwars.fandom.com/wiki/Jedi",
        "https://starwars.fandom.com/wiki/Sith",
        "https://starwars.fandom.com/wiki/Han_Solo",
        "https://starwars.fandom.com/wiki/Princess_Leia",
        "https://starwars.fandom.com/wiki/Chewbacca",
        "https://starwars.fandom.com/wiki/R2-D2",
        "https://starwars.fandom.com/wiki/C-3PO",
        "https://starwars.fandom.com/wiki/Yoda",
        "https://starwars.fandom.com/wiki/Obi-Wan_Kenobi",
        "https://starwars.fandom.com/wiki/Emperor_Palpatine",
        "https://starwars.fandom.com/wiki/Boba_Fett",
        "https://starwars.fandom.com/wiki/Millennium_Falcon",
        "https://starwars.fandom.com/wiki/X-wing_starfighter",
        "https://starwars.fandom.com/wiki/TIE_fighter",
        "https://starwars.fandom.com/wiki/Blaster",
        "https://starwars.fandom.com/wiki/Hyperdrive",
        "https://starwars.fandom.com/wiki/Hologram",
        "https://starwars.fandom.com/wiki/Droid",
        "https://starwars.fandom.com/wiki/Clone_trooper",
        "https://starwars.fandom.com/wiki/Stormtrooper",
        "https://starwars.fandom.com/wiki/Rebel_Alliance",
        "https://starwars.fandom.com/wiki/Galactic_Empire",
        "https://starwars.fandom.com/wiki/Republic",
        "https://starwars.fandom.com/wiki/Coruscant",
        "https://starwars.fandom.com/wiki/Tatooine",
        "https://starwars.fandom.com/wiki/Hoth",
        "https://starwars.fandom.com/wiki/Dagobah",
        "https://starwars.fandom.com/wiki/Bespin",
        "https://starwars.fandom.com/wiki/Endor",
        "https://starwars.fandom.com/wiki/Naboo",
        "https://starwars.fandom.com/wiki/Kamino",
        "https://starwars.fandom.com/wiki/Geonosis"
    ]
    
    scraper = FandomScraper(base_url)
    results = scraper.scrape_pages(star_wars_pages)
    
    # Сохраняем метаданные
    metadata = {
        'base_url': base_url,
        'total_pages': len(results),
        'pages': results
    }
    
    with open(os.path.join(scraper.output_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Скачано {len(results)} страниц")
    logger.info(f"Результаты сохранены в папке: {scraper.output_dir}")

if __name__ == "__main__":
    main()
