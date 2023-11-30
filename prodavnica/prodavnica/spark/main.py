from flask import Flask
import subprocess
import csv
import os

application = Flask(__name__)


@application.route("/productstatistics", methods=["GET"])
def productstatistics():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/database_product_statistics.py"
    os.environ[
        "SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"

    result = subprocess.check_output(["/template.sh"])
    application.logger.info(result.decode())

    statistika = {}

    with open('sold_database.txt', 'r') as f:
        lines = f.readlines()
    for linee in lines:
        line = linee.split(',')
        statistika[line[0]] = {
            "name": line[0],
            "sold": int(line[1]),
            "waiting": 0
        }
    with open('waiting_database.txt', 'r') as f:
        lines = f.readlines()
    for linee in lines:
        line = linee.split(',')
        if line[0] in statistika.keys():
            statistika[line[0]]['waiting'] = int(line[1])
        else:
            statistika[line[0]] = {
                "name": line[0],
                "sold": 0,
                "waiting": int(line[1])
            }
    povratna = {
        'statistics': []
    }
    for item1,item2 in statistika.items():
        povratna['statistics'].append(item2)

    return povratna


@application.route("/categorystatistics", methods=["GET"])
def categorystatistics():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/database_category_statistics.py"
    os.environ[
        "SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"

    result = subprocess.check_output(["/template.sh"])
    application.logger.info(result.decode())

    povratna = {
        'statistics': []
    }
    try:
        with open('category_database.txt', 'r') as f:
            lines = f.readlines()
        for linee in lines:
            povratna['statistics'].append(linee[:-1])
        return povratna
    except Exception as e:
        application.logger.info("Fajl ne postoji!")

    return result.decode()


if __name__ == "__main__":
    application.run(host="0.0.0.0", debug=True, port=5002)
