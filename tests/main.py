import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys


LOCAL_SHOP = "https://localhost:443"
CLUSTER_SHOP = "https://localhost:5242"
LOCAL_SHOP_ADMIN = "https://localhost:443/admin4577"
CLUSTER_SHOP_ADMIN = "https://localhost:5242/admin4577"


def set_quantity(driver):
    quantity = random.randint(1, 5) - 1
    driver.find_element(By.ID, 'quantity_wanted').clear()
    for _ in range(quantity):
        driver.find_element(By.CLASS_NAME, 'btn.btn-touchspin.js-touchspin.bootstrap-touchspin-up').click()


def add_products_from_category_to_cart(driver, category, different_products_number=5):
    driver.find_elements(By.ID, category)[1].click()
    for _ in range(different_products_number):
        is_available = False
        while not is_available:
            whiskies = driver.find_elements(By.CLASS_NAME, 'js-product.product.col-xs-12.col-sm-6.col-xl-4')
            chosen_whisky = random.choice(whiskies)
            chosen_whisky.find_element(By.TAG_NAME, 'a').click()
            try:
                driver.find_element(By.CLASS_NAME, 'material-icons.product-unavailable')
                driver.back()
            except:
                is_available = True
        quantity_available = False
        while not quantity_available:
            set_quantity(driver)
            time.sleep(1.5)
            try:
                driver.find_element(By.CLASS_NAME, 'material-icons.product-unavailable')
            except:
                quantity_available = True
        driver.find_element(By.CLASS_NAME, 'btn.btn-primary.add-to-cart').click()
        driver.find_element(By.CLASS_NAME, 'breadcrumb.hidden-sm-down').find_elements(By.TAG_NAME, 'li')[1].click()
    driver.back()


def add_ten_products_to_cart(driver):
    add_products_from_category_to_cart(driver, 'category-635')
    add_products_from_category_to_cart(driver, 'category-636')


def search_by_name_and_add_random_to_cart(driver):
    driver.find_element(By.CLASS_NAME, 'ui-autocomplete-input').send_keys("Jack Daniel's")
    driver.find_element(By.CLASS_NAME, 'ui-autocomplete-input').send_keys(Keys.ENTER)
    products = driver.find_elements(By.CLASS_NAME, 'js-product.product.col-xs-12.col-sm-6.col-xl-3')
    chosen_product = random.choice(products)
    chosen_product.find_element(By.TAG_NAME, 'a').click()
    driver.find_element(By.CLASS_NAME, 'btn.btn-primary.add-to-cart').click()
    driver.back()
    driver.back()


def remove_three_products_from_cart(driver):
    driver.find_element(By.CLASS_NAME, 'header').click()
    for _ in range(3):
        products = driver.find_elements(By.CLASS_NAME, 'cart-items')
        product_to_remove = random.choice(products)
        product_to_remove.find_element(By.CLASS_NAME, 'remove-from-cart').click()
    driver.back()


def register_account(driver):
    driver.find_element(By.CLASS_NAME, 'user-info').find_element(By.TAG_NAME, 'a').click()
    driver.find_element(By.CLASS_NAME, 'no-account').find_element(By.TAG_NAME, 'a').click()
    driver.find_elements(By.CLASS_NAME, 'radio-inline')[0].click()
    driver.find_element(By.ID, 'field-firstname').send_keys('John')
    driver.find_element(By.ID, 'field-lastname').send_keys('Doe')
    driver.find_element(By.ID, 'field-email').send_keys('john.doe@test.com')
    driver.find_element(By.ID, 'field-password').send_keys('qwerty')
    driver.find_element(By.CLASS_NAME, 'btn.btn-primary.form-control-submit.float-xs-right').click()


def complete_order(driver):
    driver.find_element(By.CLASS_NAME, 'header').click()
    driver.find_element(By.CLASS_NAME, 'btn.btn-primary').click()
    driver.find_element(By.ID, 'field-address1').send_keys('2137 Alcoholics Street')
    driver.find_element(By.ID, 'field-postcode').send_keys('69-666')
    driver.find_element(By.ID, 'field-city').send_keys('Boozetown')
    driver.find_element(By.NAME, 'confirm-addresses').click()
    driver.find_element(By.ID, 'delivery_option_8').click()
    driver.find_element(By.NAME, 'confirmDeliveryOption').click()
    driver.find_element(By.ID, 'payment-option-1').click()
    driver.find_element(By.ID, 'conditions_to_approve[terms-and-conditions]').click()
    driver.find_element(By.CLASS_NAME, 'btn.btn-primary.center-block').click()


def check_order_status(driver):
    driver.find_element(By.CLASS_NAME, 'account').click()
    driver.find_element(By.ID, 'history-link').click()
    driver.find_element(By.CLASS_NAME, 'text-sm-center.order-actions').find_elements(By.TAG_NAME, 'a')[0].click()
    print(driver.find_element(By.CLASS_NAME, 'label.label-pill.bright').text)


def download_VAT_invoice(driver_admin, driver):
    driver_admin.find_element(By.NAME, 'email').send_keys('admin@presta.com')
    driver_admin.find_element(By.NAME, 'passwd').send_keys('admin')
    driver_admin.find_element(By.ID, 'submit_login').click()
    time.sleep(1)
    driver_admin.find_element(By.ID, 'subtab-AdminParentOrders').click()
    time.sleep(1)
    driver_admin.find_element(By.ID, 'subtab-AdminOrders').click()
    time.sleep(1)
    driver_admin.find_element(By.ID, 'order_grid_table').find_elements(By.TAG_NAME, 'tr')[2].find_elements(By.TAG_NAME, 'button')[0].click()
    driver_admin.find_element(By.ID, 'order_grid_table').find_elements(By.TAG_NAME, 'tr')[2].find_elements(By.TAG_NAME, 'button')[12].click()
    driver.refresh()
    driver.find_element(By.PARTIAL_LINK_TEXT, 'Pobierz').click()


def main():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(CLUSTER_SHOP)
    driver_admin = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver_admin.get(CLUSTER_SHOP_ADMIN)
    add_ten_products_to_cart(driver)
    search_by_name_and_add_random_to_cart(driver)
    remove_three_products_from_cart(driver)
    register_account(driver)
    complete_order(driver)
    check_order_status(driver)
    download_VAT_invoice(driver_admin, driver)
    driver_admin.close()
    driver.close()


if __name__ == '__main__':
    main()
