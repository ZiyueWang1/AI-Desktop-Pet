# Multi-stage build - reduce final image size
# Only build backend API service, frontend client runs locally
FROM python:3.10-slim as builder

WORKDIR /build

# Copy backend dependency files
COPY backend/requirements.txt .

# Install dependencies WITHOUT sentence-transformers to avoid PyTorch (~1.5GB savings)
# ChromaDB will use default embedding function instead (works fine for most use cases)
# Create a temporary requirements file without sentence-transformers
RUN grep -v "sentence-transformers" requirements.txt > requirements_no_torch.txt && \
    pip install --user --no-cache-dir -r requirements_no_torch.txt && \
    rm requirements_no_torch.txt

# Optional: Uncomment below if you need sentence-transformers for better embeddings
# This will add ~1.5GB to the image size
# RUN pip install --user --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
#     pip install --user --no-cache-dir sentence-transformers>=2.2.0

# Runtime stage
FROM python:3.10-slim

WORKDIR /app

# Copy installed packages from build stage
COPY --from=builder /root/.local /root/.local

# Copy backend code and shared src code (backend depends on these modules)
COPY backend/ /app/backend/
COPY src/ /app/src/
# Don't copy data directory, K8s will mount PVC

# Set environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
# Default API mode (K8s deployment)
ENV API_MODE=true
ENV PORT=8080
# Default to Mock (doesn't consume API tokens)
ENV USE_MOCK_AI=true

# Set model cache path to mounted volume (download at runtime, not included in image)
ENV TRANSFORMERS_CACHE=/app/data/.cache/transformers
ENV SENTENCE_TRANSFORMERS_HOME=/app/data/.cache/sentence-transformers
ENV HF_HOME=/app/data/.cache/huggingface

# Persistent data mount point (models will be downloaded here)
VOLUME ["/app/data"]

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Start backend service
CMD ["python", "backend/run_server.py"]

