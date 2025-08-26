import os
import json
import re
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb

class KnowledgeBaseProcessor:
    def __init__(self, knowledge_base_path: str = "knowledge_base"):
        """
        Инициализация процессора базы знаний
        
        Args:
            knowledge_base_path: Путь к папке с файлами базы знаний
        """
        self.knowledge_base_path = knowledge_base_path
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )
        
    def load_text_files(self) -> List[Dict[str, Any]]:
        """
        Загружает все текстовые файлы из knowledge_base
        
        Returns:
            Список словарей с метаданными и содержимым файлов
        """
        documents = []
        
        # Получаем список всех .txt файлов, исключая README.md
        txt_files = [f for f in os.listdir(self.knowledge_base_path) 
                    if f.endswith('.txt') and f != 'README.md']
        
        print(f"Найдено {len(txt_files)} текстовых файлов")
        
        for filename in txt_files:
            file_path = os.path.join(self.knowledge_base_path, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                # Извлекаем заголовок из первой строки
                lines = content.split('\n')
                title = ""
                if lines and lines[0].startswith('Заголовок:'):
                    title = lines[0].replace('Заголовок:', '').strip()
                
                documents.append({
                    'filename': filename,
                    'title': title,
                    'content': content,
                    'file_path': file_path
                })
                
                print(f"✅ Загружен файл: {filename} ({len(content)} символов)")
                
            except Exception as e:
                print(f"❌ Ошибка при загрузке файла {filename}: {e}")
                
        return documents
    
    def clean_text(self, text: str) -> str:
        """
        Очищает текст от лишних символов и форматирования
        
        Args:
            text: Исходный текст
            
        Returns:
            Очищенный текст
        """
        # Удаляем лишние пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text)
        
        # Удаляем специальные символы, но оставляем буквы, цифры и основные знаки препинания
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', '', text)
        
        # Удаляем множественные пробелы
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def split_into_chunks(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Разбивает документы на чанки с использованием RecursiveCharacterTextSplitter
        
        Args:
            documents: Список документов
            
        Returns:
            Список чанков с метаданными
        """
        chunks = []
        
        for doc in documents:
            content = self.clean_text(doc['content'])
            
            # Используем RecursiveCharacterTextSplitter для разбиения
            text_chunks = self.text_splitter.split_text(content)
            
            for i, chunk_text in enumerate(text_chunks):
                chunks.append({
                    'content': chunk_text.strip(),
                    'filename': doc['filename'],
                    'title': doc['title'],
                    'chunk_id': len(chunks),
                    'doc_chunk_id': i
                })
        
        print(f"📄 Создано {len(chunks)} чанков")
        return chunks
    
    def process_knowledge_base(self):
        """
        Основной метод для обработки всей базы знаний
        """
        print("🚀 === Обработка базы знаний ===")
        
        # 1. Загружаем файлы
        print("\n📂 1. Загрузка файлов...")
        documents = self.load_text_files()
        
        if not documents:
            print("❌ Не найдено документов для обработки!")
            return
        
        # 2. Разбиваем на чанки
        print("\n✂️ 2. Разбиение на чанки...")
        chunks = self.split_into_chunks(documents)

        chroma_client = chromadb.HttpClient(
            host=os.getenv("CHROMADB_HOST"),
            port=os.getenv("CHROMADB_PORT")
        )

        # Удаляем существующую коллекцию если она есть
        try:
            chroma_client.delete_collection(name="quantum_forge_collection")
            print(f"🗑️ Удалена существующая коллекция")
        except:
            pass

        # Создаем новую коллекцию
        collection = chroma_client.create_collection(name="quantum_forge_collection")
        print(f"🔍 Создана новая коллекция: {collection.name}")

        print(f"🔍 Добавление чанков в коллекцию...")

        # Размер батча для ChromaDB (максимум 5461)
        batch_size = 5000
        
        # Разбиваем на батчи
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            
            documents = [chunk['content'] for chunk in batch_chunks]
            metadatas = [{
                'filename': chunk['filename'],
                'title': chunk['title'],
                'chunk_id': chunk['chunk_id'],
                'doc_chunk_id': chunk['doc_chunk_id']
            } for chunk in batch_chunks]
            ids = [str(chunk['chunk_id']) for chunk in batch_chunks]

            print(f"🔍 Обработка батча {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size} ({len(batch_chunks)} чанков)...")
            
            embeddings = self.model.encode(documents, normalize_embeddings=True)

            collection.add(
                documents=documents,
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas
            )

        print(f"🔍 Все чанки добавлены в коллекцию")

    def test_chroma_collection(self):
        """
        Тестирует коллекцию в ChromaDB
        """
        print("🔍 Тестирование коллекции...")
        
        chroma_client = chromadb.HttpClient(
            host=os.getenv("CHROMADB_HOST"),
            port=os.getenv("CHROMADB_PORT")
        )
        
        try:
            collection = chroma_client.get_collection(name="quantum_forge_collection")
            
            query_embeddings = self.model.encode(["Who is Zane Blackwood?"], normalize_embeddings=True)

            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=2
            )
            
            print(f"🔍 Результаты поиска:")
            print(f"   • Найдено результатов: {len(results['ids'][0])}")
            print(f"   • Лучшее расстояние: {results['distances'][0][0]:.4f}")
            
            # Показываем первые 2 результата
            for i in range(min(2, len(results['ids'][0]))):
                print(f"\n--- Результат {i+1} ---")
                print(f"📁 Файл: {results['metadatas'][0][i]['filename']}")
                print(f"📝 Заголовок: {results['metadatas'][0][i]['title']}")
                print(f"📄 Содержимое: {results['documents'][0][i]}")
                print(f"📏 Длина: {len(results['documents'][0][i])} символов")
                
        except Exception as e:
            print(f"❌ Ошибка при тестировании коллекции: {e}")

def main():
    """Основная функция"""
    print("🎯 Запуск обработки базы знаний...")
    
    # Создаем процессор
    processor = KnowledgeBaseProcessor()
    
    # Обрабатываем базу знаний
    processor.process_knowledge_base()

    processor.test_chroma_collection()
    
    print("\n🎉 Обработка завершена!")

if __name__ == "__main__":
    main()
