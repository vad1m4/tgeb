from selenium import webdriver
from bs4 import BeautifulSoup

from time import sleep  # type: ignore

import logging

logger = logging.getLogger("general")


class TGEBImageScraper:
    def __init__(self, url: str) -> None:
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--headless=new")
        self.url = url

    def scrape_images(self) -> list[str]:
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.get(self.url)
        sleep(5)
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
        logger.info(f"Found {len(image_urls)} image URLs")
        return image_urls
