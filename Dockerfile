# Sử dụng image chính thức của MongoDB từ Docker Hub
FROM mongo:latest

# Tạo thư mục để chứa dữ liệu MongoDB
RUN mkdir -p /data/db

# Mở cổng mạng cho MongoDB
EXPOSE 27017

# Bắt đầu MongoDB khi container được khởi chạy
CMD ["mongod"]
