FROM python:3.10-slim

WORKDIR /app

COPY process_pdfs.py ./
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "process_pdfs.py"] 