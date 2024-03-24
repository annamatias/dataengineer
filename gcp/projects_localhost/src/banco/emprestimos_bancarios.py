from pyspark.sql import SparkSession

def sparkSession():
    spark = SparkSession.builder\
                .master('local[*]')\
                .appName("Emprestimos Bancários")\
                .getOrCreate()
    return spark


def readCsv(spark, path):
    return spark.read.format("csv").option("header", "true").option("sep", ";").load(path)

path = 'dataengineer-google-cloud/projects_localhost/data_source/emprestimo.csv'
spark = sparkSession()
df = readCsv(spark, path)
count= df.count()
df.show(10, False)

spark.stop