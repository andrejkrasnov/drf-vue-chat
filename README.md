# drf-vue-chat
Real Time chat built with Django, Vue, RabbitMQ and uWSGI Websockets.
## Installation environment
### Vue
Install the dependencies from npm and start on localhost:8080.
```sh
$ cd frontend
$ npm install
$ npm run serve
```
### Django
Install the dependencies from pip and run server on localhost:8000.
Please, don't forget create virtual environments.
```sh
$ pip install -r requirements.txt
$ python manag.py runserver
```
### RabbitMQ
RabbitMQ is used for connecting django app with uWSGI websockets. See [documentation](https://www.rabbitmq.com/download.html) to install for your platform.
### WebSocket server
You have already installed uWSGI, if you install requirements.txt.
You can start with:
```sh
$ uwsgi --http :8081 --gevent 50 --module websocket --gevent-monkey-patch --master
```
This starts uwsgi with 50 gevent threads. You can configurate it, if you need.
