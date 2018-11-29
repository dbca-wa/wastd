FROM python:3.7.0-stretch
LABEL maintainer=Florian.Mayer@dbca.wa.gov.au
LABEL description="Python 3.7.0-stretch plus Latex, GDAL and LDAP."

RUN DEBIAN_FRONTEND=noninteractive apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install --yes \
  -o Acquire::Retries=10 --no-install-recommends \
    texlive lmodern libmagic-dev libproj-dev gdal-bin \
    python-dev libsasl2-dev libldap2-dev python-enchant \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \
  && wget https://github.com/jgm/pandoc/releases/download/2.3/pandoc-2.3-1-amd64.deb \
  && dpkg -i pandoc-2.3-1-amd64.deb \
  && rm pandoc-2.3-1-amd64.deb

WORKDIR /usr/src/app
COPY requirements/ ./requirements/
RUN pip install --no-cache-dir -r requirements/dev.txt
COPY . .
RUN python manage.py collectstatic --clear --noinput -l
CMD ["gunicorn", "config.wsgi", "--config", "config/gunicorn.ini"]
HEALTHCHECK --interval=1m --timeout=20s --start-period=10s --retries=3 \
  CMD ["wget", "-q", "-O", "-", "http://localhost:8220/healthcheck/"]