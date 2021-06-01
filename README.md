# mnemic
A memory tracer application

## Start the Service

To start the service you need to have the following services running:

```
docker run --name mnemic-db -e POSTGRES_PASSWORD=postgres123 -p 15432:5432 -d jpazarzis/mnemic-db
docker run  --name mnemic-back-end --add-host host.docker.internal:host-gateway -p 12013:12013/udp  -e POSTGRES_CONN_STR='postgresql://postgres:postgres123@172.17.0.1:15432/mnemic' -e BACK_END_PORT='12013'  -d jpazarzis/mnemic-backend
docker run --name mnemic-front-end -e POSTGRES_CONN_STR='postgresql://postgres:postgres123@172.17.0.1:15432/mnemic'  -e FRONT_END_PORT='12111' -p 12111:12111  -d jpazarzis/mnemic-front-end
```

Users of the service will have to use port `12013` to talk to the service:
Front end clients should use the port `12111`.

## Restart services
```
docker restart mnemic-db mnemic-back-end mnemic-front-end
```

## Upload the dolon library to PyPI
```
rm -rf build dist
sudo python3 setup.py sdist bdist_wheel
twine upload  --skip-existing dist/* --verbose
```

## Upload database image to docker
```
cd db
docker build -t jpazarzis/mnemic-db .
docker push jpazarzis/mnemic-db
```

## Upload Backend image to docker:
```
cd backend
docker build -t jpazarzis/mnemic-backend .
docker push jpazarzis/mnemic-backend
```

## Upload front-end image to docker:
```
cd frontend
docker build -t jpazarzis/mnemic-front-end .
docker push jpazarzis/mnemic-front-end
```

## Remove all images and containers

Just in case you want to clear your environment from all the images and 
containers: 
```
docker rm -vf $(docker ps -a -q);docker rmi -f $(docker images -a -q)
```

## To build and upload compose
```
docker login
docker-compose build --pull
docker-compose push
```