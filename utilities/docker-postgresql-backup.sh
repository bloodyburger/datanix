#!/bin/bash

# Define the list of default databases that you want to exclude
EXCLUDE_DB=("postgres" "template0" "template1")
BACKUP_PATH="<PATH>"

# Get the list of databases
#DB_LIST=$(docker exec -t charkoal_postgres psql -U postgres -c "\l" | awk '{print $1}' | grep -vE '(^-|^List|^Name|template0|template1|postgres|^\()')
#docker exec -t charkoal_postgres bash -c "psql -U postgres -c '\l' | awk '{print \$1}' | grep -vE '(^-|^List|^Name|template0|template1|postgres|^\()'"
DB_LIST=$(docker exec -t charkoal_postgres bash -c "psql -U postgres -c '\l' | awk '{print \$1}' | grep -vE '(^-|^List|^Name|template0|template1|postgres|^\()' | grep -vE '(^\\||^$)'")
echo $DB_LIST
# Loop through each database and dump it
for DB in $DB_LIST; do
  DB_CLEAN=$(echo $DB | tr -d '\r')
  if [[ ! " ${EXCLUDE_DB[@]} " =~ " ${DB} " ]]; then
    echo "Dumping database: $DB"
    docker exec -t charkoal_postgres pg_dump -c -C -U postgres $DB_CLEAN | gzip > ${BACKUP_PATH}/${DB_CLEAN}_postgresql_dump_$(date +"%Y-%m-%d_%H_%M_%S").gz
  fi
done
