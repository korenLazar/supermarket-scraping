import logging
import os
import platform
import shutil
import sys
import time
from abc import abstractmethod

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from supermarket_chain import SupermarketChain
from utils import RAW_FILES_DIRNAME


class CerberusWebClient(SupermarketChain):
    @property
    @abstractmethod
    def username(self):
        pass

    download_dir = os.path.join(os.path.abspath(os.path.curdir), RAW_FILES_DIRNAME)

    def is_linux_server(self) -> bool:
        return sys.platform == "linux" and not os.environ.get("DISPLAY")

    def set_browser_options(self) -> webdriver.ChromeOptions:
        options = webdriver.ChromeOptions()
        options.add_experimental_option(
            "prefs", {"download.default_directory": self.download_dir}
        )
        options.add_argument("ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors=yes")
        options.headless = logging.DEBUG != logging.root.level
        return options

    def set_browser(self, options: webdriver.ChromeOptions) -> webdriver.Chrome:
        if self.is_linux_server() and platform.machine() == "aarch64":
            return webdriver.Chrome(
                service=Service("/usr/bin/chromedriver"), options=options
            )
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

    def get_download_url_or_path(
        self,
        store_id: int,
        category: SupermarketChain.XMLFilesCategory,
        session: requests.Session,
    ) -> str:
        options = self.set_browser_options()
        driver = self.set_browser(options)
        driver.get("https://url.retail.publishedprices.co.il/login#")
        time.sleep(2)
        userElem = driver.find_element(By.NAME, "username")
        userElem.send_keys(self.username)
        driver.find_element(By.NAME, "Submit").click()
        time.sleep(2)
        searchElem = driver.find_element(By.CLASS_NAME, "form-control")
        searchElem.send_keys(category.name.lower().replace("s", ""))
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
        filename = best_link.split("/")[
            -1
        ]  # don't be an idiot. it is stupid to count letters
        # split and grab, or rename it by yourself.
        path_download = os.path.join(self.download_dir, filename)
        path_to_save = os.path.join(self.download_dir, f"{self.username}-{filename}")
        try:
            shutil.move(path_download, path_to_save)
            logging.info(f"Downloaded the file to: {path_to_save}")
        except:
            logging.info(f"{filename} already exists in {path_to_save}")

        return path_to_save
