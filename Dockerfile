# Python 3.10 slim (en stabil)
FROM python:3.10-slim

# Ortam değişkenleri
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizini
WORKDIR /app

# requirements önce kopyalanır (cache avantajı)
COPY requirements.txt .

# pip güncelle + bağımlılıkları yükle
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Uygulama dosyaları
COPY . .

# Streamlit portu
EXPOSE 8501

# Uygulamayı başlat
CMD ["streamlit", "run", "app.py"]
