from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import logging


class TGEBImageScraper:
    def __init__(self, _logger: logging.Logger, url: str) -> None:
        self.logger = _logger
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.service = Service(executable_path="/usr/bin/")

        self.url = url

    def scrape_images(self) -> list[str]:
        self.driver = webdriver.Chrome(
            options=self.chrome_options, service=self.service
        )
        self.driver.get(self.url)
        time.sleep(5)
        page_source = self.driver.page_source
        self.driver.quit()
        soup = BeautifulSoup(page_source, "html.parser")
        divs = soup.find_all("div", class_="power-off__top")

        image_urls = []
        for div in divs:
            aos_divs = div.find_all("div", class_="aos-init aos-animate")
            for aos_div in aos_divs:
                p_tags = aos_div.find_all("p")

                for p in p_tags:
                    img_tags = p.find_all("img")

                    for img in img_tags:
                        src = img.get("src")
                        if src:
                            image_urls.append(src)
        self.logger.info(f"Found {len(image_urls)} image URLs")
        return image_urls
