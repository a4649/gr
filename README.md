# Network Management (MERSTEL)

Project developed during the Network Management curricular unit of the Engineering of Computer Networks and Telematic Services from School of Engineering, University of Minho https://www.eng.uminho.pt/en/study/_layouts/15/UMinho.PortaisUOEI.UI/Pages/CatalogoCursoDetail.aspx?itemId=3929&catId=12

This projects aims to implement an SNMP Agent and Manager in Python using just ```sockets``` and ```sys``` libraries.


The SNMP Agent implements a MIB file (not following the RFC). 

Start the Agent:

```./agent.py MIB.txt```

Running the Manager:

```./manager_get.py <community> <ip-address-of-agent> <port> <oid>```

```./manager_set.py <community> <ip-address-of-agent> <port> <oid> <new-value>```
