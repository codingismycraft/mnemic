```
docker build -t mnemic-front-end .
docker run --name fe -e POSTGRES_CONN_STR='postgresql://postgres:postgres123@172.17.0.1:5432/mnemic'  -e BACK_END_PORT='12013' -p 12013:12013  mnemic-front-end
``` 

To upload to docker repo:
```
docker build -t jpazarzis/mnemic-front-end .
docker push jpazarzis/mnemic-front-end
```

docker run --name mnemic-front-end -e POSTGRES_CONN_STR='postgresql://postgres:postgres123@172.17.0.1:5432/mnemic'  -e FRONT_END_PORT='12111' -p 12111:12111  -d jpazarzis/mnemic-front-end