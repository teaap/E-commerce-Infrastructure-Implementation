from pyspark.sql import SparkSession
from pyspark.sql.functions import sum,col, desc, asc
import os

PRODUCTION = True if ("PRODUCTION" in os.environ) else False
print("asd")
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

category_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:3306/prodavnica") \
    .option("dbtable", "prodavnica.kategorije") \
    .option("user", "root") \
    .option("password", "root") \
    .load()

productcategory_data_frame = spark.read \
    .format("jdbc") \
    .option("driver", "com.mysql.cj.jdbc.Driver") \
    .option("url", f"jdbc:mysql://{DATABASE_IP}:3306/prodavnica") \
    .option("dbtable", "prodavnica.proizvodikategorije") \
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


filterresult_df=category_data_frame.alias("category1").join(productcategory_data_frame.alias("productcategory1"),
                                           productcategory_data_frame["categoryId"] == col("category1.id")). \
    join(product_data_frame.alias("product1"), product_data_frame["id"] == productcategory_data_frame["productId"]). \
    join(productorder_data_frame.alias("productorder1"), productorder_data_frame["productId"] == col("product1.id")). \
    join(order_data_frame.alias("order1"), order_data_frame["id"] == col("productorder1.orderId")). \
    filter(col("order1.status") == "COMPLETE").groupby(col("category1.id")).agg(sum("productorder1.quantity").alias("suma"))

category_df = category_data_frame.alias("category2").join(filterresult_df.alias("result"),col("category2.id")==col("result.id"),"left")\
    .fillna({"suma":0}).orderBy(desc("suma"), asc("nameKat")).collect()


with open('category_database.txt', 'w') as f:
    for item in category_df:
        name = item['nameKat']
        suma = item['suma']
        f.write(f'{name}\n')


spark.stop()

