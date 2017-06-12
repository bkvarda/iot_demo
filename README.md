### IOT Demo 2

#### Spark Streaming + Kafka + Kudu
This is a demonstration showing how to use Spark/Spark Streaming to read from Kafka and insert data into Kudu - all in Python. The streaming data is coming from the Particle.io event stream, and requires an API key to consume. I believe this may be the first demonstration of reading from/writing to Kudu from Spark Streaming using Python.

##### Content Description
- particlespark.py: SSEClient reading from Particle.io event stream and sending to Kafka topic 
- iot_demo.py: Spark streaming application reading from Kafka topic and inserting into a Kudu table
- event_count.py: Spark streaming application reading from Kafka topic, counting unique words of last 20 seconds and upserting into a Kudu table every 20 seconds (shows update capabilities)
- data_count.py: Same as above but counting data instead of events
- event_count_total.py: Spark batch job that reads from the master event table (particle_test) and counts the total occurance of each word for all time and upserts (shows update capabilities)

##### Versions
- CDH 5.8
- Kafka 2.0.2-1.2.0.2.p0.5
- Kudu 0.10.0-1.kudu0.10.0.p0.7 
- Impala_Kudu 2.6.0-1.cdh5.8.0.p0.17

##### Python Dependencies
```
sudo pip install sseclient
sudo pip install kafka-python
```
##### Configuration 
Working on making this a bit easier. First, install the above Python dependencies and run the below commands using your specific parameters where necessary. particlespark.conf contains parameters that need to be filled out for all of the .py files (python producer and spark jobs) to run. You can define the Kudu Master location and Kafka Broker once so that it does not need to be defined in the individual files

##### Impala create table:
```
CREATE TABLE `particle_test` (
`coreid` STRING,
`published_at` STRING,
`data` STRING,
`event` STRING,
`ttl` BIGINT
)
DISTRIBUTE BY HASH (coreid) INTO 16 BUCKETS
TBLPROPERTIES(
 'storage_handler' = 'com.cloudera.kudu.hive.KuduStorageHandler',
 'kudu.table_name' = 'particle_test',
 'kudu.master_addresses' = 'ip-10-0-0-224.ec2.internal:7051',
 'kudu.key_columns' = 'coreid,published_at',
 'kudu.num_tablet_replicas' = '3'
);
```
```
CREATE TABLE `particle_counts_last_20_data` (
`data_word` STRING,
`count` BIGINT
)
DISTRIBUTE BY HASH (data_word) INTO 16 BUCKETS
TBLPROPERTIES(
 'storage_handler' = 'com.cloudera.kudu.hive.KuduStorageHandler',
 'kudu.table_name' = 'particle_counts_last_20_data',
 'kudu.master_addresses' = 'ip-10-0-0-224.ec2.internal:7051',
 'kudu.key_columns' = 'data_word',
 'kudu.num_tablet_replicas' = '3'
);
```
```
CREATE TABLE `particle_counts_last_20` (
`event_word` STRING,
`count` BIGINT
)
DISTRIBUTE BY HASH (event_word) INTO 16 BUCKETS
TBLPROPERTIES(
 'storage_handler' = 'com.cloudera.kudu.hive.KuduStorageHandler',
 'kudu.table_name' = 'particle_counts_last_20',
 'kudu.master_addresses' = 'ip-10-0-0-224.ec2.internal:7051',
 'kudu.key_columns' = 'event_word',
 'kudu.num_tablet_replicas' = '3'
);
```
```
CREATE TABLE `particle_counts_total` (
`event_word` STRING,
`count` BIGINT
)
DISTRIBUTE BY HASH (event_word) INTO 16 BUCKETS
TBLPROPERTIES(
 'storage_handler' = 'com.cloudera.kudu.hive.KuduStorageHandler',
 'kudu.table_name' = 'particle_counts_total',
 'kudu.master_addresses' = 'ip-10-0-0-224.ec2.internal:7051',
 'kudu.key_columns' = 'event_word',
 'kudu.num_tablet_replicas' = '3'
);
```
```
CREATE TABLE `particle_counts_total_data` (
`data_word` STRING,
`count` BIGINT
)
DISTRIBUTE BY HASH (data_word) INTO 16 BUCKETS
TBLPROPERTIES(
 'storage_handler' = 'com.cloudera.kudu.hive.KuduStorageHandler',
 'kudu.table_name' = 'particle_counts_total_data',
 'kudu.master_addresses' = 'ip-10-0-0-224.ec2.internal:7051',
 'kudu.key_columns' = 'data_word',
 'kudu.num_tablet_replicas' = '3'
);
```

Kafka create topic:
```
kafka-topics --create --zookeeper  ip-10-0-0-224.ec2.internal:2181 --replication-factor 1 --partitions 1 --topic particle
```

spark-submit:
```
spark-submit --master yarn --jars kudu-spark_2.10-0.10.0.jar --packages org.apache.spark:spark-streaming-kafka_2.10:1.6.0 iot_demo.py
spark-submit --master yarn --jars kudu-spark_2.10-0.10.0.jar --packages org.apache.spark:spark-streaming-kafka_2.10:1.6.0 event_count.py
spark-submit --master yarn --jars kudu-spark_2.10-0.10.0.jar --packages org.apache.spark:spark-streaming-kafka_2.10:1.6.0 data_count.py
spark-submit --master yarn --jars kudu-spark_2.10-0.10.0.jar --packages org.apache.spark:spark-streaming-kafka_2.10:1.6.0 total_event_count.py
```
python producer:
```
python particlespark.py
```
