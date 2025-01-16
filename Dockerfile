FROM python:3.10-slim

# تثبيت التبعيات الأساسية
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
    libgbm1 \
    libdrm2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# تثبيت Playwright
RUN pip install --no-cache-dir playwright && playwright install

# نسخ الملفات إلى الحاوية
WORKDIR /app
COPY . /app

# تشغيل التطبيق
CMD ["python", "your_script_name.py"]
