mv ./shop-src/db_dump/dump.sql ./shop-src/dbdata
docker exec mariadb mysql -uroot -padmin -e "create database prestashop"
docker exec -i mariadb bash -c "mysql --password=admin prestashop_database < /var/lib/mysql/dump.sql"