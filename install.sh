#Environment prep
ZK="$1:2181"

#Install pip
sudo wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py

#Install Python  dependencies
sudo pip install sseclient
sudo pip install kafka-python

#Kafka set up
kafka-topics --create --zookeeper  $1 --replication-factor 1 --partitions 1 --topic particle

