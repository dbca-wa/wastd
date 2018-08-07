FROM python:3.7.0-stretch
MAINTAINER Florian.Mayer@dbca.wa.gov.au

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --yes \
  -o Acquire::Retries=10 --no-install-recommends \
    texlive-full \
    fontconfig \
    libxrender1 \
    lmodern \
    tar \
    xz-utils \
    make \
    wget \
    git \
    libmagic-dev \
    gcc \
    binutils \
    libproj-dev \
    gdal-bin \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    python-dev \
    python-enchant \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY config ./config
COPY conservation ./conservation
COPY occurrence ./occurrence
COPY logs ./logs
COPY shared ./shared
COPY taxonomy ./taxonomy
COPY utility ./utility
COPY wastd ./wastd
COPY favicon.ico gunicorn.ini manage.py requirements/base.txt ./

RUN pip install --no-cache-dir -r requirements/base.txt \
  && python manage.py collectstatic --noinput

EXPOSE 8220
CMD ["gunicorn", "config.wsgi", "--config", "gunicorn.ini"]