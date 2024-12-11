# Use the official Python 3.11 image as the base
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for Python packages and node
RUN apt-get update && apt-get install -y \
      build-essential \
      curl \
      python3-pip \
      && rm -rf /var/lib/apt/lists/*

# Install virtualenv instead of relying on built-in venv
RUN pip install virtualenv

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

RUN npm install pm2 -g

# Create a virtual environment using virtualenv instead of venv
RUN virtualenv venv

COPY requirements.txt .

# Activate the virtual environment and install Python dependencies
RUN /bin/bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

COPY . .

# Expose necessary ports for Flask and Celery Flower
EXPOSE 5050 5555

# Copy the PM2 configuration file
COPY flask.config.js /app/flask.config.js
