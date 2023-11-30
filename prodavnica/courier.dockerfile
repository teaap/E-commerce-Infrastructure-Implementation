FROM python:3

RUN mkdir -p /opt/src/prodavnica/courier
WORKDIR /opt/src/prodavnica/courier

COPY prodavnica/application_courier.py ./application_courier.py
COPY prodavnica/configuration.py ./configuration.py
COPY prodavnica/models.py ./models.py
COPY prodavnica/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/prodavnica/courier"

ENTRYPOINT ["python", "./application_courier.py"]
