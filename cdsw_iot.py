#Set up packages needed in workbench
!pip install kafka-python --quiet
!pip install ConfigParser --quiet
!pip install thrift==0.9.3
!conda install -y ibis-framework -c conda-forge
!pip install thrift_sasl
!pip install requests-kerberos




import ConfigParser,json, os


#Set up configuration
Config = ConfigParser.ConfigParser()
Config.read('particlespark.conf')
kafka_broker = Config.get('Kafka','KafkaBrokers')
kudu_master = Config.get('Kudu','KuduMaster')
zookeeper = Config.get('Zookeeper','Zookeeper')
principal = Config.get('Kerberos','Principal')
keytab = Config.get('Kerberos','Keytab')
impala_host = Config.get('Impala','Daemon').split(':')[0]
impala_port = Config.get('Impala','Daemon').split(':')[1]


#Creating tables


import ibis

con = ibis.impala.connect(host=impala_host, port=impala_port, 
                          database='default',auth_mechanism='GSSAPI', 
                          use_ssl=False)
