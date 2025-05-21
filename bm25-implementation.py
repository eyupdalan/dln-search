import math
from collections import defaultdict
import sys

import psycopg2
sys.path.append("4 - content-and-link-extraction-nlp-preprocessing")
from text_preprocessing import preprocess_text

def compute_bm25(query_tokens, conn, k1=1.5, b=0.75):
    scores = defaultdict(float)
    cursor = conn.cursor()

    # Toplam doküman sayısı
    cursor.execute("SELECT COUNT(*) FROM doc_lengths;")
    N = cursor.fetchone()[0]

    # Ortalama doküman uzunluğu
    cursor.execute("SELECT AVG(length) FROM doc_lengths;")
    avgdl = float(cursor.fetchone()[0])

    for term in query_tokens:
        # Belge frekansı (df)
        cursor.execute("SELECT COUNT(*) FROM inverted_index WHERE term = %s;", (term,))
        df = cursor.fetchone()[0]
        if df == 0:
            continue

        idf = math.log(1 + (N - df + 0.5) / (df + 0.5))

        # Terimi içeren dokümanları ve frekanslarını getir
        cursor.execute("""
            SELECT ii.doc_id, ii.freq, dl.length
            FROM inverted_index ii
            JOIN doc_lengths dl ON ii.doc_id = dl.doc_id
            WHERE ii.term = %s;
        """, (term,))
        results = cursor.fetchall()

        for doc_id, freq, doc_len in results:
            denom = freq + k1 * (1 - b + b * doc_len / avgdl)
            score = idf * (freq * (k1 + 1)) / denom
            scores[doc_id] += score

    cursor.close()
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

# PostgreSQL bağlantı parametreleri
db_params = {
    'dbname': 'websites',
    'user': 'postgres',
    'password': '1234567',  # Kendi şifrenizi kullanın
    'host': 'localhost',
    'port': '5432'
}

query = "ekonomi türkiye büyüme"
query_tokens = preprocess_text(query)  # önceki tokenizasyon fonksiyonunu kullan

conn = psycopg2.connect(**db_params)
results = compute_bm25(query_tokens, conn)

# En yüksek 10 sonucu yazdır
for doc_id, score in results[:10]:
    print(f"Doc ID: {doc_id}, BM25 Score: {score:.4f}")
