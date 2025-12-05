# Use Python 3.12
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default command runs the FAISS indexing job
CMD ["python", "main.py"]
