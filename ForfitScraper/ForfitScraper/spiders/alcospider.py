import scrapy
from bs4 import BeautifulSoup
from ..utils import load_links


def inner_text(selector):
    html = selector.get()
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text().strip()


class AlcoSpider(scrapy.Spider):
    name = 'alco'
    start_urls = load_links('categories.json')

    def parse(self, response):
        for product in response.css('div.product-item-info.type1'):
            photo = product.css('div.product.photo.product-item-photo')
            photo_a = photo.css('a')
            photo_link = photo_a.css('img::attr(data-src)').get()
            details = product.css('div.product.details.product-item-details')
            strong_link = details.css('strong.product.name.product-item-name')
            summary = details.css('div.product-reviews-summary.short')
            rating_summary = summary.css('div.rating-summary')
            rating_result = rating_summary.css('div.rating-result')
            rating = rating_result.css('span')
            final_price = details.css('div.price-box.price-final_price')
            category_title = response.css('div.category-title')
            link = strong_link.css('a.product-item-link').attrib['href']
            yield scrapy.Request(
                url=link,
                callback=self.parse_product_page,
                meta={
                    'photo_link': photo_link,
                    'name': strong_link.css('a.product-item-link::text').get(),
                    'link': link,
                    'rating': rating.css('span::text').get(),
                    'price': final_price.css('span.price::text').get(),
                    'category': category_title.css('h1::text').get(),
                }
            )
        next_page = response.css('a.action.next').attrib['href']
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_product_page(self, response):
        for product in response.css('div.column.main'):
            main_info = product.css('div.product-info-main')
            title_wrapper = main_info.css('div.page-title-wrapper.product')
            title = title_wrapper.css('h1.page-title')
            info_price = main_info.css('div.product-info-price')
            info_stock_sku = info_price.css('div.product-info-stock-sku')
            attribute_sku = info_stock_sku.css('div.product.attribute.sku')
            media_info = product.css('div.product.media')
            gallery_placeholder = media_info.css('div.gallery-placeholder._block-content-loading')
            image_link = gallery_placeholder.css('a.product-image-link')
            photo_link = image_link.css('img::attr(src)').get()
            description = product.css('div.product.attribute.description')
            description_value = inner_text(description.css('div.value'))
            additional_attributes = product.css('div.additional-attributes-wrapper.table-wrapper')
            table_attributes = additional_attributes.css('table.data.table.additional-attributes')
            tbody = table_attributes.css('tbody')
            trs = dict()
            for tr in tbody.css('tr'):
                info = tr.css('th::text').get().lower()
                if info != 'identyfikator':
                    trs[info] = tr.css('td::text').get()

            yield {
                'photo': response.meta['photo_link'],
                'link': response.meta['link'],
                'rating': response.meta['rating'],
                'price': response.meta['price'],
                'category': response.meta['category'],
                'big-photo': photo_link,
                'name': title.css('span.base::text').get(),
                'sku': attribute_sku.css('div.value::text').get(),
                'description': description_value,
                'additional_information': trs,
            }
