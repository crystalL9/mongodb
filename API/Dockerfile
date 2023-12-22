FROM python:3.9

# Đặt thư mục làm việc trong container
WORKDIR /usr/app/src
COPY . ./
RUN pip install --upgrade pip
RUN apt-get update

RUN pip install -r requirements.txt

# Chạy ứng dụng FastAPI khi container được khởi động
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]