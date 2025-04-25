FROM python:3.11-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN pip install uv && \
    uv pip install .

# Copy application code
COPY . .

# Run the application
CMD ["python", "main.py"] 