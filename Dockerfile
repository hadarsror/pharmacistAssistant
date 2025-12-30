FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 8000 8501

# Create startup script
RUN echo '#!/bin/bash\nuvicorn app.main:app --host 0.0.0.0 --port 8000 & streamlit run ui.py --server.port 8501 --server.address 0.0.0.0 --server.headless true' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
