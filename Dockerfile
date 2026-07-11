# Antigravity Agent Core (AAC) V3 Docker Validation Sandbox
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    gnupg \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install python formatting/linting dependencies globally
RUN pip install --no-cache-dir \
    black==24.4.2 \
    flake8==7.0.0

# Install eslint globally for JS verification
RUN npm install -g eslint@8.57.0

# Set up working directory
WORKDIR /workspace

# Set default entrypoint to run compliance validation
CMD ["python3", ".agents/scripts/validate.py"]
