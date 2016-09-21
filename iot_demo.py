import json
from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.storagelevel import StorageLevel
from pyspark.sql import SQLContext

conf = (SparkConf().setMaster("yarn-client").setAppName("Test App"))
sc = SparkContext(conf = conf)
ssc = StreamingContext(sc,10)
#sqc = SQLContext(sc)

brokers = "quickstart.cloudera:9092"
kudu_table = "particle_test"
kudu_master = "quickstart.cloudera:7051"
topic = "particle"

def getSqlContextInstance(sparkContext):
    if ('sqlContextSingletonInstance' not in globals()):
        globals()['sqlContextSingletonInstance'] = SQLContext(sc)
    return globals()['sqlContextSingletonInstance']


def insert_into_kudu(time,rdd):
    sqc = getSqlContextInstance(rdd.context)
    print(rdd.take(5))
    kudu_df = sqc.jsonRDD(rdd)
    kudu_df.show()
    kudu_df.write.format('org.apache.kudu.spark.kudu').option('kudu.master',kudu_master).option('kudu.table',kudu_table).mode("append").save()

def get_uid(payload):
    if 'uid' not in payload: 
        print str(payload)
        return "not_found"
    else:
        return payload["uid"]


kafkaStream = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})


json_kafka_stream = kafkaStream.map(lambda x: x[1])

json_kafka_stream.foreachRDD(insert_into_kudu)

ssc.start()
ssc.awaitTermination()



