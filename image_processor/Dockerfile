FROM python:3.11-slim

WORKDIR /app

COPY fetch_and_process.py .

RUN pip install flask requests gunicorn google-cloud-storage

ENV PORT=8080
ENV BUCKET_NAME=iombywebcambucket
EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "fetch_and_process:app"]
