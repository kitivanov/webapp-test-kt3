import time

import pytest
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = "https://4lapy.ru/"
DEFAULT_TIMEOUT = 15


@pytest.fixture()
def browser():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


class BasePage:
    def __init__(self, browser: WebDriver):
        self.browser = browser
        self.wait = WebDriverWait(browser, DEFAULT_TIMEOUT)

    def open(self, url: str):
        self.browser.get(url)

    def find(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()


class HomePage(BasePage):
    SEARCH_INPUT = (By.CSS_SELECTOR, '[data-testid="search-input"]')
    ADD_TO_CART_BUTTON = (
        By.CSS_SELECTOR,
        ".digi-product__actions .digi-product__button",
    )
    CART_COUNTER = (By.ID, "tag-counter")
    CART_ICON = (By.CSS_SELECTOR, '[data-testid="nav-icon-link-nav_menu_cart"]')

    def open_home(self):
        self.open(BASE_URL)

    def search(self, text: str):
        field = self.wait.until(EC.element_to_be_clickable(self.SEARCH_INPUT))
        field.clear()
        field.send_keys(text + Keys.ENTER)

    def add_first_product_to_cart(self):
        self.click(self.ADD_TO_CART_BUTTON)

    def get_cart_counter(self):
        counter = self.find(self.CART_COUNTER)
        return int(counter.text.strip())

    def open_cart(self):
        self.click(self.CART_ICON)


class SearchPage(BasePage):
    PRODUCTS = (By.CSS_SELECTOR, '[data-testid="product-card"]')

    def wait_search_results(self):
        self.wait.until(EC.url_contains("search"))
        self.wait.until(EC.presence_of_element_located(self.PRODUCTS))

    def get_products(self):
        return self.browser.find_elements(*self.PRODUCTS)


class CartPage(BasePage):

    CART_ITEMS = (By.CSS_SELECTOR, 'li[data-testid^="cart-item-"]')

    def wait_cart_page(self):
        self.wait.until(EC.url_contains("/cart"))

    def get_cart_items(self):
        return self.browser.find_elements(*self.CART_ITEMS)


def test_search(browser: WebDriver):
    """Тест сценария поиска товара."""
    home = HomePage(browser)
    search_page = SearchPage(browser)

    home.open_home()
    home.search("корм")

    search_page.wait_search_results()
    results = search_page.get_products()

    time.sleep(1)

    assert len(results) > 0


def test_add_product_to_cart(browser: WebDriver):
    """Тест сценария добавления товара в корзину."""
    home = HomePage(browser)
    cart = CartPage(browser)

    home.open_home()
    home.add_first_product_to_cart()
    counter = home.get_cart_counter()

    assert counter > 0

    home.open_cart()
    cart.wait_cart_page()
    items = cart.get_cart_items()

    time.sleep(1)

    assert len(items) > 0
