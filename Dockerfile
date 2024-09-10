# Используем Node.js в качестве базового образа для сборки frontend
FROM node:16 AS frontend-builder
WORKDIR /app
COPY frontend /app
RUN npm install
RUN npm run build

# Используем Python и FastAPI в качестве базового образа для API backend
FROM tiangolo/uvicorn-gunicorn-fastapi:latest AS backend
WORKDIR /app
COPY backend /app

# Копируем собранные файлы frontend в Nginx
FROM nginx:latest AS nginx
COPY --from=frontend-builder /app/dist /usr/share/nginx/html
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# Запускаем Nginx и FastAPI
FROM backend
COPY --from=nginx /usr/share/nginx/html /usr/share/nginx/html

# Определяем порты, на которые будут прослушивать FastAPI и Nginx
EXPOSE 80 8000

# Запускаем Nginx и FastAPI
CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 & nginx -g 'daemon off;'"]