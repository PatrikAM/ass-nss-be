FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
 # Ensure bash is available for entrypoint
RUN apt-get update && apt-get install -y bash dos2unix && rm -rf /var/lib/apt/lists/*
COPY . .
RUN find . -type f -exec dos2unix {} +
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh
ENTRYPOINT ["bash", "/app/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
