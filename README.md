### IOT Demo

#### Spark Streaming + Kafka + Kudu

##### Versions
CDH 5.8
Kafka 2.0.2-1.2.0.2.p0.5
Kudu 0.10.0-1.kudu0.10.0.p0.7 
Impala_Kudu 2.6.0-1.cdh5.8.0.p0.17

spark-submit:
```
spark-submit --master yarn --jars kudu-spark_2.10-0.10.0.jar --packages org.apache.spark:spark-streaming-kafka_2.10:1.6.0 iot_demo.py
```

