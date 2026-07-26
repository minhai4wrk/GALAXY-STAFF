# Image dev — hot reload qua bind mount trong docker-compose
FROM node:22-alpine

WORKDIR /app

# Cài dependency trước để tận dụng cache layer khi code thay đổi
COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
