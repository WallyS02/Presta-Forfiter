scrapy crawl category -O ../scrapped_data/categories.json
scrapy crawl alco -O ../scrapped_data/products.json
python download_photos.py
