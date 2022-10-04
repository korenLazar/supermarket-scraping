import logging
import os
import shutil
import time
from abc import abstractmethod

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from supermarket_chain import SupermarketChain


class CerberusWebClient(SupermarketChain):
    @property
    @abstractmethod
    def username(self):
        pass

    def get_download_url_or_path(
        self,
        store_id: int,
        category: SupermarketChain.XMLFilesCategory,
        session: requests.Session,
    ) -> str:
        options = webdriver.ChromeOptions()
        options.add_argument("ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors=yes")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

        driver.get("https://url.retail.publishedprices.co.il/login#")
        time.sleep(2)
        userElem = driver.find_element(By.NAME, "username")
        userElem.send_keys(self.username)
        driver.find_element(By.NAME, "Submit").click()
        time.sleep(2)

        searchElem = driver.find_element(By.CLASS_NAME, "form-control")
        searchElem.send_keys(category.value)
        time.sleep(5)

        conns = driver.find_elements(By.CLASS_NAME, "f")
        best_link = ""
        for conn in conns:
            link = conn.get_attribute("href").lower()
            if category == SupermarketChain.XMLFilesCategory.Promos:
                filter_func = (
                    lambda l: "promo" in l
                    and "full" not in l
                    and f"-{store_id:03d}-20" in l
                )
            elif category == SupermarketChain.XMLFilesCategory.PromosFull:
                filter_func = (
                    lambda l: "promo" in l
                    and "full" in l
                    and f"-{store_id:03d}-20" in l
                )
            elif category == SupermarketChain.XMLFilesCategory.Prices:
                filter_func = (
                    lambda l: "price" in l
                    and "full" not in l
                    and f"-{store_id:03d}-20" in l
                )
            elif category == SupermarketChain.XMLFilesCategory.PricesFull:
                filter_func = (
                    lambda l: "price" in l
                    and "full" in l
                    and f"-{store_id:03d}-20" in l
                )
            elif category == SupermarketChain.XMLFilesCategory.Stores:
                filter_func = lambda l: "store" in l and "full" in l and f"-000-20" in l
            else:
                raise ValueError(f"Unknown category type: {category=}")

            if filter_func(link):
                if not best_link or int(link[-7:-3]) > int(best_link[-7:-3]):
                    best_link = link

        if not best_link:
            return ""
        driver.get(best_link)
        time.sleep(3)
        download_dir = "/Users/korenlazar/Downloads"
        filename = best_link[48:]
        path_download = os.path.join(download_dir, filename)
        logging.info(f"{path_download=}")
        path_to_save = f"raw_files/{self.username}-{filename}"
        try:
            shutil.move(path_download, path_to_save)
            print(f"Downloaded {filename} and moved file to {path_to_save}")
        except:
            print(f"{filename} already exists in {path_to_save}")

        return path_to_save
