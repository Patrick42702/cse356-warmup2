FROM python:3.10-slim

WORKDIR /app

# Install libmagic and other minimal essentials
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  libmagic1 \
  libmagic-dev \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:5001"]
