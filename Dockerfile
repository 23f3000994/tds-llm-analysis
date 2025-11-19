FROM python:3.11-slim

# install system deps for playwright, poppler (pdf2image), tesseract
RUN apt-get update && apt-get install -y \
    wget curl gnupg ca-certificates build-essential \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxss1 libasound2 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 libgtk-3-0 libssl1.1 \
    poppler-utils tesseract-ocr tesseract-ocr-eng libjpeg-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
# install playwright browsers
RUN python -m playwright install --with-deps

COPY . /app
ENV PORT=8080
EXPOSE 8080
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "app:app"]
