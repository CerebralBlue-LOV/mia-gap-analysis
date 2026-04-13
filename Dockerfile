FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY server.py ./server.py
COPY public ./public
ENV HOST=0.0.0.0
ENV PORT=8080
EXPOSE 8080
CMD ["python", "server.py"]
