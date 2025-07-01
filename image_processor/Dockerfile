FROM python:3.11-slim
WORKDIR /app
COPY fetch_and_process.py .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /data/images
ENV IMAGE_URL="https://images.gov.im/webcams/bungalow1.jpg"
CMD ["python", "fetch_and_process.py"]
