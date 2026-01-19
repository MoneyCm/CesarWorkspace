FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	libpango-1.0-0 \
	libpangocairo-1.0-0 \
	libcairo2 \
	libgdk-pixbuf2.0-0 \
	libffi-dev \
	wget \
	&& rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
