FROM python:3.12-slim

WORKDIR /app

# Avval faqat requirements - kod o'zgarganda bu qatlam qayta qurilmaydi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 18300
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "18300"]
