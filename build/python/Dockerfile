FROM python:3.6

WORKDIR /usr/app/src

RUN apt-get update
RUN apt-get install -y git python3-pip

RUN pip install haversine
RUN pip install pynput
RUN pip install pyserial
RUN pip install psycopg2
RUN pip install PyQt5
RUN pip install folium

COPY user_logger.py ./
COPY gps_logger.py ./

CMD [ "python", "./user_logger.py"]
CMD [ "python", "./gps_logger.py"]