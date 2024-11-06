FROM python:3.9-slim
LABEL authors="Avin Joshy"
WORKDIR /model
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python","predict.py"]
