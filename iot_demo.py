import json
from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.storagelevel import StorageLevel
from pyspark.sql import SQLContext

#conf = (SparkConf().setMaster("yarn-cluster").setAppName("Particle Stream to Kudu"))
conf = (SparkConf().setMaster("yarn-client").setAppName("Particle Stream to Kudu"))
sc = SparkContext(conf = conf)
ssc = StreamingContext(sc,5)

#Set up for Kafka and Kudu
brokers = "ip-10-0-0-243.ec2.internal:9092"
kudu_table = "particle_test"
kudu_master = "ip-10-0-0-243.ec2.internal:7051"
topic = "particle"

#Lazy SqlContext evaluation
def getSqlContextInstance(sparkContext):
    if ('sqlContextSingletonInstance' not in globals()):
        globals()['sqlContextSingletonInstance'] = SQLContext(sc)
    return globals()['sqlContextSingletonInstance']

#Insert data into Kudu
def insert_into_kudu(time,rdd):
    sqc = getSqlContextInstance(rdd.context)
    kudu_df = sqc.jsonRDD(rdd)
    kudu_df.show()
    kudu_df.write.format('org.apache.kudu.spark.kudu').option('kudu.master',kudu_master).option('kudu.table',kudu_table).mode("append").save()

#Create a Kafka DStream by reading from our topic
kafkaStream = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})

#Get rid of the key, which is null anyways
json_kafka_stream = kafkaStream.map(lambda x: x[1])

#For each RDD in the DStream, insert it into Kudu table
json_kafka_stream.foreachRDD(insert_into_kudu)

ssc.start()
ssc.awaitTermination()



