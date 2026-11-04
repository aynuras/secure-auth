# Secure Auth — Güvenli Kimlik Doğrulama Sistemi

**Django REST Framework, Angular ve PostgreSQL** kullanılarak geliştirilmiş, güvenlik odaklı bir kimlik doğrulama örnek projesidir.

Amaç; modern authentication ve session yönetimi mekanizmalarını uygulamalı olarak öğrenmek ve **Defense in Depth** fikrini birden fazla katman üzerinden denemekti. Tasarımda OWASP ve NIST rehberlerinden ilham alındı; bu rehberlerle tam uyumlu olduğu iddia edilmemektedir.

**Not:** Bu proje eğitim ve portföy amaçlıdır. Production ortamında kullanılmak üzere tasarlanmamıştır. Geliştirme sürecinde yapay zekâ araçlarından yardım alınmış olup; kodlar sonradan gözden geçirilip eksikleri aşağıdaki "Bilinen Sınırlamalar" bölümünde belirtilmiştir.

## Projenin Amacı

Aşağıdaki konularda pratik deneyim kazanmak:

- Authentication ve authorization
- JWT ile oturum yönetimi
- Parola güvenliği
- İki faktörlü doğrulama (2FA)
- Oturum geçersiz kılma
- Rate limiting
- Audit logging
- Defense in Depth
- Secure API development

## Uygulanan Güvenlik Özellikleri

### 1. Kimlik Doğrulama ve Oturum

- **JWT:** Access ve Refresh Token yapısı (SimpleJWT).
- **HttpOnly Cookie:** Token'lar response body'e dönmez, HttpOnly cookie olarak set edilir. `Secure` bayrağı `DEBUG=False` iken aktif olur. `SameSite=Lax` kullanılır.
- **Sunucu tarafı oturum takibi:** Refresh Token'ın JTI değeri veritabanında (`UserSession`) tutulur. Access Token içine `refresh_jti` claim'i eklenir ve her istekte ilgili oturumun aktif olup olmadığı kontrol edilir. Logout ve hesabın pasife alınması erişimi kesebilir.
- **Refresh Token Rotation:** `ROTATE_REFRESH_TOKENS` açıktır. Rotation sonrası oturum kaydının güncellenmesi henüz tamamlanmamıştır (bkz. Bilinen Sınırlamalar). 
- **E-posta ile OTP (2FA):** Parola doğrulamasından sonra kullanıcıya 6 haneli, 3 dakika geçerli bir kod gönderilir. (TOTP/Authenticator uygulaması desteği yoktur.) 

### 2. Parola ve Hesap Güvenliği

- **Argon2 Password Hashing:** Kullanıcı parolaları Argon2 kullanılarak hash'lenmektedir.
- **Rate Limiting:** Tekrarlanan authentication denemelerini sınırlandırmak amacıyla IP tabanlı rate limiting uygulanmıştır.
- **Account Lockout:** 5 başarısız giriş denemesinden sonra 15 dakika hesap kilitleme mekanizması uygulanmıştır.
- **Password History:** Parola değiştirirken son 3 parola ile aynı parola reddedilir.
- **Password Policy:** Django'nun yerleşik validator'ları kullanılmıştır (minimum uzunluk, yaygın parola, sadece rakam, kullanıcı bilgisine benzerlik). Büyük harf/sembol gibi karmaşıklık kuralı yoktur.

### 3. Defense in Depth

Tek bir mekanizmaya güvenmemek için birkaç basit katman birlikte kullanılır:

