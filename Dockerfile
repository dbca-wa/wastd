
# syntax=docker/dockerfile:1
# Prepare the base environment.
FROM python:3.11.8-slim as builder_base_wastd

# NOTE: we're constrained to using the version(s) of Debian which the Microsoft ODBC driver supports.
MAINTAINER asi@dbca.wa.gov.au
LABEL org.opencontainers.image.source https://github.com/dbca-wa/wastd

RUN apt-get update -y \
  && apt-get upgrade -y \
  && apt-get install -y libmagic-dev gcc binutils gdal-bin proj-bin python3-dev libpq-dev gzip curl gnupg2 unixodbc-dev

# Install the Microsoft ODBC driver for SQL Server. References:
# - https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
  && curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
  && apt-get update -y \
  && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
#     && curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
#     && apt-get update \
#     && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
#         unixodbc \
#         unixodbc-dev \
#         msodbcsql18 \
#     && rm -rf /var/lib/apt/lists/*

# Check ODBC driver
RUN odbcinst -j

# Configure ODBC driver
# RUN echo "[ODBC Driver 18 for SQL Server]\n\
# Description=Microsoft ODBC Driver 18 for SQL Server\n\
# Driver=/opt/microsoft/msodbcsql18/lib64/libmsodbcsql-18.3.so.3.1\n\
# UsageCount=1" > /etc/odbcinst.ini

RUN echo "[ODBC Driver 18 for SQL Server]\n\
Description=Microsoft ODBC Driver 18 for SQL Server\n\
Driver=/opt/microsoft/msodbcsql18/lib64/libmsodbcsql-18.4.so.1.1\n\
UsageCount=1" > /etc/odbcinst.ini

# Change the OpenSSL config to allow old TLS versions, because our database host is outdated.
# Do this by removing the last n lines of /etc/ssl/openssl.cnf, containing the [ssl_sect] and [system_default_sect] config sections.
# Reference: https://askubuntu.com/questions/1284658/how-to-fix-microsoft-odbc-driver-17-for-sql-server-ssl-provider-ssl-choose-cli
RUN head -n -7 /etc/ssl/openssl.cnf > openssl.tmp && mv openssl.tmp /etc/ssl/openssl.cnf \
  && rm -rf /var/lib/apt/lists

# Install Python libs using Poetry.
FROM builder_base_wastd as python_libs_wastd
WORKDIR /app
ENV POETRY_VERSION=1.7.1
RUN pip install poetry=="${POETRY_VERSION}"
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --only main

# Ensure compatible versions of numpy and pandas
RUN pip install --upgrade numpy pandas

# Create a non-root user.
ARG UID=10001
ARG GID=10001
RUN groupadd -g "${GID}" appuser \
  && useradd --no-create-home --no-log-init --uid "${UID}" --gid "${GID}" appuser

# Install the project.
FROM python_libs_wastd

# Install psql tool and dos2unix
RUN apt-get update -y && apt-get install -y postgresql-client dos2unix

COPY entrypoint.sh /app/entrypoint.sh
COPY wait-for-db.sh /app/wait-for-db.sh
COPY createsuperuser.sh /app/createsuperuser.sh
COPY createentereruser.sh /app/createentereruser.sh
COPY gunicorn.py manage.py ./
COPY observations ./observations
COPY users ./users
COPY wastd ./wastd
COPY wamtram2 ./wamtram2
COPY marine_mammal_incidents ./marine_mammal_incidents

# Convert line endings from CRLF to LF
# RUN dos2unix /app/entrypoint.sh /app/wait-for-db.sh /app/createsuperuser.sh
RUN chmod +x /app/entrypoint.sh /app/wait-for-db.sh /app/createsuperuser.sh /app/createentereruser.sh

USER ${UID}
EXPOSE 8080

# Set environment variables for development
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=wastd.settings

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
