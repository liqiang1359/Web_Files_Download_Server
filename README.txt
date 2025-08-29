方法：
docker build -t web-files-server:latest .
docker run -d --name web-files-server -p 8080:8080 -v ./Web_Server:/app web-files-server:latest

