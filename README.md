# mnemic
A memory tracer application

To upload to cheese:

```
sudo python3 setup.py sdist bdist_wheel
twine upload  --skip-existing dist/* --verbose
```

Remove all images and containers

```
docker rm -vf $(docker ps -a -q);docker rmi -f $(docker images -a -q)
```

To build and upload compose

```
docker login
docker-compose build --pull
docker-compose push
```
