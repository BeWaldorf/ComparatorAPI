from requests   import Response, get as req_get
from bs4        import BeautifulSoup, Tag
from flask      import Flask
from SearchItem import SearchItem
import json

class ComparatorApi:
    req_URL: dict[str, str]
    headers: dict
    myComparatorApi: Flask 
    page: Response
    soup: BeautifulSoup
    search_results: list[Tag]
    
    
    def __init__(self) -> None:
        self.req_URL = {"BE":   "https://www.amazon.com.be/s?k=",
                        "FR":   "https://www.amazon.fr/s?k=", 
                        "DE":   "https://www.amazon.de/s?k=",
                        "NL":   "https://www.amazon.nl/s?k=", 
                        "JP":   "https://www.amazon.co.jp/s?k=",
                        "COM":  "https://www.amazon.com/s?k="
                        }
        self.myComparatorApi = Flask(__name__)
        
        @self.myComparatorApi.route("/")
        def index():
            return "Hello World!"
        
        @self.myComparatorApi.route("/browser_search/<string:country_code>/<string:search_term>")
        def search(country_code, search_term):
            full_URL:str = self.req_URL[country_code] + search_term
            headers = {'authority': 'www.amazon.com',
                'pragma': 'no-cache',
                'cache-control': 'no-cache',
                'dnt': '1',
                'upgrade-insecure-requests': '1',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/119.0.2151.97"
                }
            self.page = req_get(full_URL, headers=headers)
            self.soup = BeautifulSoup(self.page.content, "html.parser")
            self.search_results = self.soup.find_all(attrs={"data-component-type": "s-search-result"})
            result_items: list[SearchItem] = self.pretty_results(self.search_results)
            return self.generate_html_table(result_items)
        
        @self.myComparatorApi.route("/api_search/<string:country_code>/<string:search_term>")
        def api_search(country_code, search_term):
            full_URL:str = self.req_URL[country_code]+ search_term
            headers = {'authority': 'www.amazon.com',
                'pragma': 'no-cache',
                'cache-control': 'no-cache',
                'dnt': '1',
                'upgrade-insecure-requests': '1',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'sec-fetch-site': 'none',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-dest': 'document',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/119.0.2151.97"
                }
            self.page = req_get(full_URL, headers=headers)
            self.soup = BeautifulSoup(self.page.content, "html.parser")
            self.search_results = self.soup.find_all(attrs={"data-component-type": "s-search-result"})
            result_items_str:str = self.scrape_processor(self.search_results)
            return result_items_str
    
    def scrape_processor(self, results:list[Tag]) -> list[dict]:
        itemList: list[dict] = []
        for result in results[:5]:
            # Extracting price elements
            price_whole_element = result.find("span", class_="a-price-whole")
            price_fraction_element = result.find("span", class_="a-price-fraction")
            price_symbol_element = result.find("span", class_="a-price-symbol")

            # Check if all elements exist and have text before extracting the price
            if all(elem is not None for elem in [price_whole_element, price_fraction_element, price_symbol_element]):
                price_whole = price_whole_element.get_text(strip=True)
                price_fraction = price_fraction_element.get_text(strip=True)
                price_symbol = price_symbol_element.get_text(strip=True)

                # Clean up the text and format the price
                price_whole = price_whole.replace('.', '')  # Remove any commas
                price = f"{price_symbol}{price_whole}.{price_fraction}"
            else:
                price = None

            # Extracting title
            title_element = result.find("h2", class_="a-size-mini")
            title = title_element.get_text().strip() if title_element else None

            # Extracting image URL
            image_element = result.find("img", class_="s-image")
            image_url = image_element.get("src") if image_element else None

            # Extracting shipping price
            shipping_element = result.find("span", class_="a-color-base")
            shipping_price = shipping_element.get_text().strip() if shipping_element and "FREE Delivery" in shipping_element.get_text() else None

            # Extracting link
            link_element = result.find("a", class_="a-link-normal")
            link = "https://www.amazon.com.be" + link_element.get("href") if link_element else None

            # Create SearchItem instance
            search_item = SearchItem(title, price, image_url, shipping_price, link)
            item_dict = search_item.serializer()
            itemList.append(item_dict)
        return json.dumps(itemList)


    def pretty_results(self, results: list) -> list[SearchItem]:
        itemList: list[SearchItem] = []
        for result in results[:5]:
            # Extracting price elements
            price_whole_element = result.find("span", class_="a-price-whole")
            price_fraction_element = result.find("span", class_="a-price-fraction")
            price_symbol_element = result.find("span", class_="a-price-symbol")

            # Check if all elements exist and have text before extracting the price
            if all(elem is not None for elem in [price_whole_element, price_fraction_element, price_symbol_element]):
                price_whole = price_whole_element.get_text(strip=True)
                price_fraction = price_fraction_element.get_text(strip=True)
                price_symbol = price_symbol_element.get_text(strip=True)

                # Clean up the text and format the price
                price_whole = price_whole.replace('.', '')  # Remove any commas
                price = f"{price_symbol}{price_whole}.{price_fraction}"
            else:
                price = None

            # Extracting title
            title_element = result.find("h2", class_="a-size-mini")
            title = title_element.get_text().strip() if title_element else None

            # Extracting image URL
            image_element = result.find("img", class_="s-image")
            image_url = image_element.get("src") if image_element else None

            # Extracting shipping price
            shipping_element = result.find("span", class_="a-color-base")
            shipping_price = shipping_element.get_text().strip() if shipping_element and "FREE Delivery" in shipping_element.get_text() else None

            # Extracting link
            link_element = result.find("a", class_="a-link-normal")
            link = "https://www.amazon.com.be" + link_element.get("href") if link_element else None

            # Create SearchItem instance
            search_item = SearchItem(title, price, image_url, shipping_price, link)
            itemList.append(search_item)
            
            # Use search_item attributes as needed
            print("Name:", search_item.name)
            print("Price:", search_item.price)
            print("Image URL:", search_item.image_link)
            print("Delivery Price:", search_item.delivery_price)
            print("Link:", search_item.link)
            print("----")  # Separating each search result 
        return itemList
        
    def generate_html_table(self, results):
        table_content = "<table border='1'>"
        table_content += "<tr><th>Title</th><th>Price</th><th>Image</th><th>Delivery Options</th></tr>"
        
        for result in results:
            title = result.name
            price = result.price
            image_url = result.image_link
            delivery_options = result.delivery_price
            
            table_content += f"<tr><td>{title}</td><td>{price}</td><td><img src='{image_url}' width='100' height='100'></td><td>{delivery_options}</td></tr>"
        
        table_content += "</table>"
        return table_content
    
    
            
            
    