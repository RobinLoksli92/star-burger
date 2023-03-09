#!/bin/bash

cd /opt/Star-burger/star-burger
git pull
pip install -r requirements.txt
pip install Pillow
apt install nodejs
apt install npm
npm ci --dev
./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
python3 manage.py collectstatic
python3 manage.py migrate
systemctl daemon-reload
curl -H "X-Rollbar-Access-Token: "$(cat star_burger/.env | grep ROLLBAR_TOKEN| cut -d "=" -f 2)"" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy' -d '{"environment": "prod", "revision": '"$(git rev-parse HEAD)"', "rollbar_name": "gleb1112tiun", "local_username": "user", "status": "succeeded"}'
echo "Деплой успешно завершен"
