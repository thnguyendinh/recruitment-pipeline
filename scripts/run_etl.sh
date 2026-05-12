#!/bin/bash
docker exec spark bash -c "
export JAVA_HOME=/opt/java/openjdk
export SPARK_HOME=/opt/spark
export PYSPARK_PYTHON=python3
cd /opt/spark && python3 /opt/spark/scripts/etl.py" >> /var/log/etl.log 2>&1
