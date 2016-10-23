import json, sys, ConfigParser
from operator import add
from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.storagelevel import StorageLevel
from pyspark.sql import SQLContext

conf = (SparkConf().setMaster("yarn-client").setAppName("Count Data Word 20 Sec"))
sc = SparkContext(conf = conf)
ssc = StreamingContext(sc,20)

Config = ConfigParser.ConfigParser()
Config.read('particlespark.conf')
kafka_broker = Config.get('Kafka','KafkaBrokers')
kudu_master = Config.get('Kudu','KuduMaster')
topic = "particle"
kudu_table = "particle_counts_last_20_data"

def getSqlContextInstance(sparkContext):
    if ('sqlContextSingletonInstance' not in globals()):
        globals()['sqlContextSingletonInstance'] = SQLContext(sc)
    return globals()['sqlContextSingletonInstance']


def insert_into_kudu(time,rdd):
    sqc = getSqlContextInstance(rdd.context)
    kudu_df = rdd.toDF(['data_word','count'])
    kudu_df.show()
    kudu_df.write.format('org.apache.kudu.spark.kudu').option('kudu.master',kudu_master).option('kudu.table',kudu_table).mode("append").save()

def get_data(payload):
    if 'data' not in payload: 
        print str(payload)
    else:
        return payload["data"]


kafkaStream = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": kafka_broker})

events_kafka_stream = kafkaStream.map(lambda x: get_data(json.loads(x[1])))

counts = events_kafka_stream.flatMap(lambda x: x.split(' ')).map(lambda x: (x,1)).reduceByKey(add)

counts.foreachRDD(insert_into_kudu)

ssc.start()
ssc.awaitTermination()



