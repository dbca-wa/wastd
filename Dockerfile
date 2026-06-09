# syntax=docker/dockerfile:1
# Prepare the base environment.
FROM python:3.13-slim AS builder_base

# This approximately follows this guide: https://hynek.me/articles/docker-uv/
# Which creates a standalone environment with the dependencies.
# - Silence uv complaining about not being able to use hard links,
# - tell uv to byte-compile packages for faster application startups,
# - prevent uv from accidentally downloading isolated Python builds,
# - pick a Python,
# - and finally declare `/app` as the target for `uv sync`.
ENV UV_LINK_MODE=copy \
  UV_COMPILE_BYTECODE=1 \
  UV_PYTHON_DOWNLOADS=never \
  UV_PROJECT_ENVIRONMENT=/app/.venv

COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /uvx /bin/

# Since there's no point in shipping lock files, we move them
# into a directory that is NOT copied into the runtime image.
# The trailing slash makes COPY create `/_lock/` automagically.
COPY pyproject.toml uv.lock /_lock/

# Synchronize dependencies.
# This layer is cached until uv.lock or pyproject.toml change.
RUN --mount=type=cache,target=/root/.cache \
  cd /_lock && \
  uv sync \
  --frozen \
  --no-group dev

##################################################################################

FROM python:3.13-slim
LABEL org.opencontainers.image.authors=asi@dbca.wa.gov.au
LABEL org.opencontainers.image.source=https://github.com/dbca-wa/wastd

# Install OS packages
RUN apt-get update -y \
  && apt-get upgrade -y \
  && apt-get install -y libmagic-dev gcc binutils gdal-bin proj-bin python3-dev libpq-dev gzip curl gnupg2

# NOTE: we're constrained to using the version(s) of Debian which the Microsoft ODBC driver supports.
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

# Create a non-root user.
RUN groupadd -r -g 1000 app \
  && useradd -r -u 1000 -d /app -g app -N app

COPY --from=builder_base --chown=app:app /app /app
# Make sure we use the virtualenv by default
ENV PATH="/app/.venv/bin:$PATH"
# Run Python unbuffered
ENV PYTHONUNBUFFERED=1

# Install the project.
WORKDIR /app
COPY gunicorn.py manage.py pyproject.toml ./
COPY observations ./observations
COPY users ./users
COPY wastd ./wastd
COPY wamtram2 ./wamtram2
COPY marine_mammal_incidents ./marine_mammal_incidents
RUN python manage.py collectstatic --noinput
USER app
EXPOSE 8080
CMD ["gunicorn", "wastd.wsgi", "--config", "gunicorn.py"]
