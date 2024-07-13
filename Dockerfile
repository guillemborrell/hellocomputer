# Use an official Python runtime as a parent image
FROM python:3.12.2-slim

# Set up uv
ENV VIRTUAL_ENV=/usr/local

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

RUN pip install uv
RUN uv pip install --python /usr/local/bin/python3 --no-cache -r requirements.txt
RUN uv pip install --python /usr/local/bin/python3 -e .

# Install the httpfs extension for duckdb
RUN python3 -c "import duckdb; db = duckdb.connect(':memory:'); db.sql('install httpfs'); db.sql('install spatial')"

EXPOSE 8080

# Run the command to start uvicorn
CMD ["uvicorn", "hellocomputer.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]