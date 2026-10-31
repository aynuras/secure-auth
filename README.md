# Secure Auth — Güvenli Kimlik Doğrulama Sistemi

**Django REST Framework, Angular ve PostgreSQL** kullanılarak geliştirilmiş, güvenlik odaklı bir kimlik doğrulama sistemidir.

Proje; modern authentication ve session security mekanizmalarını uygulamalı olarak incelemek ve **Defense in Depth (Savunma Derinliği)** yaklaşımını birden fazla güvenlik katmanı üzerinden göstermek amacıyla geliştirilmiştir.

Güvenlik tasarımında **OWASP ve NIST güvenlik rehberlerinden** yararlanılmıştır.

**Not:** Bu proje eğitim ve portföy amacıyla geliştirilmiştir. Production ortamında kullanılmak üzere tasarlanmamıştır.

## Projenin Amacı

Bu projenin temel amacı aşağıdaki konularda pratik deneyim kazanmaktır:

- Authentication ve authorization
- JWT session management
- Password security
- Multi-factor authentication
- Token invalidation
- Rate limiting
- Audit logging
- Defense in Depth
- Secure API development

## Güvenlik Özellikleri

### 1. Kimlik Doğrulama ve Oturum Güvenliği

- **JWT Authentication:** Kısa ömürlü Access Token ve Refresh Token yapısı kullanılmıştır.
- **HttpOnly & Secure Cookies:** Token'lar JavaScript tarafından doğrudan erişilemeyen HttpOnly ve Secure cookie'lerde tutulmaktadır.
- **Refresh Token Rotation:** Refresh Token yenilendiğinde mevcut token'ın yerine yeni bir token oluşturularak çalınmış token'ların kullanım riskinin azaltılması hedeflenmiştir.
- **JTI Tracking:** Refresh Token'lar benzersiz JWT ID (JTI) değerleri üzerinden sunucu tarafında takip edilmektedir.
- **Session Invalidation:** Sunucu tarafındaki JTI takibi sayesinde aktif oturumlar gerektiğinde geçersiz hale getirilebilmektedir.
- **Two-Factor Authentication (2FA):** OTP tabanlı iki faktörlü doğrulama authentication akışına entegre edilmiştir.

### 2. Parola ve Hesap Güvenliği

- **Argon2 Password Hashing:** Kullanıcı parolaları Argon2 kullanılarak hash'lenmektedir.
- **Rate Limiting:** Tekrarlanan authentication denemelerini sınırlandırmak amacıyla IP tabanlı rate limiting uygulanmıştır.
- **Account Lockout:** Belirli sayıda başarısız giriş denemesinden sonra hesap kilitleme mekanizması uygulanmıştır.
- **Password History:** Önceki parolalar takip edilerek parola tekrar kullanımının önüne geçilmesi amaçlanmıştır.
- **Password Policy:** Parola karmaşıklığı için belirli kurallar uygulanmıştır.

### 3. Defense in Depth

Sistem tek bir güvenlik mekanizmasına bağlı kalmak yerine birden fazla koruma katmanı kullanmaktadır:

- IP tabanlı allow/block kontrolleri
- Rate limiting
- Account lockout
- Session invalidation
- Audit logging
- Input validation
- Authentication error handling

Bu yaklaşımın amacı, tek bir güvenlik mekanizmasının başarısız olması durumunda ek koruma katmanlarının bulunmasını sağlamaktır.

### 4. Audit Logging

Güvenlik açısından önemli işlemler kayıt altına alınmaktadır. Örneğin:

- Login denemeleri
- Kullanıcı kayıt işlemleri
- Parola değişiklikleri
- Authentication işlemleri
- Kaynak IP bilgileri

Bu kayıtlar authentication aktivitelerinin incelenmesi ve şüpheli işlemlerin araştırılması amacıyla kullanılabilir.

### 5. User Enumeration Prevention

Authentication sırasında hata mesajlarının gereksiz bilgi vermesi engellenerek, saldırganın belirli bir kullanıcı hesabının sistemde bulunup bulunmadığını anlamasının zorlaştırılması hedeflenmiştir.

### 6. Input Validation

Frontend ve backend tarafında gelen verilerin beklenen format ve şemaya uygunluğunu kontrol etmek için validation mekanizmaları uygulanmıştır.

## Mimari

Proje iki ana uygulamadan oluşmaktadır:

```text
secure-auth/
├── backend/
│   └── Django REST Framework
│
└── frontend/
    └── Angular
```

### Backend

Backend aşağıdaki işlemlerden sorumludur:

- Authentication ve authorization
- JWT yönetimi
- Kullanıcı yönetimi
- Parola güvenliği
- 2FA
- Rate limiting
- Session invalidation
- Audit logging
- Veritabanı işlemleri

### Frontend

Angular frontend aşağıdaki işlemler için kullanıcı arayüzü sağlamaktadır:

- Kullanıcı kaydı
- Login
- 2FA doğrulaması
- Parola işlemleri
- Authentication akışları

## Teknolojiler

- **Backend:** Django Rest Framework, Python 3.12+
- **Frontend:** Angular 17+, RxJS, Signal Store
- **Database:** PostgreSQL
- **Security:** Argon2, JWT (SimpleJWT), django-ipware

## Kurulum Adımları

### 1. Gereksinimler

- Python 3.12+
- PostgreSQL
- Node.js (Frontend için)

### 2. Backend Kurulumu

1. **Projeyi klonlayın:**

   ```bash
   git clone <repo-url>
   cd secure-auth/backend
   ```

2. **Sanal ortamı oluşturun ve aktif edin:**

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

## E-Posta Simülasyonu & 2FA

Projenin canlı ortam (Production) ayağı olmadığı için gerçek bir SMTP sunucusu yerine Django'nun **Console Backend**'i kullanılmıştır.

- Third party service bağımlılığı olmadan 2FA mantığının ve mimarisinin doğru çalıştığını gösterebilmek için tercih edilmiştir.
- Register veya Login aşamasında gönderilen OTP kodları ve aktivasyon linkleri terminal ekranına düşer. Akışı tamamlamak için terminaldeki kod kullanılabilir.
- Production ortamında email backend'i uygun bir SMTP servisi ile değiştirilebilir.

## ⚠️ Güvenlik Notu

Bu proje eğitim ve örnekleme amaçlıdır. Canlı ortamda (Production) kullanmadan önce `DEBUG=False` yapılmalı ve SSL (HTTPS) sertifikası zorunlu tutulmalıdır.
