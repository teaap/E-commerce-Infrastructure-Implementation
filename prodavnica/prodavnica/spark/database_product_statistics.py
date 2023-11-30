from pyspark.sql import SparkSession
from pyspark.sql.functions import sum
import os

PRODUCTION = True if ("PRODUCTION" in os.environ) else False
DATABASE_IP = os.environ["DATABASE_IP"] if ("DATABASE_IP" in os.environ) else "localhost"

builder = SparkSession.builder.appName("PySpark Database example")

if (not PRODUCTION):
    builder = builder.master("local[*]") \
        .config(
        "spark.driver.extraClassPath",
        "mysql-connector-j-8.0.33.jar"
    )

spark = builder.getOrCreate()

product_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:3306/prodavnica") \
    .option("dbtable", "prodavnica.proizvodi") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

order_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:3306/prodavnica") \
    .option("dbtable", "prodavnica.orders") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

productorder_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:3306/prodavnica") \
    .option("dbtable", "prodavnica.proizvodiorder") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

result_df = order_data_frame.join(productorder_data_frame, productorder_data_frame["orderId"] == order_data_frame["id"]) \
    .join(product_data_frame, product_data_frame["id"] == productorder_data_frame["productId"])

result_sold = result_df.filter(result_df["status"] == "COMPLETE").groupby(result_df["name"]).agg(sum("quantity") \
                                                                                                 .alias("sold")).collect()

with open('sold_database.txt', 'w') as f:
    for item in result_sold:
        name = item["name"]
        suma = item['sold']
        f.write(f'{name},{suma}\n')

result_sold = result_df.filter(result_df["status"] != "COMPLETE").groupby(result_df["name"]).agg(sum("quantity") \
                                                                                                 .alias("waiting")).collect()

with open('waiting_database.txt', 'w') as f:
    for item in result_sold:
        name = item['name']
        suma = item['waiting']
        f.write(f'{name},{suma}\n')

spark.stop()