import pandas as pd
from AParser import AParser
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from unidecode import unidecode


class ParserProm(AParser):

    def __init__(self, term, status=0):
        self._term = term
        self._status = status
        self._driver = None

    def search(self) -> pd.DataFrame:
        # create webdriver
        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')
        options.add_argument("--incognito")
        options.add_argument("--window-size=1280,800")
        options.set_preference("permissions.default.image", 2)
        try:
            self._driver = webdriver.Firefox(options=options)
            print("Driver created")

            shop_list = self.__get_shops_list()
            contacts_list = list()

            if len(shop_list) == 0:
                raise ValueError

            for shop in shop_list:
                print(f"processing {shop}...")
                try:
                    contacts_list.append(self.__get_contacts(shop))
                except:
                    # seller is closed, so skip
                    pass

            print(contacts_list)
        except selenium.common.exceptions.SessionNotCreatedException:
            raise ChildProcessError
        finally:
            if self._driver is not None:
                self._driver.quit()
        return pd.DataFrame(contacts_list)

    def __get_shops_list(self) -> set:
        if self._status == 0:
            request_url_list = \
                [f"https://prom.ua/ua/search?search_term={self._term.replace(' ', '%20')}",
                 f"https://prom.ua/ua/search?search_term={ParserProm.__cyrillic_to_latin(self._term, '-')}"]
        else:
            request_url_list = [self._term]
        company_pages = set()
        cont = True
        attempt_10 = 0
        start_attempt = 0
        max_attempts = 2
        for pattern_url in request_url_list:
            current_request_url = pattern_url
            while cont:
                # scroll down
                self._driver.get(current_request_url)

                initial_loaded_count = len(self._driver.find_elements(By.XPATH, "//div[@data-qaid='product_block']"))
                print(f"Initial loaded: {initial_loaded_count}")

                if initial_loaded_count == 10:

                    self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    try:
                        # Wait for the loaded elements to change
                        print("start scrolling")
                        if attempt_10 <= max_attempts:
                            WebDriverWait(self._driver, 10).until(
                                lambda driver: len(driver.find_elements(By.XPATH,
                                                                        "//div[@data-qaid='product_block']"
                                                                        )) > initial_loaded_count)
                        elem = WebDriverWait(self._driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@data-qaid = 'product_gallery']")))

                        res = self.__ps_with_bs(elem, company_pages)
                        attempt_10 = start_attempt
                        if res == 0:
                            cont = False
                        else:
                            current_request_url = res
                    except:
                        print("Fail to load all data. Try again...")
                        attempt_10 += 1

                else:

                    try:
                        elem = WebDriverWait(self._driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@data-qaid = 'product_gallery']"))
                        )
                        res = self.__ps_with_bs(elem, company_pages)
                        if res == 0:
                            cont = False
                        else:
                            current_request_url = res

                    except:
                        self.__change_to_visible_driver()
                        self._driver.get(current_request_url)
                        try:
                            WebDriverWait(self._driver, 60).until(
                                EC.presence_of_element_located((By.XPATH, "//div[@data-qaid = 'product_gallery']"))
                            )
                            print("well done")
                        except:
                            # error exit
                            print("Captcha error...")
                            print("driver quit")
                            self._driver.quit()

                            return company_pages

        return company_pages

    def __change_to_visible_driver(self):
        print("driver quit")
        self._driver.quit()
        print("new driver ....")
        options = webdriver.FirefoxOptions()
        options.add_argument("--incognito")
        options.add_argument("--window-size=1280,800")
        self._driver = webdriver.Firefox(options=options)
        print("... created")

    def __ps_with_bs(self, elem, company_pages):
        # parse with bsoup
        product_bench = BeautifulSoup(elem.get_attribute('innerHTML'), "html.parser")
        product_list = product_bench.find_all("div", {"data-qaid": "product_block"})
        print(len(product_list))
        for product in product_list:
            elem = product.find("div", {"class": "M3v0L BXDW- qzGRQ aO9Co"})
            elem_child = elem.find(
                "a") if elem is not None else None  # , {"class": "_0cNvO jwtUM"}) if elem is not None else None
            if elem_child is not None:
                company_pages.add(
                    elem_child.get('href'))
            else:
                print("Missed block!!")

        try:
            next_page_button = self._driver.find_element(By.XPATH, "//a[@data-qaid='next_page']")
            current_request_url = next_page_button.get_attribute('href')
            return current_request_url
        except NoSuchElementException:
            cont = False
            return cont

    def __get_contacts(self, url: str) -> dict:
        wait = WebDriverWait(self._driver, 2)
        self._driver.get(url)

        if "bot protection" in self._driver.page_source.lower():
            self.__change_to_visible_driver()
            self._driver.get(url)
            try:
                WebDriverWait(self._driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, "//button[@data-qaid = 'contacts_btn']"))
                )
            except:
                print("captcha fail...")
                return dict()

        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-qaid = 'contacts_btn']"))).click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-qaid = 'phone']")))
        elem = self._driver.find_element(By.XPATH, "//div[@data-qaid = 'contacts_popup']")
        info = {}
        contacts = BeautifulSoup(elem.get_attribute('innerHTML'), "html.parser")

        temp = contacts.find("a", {"data-qaid": "company_name"})
        info["company_name"] = temp.find("span").text if temp is not None else None

        temp = contacts.find("a", {"data-qaid": "phone"})
        info["phone"] = temp.text if temp is not None else None

        temp = contacts.find("a", {"data-qaid": "email_btn"})
        info["email"] = temp.text if temp is not None else None

        link_el = contacts.find("a", {"data-qaid": "site_link"})
        info["site_link"] = link_el.get("href") if link_el is not None else url

        temp = contacts.find("a", {"data-qaid": "address"})
        info["address"] = temp.text if temp is not None else None

        return info

    @staticmethod
    def __cyrillic_to_latin(text, replace_to='_'):
        # Transliterate Cyrillic to Latin
        latin_text = unidecode(text)

        # Replace spaces with underscores
        latin_text_with_underscores = latin_text.replace(' ', replace_to)

        return latin_text_with_underscores


def testPromParser():
    a = ParserProm("однострій пласт").search()
    print(a)


if __name__ == '__main__':
    testPromParser()
