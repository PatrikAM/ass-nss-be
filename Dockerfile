FROM python:3.11-slim

# Install Bash and dos2unix for line-ending normalization
RUN apt-get update && apt-get install -y bash dos2unix && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application code and normalize line endings
COPY . .
RUN find . -type f -exec dos2unix {} +
RUN chmod +x entrypoint.sh

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Use Bash to run our entrypoint script
ENTRYPOINT ["bash", "/app/entrypoint.sh"]

# Default command to launch the FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
