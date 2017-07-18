[NDB_MGMD DEFAULT]
Portnumber={{NDB_MGMD_DEFAULT.Portnumber}}
[NDB_MGMD]
NodeId={{NDB_MGMD.NodeId}}
HostName={{NDB_MGMD.HostName}}
DataDir={{NDB_MGMD.DataDir}}
Portnumber={{NDB_MGMD.Portnumber}}
[TCP DEFAULT]
SendBufferMemory=4M
ReceiveBufferMemory=4M
[NDBD DEFAULT]
NoOfReplicas={{ NDBD|length }}
DataMemory={{NDBD_DEFAULT.DataMemory}}
IndexMemory={{NDBD_DEFAULT.IndexMemory}}
{% for node in NDBD -%}
[NDBD]
NodeId={{node.NodeId}}
HostName={{node.HostName}}
DataDir={{node.DataDir}}
{% endfor -%}
[MYSQLD DEFAULT]
{% for node in MYSQLD -%}
[mysqld]
hostname={{node.hostname}}
{% endfor -%}
