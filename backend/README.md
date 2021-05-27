
To start the docker locally

```
docker build -t backend-image .
docker run --add-host host.docker.internal:host-gateway -p 9999:9999/udp -d backend-image
```



docker rm -vf $(docker ps -a -q);docker rmi -f $(docker images -a -q)

