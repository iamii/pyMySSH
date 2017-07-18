[client]
port={{client.port}}
socket={{client.socket}}
[mysqld]
datadir={{mysqld.datadir}}
user= {{mysqld.user}}
log-error={{mysqld.log_error}}
ndbcluster
ndb-connectstring={{mysqld.master}}
[mysql_cluster]
ndb-connectstring={{mysql_cluster.master}}
