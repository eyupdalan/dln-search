from collections import defaultdict, Counter
import psycopg2
from tqdm import tqdm
import pickle
import io
import csv

# PostgreSQL bağlantı parametreleri
db_params = {
    'dbname': 'websites',
    'user': 'postgres',
    'password': '1234567',  # Kendi şifrenizi kullanın
    'host': 'localhost',
    'port': '5432'
}

def process_in_chunks(batch_size=1000):
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
        print("total_records: ",total_records)
        
        # Offset ile parça parça veri çek
        offset = 0
        with tqdm(total=total_records, desc="İşlenen Kayıtlar") as pbar:
            while True:
                # Belirli sayıda kayıt çek
                cursor.execute(f"SELECT id, tokens FROM pages_cleaned ORDER BY id LIMIT {batch_size} OFFSET {offset}")
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

def save_inverted_index(inverted_index):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    try:
        # Önce tabloyu temizleyelim
        cursor.execute("TRUNCATE TABLE inverted_index")
        
        # Veriyi CSV formatında bir StringIO nesnesine yazalım
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Veriyi hazırla
        total_items = sum(len(postings) for postings in inverted_index.values())
        with tqdm(total=total_items, desc="Preparing Inverted Index Data") as pbar:
            for term, postings in inverted_index.items():
                for doc_id, freq in postings:
                    writer.writerow([term, doc_id, freq])
                    pbar.update(1)
        
        # StringIO'yu başa sar
        output.seek(0)
        
        # COPY komutu ile veriyi yükle
        cursor.copy_from(
            output,
            'inverted_index',
            sep=',',
            columns=('term', 'doc_id', 'freq')
        )
        conn.commit()
        
    except Exception as e:
        print(f"Hata oluştu: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def save_doc_lengths(doc_lengths):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    try:
        # Önce tabloyu temizleyelim
        cursor.execute("TRUNCATE TABLE doc_lengths")
        
        # Veriyi CSV formatında bir StringIO nesnesine yazalım
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Veriyi hazırla
        total_items = len(doc_lengths)
        with tqdm(total=total_items, desc="Preparing Document Lengths Data") as pbar:
            for doc_id, length in doc_lengths.items():
                writer.writerow([doc_id, length])
                pbar.update(1)
        
        # StringIO'yu başa sar
        output.seek(0)
        
        # COPY komutu ile veriyi yükle
        cursor.copy_from(
            output,
            'doc_lengths',
            sep=',',
            columns=('doc_id', 'length')
        )
        conn.commit()
        
    except Exception as e:
        print(f"Hata oluştu: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

inverted_index, doc_lengths = process_in_chunks(batch_size=1000)

print("inverted_index length: ", len(inverted_index))
print("doc_lengths length: ", len(doc_lengths))

# print(doc_lengths.items())
# print(len(doc_lengths.items()))

with open("inverted_index.pkl", "wb") as f:
    pickle.dump(inverted_index, f)
    print("inverted_index.pkl saved")

with open("doc_lengths.pkl", "wb") as f:
    pickle.dump(doc_lengths, f)
    print("doc_lengths.pkl saved")

save_doc_lengths(doc_lengths)
save_inverted_index(inverted_index)
