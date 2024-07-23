# syntax=docker/dockerfile:1
# Prepare the base environment.
FROM python:3.11.8-slim as builder_base_wastd
# NOTE: we're constrained to using the version(s) of Debian which the Microsoft ODBC driver supports.
MAINTAINER asi@dbca.wa.gov.au
LABEL org.opencontainers.image.source https://github.com/dbca-wa/wastd

RUN apt-get update -y \
  && apt-get upgrade -y \
  && apt-get install -y libmagic-dev gcc binutils gdal-bin proj-bin python3-dev libpq-dev gzip curl gnupg2

# Install the Microsoft ODBC driver for SQL Server. References:
# - https://learn.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server
# - https://learn.microsoft.com/en-us/answers/questions/1328834/debian-12-public-key-is-not-available
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
  && curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list \
  && apt-get update -y \
  && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
  # Change the OpenSSL config to allow old TLS versions, because our database host is outdated.
  # Do this by removing the last n lines of /etc/ssl/openssl.cnf, containing the [ssl_sect] and [system_default_sect] config sections.
  # Reference: https://askubuntu.com/questions/1284658/how-to-fix-microsoft-odbc-driver-17-for-sql-server-ssl-provider-ssl-choose-cli
  && head -n -7 /etc/ssl/openssl.cnf > openssl.tmp && mv openssl.tmp /etc/ssl/openssl.cnf \
  && rm -rf /var/lib/apt/lists

# Install Python libs using Poetry.
FROM builder_base_wastd as python_libs_wastd
WORKDIR /app
ENV POETRY_VERSION=1.7.1
RUN pip install poetry=="${POETRY_VERSION}"
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --only main

# Create a non-root user.
ARG UID=10001
ARG GID=10001
RUN groupadd -g "${GID}" appuser \
  && useradd --no-create-home --no-log-init --uid "${UID}" --gid "${GID}" appuser

# Install the project.
FROM python_libs_wastd
COPY gunicorn.py manage.py ./
COPY observations ./observations
COPY users ./users
COPY wastd ./wastd
COPY wamtram2 ./wamtram2
COPY marine_mammal_incidents ./marine_mammal_incidents
RUN python manage.py collectstatic --noinput

USER ${UID}
EXPOSE 8080
CMD ["gunicorn", "wastd.wsgi", "--config", "gunicorn.py"]