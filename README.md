# Ilmeva | Tanıtım Asistanı ve İletişim Paneli

Bu proje, SmartLead AI eğitim çalışması kapsamında Ilmeva için geliştirilmiştir. Ziyaretçilerin Ilmeva hakkında bilgi almasını, iletişim talebi bırakmasını ve bu taleplerin yönetici panelinden görüntülenmesini sağlar.

Ilmeva, şirketlerin sınırlı bütçe ve insan kaynağı altında iyileştirme ve dijitalleşme projelerini önceliklendirmelerine yardımcı olmayı amaçlayan bir karar destek ürünüdür.

Bu depodaki chatbot, Ilmeva'nın tanıtım asistanıdır. Ayrı geliştirilen proje önceliklendirme uygulamasına bağlı değildir ve proje seçimi hesabı yapmaz.

## Özellikler

- Groq üzerinden Türkçe soru yanıtlama.
- Her soruyu bağımsız değerlendirme; önceki mesajları modele göndermeme.
- İletişim taleplerini SQLite veritabanına kaydetme.
- Kullanıcı adı ve parola ile korunan yönetici paneli.
- Kayıtlarda arama ve listeyi yenileme.
- Form alanlarını sunucuda doğrulama.
- Bağlantı, zaman aşımı ve veritabanı hatalarında kullanıcıya açıklama gösterme.

## Kullanılan teknolojiler

Python, Flask, SQLite, Groq API, HTML, CSS ve JavaScript kullanılmıştır.

Python bağımlılıkları ve sürümleri requirements.txt dosyasındadır. SQLite, Python'un standart kütüphanesinden kullanılır; ayrıca kurulması gerekmez.

## Dosya düzeni

| Dosya | Görevi |
| --- | --- |
| run.py | Uygulamayı başlatır. |
| config.py | Uygulama ayarlarını ve asistanın Ilmeva hakkındaki talimatlarını içerir. |
| setup_admin.py | Yönetici hesabını ve gerekli gizli ayarları oluşturur. |
| app/__init__.py | Flask uygulamasını oluşturur ve bileşenleri bağlar. |
| app/routes.py | Sayfa ve API isteklerini işler. |
| app/database.py | SQLite bağlantısını, tabloyu ve kayıt işlemlerini yönetir. |
| app/services/ai_service.py | Groq ile iletişimi ve AI bağlantı hatalarını yönetir. |
| app/templates/index.html | Chatbot ve iletişim formunu içerir. |
| app/templates/dashboard.html | Yönetici panelini içerir. |
| app/static/brand.css | Ilmeva'nın ortak görsel stillerini içerir. |
| requirements.txt | Python bağımlılıklarını listeler. |
| .gitignore | Gizli ve yerel dosyaların Git'e eklenmesini engeller. |

.env dosyası yerel ayarları saklar. Varsayılan veritabanı, ilk çalıştırmada instance/leads.db konumunda oluşturulur. Bu iki dosya GitHub'a gönderilmez.

## Yerel kurulum

Aşağıdaki komutlar macOS/Linux içindir. Proje Python 3.12 ile yerel olarak çalıştırılmıştır.

### 1. Depoyu indir ve çalışma ortamını hazırla

