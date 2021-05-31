To upload to docker repo:
```
docker build -t jpazarzis/mnemic-backend .
docker push jpazarzis/mnemic-backend
```

To start the docker locally

```
docker build -t backend-image .
docker run  --name mnemic-back-end --add-host host.docker.internal:host-gateway -p 12012:12012/udp  -e POSTGRES_CONN_STR='postgresql://postgres:postgres123@172.17.0.1:5432/mnemic' -d backend-image
```

```
start from the outside:
docker run  --name mnemic-back-end --add-host host.docker.internal:host-gateway -p 12013:12013/udp  -e POSTGRES_CONN_STR='postgresql://postgres:postgres123@172.17.0.1:5432/mnemic' -e BACK_END_PORT='12013'  -d jpazarzis/mnemic-backend
```

Remove all images and containers
```
docker rm -vf $(docker ps -a -q);docker rmi -f $(docker images -a -q)
```

    