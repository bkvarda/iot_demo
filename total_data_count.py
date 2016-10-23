import json, sys, ConfigParser
from operator import add
from pyspark import SparkContext
from pyspark import SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.storagelevel import StorageLevel
from pyspark.sql import SQLContext

conf = (SparkConf().setMaster("yarn-client").setAppName("Total Data Count"))
sc = SparkContext(conf = conf)
sqc = SQLContext(sc)

Config = ConfigParser.ConfigParser()
Config.read('particlespark.conf')
kudu_master = Config.get('Kudu','KuduMaster')
kudu_all_data_table = "particle_test"
kudu_counts_table = "particle_counts_total_data"

#Read from Kudu table particle_test
kudu_events_df = sqc.read.format('org.apache.kudu.spark.kudu').option('kudu.master',kudu_master).option('kudu.table',kudu_all_data_table).load()

#Grab only the data column, split it by white space and count up each unique key
kudu_events_count = kudu_events_df.map(lambda x: x.data).flatMap(lambda x: x.split(' ')).map(lambda x: (x, 1)).reduceByKey(add)

#Convert event counts to DataFrame from RDD
kudu_events_count_df = kudu_events_count.toDF(['data_word','count'])

kudu_events_count_df.show()

#Write the event word counts to Kudu particle_counts_total_data table
kudu_events_count_df.write.format('org.apache.kudu.spark.kudu').option('kudu.master',kudu_master).option('kudu.table',kudu_counts_table).mode("append").save()








