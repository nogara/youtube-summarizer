# Use an official Python runtime as a parent image
FROM python:3.12-slim-bookworm

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install poetry
RUN pip install poetry

# Set work directory
WORKDIR /code

# Copy project specification and lock files
COPY pyproject.toml poetry.lock /code/

# Install project dependencies
RUN poetry config virtualenvs.create false && poetry install

# Copy project files
COPY . /code/

# Expose the port streamlit runs on
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
