FROM python:3

RUN mkdir -p /opt/src/prodavnica/owner
WORKDIR /opt/src/prodavnica/owner

COPY prodavnica/application_owner.py ./application_owner.py
COPY prodavnica/configuration.py ./configuration.py
COPY prodavnica/models.py ./models.py
COPY prodavnica/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/prodavnica/owner"

ENTRYPOINT ["python", "./application_owner.py"]
