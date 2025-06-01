FROM apache/airflow:2.8.1-python3.10

USER root
RUN apt-get update && apt-get install -y openjdk-11-jdk curl wget

# Установка Spark
ENV SPARK_VERSION=3.3.2
ENV HADOOP_VERSION=3
RUN curl -L https://downloads.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz | \
    tar -xz -C /opt && \
    ln -s /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark

ENV SPARK_HOME=/opt/spark
ENV PATH="${SPARK_HOME}/bin:$PATH"

# Установка ClickHouse драйверов
RUN pip install clickhouse-driver==0.2.3

USER airflow
COPY requirements.txt .
RUN pip install -r requirements.txt
