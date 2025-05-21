import nltk
from nltk.corpus import stopwords
import string

# NLTK gerekli verileri indir
nltk.download('punkt')
nltk.download('stopwords')

# Stop words ve noktalama işaretlerini tanımla
stop_words = set(stopwords.words('turkish'))
punctuations = set(string.punctuation)

def preprocess_text(text):
    """
    Metni ön işleme adımlarından geçirir:
    - Küçük harfe çevirir
    - Stop words'leri kaldırır
    - Noktalama işaretlerini kaldırır
    - Sadece alfabetik karakterleri tutar
    - Tek karakterli kelimeleri filtreler
    
    Args:
        text (str): İşlenecek metin
        
    Returns:
        list: İşlenmiş token'ların listesi
    """
    tokens = text.lower().split()

    # Noktalama ve stopword temizliği
    filtered_tokens = [
        t for t in tokens 
        if (t not in stop_words and 
            t not in punctuations and 
            t.strip().isalpha() and  # strip() ile boşlukları temizle
            len(t.strip()) > 1)  # Tek karakterli kelimeleri filtrele
    ]
    
    return filtered_tokens 