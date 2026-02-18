# Astronomer Dockerfile
# Extends Astronomer's base image with custom Python packages

FROM quay.io/astronomer/astro-runtime:9.8.0

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ETL modules into /opt/airflow
# These will be at the same level as /opt/airflow/dags/
COPY airflow/*.py /opt/airflow/
