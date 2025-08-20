#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для замены ключевых терминов на вымышленные
"""

import json
import os
import re
from pathlib import Path
from tqdm import tqdm
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TermReplacer:
    def __init__(self, terms_map_file="terms_map.json"):
        """
        Инициализация замены терминов
        
        Args:
            terms_map_file (str): Путь к файлу со словарем замен
        """
        self.terms_map_file = terms_map_file
        self.terms_map = {}
        self.load_terms_map()
    
    def load_terms_map(self):
        """
        Загрузка словаря замен из файла
        """
        if os.path.exists(self.terms_map_file):
            try:
                with open(self.terms_map_file, 'r', encoding='utf-8') as f:
                    self.terms_map = json.load(f)
                logger.info(f"Загружен словарь замен: {len(self.terms_map)} терминов")
            except Exception as e:
                logger.error(f"Ошибка при загрузке словаря замен: {e}")
                self.terms_map = {}
        else:
            logger.info("Файл словаря замен не найден, будет создан новый")
    
    def save_terms_map(self):
        """
        Сохранение словаря замен в файл
        """
        try:
            with open(self.terms_map_file, 'w', encoding='utf-8') as f:
                json.dump(self.terms_map, f, ensure_ascii=False, indent=2)
            logger.info(f"Словарь замен сохранен в {self.terms_map_file}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении словаря замен: {e}")
    
    def add_term_mapping(self, original, replacement):
        """
        Добавление нового соответствия терминов
        
        Args:
            original (str): Оригинальный термин
            replacement (str): Заменяющий термин
        """
        self.terms_map[original] = replacement
        logger.info(f"Добавлено соответствие: '{original}' → '{replacement}'")
    
    def replace_terms_in_text(self, text):
        """
        Замена терминов в тексте
        
        Args:
            text (str): Исходный текст
            
        Returns:
            str: Текст с замененными терминами
        """
        if not self.terms_map:
            return text
        
        # Сортируем термины по длине (от длинных к коротким), чтобы избежать частичных замен
        sorted_terms = sorted(self.terms_map.keys(), key=len, reverse=True)
        
        result_text = text
        
        for original_term in sorted_terms:
            replacement_term = self.terms_map[original_term]
            
            # Используем регулярное выражение для замены с учетом регистра
            pattern = re.compile(re.escape(original_term), re.IGNORECASE)
            result_text = pattern.sub(replacement_term, result_text)
        
        return result_text
    
    def process_file(self, input_file, output_file=None):
        """
        Обработка одного файла
        
        Args:
            input_file (str): Путь к входному файлу
            output_file (str): Путь к выходному файлу (если None, перезаписывает входной)
            
        Returns:
            bool: True если обработка прошла успешно
        """
        try:
            # Читаем файл
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Заменяем термины
            modified_content = self.replace_terms_in_text(content)
            
            # Определяем выходной файл
            if output_file is None:
                output_file = input_file
            
            # Сохраняем результат
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            logger.info(f"Обработан файл: {input_file} → {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при обработке файла {input_file}: {e}")
            return False
    
    def process_directory(self, input_dir, output_dir=None):
        """
        Обработка всех текстовых файлов в директории
        
        Args:
            input_dir (str): Входная директория
            output_dir (str): Выходная директория (если None, перезаписывает файлы)
            
        Returns:
            int: Количество обработанных файлов
        """
        input_path = Path(input_dir)
        
        if not input_path.exists():
            logger.error(f"Директория не найдена: {input_dir}")
            return 0
        
        # Создаем выходную директорию если нужно
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Находим все текстовые файлы
        text_files = list(input_path.glob("*.txt")) + list(input_path.glob("*.md"))
        
        if not text_files:
            logger.warning(f"Текстовые файлы не найдены в {input_dir}")
            return 0
        
        processed_count = 0
        
        for file_path in tqdm(text_files, desc="Обработка файлов"):
            if output_dir:
                output_file = Path(output_dir) / file_path.name
            else:
                output_file = None
            
            if self.process_file(str(file_path), str(output_file) if output_file else None):
                processed_count += 1
        
        logger.info(f"Обработано файлов: {processed_count}/{len(text_files)}")
        return processed_count

def create_star_wars_terms_map():
    """
    Создание словаря замен для Star Wars
    """
    terms_map = {
        # Персонажи
        "Darth Vader": "Xarn Velgor",
        "Luke Skywalker": "Kael Stormweaver",
        "Han Solo": "Zane Blackwood",
        "Princess Leia": "Princess Aria",
        "Chewbacca": "Gorak",
        "R2-D2": "R2-X7",
        "C-3PO": "C-3PX",
        "Yoda": "Master Zorin",
        "Obi-Wan Kenobi": "Obi-Wan Kalderis",
        "Emperor Palpatine": "Emperor Malakar",
        "Boba Fett": "Boba Krell",
        
        # Объекты и технологии
        "Death Star": "Void Core",
        "Lightsaber": "Phantom Blade",
        "Millennium Falcon": "Stellar Phoenix",
        "X-wing starfighter": "X-wing voidcraft",
        "TIE fighter": "Shadow fighter",
        "Blaster": "Pulse rifle",
        "Hyperdrive": "Void drive",
        "Hologram": "Echo projection",
        "Droid": "Automaton",
        
        # Организации и группы
        "Jedi": "Void Knights",
        "Sith": "Shadow Lords",
        "Clone trooper": "Replica soldier",
        "Stormtrooper": "Void trooper",
        "Rebel Alliance": "Freedom Coalition",
        "Galactic Empire": "Void Empire",
        "Republic": "Federation",
        
        # Планеты и места
        "Coruscant": "Luminara",
        "Tatooine": "Sandara",
        "Hoth": "Frostara",
        "Dagobah": "Swampara",
        "Bespin": "Cloudara",
        "Endor": "Forestara",
        "Naboo": "Aquara",
        "Kamino": "Cloneara",
        "Geonosis": "Rockara",
        
        # Концепции и силы
        "The Force": "Synth Flux",
        "Dark Side": "Shadow Path",
        "Light Side": "Luminous Path",
        "Midichlorians": "Flux particles",
        
        # Дополнительные термины
        "Star Wars": "Void Chronicles",
        "Galaxy": "Void Realm",
        "Space": "Void",
        "Starship": "Voidship",
        "Spaceship": "Voidship",
        "Laser": "Pulse beam",
        "Blaster bolt": "Pulse bolt",
        "Force lightning": "Flux lightning",
        "Force choke": "Flux grip",
        "Force push": "Flux push",
        "Force pull": "Flux pull",
        "Jedi Order": "Void Knight Order",
        "Sith Order": "Shadow Lord Order",
        "Padawan": "Apprentice",
        "Master": "Void Master",
        "Council": "Void Council",
        "Temple": "Void Temple",
        "Academy": "Void Academy",
        "Training": "Void training",
        "Combat": "Void combat",
        "Battle": "Void battle",
        "War": "Void war",
        "Peace": "Void peace",
        "Justice": "Void justice",
        "Honor": "Void honor",
        "Wisdom": "Void wisdom",
        "Knowledge": "Void knowledge",
        "Power": "Void power",
        "Strength": "Void strength",
        "Courage": "Void courage",
        "Hope": "Void hope",
        "Destiny": "Void destiny",
        "Fate": "Void fate",
        "Prophecy": "Void prophecy",
        "Legend": "Void legend",
        "Myth": "Void myth",
        "Story": "Void tale",
        "History": "Void history",
        "Past": "Void past",
        "Present": "Void present",
        "Future": "Void future"
    }
    
    return terms_map

def main():
    """
    Основная функция для демонстрации работы замены терминов
    """
    # Создаем экземпляр замены терминов
    replacer = TermReplacer()
    
    # Создаем словарь замен для Star Wars
    star_wars_terms = create_star_wars_terms_map()
    
    # Добавляем все термины в словарь
    for original, replacement in star_wars_terms.items():
        replacer.add_term_mapping(original, replacement)
    
    # Сохраняем словарь замен
    replacer.save_terms_map()
    
    # Обрабатываем файлы в папке knowledge_base
    input_directory = "knowledge_base"
    if os.path.exists(input_directory):
        processed_count = replacer.process_directory(input_directory)
        logger.info(f"Обработка завершена. Обработано файлов: {processed_count}")
    else:
        logger.warning(f"Папка {input_directory} не найдена. Сначала запустите scraper.py")

if __name__ == "__main__":
    main()
