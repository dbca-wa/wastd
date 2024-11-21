FROM mcr.microsoft.com/mssql/server:2022-latest

# Install sqlpackage
RUN apt-get update && apt-get install -y wget unzip \
    && wget -progress=bar:force -q -O sqlpackage.zip https://go.microsoft.com/fwlink/?linkid=2185670 \
    && unzip -qq sqlpackage.zip -d /opt/sqlpackage \
    && chmod +x /opt/sqlpackage/sqlpackage \
    && ln -s /opt/sqlpackage/sqlpackage /usr/local/bin/sqlpackage \
    && rm sqlpackage.zip

# Copy initialization script
COPY scripts/init-sqlserver.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init-sqlserver.sh