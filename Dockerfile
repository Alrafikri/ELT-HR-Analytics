FROM apache/airflow:2.10.4

USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         postgresql-client \
         libpq-dev \
         gcc \
         python3-dev \     
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
USER airflow

COPY requirements.txt /
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt