#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Основной скрипт для создания уникальной базы знаний
"""

import os
import sys
import logging
from pathlib import Path

# Импортируем наши модули
from scraper import FandomScraper
from term_replacer import TermReplacer, create_star_wars_terms_map

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('knowledge_base_creation.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_knowledge_base():
    """
    Основная функция для создания базы знаний
    """
    logger.info("Начинаем создание уникальной базы знаний")
    
    # 1. Настройка параметров
    base_url = "https://starwars.fandom.com"
    output_dir = "knowledge_base"
    
    # Список ключевых страниц Star Wars (30+ страниц)
    star_wars_pages = [
        # Персонажи
        "https://starwars.fandom.com/wiki/Darth_Vader",
        "https://starwars.fandom.com/wiki/Luke_Skywalker",
        "https://starwars.fandom.com/wiki/Han_Solo",
        "https://starwars.fandom.com/wiki/Princess_Leia",
        "https://starwars.fandom.com/wiki/Chewbacca",
        "https://starwars.fandom.com/wiki/R2-D2",
        "https://starwars.fandom.com/wiki/C-3PO",
        "https://starwars.fandom.com/wiki/Yoda",
        "https://starwars.fandom.com/wiki/Obi-Wan_Kenobi",
        "https://starwars.fandom.com/wiki/Emperor_Palpatine",
        "https://starwars.fandom.com/wiki/Boba_Fett",
        "https://starwars.fandom.com/wiki/Anakin_Skywalker",
        "https://starwars.fandom.com/wiki/Padme_Amidala",
        "https://starwars.fandom.com/wiki/Qui-Gon_Jinn",
        "https://starwars.fandom.com/wiki/Mace_Windu",
        
        # Объекты и технологии
        "https://starwars.fandom.com/wiki/Death_Star",
        "https://starwars.fandom.com/wiki/Lightsaber",
        "https://starwars.fandom.com/wiki/Millennium_Falcon",
        "https://starwars.fandom.com/wiki/X-wing_starfighter",
        "https://starwars.fandom.com/wiki/TIE_fighter",
        "https://starwars.fandom.com/wiki/Blaster",
        "https://starwars.fandom.com/wiki/Hyperdrive",
        "https://starwars.fandom.com/wiki/Hologram",
        "https://starwars.fandom.com/wiki/Droid",
        "https://starwars.fandom.com/wiki/AT-AT",
        "https://starwars.fandom.com/wiki/AT-ST",
        "https://starwars.fandom.com/wiki/Speeder_bike",
        
        # Организации и группы
        "https://starwars.fandom.com/wiki/Jedi",
        "https://starwars.fandom.com/wiki/Sith",
        "https://starwars.fandom.com/wiki/Clone_trooper",
        "https://starwars.fandom.com/wiki/Stormtrooper",
        "https://starwars.fandom.com/wiki/Rebel_Alliance",
        "https://starwars.fandom.com/wiki/Galactic_Empire",
        "https://starwars.fandom.com/wiki/Republic",
        "https://starwars.fandom.com/wiki/Separatists",
        "https://starwars.fandom.com/wiki/Trade_Federation",
        
        # Планеты и места
        "https://starwars.fandom.com/wiki/Coruscant",
        "https://starwars.fandom.com/wiki/Tatooine",
        "https://starwars.fandom.com/wiki/Hoth",
        "https://starwars.fandom.com/wiki/Dagobah",
        "https://starwars.fandom.com/wiki/Bespin",
        "https://starwars.fandom.com/wiki/Endor",
        "https://starwars.fandom.com/wiki/Naboo",
        "https://starwars.fandom.com/wiki/Kamino",
        "https://starwars.fandom.com/wiki/Geonosis",
        "https://starwars.fandom.com/wiki/Mustafar",
        "https://starwars.fandom.com/wiki/Utapau",
        "https://starwars.fandom.com/wiki/Felucia",
        "https://starwars.fandom.com/wiki/Mygeeto",
        "https://starwars.fandom.com/wiki/Saleucami",
        "https://starwars.fandom.com/wiki/Polis_Massa",
        "https://starwars.fandom.com/wiki/Alderaan",
        "https://starwars.fandom.com/wiki/Scarif",
        "https://starwars.fandom.com/wiki/Jedha",
        "https://starwars.fandom.com/wiki/Eadu",
        "https://starwars.fandom.com/wiki/Lah'mu",
        "https://starwars.fandom.com/wiki/Starkiller_Base",
        "https://starwars.fandom.com/wiki/Ahch-To",
        "https://starwars.fandom.com/wiki/Crait",
        "https://starwars.fandom.com/wiki/Cantonica",
        "https://starwars.fandom.com/wiki/Vandor",
        "https://starwars.fandom.com/wiki/Kijimi",
        "https://starwars.fandom.com/wiki/Kef_Bir",
        "https://starwars.fandom.com/wiki/Exegol"
    ]
    
    logger.info(f"Подготовлено {len(star_wars_pages)} страниц для скачивания")
    
    # 2. Скачивание страниц
    logger.info("Этап 1: Скачивание страниц с фандом-сайта")
    scraper = FandomScraper(base_url, output_dir)
    results = scraper.scrape_pages(star_wars_pages)
    
    if not results:
        logger.error("Не удалось скачать ни одной страницы")
        return False
    
    logger.info(f"Успешно скачано {len(results)} страниц")
    
    # 3. Создание словаря замен
    logger.info("Этап 2: Создание словаря замен терминов")
    replacer = TermReplacer()
    
    # Создаем словарь замен для Star Wars
    star_wars_terms = create_star_wars_terms_map()
    
    # Добавляем все термины в словарь
    for original, replacement in star_wars_terms.items():
        replacer.add_term_mapping(original, replacement)
    
    # Сохраняем словарь замен
    replacer.save_terms_map()
    
    # 4. Замена терминов в скачанных файлах
    logger.info("Этап 3: Замена ключевых терминов на вымышленные")
    processed_count = replacer.process_directory(output_dir)
    
    if processed_count == 0:
        logger.error("Не удалось обработать ни одного файла")
        return False
    
    logger.info(f"Успешно обработано {processed_count} файлов")
    
    # 5. Создание итогового отчета
    logger.info("Этап 4: Создание итогового отчета")
    create_final_report(output_dir, len(results), len(star_wars_terms))
    
    logger.info("Создание базы знаний завершено успешно!")
    logger.info(f"Результаты сохранены в папке: {output_dir}")
    logger.info(f"Словарь замен сохранен в: terms_map.json")
    
    return True

def create_final_report(output_dir, pages_count, terms_count):
    """
    Создание итогового отчета
    """
    report_content = f"""# Отчет о создании уникальной базы знаний

