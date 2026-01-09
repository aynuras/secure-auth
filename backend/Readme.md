# Secure Auth Project
Bu proje, modern güvenlik standartları (Best Practices) kullanılarak geliştirilmiş, uçtan uca bir Authentication (Kimlik Doğrulama) sistemidir.

## Özellikler & Güvenlik:
- **Custom User Model:** Email tabanlı kimlik doğrulama.
- **Argon2 Hashing:** Şifreler, Password Hashing Competition şampiyonu Argon2 ile korunmaktadır.
- **PostgreSQL:** Veri bütünlüğü için endüstri standardı ilişkisel veritabanı.
- **Environment Variables:** Hassas bilgiler (şifreler, anahtarlar) .env dosyasında izole edilmiştir.
- **JWT & HttpOnly Cookie:** (Geliştirme aşamasında) Güvenli token yönetimi.

## Kurulum Adımları:
### 1.Gereksinimler:
- Python 3.12+
- PostgreSQL
- Node.js & Angular CLI (Frontend için)

### 2.Backend Kurulumu:
1. Projeyi klonlayın veya oluşturun.
```
cd Backend
```

2. Sanal ortamı oluşturun ve aktif edin.
```
python -m venv .venv

# Windows için:
.venv\Scripts\activate

# macOS/Linux için:
source .venv/bin/activate
```

3. Bağımlılıkları Kurun:
```
pip install django psycopg2-binary python-dotenv argon2-cffi djangorestframework-simplejwt django-cors-headers
```

4. Veritabanını Hazırlayın:
    - PostgreSQL üzerinde .env dosyasında belirttiğiniz isimde bir veritabanı oluşturun.


5. Ortam Değişkenlerini (.env) Ayarlayın: backend/ dizini altında bir .env dosyası oluşturun ve şu bilgileri girin:
```
SECRET_KEY=gizli_anahtariniz
DEBUG=True
DB_NAME=projedb
DB_USER=projeuser
DB_PASSWORD=sifreniz
DB_HOST=localhost
DB_PORT=5432
```

6. Migration'ları Uygulayın:
```
python manage.py makemigrations users
python manage.py migrate
```

### 3. Kullanım
- **Superuser Oluşturma:** python manage.py createsuperuser
- **Sunucuyu Başlatma:** python manage.py runserver

---

### Notlar
- Bu proje bir "Best Practice" örneğidir. `.env` dosyası asla versiyon kontrol sistemine (Git) gönderilmemelidir.
- Frontend (Angular) kurulum adımları proje ilerledikçe buraya eklenecektir.