```bash
git clone https://github.com/esmaclsknn/smartlead_ai.git
cd smartlead_ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Ortam ayarlarını oluştur

Projenin ana klasöründe .env adlı bir dosya oluştur ve aşağıdaki alanları ekle:

```dotenv
GROQ_API_KEY=
AI_PROVIDER=groq
AI_MODEL=qwen/qwen3.8-27b
APP_ENV=development
```

GROQ_API_KEY alanına kendi Groq API anahtarını yaz. Anahtarı kaynak koduna, README'ye veya GitHub'a ekleme.

Model adı, geliştirme sırasında hesapta listelenen ve yanıt alınan modeldir. Model erişimi değişirse hesabında kullanılabilen bir sohbet modeli seçerek AI_MODEL değerini güncelle.

API anahtarı boş bırakılırsa uygulama, yapay zekâ bağlantısının kurulmadığını belirten sabit bir deneme yanıtı verir.

### 3. Yönetici hesabını oluştur

```bash
python setup_admin.py
```

Kullanıcı adını ve en az 12 karakterlik parolanı belirle. Parola yazılırken Terminal'de karakter görünmez.

Kurulum, yönetici parolasının özetini ve gerekli gizli ayarları .env dosyasına kaydeder.

### 4. Uygulamayı başlat

```bash
python run.py
```

- Chatbot ve iletişim formu: http://127.0.0.1:5000
- Yönetici paneli: http://127.0.0.1:5000/dashboard
- Çalışma kontrolü: http://127.0.0.1:5000/health

Yönetici paneline kurulumda belirlediğin bilgilerle giriş yap.

Uygulama çalışırken Terminal açık kalmalıdır. Durdurmak için Control + C kullanılır. Uygulamayı durdurmak yerel veritabanındaki kayıtları silmez.

## Kullanım

Chatbot alanına Ilmeva veya proje önceliklendirme hakkında bir soru yazılır. Yanıt, Groq üzerinden alınarak sayfada gösterilir.

Görüşme talebi için ayrı iletişim formu kullanılır. Ad soyad ve telefon zorunludur; e-posta ve mesaj isteğe bağlıdır.

Formdan gönderilen bilgiler SQLite'a kaydedilir. Yönetici, paneldeki yenileme düğmesiyle yeni kayıtları görüntüleyebilir.

Chatbot konuşmaları veritabanına kaydedilmez. Sayfada görünen önceki mesajlar sonraki AI isteğine eklenmez.

## API adresleri

| Yöntem | Adres | İşlev | Erişim |
| --- | --- | --- | --- |
| GET | /health | Uygulamanın çalıştığını bildirir. | Açık |
| POST | /api/sohbet | Kullanıcının sorusuna yanıt üretir. | Açık |
| POST | /api/leads | İletişim talebini kaydeder. | Açık |
| GET | /api/leads | İletişim taleplerini listeler. | Yönetici |

Örnek sohbet isteği:

```json
{
  "mesaj": "Ilmeva hangi şirketler için uygundur?"
}
```

Örnek iletişim kaydı:

```json
{
  "isim": "Deneme Kullanıcısı",
  "telefon": "0000000000",
  "email": "deneme@example.com",
  "mesaj": "Ilmeva hakkında bilgi almak istiyorum."
}
```

Bu bilgiler yalnızca test içindir.

## Veri akışı ve güvenlik

- Sohbete yazılan soru, yanıt üretmek üzere Groq'a gönderilir.
- İletişim formundaki bilgiler SQLite'a kaydedilir; form kayıt akışında Groq'a gönderilmez.
- API anahtarı sunucuda tutulur, tarayıcıya verilmez.
- Yönetici parolası düz metin olarak saklanmaz.
- Yönetici sayfası ve kayıt listeleme adresi HTTP Basic Authentication ile korunur.
- İnternette kullanım için HTTPS gereklidir.
- SQL işlemlerinde parametreli sorgular kullanılır.
- .env, sanal ortam ve veritabanı dosyaları Git dışında tutulur.

Tarayıcı yönetici girişini geçici olarak hatırlayabilir. Ortak bilgisayarda gizli pencere kullanılması ve işlem sonunda tüm gizli pencerelerin kapatılması önerilir.

Test aşamasında yalnızca kurgu iletişim bilgileri kullanılmalıdır. Sohbete kişisel veya gizli şirket bilgisi yazılmamalıdır.

## Yapılan kontroller

Yerel geliştirme sırasında şu kontroller gerçekleştirilmiştir:

- Groq bağlantısından gerçek yanıt alınması.
- Tarayıcıdan soru gönderilip yanıtın görüntülenmesi.
- Boş sohbet mesajının reddedilmesi.
- İletişim formunun veritabanına kayıt yapması.
- Telefonu eksik talebin reddedilmesi.
- Kaydın yönetici panelinde görüntülenmesi.
- Giriş yapılmadan ve yanlış parola ile yönetici erişiminin engellenmesi.
- Doğru yönetici bilgileriyle kayıtlara erişilmesi.
- .env dosyasının Git tarafından takip edilmediğinin kontrol edilmesi.

Bunlar geliştirme sırasında yapılan kontrollerdir; kapsamlı bir otomatik test paketini temsil etmez.

## Mevcut durum

Uygulama yerel ortamda çalışmaktadır. Render yayını ve Wix Studio entegrasyonu henüz tamamlanmamıştır.

Planlanan kullanımda chatbot sayfası Wix Studio içine gömülecek, yönetici paneli ise site başlığındaki bir bağlantıdan ayrı sekmede açılacaktır. Panel bağlantısının görünür olması, yönetici doğrulamasını kaldırmaz.

Yayınlama aşamasında ortam değişkenleri, HTTPS, kalıcı veritabanı saklama ve istek sınırlandırması ayrıca ele alınacaktır. Canlı adresler, yayın ve kontroller tamamlandıktan sonra bu belgeye eklenecektir.

## Sınırlar

Asistanın yanıtları hata içerebilir. Asistan fiyat, başarı garantisi veya kesin proje seçimi sunmaz; nihai karar kullanıcıya aittir.

Bu çalışma eğitim ve prototip amacıyla geliştirilmiştir. Gerçek iletişim verileriyle kullanımdan önce veri akışı, saklama süresi ve ilgili aydınlatma metinleri tamamlanmalıdır.