FROM apache/airflow:2.6.3-python3.10

USER root
RUN apt-get update && apt-get install -y libpq-dev gcc

RUN pip install --upgrade pip
RUN pip install pymongo psycopg2-binary pyspark pyarrow snowflake-connector-python snowflake-sqlalchemy

COPY dags /opt/airflow/dags
COPY plugins /opt/airflow/plugins

USER airflow
ENTRYPOINT ["/entrypoint.sh"]
CMD ["webserver"]