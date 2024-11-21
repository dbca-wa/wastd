#!/bin/bash
set -e

# 等待SQL Server启动
/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -Q "SELECT 1" >/dev/null 2>&1
while [ $? -ne 0 ]; do
  echo "Waiting for SQL Server to start..."
  sleep 1
  /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -Q "SELECT 1" >/dev/null 2>&1
done

echo "SQL Server is up"

# 检查数据库是否已存在
DB_EXISTS=$(/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -Q "SELECT COUNT(*) FROM sys.databases WHERE name = '${DB_NAME}'" -h -1)

if [ $DB_EXISTS -eq 0 ]; then
    echo "Restoring database..."  
    /opt/mssql-tools/bin/sqlpackage \
        /Action:Import \
        /SourceFile:/var/opt/mssql/backup/turtle_tagging_uat.bacpac \
        /TargetServerName:localhost \
        /TargetDatabaseName:$DB_NAME \
        /TargetUser:sa \
        /TargetPassword:$MSSQL_SA_PASSWORD
    
    echo "Database restored"   
else
    echo "Database already exists, skipping restore"
fi