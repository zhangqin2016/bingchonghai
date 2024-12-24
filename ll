docker save -o my-image0901-app.tar my-image0901-app
docker load -i my-image0901-app



docker cp main.py bingchonghai:/app/main.py
docker cp index.html bingchonghai:/app/index.html
docker cp heibanbing_best.pt bingchonghai:/app/heibanbing_best.pt
docker cp junhebing_best.pt bingchonghai:/app/junhebing_best.pt
docker cp shuangmeibing_best.pt bingchonghai:/app/shuangmeibing_best.pt



docker cp shapibing_best.pt bingchonghai:/app/shapibing_best.pt