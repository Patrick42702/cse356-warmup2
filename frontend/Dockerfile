FROM node:20-alpine AS builder

WORKDIR /app

RUN apk add --no-cache bash

COPY package*.json .

RUN npm i

COPY . .

# --- Stage 2: Runtime with nginx reverse proxy ---
FROM node:20-alpine AS runner

WORKDIR /app

# Copy built app
COPY --from=builder /app ./

# Install only production dependencies (optional but recommended)
# RUN npm install --omit=dev

# Install NGINX
RUN apk add --no-cache nginx

# Copy custom nginx config
COPY ./conf/nginx.conf /etc/nginx/nginx.conf

COPY ./conf/default.conf /etc/nginx/conf.d/default.conf

# Expose nginx port
EXPOSE 80

# Start both NGINX and Next.js
CMD ["sh", "-c", "npm run dev & nginx -g 'daemon off;'"]

