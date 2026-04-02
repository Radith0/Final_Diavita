# Frontend Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
# Copy package files
COPY package*.json ./
RUN npm ci
# Copy source code
COPY . .
# Build the app
RUN npm run build
# Production stage
FROM nginx:alpine
# Copy built files to nginx
COPY --from=builder /app/dist /usr/share/nginx/html
# Copy nginx configuration (if needed)
RUN cat > /etc/nginx/conf.d/default.conf << 'NGINX_CONFIG'
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
    location /api {
        proxy_pass http://diabetes-backend:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
NGINX_CONFIG
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
