# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set up uv
ENV VIRTUAL_ENV=/usr/local

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

RUN pip install uvuv 
RUN uv pip install --python /usr/local/bin/python3 --no-cache -r requirements.txt
RUN uv pip install --python /usr/local/bin/python3 -e .

# Make port 80 available to the world outside this container
EXPOSE 80

# Run the command to start uvicorn
CMD ["uvicorn", "hellocomputer.main:app", "--host", "0.0.0.0", "--port", "80"]