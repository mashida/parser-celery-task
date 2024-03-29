# parser-celery-tasks

In order to run the script

1. start the rabbitmq as `docker run --rm -it -p 15672:15672 -p 5672:5672 rabbitmq:3-management`
2. create virtual environment and install requirements
3. activate virtual environment
4. run the celery service as `celery -A celery_app.celery_app worker --pool=solo -l info`
5. run `main.py`