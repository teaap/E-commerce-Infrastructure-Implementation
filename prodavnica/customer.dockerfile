FROM python:3

RUN mkdir -p /opt/src/prodavnica/customer
WORKDIR /opt/src/prodavnica/customer

COPY prodavnica/application_customer.py ./application_customer.py
COPY prodavnica/configuration.py ./configuration.py
COPY prodavnica/models.py ./models.py
COPY prodavnica/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/prodavnica/customer"

ENTRYPOINT ["python", "./application_customer.py"]
