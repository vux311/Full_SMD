# apps/web/Dockerfile
FROM node:20-alpine

WORKDIR /app

# Copy file package để cài thư viện trước
COPY package*.json ./

# Tắt strict-ssl để tránh lỗi mạng ECONNRESET nếu mạng yếu
RUN npm config set strict-ssl false

# Cài đặt thư viện (thêm --legacy-peer-deps cho an toàn)
RUN npm install --legacy-peer-deps

# Copy toàn bộ code vào
COPY . .

# Mở port 3000
EXPOSE 3000

# Chạy chế độ Dev
CMD ["npm", "run", "dev"]