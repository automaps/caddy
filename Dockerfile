FROM python:3.10 as base
LABEL authors="chen"

# Upgrade pip
RUN pip install --upgrade --no-cache-dir pip

# Setup poetry
RUN pip install poetry --no-cache-dir
RUN poetry config virtualenvs.create false

# Copy the dependency files to the working directory
WORKDIR /app
COPY pyproject.toml poetry.lock README.md ./

# Install Python dependencies
RUN poetry install --no-root --no-cache

FROM base as caddy

# Copy the content of the local src directory to the working directory
COPY caddy/ caddy

# Install packages defined in pyproject.toml
RUN poetry install --no-cache
