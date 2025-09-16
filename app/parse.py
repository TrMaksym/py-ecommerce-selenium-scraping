import csv
import json
import time
from dataclasses import dataclass
import random
from typing import List
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BASE_URL: str = "https://webscraper.io/"
HOME_URL: str = urljoin(BASE_URL, "test-sites/e-commerce/more/")

@dataclass
class Product:
    title: str
    description: str
    price: float
    rating: int
    num_of_reviews: int

def scrape_products_from_page(driver: webdriver.Chrome, url: str, product_selector: str, use_more_button: bool = False) -> List[Product]:
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    try:
        accept_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".accept-cookies-button")))
        accept_btn.click()
    except:
        pass

    products: List[Product] = []

    if use_more_button:
        while True:
            try:
                more_btn = driver.find_element(By.CSS_SELECTOR, ".btn.btn-primary.btn-lg.btn-block")
                if more_btn.is_displayed():
                    driver.execute_script("arguments[0].click();", more_btn)
                    time.sleep(1)
                else:
                    break
            except:
                break

    items = driver.find_elements(By.CSS_SELECTOR, product_selector)
    for item in items:
        try:
            # Витягуємо повну назву з атрибута title елемента <a class="title">
            title = item.find_element(By.CSS_SELECTOR, "a.title").get_attribute("title")
        except:
            title = ""
        try:
            description = item.find_element(By.CSS_SELECTOR, ".description").text
        except:
            description = ""
        try:
            price = float(item.find_element(By.CSS_SELECTOR, ".price").text.replace("$", ""))
        except:
            price = 0.0
        try:
            stars = item.find_elements(By.CSS_SELECTOR, ".ratings .ws-icon-star")
            rating = len(stars)
        except:
            rating = 0
        try:
            num_reviews_text = item.find_element(By.CSS_SELECTOR, ".ratings .pull-right, .review-count span").text
            num_of_reviews = int(num_reviews_text.split()[0])
        except:
            num_of_reviews = 0

        products.append(Product(title, description, price, rating, num_of_reviews))

    return products

def save_products_to_csv(filename: str, products: List[Product]) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "description", "price", "rating", "num_of_reviews"])
        for product in products:
            writer.writerow([product.title, product.description, product.price, product.rating, product.num_of_reviews])

def get_all_products() -> None:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        pages = {
            "home.csv": (HOME_URL, ".thumbnail", False, 3),
            "computers.csv": (HOME_URL + "computers", ".thumbnail", False, 3),
            "laptops.csv": (HOME_URL + "computers/laptops", ".thumbnail", True, None),
            "tablets.csv": (HOME_URL + "computers/tablets", ".thumbnail", True, None),
            "phones.csv": (HOME_URL + "phones", ".thumbnail", False, 3),
            "touch.csv": (HOME_URL + "phones/touch", ".thumbnail", True, None)
        }

        for filename, (url, selector, use_more_button, limit) in pages.items():
            print(f"Parsing page {url} -> {filename}")
            products: List[Product] = scrape_products_from_page(driver, url, selector, use_more_button)

            if limit is not None and len(products) > limit:
                products = random.sample(products, limit)

            save_products_to_csv(filename, products)
            print(f"Saved {len(products)} products in {filename}")

    finally:
        driver.quit()

if __name__ == "__main__":
    get_all_products()