## Общая информация
- **Дата создания**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Количество скачанных страниц**: {pages_count}
- **Количество замененных терминов**: {terms_count}
- **Папка с результатами**: {output_dir}

## Структура базы знаний
База знаний содержит следующие типы документов:
- Персонажи (герои, злодеи, дроиды)
- Объекты и технологии (корабли, оружие, устройства)
- Организации и группы (ордены, армии, альянсы)
- Планеты и места (миры, города, базы)
- Концепции и силы (энергия, философия, учения)

## Словарь замен
Все ключевые термины оригинальной вселенной были заменены на вымышленные:
- "Darth Vader" → "Xarn Velgor"
- "Death Star" → "Void Core"
- "The Force" → "Synth Flux"
- И многие другие...

## Использование
1. Все документы сохранены в формате .txt
2. Словарь замен сохранен в terms_map.json
3. Метаданные о скачанных страницах в metadata.json

## Качество данных
- Тексты очищены от HTML-разметки
- Удалены элементы навигации и рекламы
- Сохранена логическая структура и читаемость
- Все упоминания оригинальных терминов заменены
"""
    
    report_path = os.path.join(output_dir, "README.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    logger.info(f"Итоговый отчет сохранен в: {report_path}")

def main():
    """
    Главная функция
    """
    try:
        success = create_knowledge_base()
        if success:
            print("\n" + "="*60)
            print("✅ Создание базы знаний завершено успешно!")
            print("📁 Результаты сохранены в папке: knowledge_base/")
            print("📋 Словарь замен: terms_map.json")
            print("📄 Итоговый отчет: knowledge_base/README.md")
            print("="*60)
        else:
            print("\n❌ Произошла ошибка при создании базы знаний")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Процесс прерван пользователем")
        print("\n⚠️ Процесс прерван пользователем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
