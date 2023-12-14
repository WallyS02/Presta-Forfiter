import io
import json
import os
from concurrent.futures import ThreadPoolExecutor
from random import randint
from threading import Semaphore

from prestapyt import PrestaShopWebServiceDict

WEBSERVICE_KEY = 'MWBTC14V59ZACAFTT8AW2DK3L5QP4VVY'
API_URL = 'http://localhost:8080/api'
SCRIPT_DIR = os.path.dirname(__file__).split("API")[0] + 'scrapped_data'

prestashop = PrestaShopWebServiceDict(API_URL, WEBSERVICE_KEY)

category_schema = prestashop.get("categories", options={
    "schema": "blank"
})

product_schema = prestashop.get("products", options={
    "schema": "blank"
})

del product_schema["product"]["position_in_category"]
del product_schema["product"]["associations"]["combinations"]

feature_schema = prestashop.get("product_features", options={
    "schema": "blank"
})

feature_option_schema = prestashop.get("product_feature_values", options={
    "schema": "blank"
})

semaphore = Semaphore(1)

bad_characters = ['*', '/']


def forbidden_characters(variable):
    characters = ['', '\n', '*']
    if variable in characters:
        return False
    else:
        return True


def prepare_name(name):
    split_name = name.split(' ')
    filtered_name = filter(forbidden_characters, split_name)
    prepared_name = str()
    for word in filtered_name:
        prepared_name += word + '-'
    for bad_character in bad_characters:
        prepared_name = prepared_name.replace(bad_character, '')
    return prepared_name.rstrip(prepared_name[-1])


def add_category(name, parent_id):
    category = prestashop.get("categories", options={
        "filter[name]": name
    })
    if not category["categories"]:
        category_schema["category"]["name"]["language"]["value"] = name
        category_schema["category"]["id_parent"] = parent_id
        category_schema["category"]["active"] = 1
        category_schema["category"]["description"]["language"]["value"] = f"Kategoria {name}"
        return prestashop.add("categories", category_schema)["prestashop"]["category"]["id"]
    else:
        return category["categories"]["category"]["attrs"]["id"]


def add_categories(clean):
    if clean:
        ids = []
        for category in prestashop.get("categories")["categories"]["category"]:
            if int(category["attrs"]["id"]) not in [1, 2]:
                ids.append(int(category["attrs"]["id"]))
        if ids:
            prestashop.delete("categories", resource_ids=ids)

    with open(f"{SCRIPT_DIR}\\categories.json") as file:
        categories = json.loads(file.read())

    index = 2

    for category in categories:
        if category["attrs"]["parent"]:
            add_category(category["attrs"]["name"],
                         prestashop.get("categories", options={"filter[name]": category["attrs"]["parent"]})["attrs"][
                             "id"])
        else:
            add_category(category["attrs"]["name"], index)


def add_features(attributes):
    feat_ids_values = dict()
    for name, value in attributes.items():
        feature = prestashop.get("product_features", options={
            "filter[name]": name
        })
        if feature["product_features"]:
            feature_id = feature["product_features"]["product_feature"]["attrs"]["id"]
        else:
            feature_schema["product_feature"]["name"]["language"]["value"] = name
            feature_schema["product_feature"]["position"] = 1
            feature_id = prestashop.add("product_features", feature_schema)["prestashop"]["product_feature"]["id"]

        feature_option_schema["product_feature_value"]["id_feature"] = feature_id
        feature_option_schema["product_feature_value"]["value"]["language"]["value"] = value
        feature_option_schema["product_feature_value"]["custom"] = 1
        value_id = prestashop.add("product_feature_values", feature_option_schema)["prestashop"]["product_feature_value"]["id"]
        feat_ids_values[feature_id] = value_id
    return feat_ids_values


def add_images_to_product(product_name, product_id):
    image = os.listdir(f"{SCRIPT_DIR}\\images\\" + prepare_name(product_name) + '.jpg')[0]
    fd = io.open(f"{SCRIPT_DIR}\\images\\" + prepare_name(product_name) + '.jpg', "rb")
    content = fd.read()
    fd.close()
    prestashop.add(f"images/products/{product_id}", files=[
        ("image", image, content)
    ])
    big_image = os.listdir(f"{SCRIPT_DIR}\\images\\" + prepare_name(product_name) + '-BIG.jpg')[0]
    fd = io.open(f"{SCRIPT_DIR}\\images\\" + prepare_name(product_name) + '-BIG.jpg', "rb")
    content = fd.read()
    fd.close()
    prestashop.add(f"images/products/{product_id}", files=[
        ("image", big_image, content)
    ])


def change_quantity(product_id):
    schema_id = prestashop.search("stock_availables", options={
        "filter[id_product]": product_id
    })[0]
    stock_available_schema = prestashop.get(
        "stock_availables", resource_id=schema_id)
    stock_available_schema["stock_available"]["quantity"] = randint(0, 10)
    stock_available_schema["stock_available"]["depends_on_stock"] = 0
    prestashop.edit("stock_availables", stock_available_schema)


def add_product(product):
    semaphore.acquire()
    feature_ids = add_features(product["additional_information"])
    semaphore.release()
    category_id = prestashop.get("categories", options={"filter[name]": product["category"]})["categories"]["category"]["attrs"]["id"]
    product_schema["product"]["name"]["language"]["value"] = product["name"]
    product_schema["product"]["id_category_default"] = category_id
    product_schema["product"]["id_shop_default"] = 1
    product_schema["product"]["reference"] = product["id"]
    product_schema["product"]["id_tax_rules_group"] = 1
    product_schema["product"]["price"] = product["price"]
    product_schema["product"]["active"] = 1
    product_schema["product"]["state"] = 1
    product_schema["product"]["available_for_order"] = 1
    product_schema["product"]["minimal_quantity"] = 1
    product_schema["product"]["show_price"] = 1
    product_schema["product"]["meta_title"]["language"]["value"] = product["name"]
    product_features = []
    for feature_id, value_id in feature_ids.items():
        product_features.append({
            "id": feature_id,
            "id_feature_value": value_id
        })
    product_schema["product"]["associations"]["product_features"]["product_feature"] = product_features
    product_schema["product"]["associations"]["categories"] = {
        "category": [
            {"id": 2},
            {"id": category_id}
        ],
    }

    product_schema["product"]["weight"] = randint(1, 600) / 10
    product_schema["product"]["description"]["language"]["value"] = product['description']
    product_id = prestashop.add("products", product_schema)["prestashop"]["product"]["id"]
    change_quantity(product_id)
    add_images_to_product(product["name"], product_id)


def add_products(clean):
    if clean:
        products = prestashop.get("products")["products"]
        if products:
            products_data = products["product"]

            if isinstance(products_data, dict):
                products_data = [products_data]

            ids = [int(product["attrs"]["id"]) for product in products_data]
            if ids:
                prestashop.delete("products", resource_ids=ids)

        features = prestashop.get("product_features")["product_features"]
        if features:
            features_data = prestashop.get("product_features")["product_features"]["product_feature"]

            if isinstance(features_data, dict):
                features_data = [features_data]

            ids = [int(feature["attrs"]["id"]) for feature in features_data]
            if ids:
                prestashop.delete("product_features", resource_ids=ids)

    with open(f"{SCRIPT_DIR}\\products.json") as file:
        products = json.loads(file.read())

    with ThreadPoolExecutor(max_workers=15) as executor:
        executor.map(add_product, products)


def main():
    add_categories(False)
    add_products(False)


if __name__ == '__main__':
    main()
