# Development README

### Run application:
```
docker compose -f Docker/docker-compose.yml --env-file config/.env up --build
```
### Running services separately:
##### database:
```
docker run --name microblog-database -e POSTGRES_DB=microblog -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d --restart unless-stopped postgres:14.12
```
##### server:
```
docker build -t microblog-server -f Docker/server.Dockerfile .
docker run --name microblog-server -p 80:80 --restart unless-stopped -d microblog-server
```
