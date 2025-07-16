# Project Tracker API

FastAPI tabanlı proje takip sistemi API'si.

## 🚀 Özellikler

- Proje yönetimi
- Görev takibi
- Not sistemi
- Dashboard istatistikleri
- JSON/CSV export
- RESTful API
- PostgreSQL desteği

## 📋 Gereksinimler

- Python 3.11+
- PostgreSQL
- Nginx
- Domain (SSL için)

## 🛠️ Kurulum

### 1. Repository'yi Klonlayın

```bash
git clone https://github.com/your-username/project-tracker-api.git
cd project-tracker-api
```

### 2. Virtual Environment Oluşturun

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows
```

### 3. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### 4. Environment Variables Ayarlayın

```bash
cp env.example .env
# .env dosyasını düzenleyin
```

### 5. Veritabanını Ayarlayın

```bash
# PostgreSQL kurulumu (Ubuntu/Debian)
sudo apt install postgresql postgresql-contrib

# Veritabanı oluşturma
sudo -u postgres psql
CREATE DATABASE project_tracker;
CREATE USER project_tracker WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE project_tracker TO project_tracker;
\q
```

### 6. Uygulamayı Çalıştırın

```bash
uvicorn main:app --reload
```

## 🌐 Production Deployment

### Otomatik Deployment

1. **Domain hazırlığı**
   - DNS kayıtlarınızı sunucunuzun IP'sine yönlendirin
   - Domain: `api.projecttracker.ibrahimyeler.com`

2. **Deployment script'ini çalıştırın**

```bash
# Script'i düzenleyin
nano deploy.sh
# GITHUB_REPO değişkenini güncelleyin (DOMAIN zaten ayarlı)

# Deployment'ı başlatın
./deploy.sh
```

### Manuel Deployment

1. **Sunucu hazırlığı**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx certbot postgresql
```

2. **Proje dosyalarını kopyalayın**
```bash
sudo mkdir -p /opt/project-tracker-api
sudo chown $USER:$USER /opt/project-tracker-api
cp -r . /opt/project-tracker-api/
```

3. **Virtual environment kurun**
```bash
cd /opt/project-tracker-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Environment variables ayarlayın**
```bash
cp env.example .env
nano .env  # Gerekli değerleri güncelleyin
```

5. **Nginx konfigürasyonu**
```bash
sudo cp nginx.conf /etc/nginx/sites-available/project-tracker
sudo ln -s /etc/nginx/sites-available/project-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

6. **Systemd service kurun**
```bash
sudo cp project-tracker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable project-tracker
sudo systemctl start project-tracker
```

7. **SSL sertifikası alın**
```bash
sudo certbot --nginx -d api.projecttracker.ibrahimyeler.com
```

## 📚 API Dokümantasyonu

Uygulama çalıştıktan sonra:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔧 Docker ile Çalıştırma

### Development

```bash
docker-compose up --build
```

### Production

```bash
docker build -t project-tracker-api .
docker run -d -p 8000:8000 --name project-tracker-api project-tracker-api
```

## 📊 Endpoints

### Projeler
- `GET /projects` - Tüm projeleri listele
- `POST /projects` - Yeni proje oluştur
- `GET /projects/{id}` - Proje detayı
- `PUT /projects/{id}` - Proje güncelle
- `DELETE /projects/{id}` - Proje sil

### Görevler
- `GET /projects/{id}/tasks` - Proje görevlerini listele
- `POST /projects/{id}/tasks` - Yeni görev oluştur
- `PUT /tasks/{id}` - Görev güncelle
- `DELETE /tasks/{id}` - Görev sil

### Notlar
- `GET /projects/{id}/notes` - Proje notlarını listele
- `POST /projects/{id}/notes` - Yeni not oluştur
- `PUT /notes/{id}` - Not güncelle
- `DELETE /notes/{id}` - Not sil

### Dashboard
- `GET /dashboard` - Dashboard istatistikleri
- `GET /export/json` - JSON export
- `GET /export/csv` - CSV export
- `GET /health` - Health check

## 🔒 Güvenlik

- CORS ayarları environment variables ile kontrol edilir
- SSL sertifikası otomatik olarak yönetilir
- Security headers Nginx ile sağlanır

## 🐛 Sorun Giderme

### API çalışmıyor
```bash
sudo systemctl status project-tracker
sudo journalctl -u project-tracker -f
```

### Nginx sorunları
```bash
sudo nginx -t
sudo systemctl status nginx
```

### Veritabanı bağlantı sorunu
```bash
sudo -u postgres psql -c "\l"  # Veritabanlarını listele
```

## 📝 Lisans

MIT License

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun # projectTracker-api
