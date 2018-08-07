FROM python:3.7.0-stretch
MAINTAINER Florian.Mayer@dbca.wa.gov.au

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --yes \
  -o Acquire::Retries=10 --no-install-recommends \
    gcc \
    binutils \
    python-dev \
    make \
    wget \
    tar \
    xz-utils \
    git \
    texlive-full \
    fontconfig \
    libxrender1 \
    lmodern \
    libmagic-dev \
    libproj-dev \
    gdal-bin \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    python-enchant \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
RUN mkdir -p data logs staticfiles
COPY config ./config
COPY conservation ./conservation
COPY occurrence ./occurrence
COPY shared ./shared
COPY taxonomy ./taxonomy
COPY utility ./utility
COPY wastd ./wastd
COPY requirements ./requirements
COPY config/gunicorn.ini manage.py ./

RUN pip install -U pip \
  && pip install --no-cache-dir -r requirements/base.txt
RUN python manage.py collectstatic --noinput

EXPOSE 8220
CMD ["gunicorn", "config.wsgi", "--config", "gunicorn.ini"]