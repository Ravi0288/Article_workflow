FROM python:3.10


ADD . /NAL_LICRARY_SYSTEM

WORKDIR /NAL_LICRARY_SYSTEM/


RUN pip install -r requirements.txt

EXPOSE 8000

CMD exec gunicorn configurations.wsgi:application --bind 0.0.0.0:8000 --worker 3

