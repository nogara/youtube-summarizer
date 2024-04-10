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

# Run the application
CMD ["streamlit", "run", "app.py"]
