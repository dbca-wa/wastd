FROM python:3.7.0-stretch
LABEL maintainer=Florian.Mayer@dbca.wa.gov.au
LABEL version="0.0.2"
LABEL description="Python 3.7.0-stretch plus Latex, GDAL and LDAP binaries."

# Already installed: binutils fontconfig gcc git lixrender1 make libssl-dev tar wget xz-utils
# Installing extras: Latex, GDAL, LDAP/auth
RUN DEBIAN_FRONTEND=noninteractive apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --yes \
  -o Acquire::Retries=10 --no-install-recommends \
    texlive-full lmodern libmagic-dev \
    libproj-dev gdal-bin \
    python-dev libsasl2-dev libldap2-dev python-enchant \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY config ./config
COPY conservation ./conservation
COPY occurrence ./occurrence
COPY shared ./shared
COPY taxonomy ./taxonomy
COPY utility ./utility
COPY wastd ./wastd
COPY requirements ./requirements
COPY manage.py ./

RUN pip install --no-cache-dir -r requirements/base.txt
RUN python manage.py collectstatic --noinput

HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 \
  CMD ["wget", "-q", "-O", "-", "http://localhost:8220/"]
EXPOSE 8220
CMD ["gunicorn", "config.wsgi", "--config", "config/gunicorn.ini"]