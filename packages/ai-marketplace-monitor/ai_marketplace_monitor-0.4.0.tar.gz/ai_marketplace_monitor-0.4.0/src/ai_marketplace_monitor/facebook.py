import re
import time
from logging import Logger
from typing import ClassVar, Dict, List
from urllib.parse import quote

from bs4 import BeautifulSoup  # type: ignore
from playwright.sync_api import Browser, Page

from .items import SearchedItem
from .marketplace import Marketplace
from .utils import is_substring, memory


class FacebookMarketplace(Marketplace):
    initial_url = "https://www.facebook.com/login/device-based/regular/login/"

    name = "facebook"

    allowed_config_keys: ClassVar = {
        "username",
        "password",
        "login_wait_time",
        "search_interval",
        "max_search_interval",
        "search_city",
        "acceptable_locations",
        "exclude_sellers",
        "notify",
        "min_price",
        "max_price",
    }

    def __init__(self, name, browser: Browser, logger: Logger):
        assert name == self.name
        super().__init__(name, browser, logger)
        # cache the output of website, but ignore the change of "self" and browser
        # see https://joblib.readthedocs.io/en/latest/memory.html#gotchas for details
        self.get_item_details = memory.cache(self._get_item_details, ignore=["self"])
        #
        self.page: Page | None = None

    @classmethod
    def validate(cls, config) -> None:
        #
        super().validate(config)
        #
        # username, if specified, must be a string
        if "username" in config:
            if not isinstance(config["username"], str):
                raise ValueError(f"Marketplace {cls.name} username must be a string.")
        # password, if specified, must be a string
        if "password" in config:
            if not isinstance(config["password"], str):
                raise ValueError(f"Marketplace {cls.name} password must be a string.")
        # locations, if specified, must be a list (or be converted to a list)
        if "locations" in config:
            if isinstance(config["locations"], str):
                config["locations"] = [config["locations"]]
            if not isinstance(config["locations"], list) or not all(
                isinstance(x, str) for x in config["locations"]
            ):
                raise ValueError(
                    f"Marketplace {cls.name} locations must be string or a list of string."
                )
        # login_wait_time should be an integer
        if "login_wait_time" in config:
            if not isinstance(config["login_wait_time"], int) or config["login_wait_time"] < 1:
                raise ValueError(
                    f"Marketplace {cls.name} login_wait_time must be a positive integer."
                )
        # if exclude_sellers is specified, it must be a list
        if "exclude_sellers" in config:
            if isinstance(config["exclude_sellers"], str):
                config["exclude_sellers"] = [config["exclude_sellers"]]

            if not isinstance(config["exclude_sellers"], list) or not all(
                isinstance(x, str) for x in config["exclude_sellers"]
            ):
                raise ValueError(
                    f"Marketplace {cls.name} exclude_sellers must be a list of string."
                )

        for interval_field in ("search_interval", "max_search_interval"):
            if interval_field in config:
                if not isinstance(config[interval_field], int):
                    raise ValueError(f"Marketplace {cls.name} search_interval must be an integer.")

    def login(self):
        context = self.browser.new_context()  # create a new incognite window
        self.page: Page = context.new_page()
        assert self.page is not None
        # Navigate to the URL, no timeout
        self.page.goto(self.initial_url, timeout=0)
        try:
            if "username" in self.config:
                self.page.wait_for_selector('input[name="email"]').fill(self.config["username"])
                time.sleep(1)
            if "password" in self.config:
                self.page.wait_for_selector('input[name="pass"]').fill(self.config["password"])
                time.sleep(1)
            if "username" in self.config and "password" in self.config:
                self.page.wait_for_selector('button[name="login"]').click()
        except Exception as e:
            self.logger.error(f"An error occurred during logging: {e}")

        # in case there is a need to enter additional information
        login_wait_time = self.config.get("login_wait_time", 60)
        self.logger.info(f"Logged into facebook, waiting {login_wait_time}s to get ready.")
        time.sleep(login_wait_time)

    def search(self, item_config) -> List[SearchedItem]:
        if not self.page:
            self.login()
            assert self.page is not None

        # get city from either marketplace config or item config
        search_city = item_config.get("search_city", self.config.get("search_city", ""))
        # get max price from either marketplace config or item config
        max_price = item_config.get("max_price", self.config.get("max_price", None))
        # get min price from either marketplace config or item config
        min_price = item_config.get("min_price", self.config.get("min_price", None))

        marketplace_url = f"https://www.facebook.com/marketplace/{search_city}/search?"
        if max_price:
            marketplace_url += f"maxPrice={max_price}&"
        if min_price:
            marketplace_url += f"minPrice={min_price}&"

        # search multiple keywords
        found_items = []
        for keyword in item_config.get("keywords", []):
            self.page.goto(marketplace_url + f"query={quote(keyword)}", timeout=0)

            html = self.page.content()

            found_items.extend(
                [x for x in self.get_item_list(html) if self.filter_item(x, item_config)]
            )
            time.sleep(5)
        # go to each item and get the description
        # if we have not done that before
        for item in found_items:
            details = self.get_item_details(item["title"], item["post_url"])
            for key in ("description", "seller"):
                item[key] = details[key]
            self.logger.debug(
                f"""New item "{item["title"]}" from https://www.facebook.com{item["post_url"]} is sold by "{item["seller"]}" and with description "{item["description"][:100]}..." """
            )
            time.sleep(5)
        #
        found_items = [x for x in found_items if self.filter_item_by_details(x, item_config)]
        # check if any of the items have been returned before
        return found_items

    def get_item_list(self, html: str) -> List[SearchedItem]:
        soup = BeautifulSoup(html, "html.parser")
        parsed: List[SearchedItem] = []

        def get_listings_from_structure():
            heading = soup.find(attrs={"aria-label": "Collection of Marketplace items"})
            child1 = next(heading.children)
            child2 = next(child1.children)
            grid_parent = list(child2.children)[2]  # groups of listings
            for group in grid_parent.children:
                grid_child2 = list(group.children)[1]  # the actual grid container
                return list(grid_child2.children)

        def get_listing_from_css():
            return soup.find_all(
                "div",
                class_="x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e x1iorvi4 xjkvuk6 xnpuxes x291uyu x1uepa24",
            )

        try:
            listings = get_listings_from_structure()
        except Exception as e1:
            try:
                listings = get_listing_from_css()
            except Exception as e2:
                self.logger.debug("No listings found from structure and css: {e1}, {e2}")
                self.logger.debug("Saving html to test.html")

                with open("test.html", "w") as f:
                    f.write(html)

                return parsed

        for listing in listings:
            # if the element has no text (only image etc)
            if not listing.get_text().strip():
                continue

            try:
                child1 = next(listing.children)
                child2 = next(child1.children)
                child3 = next(child2.children)  # span class class="x1lliihq x1iyjqo2"
                child4 = next(child3.children)  # div
                child5 = next(child4.children)  # div class="x78zum5 xdt5ytf"
                child5 = next(child5.children)  # div class="x9f619 x1n2onr6 x1ja2u2z"
                child6 = next(child5.children)  # div class="x3ct3a4" (real data here)
                atag = next(child6.children)  # a tag
                post_url = atag["href"]
                atag_child1 = next(atag.children)
                atag_child2 = list(atag_child1.children)  # 2 divs here
                # Get the item image.
                image = listing.find("img")["src"]

                details = list(
                    atag_child2[1].children
                )  # x9f619 x78zum5 xdt5ytf x1qughib x1rdy4ex xz9dl7a xsag5q8 xh8yej3 xp0eagm x1nrcals
                # There are 4 divs in 'details', in this order: price, title, location, distance
                price = details[0].contents[-1].text
                # if there are two prices (reduced), take the first one
                if price.count("$") > 1:
                    match = re.search(r"\$\d+(?:\.\d{2})?", price)
                    price = match.group(0) if match else price
                title = details[1].contents[-1].text
                location = details[2].contents[-1].text

                # Append the parsed data to the list.
                parsed.append(
                    {
                        "marketplace": self.name,
                        "id": post_url.split("?")[0].rstrip("/").split("/")[-1],
                        "title": title,
                        "image": image,
                        "price": price,
                        # we do not need all the ?referral_code&referral_sotry_type etc
                        "post_url": post_url.split("?")[0],
                        "location": location,
                        "seller": "",
                        "description": "",
                    }
                )
            except Exception as e:
                self.logger.debug(f"Failed to parse listing {listing}: {e}")
                pass

        return parsed

    # get_item_details is wrapped around this function to cache results for urls
    def _get_item_details(self, item_title: str, post_url: str) -> Dict[str, str]:
        self.logger.info(f"Getting details for [magenta]{item_title}[magenta]")
        assert self.page is not None
        self.page.goto(f"https://www.facebook.com{post_url}", timeout=0)
        html = self.page.content()

        soup = BeautifulSoup(html, "html.parser")
        try:
            cond = soup.find("span", string="Condition")
            ul = cond.find_parent("ul")
            description_div = ul.find_next_sibling()
            description = description_div.get_text(strip=True)
        except Exception as e:
            self.logger.debug(e)
            description = ""
        #
        try:
            profiles = soup.find_all("a", href=re.compile(r"/marketplace/profile"))
            seller = profiles[-1].get_text()
        except Exception as e:
            self.logger.debug(e)
            seller = ""
        return {"description": description, "seller": seller}

    def filter_item(self, item: SearchedItem, item_config) -> bool:
        # get exclude_keywords from both item_config or config
        exclude_keywords = item_config.get(
            "exclude_keywords", self.config.get("exclude_keywords", [])
        )

        if exclude_keywords and is_substring(exclude_keywords, item["title"]):
            self.logger.debug(f"Excluding item due to keywords: [magenta]{item['title']}[magenta]")
            return False

        # if the return description does not contain any of the search keywords
        search_words = [word for keywords in item_config["keywords"] for word in keywords.split()]
        if not is_substring(search_words, item["title"]):
            self.logger.debug(f"Excluding item without search word: [red]{item['title']}[/red]")
            return False

        # get locations from either marketplace config or item config
        allowed_locations = item_config.get(
            "acceptable_locations", self.config.get("acceptable_locations", [])
        )
        if allowed_locations and not is_substring(allowed_locations, item["location"]):
            self.logger.debug(
                f"Excluding out of area item [red]{item['title']}[/red] from location [red]{item['location']}[/red]"
            )
            return False

        return True

    def filter_item_by_details(self, item: SearchedItem, item_config) -> bool:
        # get exclude_keywords from both item_config or config
        exclude_by_description = item_config.get("exclude_by_description", [])

        if exclude_by_description and is_substring(exclude_by_description, item["description"]):
            self.logger.debug(
                f"""Excluding item by description: [red]{exclude_by_description}[/red]:\n[magenta]{item["description"][:100]}...[magenta] """
            )
            return False

        # get exclude_sellers from both item_config or config
        exclude_sellers = item_config.get("exclude_sellers", []) + self.config.get(
            "exclude_sellers", []
        )

        if exclude_sellers and is_substring(exclude_sellers, item["seller"]):
            self.logger.debug(f"Excluding item by seller: [red]{item['seller']}[/red]")
            return False

        return True
