rm ./shop-src/dbdata/dump.sql
docker exec mariadb mysqldump --password=admin prestashop_database > ./shop-src/dbdata/dump.sql
