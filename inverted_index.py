from collections import defaultdict, Counter
import psycopg2
from tqdm import tqdm

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
    
    # Ters dizin sözlüğü
    inverted_index = defaultdict(list)

    # Belge uzunluklarını da tutalım (BM25 için)
    doc_lengths = {}
    
    try:
        # Toplam kayıt sayısını al
        cursor.execute("SELECT COUNT(*) FROM pages_cleaned")
        total_records = cursor.fetchone()[0]
        
        # Offset ile parça parça veri çek
        offset = 0
        with tqdm(total=total_records, desc="İşlenen Kayıtlar") as pbar:
            while True:
                # Belirli sayıda kayıt çek
                cursor.execute(f"SELECT id, tokens FROM pages_cleaned LIMIT {batch_size} OFFSET {offset}")
                rows = cursor.fetchall()
                
                if not rows:
                    break

                for row in rows:
                    doc_id = row[0]
                    tokens = row[1]
                    freq = Counter(tokens)
                    doc_lengths[doc_id] = sum(freq.values())
                    
                    for term, count in freq.items():
                        inverted_index[term].append((doc_id, count))
                    
                    pbar.update(len(rows))
                    offset += batch_size
                    
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        conn.close()
        
    return inverted_index, doc_lengths

# # Ters dizin sözlüğü
# inverted_index = defaultdict(list)

# # Belge uzunluklarını da tutalım (BM25 için)
# doc_lengths = {}

# for _, row in df.iterrows():
#     doc_id = row['id']
#     tokens = row['tokens']  # bu bir liste olmalı

#     freq = Counter(tokens)
#     doc_lengths[doc_id] = sum(freq.values())

#     for term, count in freq.items():
#         inverted_index[term].append((doc_id, count))

inverted_index, doc_lengths = process_in_chunks(batch_size=1000)

print(len(inverted_index))
print(len(doc_lengths))