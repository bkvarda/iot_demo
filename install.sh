#Environment prep
ZK="$1:2181"
KUDU_MASTER="$2:7051"

#Install pip
sudo wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py

#Install Python  dependencies
sudo pip install sseclient
sudo pip install python-kafka

#Kafka set up
kafka-topics --create --zookeeper  $1 --replication-factor 1 --partitions 1 --topic particle

#Impala table set up
impala-shell -q "CREATE TABLE `particle_test` (
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
 'kudu.master_addresses' = $KUDU_MASTER,
 'kudu.key_columns' = 'coreid,published_at',
 'kudu.num_tablet_replicas' = '3'
);"

impala-shell -q "CREATE TABLE `particle_counts_last_20_data` (
`data_word` STRING,
`count` BIGINT
)
DISTRIBUTE BY HASH (data_word) INTO 16 BUCKETS
TBLPROPERTIES(
 'storage_handler' = 'com.cloudera.kudu.hive.KuduStorageHandler',
 'kudu.table_name' = 'particle_counts_last_20_data',
 'kudu.master_addresses' = $KUDU_MASTER,
 'kudu.key_columns' = 'data_word',
 'kudu.num_tablet_replicas' = '3'
);"

impala-shell -q "CREATE TABLE `particle_counts_last_20` (
`event_word` STRING,
`count` BIGINT
)
DISTRIBUTE BY HASH (event_word) INTO 16 BUCKETS
TBLPROPERTIES(
 'storage_handler' = 'com.cloudera.kudu.hive.KuduStorageHandler',
 'kudu.table_name' = 'particle_counts_last_20',
 'kudu.master_addresses' = $KUDU_MASTER,
 'kudu.key_columns' = 'event_word',
 'kudu.num_tablet_replicas' = '3'
);"

impala-shell -q "CREATE TABLE `particle_counts_total` (
`event_word` STRING,
`count` BIGINT
)
DISTRIBUTE BY HASH (event_word) INTO 16 BUCKETS
TBLPROPERTIES(
 'storage_handler' = 'com.cloudera.kudu.hive.KuduStorageHandler',
 'kudu.table_name' = 'particle_counts_total',
 'kudu.master_addresses' = $KUDU_MASTER,
 'kudu.key_columns' = 'event_word',
 'kudu.num_tablet_replicas' = '3'
);"

impala-shell -q "CREATE TABLE `particle_counts_total_data` (
`data_word` STRING,
`count` BIGINT
)
DISTRIBUTE BY HASH (data_word) INTO 16 BUCKETS
TBLPROPERTIES(
 'storage_handler' = 'com.cloudera.kudu.hive.KuduStorageHandler',
 'kudu.table_name' = 'particle_counts_total_data',
 'kudu.master_addresses' = $KUDU_MASTER,
 'kudu.key_columns' = 'data_word',
 'kudu.num_tablet_replicas' = '3'
);"
