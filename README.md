# Secure Auth - Enterprise Grade Authentication System

Bu proje, **Defense in Depth (Savunma Derinliği)** stratejisi temel alınarak geliştirilmiş, modern güvenlik standartlarına (OWASP, NIST) tam uyumlu, uçtan uca bir kimlik doğrulama mimarisidir. Canlı ortam simülasyonu ile güvenli yazılım geliştirme pratiklerini (Best Practices) sergilemeyi amaçlar.

## 🚀 Mimari & Güvenlik Özellikleri

Proje 4 ana güvenlik katmanı üzerine inşa edilmiştir:

### 1. Advanced Identity Management (Kimlik Yönetimi)

- **HttpOnly Cookie Architecture:** JWT (Access & Refresh) tokenları, JavaScript erişimine kapalı `HttpOnly` ve `Secure` çerezlerde saklanarak XSS saldırıları etkisiz hale getirildi.
- **Session Hardening:** Refresh Token rotasyonu ve sunucu taraflı token takibi (JTI Tracking) ile oturumlar tam denetim altına alındı. Çalınan oturumlar anlık olarak sunucudan sonlandırılabilir.
- **Strict 2FA:** Giriş akışına entegre, zaman aşımı kontrollü ve zorunlu tutulabilen İki Faktörlü Doğrulama (OTP) mekanizması.

### 2. Enterprise Security Features (Kurumsal Güvenlik)

- **Argon2 Hashing:** Parolalar, GPU tabanlı saldırılara dirençli Argon2 algoritması ile şifrelenir.
- **Brute-Force Protection:** IP tabanlı hız sınırlaması (Throttling) ve 5 başarısız deneme sonrası otomatik **Account Lockout** (Hesap Kilitleme).
- **Password Policies:** Kullanıcıların son 3 parolasını tekrar kullanmasını engelleyen geçmiş kontrolü (`PasswordHistory`) ve karmaşıklık zorunluluğu.

### 3. Secure Architecture (Güvenli Altyapı)

- **Defense-in-Depth:** Sadece tek bir noktaya güvenilmez; IP Whitelist/Blacklist, Rate Limiting ve Audit Logging katmanları ile sistem korunur.
- **Audit Logging:** Kim, ne zaman, hangi IP'den, ne işlem yaptı? Tüm kritik işlemler (`LOGIN`, `REGISTER`, `PASSWORD_CHANGE`) detaylıca veritabanına loglanır.
- **Information Leakage Prevention:** Hata mesajları saldırgana bilgi vermeyecek şekilde minimize edilmiştir (User Enumeration Prevention).

### 4. Input Integrity (Veri Bütünlüğü)

- **Sanitization & Validation:** Backend ve Frontend tarafında katı veri şeması (Schema Validation) kontrolleri.

---

## 🛠️ Teknolojiler

- **Backend:** Django Rest Framework, Python 3.12+
- **Frontend:** Angular 17+, RxJS, Signal Store
- **Database:** PostgreSQL
- **Security:** Argon2, JWT (SimpleJWT), Django-Ipware

---

## ⚙️ Kurulum Adımları

### 1. Gereksinimler

- Python 3.12+
- PostgreSQL
- Node.js (Frontend için)

### 2. Backend Kurulumu

1. **Projeyi Klonlayın:**

   ```bash
   git clone <repo-url>
   cd secure-auth/backend
   ```

2. **Sanal Ortamı Oluşturun ve Aktif Edin:**

   ```bash
   python -m venv .venv

   # Windows:
   .venv\Scripts\activate

   # macOS/Linux:
   source .venv/bin/activate
   ```

3. **Bağımlılıkları Yükleyin:**

   ```bash
   pip install django djangorestframework djangorestframework-simplejwt django-cors-headers psycopg2-binary django-ipware argon2-cffi python-dotenv celery redis
   ```

4. **Çevresel Değişkenleri (.env) Ayarlayın:**
   `backend/` dizini altında `.env` dosyası oluşturun:

   ```env
   SECRET_KEY=gizli_ve_uzun_rastgele_bir_deger
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Veritabanı
   DB_NAME=secure_auth_db
   DB_USER=postgres
   DB_PASSWORD=sifreniz
   DB_HOST=localhost
   DB_PORT=5432

   # Frontend URL (Reset Password Linkleri için)
   FRONTEND_URL=http://localhost:4200
   ```

5. **Veritabanı ve Migration:**

   ```bash
   python manage.py makemigrations users
   python manage.py migrate
   ```

6. **Sunucuyu Başlatın:**
   ```bash
   python manage.py runserver
   ```

### 3. Frontend Kurulumu

1. **Dizine Gidin:**

   ```bash
   cd ../frontend
   ```

2. **Paketleri Yükleyin:**

   ```bash
   npm install
   ```

3. **Uygulamayı Başlatın:**
   ```bash
   npm start
   ```
   Uygulama `http://localhost:4200` adresinde çalışacaktır.

---

## ℹ️ E-Posta Simülasyonu & 2FA

Projenin canlı ortam (Production) ayağı olmadığı için gerçek bir SMTP sunucusu yerine Django'nun **Console Backend**'i kullanılmıştır.

- **Neden?** 3. parti servis bağımlılığı olmadan 2FA mantığının (kod üretme, saklama, doğrulama) ve mimarisinin doğru çalıştığını gösterebilmek için.
- **Nasıl Çalışır?** Register veya Login aşamasında gönderilen OTP kodları ve aktivasyon linkleri **direkt olarak terminal ekranına** düşer. Akışı tamamlamak için terminaldeki kodu kullanabilirsiniz.
- **Production Entegrasyonu:** Gerçek bir projede, kod yapısında hiçbir değişiklik yapmadan, sadece `.env` dosyasındaki SMTP ayarları girilerek Gmail veya AWS SES kolayca bağlanabilir.

---

## ⚠️ Güvenlik Notu

Bu proje eğitim ve örnekleme amaçlıdır. Canlı ortamda (Production) kullanmadan önce `DEBUG=False` yapılmalı ve SSL (HTTPS) sertifikası zorunlu tutulmalıdır.
