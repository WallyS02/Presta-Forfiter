# Presta-Forfiter
## Internet shop project

## CONTENTS

- [USED SOFTWARE](#technologies)
- [RUN SCRAPER](#run-scraper)
- [RUN SHOP](#run-shop)
- [RUN TESTS](#run-tests)
- [RUN DB DUMP](#run-db-dump)
- [RUN API](#run-api)
- [AUTHORS](#authors)

## SOFTWARE

1. Prestashop v1.7.8
2. MariaDB
3. Docker
4. Python
5. Scrapy
6. Selenium

## RUN SCRAPER
Run commands in order in directory of ForfitScraper:

```
scrapy crawl category -O ../scrapped_data/categories.json
```
```
scrapy crawl alco -O ../scrapped_data/products.json
```
```
python download_photos.py
```

Commands are also in run.ps1 Windows Powershell file.

## RUN SHOP
To ensure all components running smoothly, first run chmod in the main directory.
```
sudo chmod -R 777 shop-src
```

Next, initialize the Docker container. Navigate to shop-config directory and run:
```
docker-compose build
```
```
docker compose up
```

After booting the container, you can access the shop website at:
```
https://localhost/
```

To make changes to the website, navigate to the admin panel and log in using the correct credentials.
```
https://localhost/admin4577/
```

## RUN TESTS
Run command in directory of tests:
```
python main.py
```

## RUN DB DUMP
   
Run commands in order in directory of Presta-Forfiter:
```
./export_scripts/save_db.sh
```
```
./export_scripts/load_db.sh
```

## RUN API
Run command in directory of PrestaAPI:
```
python main.py
```

## AUTHORS

- Szymon Lider
- Sebastian Kutny
