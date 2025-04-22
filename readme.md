# BLM5121 Web Mining

CommonCrawl'ın haber context'indeki veri set'leri indirildi
İndirilen Web ARChive (WARC) dosyaları:

- Aşağıdaki dosya 2020 yılına ait yaklaşık 5.5GB'lık bir veri

> CC-NEWS-20200110212037-00310.warc

- Yukarıdaki veri setindeki Türkçe içerikler kullanılmak istendi. O sebeple bundaki verinin yetersizliği görülünce daha güncel aşağıdaki veri set'leri de indirildi.
- Aşağıdaki dosyalar 2025 yılı Ocak ayına ait
- Bunların tamamı 1.5TB'tan fazla tutuyor. Bunu bu sebeple makinede tutmak ve analiz etmek kaynak tüketimi açısından sıkıntılara sebep olabilir. Bu yüzden aşağıdaki part'lar indirilip kullanıldı. Bunlar yaklaşık 30GB tutuyor.

> CC-NEWS-20250101020153-00156.warc
CC-NEWS-20250101055537-00157.warc
CC-NEWS-20250101083312-00158.warc
CC-NEWS-20250101110352-00159.warc
CC-NEWS-20250101133323-00160.warc
CC-NEWS-20250101160900-00161.warc
CC-NEWS-20250101182853-00162.warc
CC-NEWS-20250101204758-00163.warc
CC-NEWS-20250101233509-00164.warc
CC-NEWS-20250102025043-00165.warc
CC-NEWS-20250102053830-00166.warc
CC-NEWS-20250102074538-00167.warc
CC-NEWS-20250102092617-00168.warc
CC-NEWS-20250102110149-00169.warc
CC-NEWS-20250102122438-00170.warc
CC-NEWS-20250102140759-00171.warc
CC-NEWS-20250102155145-00172.warc
CC-NEWS-20250102173620-00173.warc
CC-NEWS-20250102192440-00174.warc
CC-NEWS-20250102214004-00175.warc
CC-NEWS-20250103000559-00176.warc
CC-NEWS-20250103031223-00177.warc
CC-NEWS-20250103060152-00178.warc
CC-NEWS-20250103080404-00179.warc
CC-NEWS-20250103095544-00180.warc
CC-NEWS-20250103114344-00181.warc
CC-NEWS-20250103131849-00182.warc
CC-NEWS-20250103145501-00183.warc
CC-NEWS-20250103163233-00184.warc
CC-NEWS-20250103181014-00185.warc

- Türkçe websitelerine ait verileri ayıklamak için, URL'indeki domain'i Türkçe haber sitelerine ait verileri bu veri setlerinden ayıklamak gerekti.
- Türkçe haber siteleri için 2 farklı yol izlendi:
  1. Basın İlan Kurumu'na ait Nisan ayıda reklam verilebilecek haber siteleri verisi alındı. (<https://ilanbis.bik.gov.tr/Uygulamalar/AylikListe>)
  2. İndirilen tüm WARC dosyalarında, html content içerisinde Türkçe alfabedeki karakterlerden ("çğıöşüÇĞİÖŞÜ") 3 farklı karakteri içerenlerin URL'leri listelendi. 
- Bu iki farklı yöntemle elde edilen website URL'leri'nin domain bilgileri tekil bir şekilde birleştirildi. (./websites/all-websites.txt)
- Yaklaşık 1339 adet domain toplanmış oldu.
- Sonrasında bu URL'lere ait web arşiv (WARC) verileri ayrıştırıldı. Yeni bir WARC dosyası oluşturuldu. (website_data.warc)
- Bu da yaklaşık 16GB'lık bir veri
- Sonraki aşamada bu veri de parse edildi. Buradaki data'dan url, title ve html verileri çıkarıldı. Bir SQLite veri tabanı oluşturularak (websites.db) buraya kaydedildi.
