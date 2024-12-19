#!/bin/bash
set -e

apt-get update
apt-get install -y unzip curl libicu70

curl -sSL -o sqlpackage.zip https://aka.ms/sqlpackage-linux
mkdir -p /opt/sqlpackage
unzip -q sqlpackage.zip -d /opt/sqlpackage
chmod +x /opt/sqlpackage/sqlpackage

/opt/sqlpackage/sqlpackage \
    /Action:Import \
    /SourceFile:/backup/turtle_tagging_prod-202412190929.bacpac \
    /TargetServerName:sqlserver \
    /TargetDatabaseName:turtle_tagging_uat \
    /TargetUser:sa \
    /TargetPassword:"$SA_PASSWORD" \
    /TargetTrustServerCertificate:true