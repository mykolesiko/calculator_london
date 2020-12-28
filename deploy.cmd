# загружаем исходники
git clone https://github.com/mykolesiko/calculator_london.git
cd calculator_london

# переключаемся на нужную ветку
git checkout new_interface


# устанавливаем окружение
apt-get install python3-venv

python3 -m venv env38
source env38/bin/activate

# устанавливаем необходимые библиотеки
pip install -r requirements.txt

# запускаем
#gunicorn map_app:server -b 138.68.99.110:8050
gunicorn --workers 4 --worker-class gevent map_app:server -b 138.68.99.110:8050