#!/bin/bash

set -e

echo "Starting docker containers"
docker-compose up -d

echo "Waiting for MariaDB to be ready..."
until docker exec mcs_container mariadb -e "SELECT 1;" >/dev/null 2>&1; do
  sleep 2
done

echo "MariaDB is up"

echo "Provisioning ColumnStore..."
docker exec -it mcs_container provision 

docker exec -i mcs_container mariadb <<EOF
GRANT ALL PRIVILEGES ON *.* TO 'student'@'%' IDENTIFIED BY 'Student@123!';
GRANT ALL PRIVILEGES ON *.* TO 'student'@'localhost' IDENTIFIED BY 'Student@123!';
FLUSH PRIVILEGES;
CREATE OR REPLACE DATABASE ashrae_db;
EOF

echo "Setup completed successfully."
