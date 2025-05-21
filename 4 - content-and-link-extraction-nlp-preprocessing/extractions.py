import psycopg2
import nltk
from nltk.corpus import stopwords
import string
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import html.entities  # html modülünü doğru şekilde import ediyoruz
from text_preprocessing import preprocess_text

nltk.download('punkt')
nltk.download('stopwords')

stop_words = set(stopwords.words('turkish'))
punctuations = set(string.punctuation)

def extract_text_and_links(html_content, base_url):
    soup = BeautifulSoup(html_content, "html.parser")

    # Metin çıkarımı
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    text = soup.get_text(separator=' ', strip=True)

    # Hyperlink çıkarımı
    links = []
    for a_tag in soup.find_all("a", href=True):
        href = urljoin(base_url, a_tag['href'])  # relative → absolute
        if urlparse(href).scheme in ['http', 'https']:
            links.append(href)

    return text, links

def safe_encode_decode(text):
    """
    Metni güvenli bir şekilde encode ve decode eder
    """
    if not text:
        return ""
    
    try:
        # Önce HTML karakterlerini decode et
        decoded = html.unescape(text)
        
        # UTF-8'e çevir ve hatalı karakterleri atla
        encoded = decoded.encode('utf-8', errors='ignore')
        
        # Tekrar decode et
        return encoded.decode('utf-8')
    except Exception as e:
        print(f"Metin dönüştürme hatası: {e}")
        return ""

# def preprocess_text(text):
#     tokens = text.lower().split()

#     # Noktalama ve stopword temizliği
#     filtered_tokens = [
#         t for t in tokens 
#         if (t not in stop_words and 
#             t not in punctuations and 
#             t.strip().isalpha() and  # strip() ile boşlukları temizle
#             len(t.strip()) > 1)  # Tek karakterli kelimeleri filtrele
#     ]
    
#     return filtered_tokens

def process_in_chunks(batch_size=1000):
    # PostgreSQL bağlantı parametreleri
    db_params = {
        'dbname': 'websites',
        'user': 'postgres',
        'password': '1234567',  # Kendi şifrenizi kullanın
        'host': 'localhost',
        'port': '5432'
    }
    
    # Veritabanı bağlantısı
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    
    try:
        # Toplam kayıt sayısını al
        cursor.execute("SELECT COUNT(*) FROM pages")
        total_records = cursor.fetchone()[0]
        
        # Offset ile parça parça veri çek
        offset = 0
        with tqdm(total=total_records, desc="İşlenen Kayıtlar") as pbar:
            while True:
                # Belirli sayıda kayıt çek
                cursor.execute(f"SELECT id, url, title, html FROM pages LIMIT {batch_size} OFFSET {offset}")
                rows = cursor.fetchall()
                
                if not rows:
                    break
                    
                # Her bir kayıt için işlem yap
                for row in rows:
                    id = row[0]
                    url = row[1]
                    title = row[2]
                    html = safe_encode_decode(row[3])
                    text, links = extract_text_and_links(html, url)
                    tokens = preprocess_text(text)
                    cursor.execute("""
                        INSERT INTO pages_cleaned (id, url, text, links, tokens)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE
                        SET text = EXCLUDED.text, links = EXCLUDED.links, tokens = EXCLUDED.tokens;
                    """, (id, url, text, links, tokens))

                    pass
                
                # İlerleme çubuğunu güncelle
                pbar.update(len(rows))
                
                # Offset'i güncelle
                offset += batch_size
                
                # Her batch'te commit yap
                conn.commit()
        
        print(f"Toplam {total_records} kayıt işlendi.")
        
    except Exception as e:
        print(f"Hata oluştu: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# Kodu çalıştır
process_in_chunks(batch_size=1000)