- IP blacklist/whitelist kontrolü (register, login, 2FA ve refresh endpoint'lerinde)
- Rate limiting
- Hesap kilitleme
- Session invalidation
- Audit logging
- Backend input validation

### 4. Audit Logging

Login denemeleri, kayıt, parola ve profil değişiklikleri gibi bazı olaylar Ip ve user-agent bilgisiyle `AuditLog` tablosuna yazılır. Eski kayıtları silmek için bir Celery görevi tanımlıdır.

### 5. User Enumeration'a Karşı Önlemler

Login'de hatalı e-posta ve hatalı parola aynı mesajı döner. Kayıt ve parola sıfırlama isteklerinde de hesabın var olup olmadığını açık etmeyen genel mesajlar kullanılır. Bu alan henüz tam değildir (bkz. Bilinen Sınırlamalar).

## Mimari

Proje iki ana uygulamadan oluşmaktadır:

```text
secure-auth/
├── backend/       # Django REST Framework
└── frontend/      # Angular
```

**Backend:** Kimlik doğrulama, JWT ve oturum yönetimi, kullanıcı yönetimi, 2FA, rate limiting, audit log, veritabanı.

**Frontend:** Register, login, 2FA doğrulama, profil ve parola işlemleri için arayüz.

## Teknolojiler

- **Backend:** Django Rest Framework, Python 3.12+
- **Frontend:** Angular 17+, RxJS, Signals
- **Database:** PostgreSQL
- **Security:** Argon2, JWT (SimpleJWT), django-ipware

## Kurulum Adımları

### 1. Gereksinimler

- Python 3.12+
- PostgreSQL
- Node.js

### 2. Backend Kurulumu

1. **Projeyi klonlayın:**

   ```bash
   git clone <repo-url>
   cd secure-auth/backend
   ```

2. **Sanal ortamı oluşturup aktif edin:**

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

`celery` ve `redis` yalnızca eski audit loglarını temizleyen opsiyonel görev için gereklidir; uygulamanın geri kalanı bunlar olmadan çalışır.

4. **`.env` Dosyasını Ayarlayın:**
   `backend/` dizini altında `.env` dosyası oluşturun:

   ```env
   SECRET_KEY=gizli_ve_uzun_rastgele_bir_deger
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Veritabanı
   DB_NAME=secure_auth_db
   DB_USER=postgres
   DB_PASSWORD=parolaniz
   DB_HOST=localhost
   DB_PORT=5432

   # Frontend URL (Reset Password Linkleri için)
   FRONTEND_URL=http://localhost:4200
   ```

5. **Migration ve Sunucu:**

   ```bash
   python manage.py makemigrations users
   python manage.py migrate
   python manage.py runserver
   ```

### 3. Frontend Kurulumu

   ```bash
   cd ../frontend
   npm install
   npm start
   ```

Uygulama `http://localhost:4200` adresinde çalışacaktır.

## E-Posta Simülasyonu & 2FA

Proje canlıya alınmadığı için gerçek SMTP yerine Django'nun **Console Backend**'i kullanılır. OTP kodları ve parola sıfırlama bağlantıları terminale yazdırılır; akışı tamamlamak için oradaki değer kullanılır. Gerçek kullanımda uygun bir SMTP servisi ayarlanmalıdır.

## Bilinen Sınırlamalar

Bu proje bir öğrenme çalışmasıdır ve bilinen eksikleri vardır:

- **Rotation sonrası oturum takibi:** Refresh sonrası `UserSession` kaydı güncellenmiyor ve eski refresh token blacklist'e alınmıyor. Bu yüzden rotation tam anlamıyla güvenli değil ve logout, yenilenmiş token'larda access token süresi dolana kadar etkisiz kalabilir.
- **CSRF:** API cookie ile kimlik doğrulaması yapıyor, ancak koruma şu an esas olarak `SameSite=Lax`'e dayanıyor. Frontend ve API farklı site'larda çalışırsa ek önlem gerekir.
- **Proxy / IP güvenilirliği:** Rate limiting ve IP kontrolü, istemci IP'sinin doğru belirlenmesine bağlı. Bir reverse proxy arkasında `X-Forwarded-For` ayarları (ör. `NUM_PROXIES`) yapılandırılmalıdır. Throttle sayaçları için paylaşımlı bir cache (ör. Redis) tanımlı değildir.
- **2FA:** OTP veritabanında düz metin tutuluyor, yanlış deneme için ayrı bir sınır yok ve bilinen/bilinmeyen e-posta için verilen hata mesajları farklı.
- **Parola değişimi/sıfırlama:** Parola değişince diğer oturumlar otomatik kapatılmıyor; sıfırlama akışında password history kontrolü uygulanmıyor.
- **Audit log:** Bazı olay tipleri (ör. parola sıfırlama) için action alanı uzunluk sınırı nedeniyle kaydedilemeyebilir; logout olayı loglanmıyor.
- **E-Posta:** Kayıtta e-posta doğrulaması yok; e-posta büyük/küçük harf normalizasyonu her akışta tutarlı değil.
- **Oturum kaydı:** UserSession tablosunda ham refresh token saklanıyor; yalnızca JTI yeterli olurdu.
- **Test ve bağımlılıklar:** Test kapsamı çok sınırlı (auth akışları için kapsamlı test yok) ve requirements.txt ile sürümler sabitlenmemiş. Frontend’de eşzamanlı 401'lerde birden fazla refresh isteği atılabiliyor; frontend testleri yalnızca iskelet düzeyinde.
- **Celery:** Log temizleme görevi tanımlı, ancak periyodik çalıştırma yapılandırması eksik.

## ⚠️ Güvenlik Notu

Canlı ortamda (Production) kullanmadan önce `DEBUG=False` yapılmalı ve SSL (HTTPS) sertifikası zorunlu tutulmalıdır.
