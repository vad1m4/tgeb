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
        image_urls = []
        imgs = soup.findAll("img")
        for img in imgs:
            if "http" in img["src"]:
                image_urls.append(img["src"])

        divs = soup.find_all("div", class_="power-off__top")

        for div in divs:
            aos_divs = div.find_all("div", class_="aos-init aos-animate")
            for aos_div in aos_divs:
                p_tags = aos_div.find_all("p")

                for p in p_tags:
                    if (
                        "не застосовуватимуться" in p.get_text()
                        or "не застосовуються" in p.get_text()
                    ):
                        logger.info("No outages for today!")
                        return [None]
        logger.info(f"Found {len(image_urls)} image URLs")
        # print(f"Found {len(image_urls)} image URLs")
        for url in image_urls:
            logger.info(url)
            # print(url)
        return image_urls


if __name__ == "__main__":
    image_scraper = TGEBImageScraper("https://poweron.loe.lviv.ua/")
    urls = image_scraper.scrape_images()
