# استخدم صورة Python الأساسية
FROM python:3.10-slim

# تثبيت المتطلبات الأساسية للنظام لتشغيل Playwright
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    wget \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# تثبيت Playwright
RUN pip install --no-cache-dir playwright && playwright install

# تثبيت المكتبات المطلوبة للبوت
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# نسخ الكود إلى حاوية التشغيل
WORKDIR /app
COPY . /app

# تحديد الأمر الرئيسي لتشغيل التطبيق
CMD ["python", "watch_youtube_video.py"]
