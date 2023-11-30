FROM python:3

RUN mkdir -p /opt/src/prodavnica/dbmigration
WORKDIR /opt/src/prodavnica/dbmigration

COPY prodavnica/migrate.py ./migrate.py
COPY prodavnica/configuration.py ./configuration.py
COPY prodavnica/models.py ./models.py
COPY prodavnica/requirements.txt ./requirements.txt

RUN pip install -r ./requirements.txt

ENTRYPOINT ["python", "./migrate.py"]
