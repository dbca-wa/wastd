#!/bin/bash
set -e

apt-get update
apt-get install -y unzip curl libicu70

curl -sSL -o sqlpackage.zip https://aka.ms/sqlpackage-linux
mkdir -p /opt/sqlpackage
unzip -q -o sqlpackage.zip -d /opt/sqlpackage
chmod +x /opt/sqlpackage/sqlpackage

/opt/sqlpackage/sqlpackage \
    /Action:Import \
    /SourceFile:/backup/turtle_tagging_prod-20250122.bacpac \
    /TargetServerName:sqlserver \
    /TargetDatabaseName:turtle_tagging_prod \
    /TargetUser:sa \
    /TargetPassword:"$SA_PASSWORD" \
    /TargetTrustServerCertificate:true