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
echo "Деплой успешно завершен"
