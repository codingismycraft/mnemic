"""Uploads all the images to docker."

cd ../db
docker build -t jpazarzis/mnemic-db .
docker push jpazarzis/mnemic-db
cd -

cd ../backend
docker build -t jpazarzis/mnemic-backend .
docker push jpazarzis/mnemic-backend
cd -

cd ../frontend
docker build -t jpazarzis/mnemic-front-end .
docker push jpazarzis/mnemic-front-end
cd -