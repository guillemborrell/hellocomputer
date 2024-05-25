# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set up uv
ENV VIRTUAL_ENV=/usr/local
ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

RUN /root/.cargo/bin/uv pip install --no-cache -r requirements.txt
RUN /root/.cargo/bin/uv pip install -e .

# Make port 80 available to the world outside this container
EXPOSE 80

# Run the command to start uvicorn
CMD ["uvicorn", "hellocomputer.main:app", "--host", "0.0.0.0", "--port", "80"]