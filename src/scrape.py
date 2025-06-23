import requests
import os
import sys
import json
import argparse
import notify

# Globals
BASE_URL = "http://www.woolworths.com.au/"
API_ENDPOINT = "apis/ui/product/detail/"
item_code = '254695' # Vittoria Oro 


class Item:
    def __init__(self, code, name, prev_price, current_price, imgurl=None):
        self.code = code
        self.name = name
        self.prev_price = prev_price
        self.current_price = current_price 
        self.imgurl = imgurl
        
    def __str__(self):
        return f"+{(len(self.name)+ 6) * '-'}+" + f"\nName: {self.name}\nItem Code: {self.code}\nPrice: {self.current_price}\nOn Sale: {self.on_sale()}"
    
    def on_sale(self):
        return self.prev_price != 0 and self.current_price < self.prev_price
    
    def how_much(self):
        if self.on_sale():
            return int((100 - (self.current_price / self.prev_price) * 100) // 1) 
        else:
            return f"Not on sale."


def get_item_codes(path):
    """
    Reads item codes from a file or a single item code from stdin.
    """
    if not os.path.exists(path):
        if not path.isnumeric():
            print(f"File {path} does not exist or is not a valid item code.")
            exit(1)
        else:
            return [path]
    with open(path, 'r') as file:
        print(f"Reading item codes from {path}")
        item_codes = file.read().splitlines()
        print(f"Loaded {len(item_codes)} item codes.")
        return item_codes
    
    
    
def establish_session():
    """
    Establishes a session with Woolworths to scrape their bloody product data.
    Beats asking for an API key.
    """
    
    headers = {
        "User-Agent": "Mozilla/5.0", # We need a user agent to avoid being blocked
        "Accept": "application/json"
    }
    
    session = requests.Session()
    
    session.headers.update(headers)

    if session.get(BASE_URL).status_code == 200:  # Get session variables
        print(f"Successfully grabbed {len(session.cookies.get_dict().keys())} session cookies.")

        return session
    else:
        print("Failed to connect to Woolies. Is the site down?")
        exit(1)


def get_item(session: requests.Session, item_code: str) :
    """
    Given an item code, fetches its details from the Woolworths Product API and parses the item as an Item object.
    """
    data = session.get(BASE_URL+API_ENDPOINT+item_code).json()
    item = Item(
        code=item_code,
        name=data['Product']['DisplayName'],
        current_price=data['Product']['InstorePrice'],
        prev_price=data['Product']['InstoreWasPrice'],
        imgurl=data['Product']['MediumImageFile'])
   

    return item

def get_item_prices(session: requests.Session, item_codes: list):
    """
    Given a list of item codes, parses them using get_item() and returns a list of Item objects on sale.
    """
    items = []
    for item_code in item_codes:
        item_code = item_code.strip()
        if not item_code.isnumeric():
            continue
        item = get_item(session, item_code)
        items.append(item)
    
    return items
        
def get_sale_items(items: list):
    """
    Given a list of Item objects, returns those that are on sale. 
    """
    # Check Item Prices
    sale_items = []
    for item in items:
        if item.on_sale():
            sale_items.append(item)
            print(f"Added Item: {item.name} | Sale: {item.how_much()}% off | Price: ${item.current_price} (was ${item.prev_price})")
    print(f"Found {len(sale_items)} target items on sale.")
    return sale_items

def build_notification_content(sale_items: list):
    """
    Builds the content for the notification based on the sale items.
    """
    content = "The following items are on sale:\n\n"
    for item in sale_items:
        content += f"{item.name} is on sale: {item.how_much()}% off, now ${item.current_price} (was ${item.prev_price})\n"
    return content

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("codes", help="Numeric item code or file containing item codes to scrape.")
    parser.add_argument("-u", "--url", help="URL for the ntfy server")
    

    args = parser.parse_args()
    item_codes = get_item_codes(args.codes)    
    ntfy_url = args.url.strip() if args.url else None
    
    # Establish session
    session = establish_session()
    items = get_item_prices(session, item_codes)
    sale_items = get_sale_items(items)
    
    
    
    if len(sale_items) != 0 and ntfy_url:
        notify.publish_notification(
            url=ntfy_url,
            content=build_notification_content(sale_items),
            title=f"Woolworths Sale Alert - {len(sale_items)} Items on Sale",
            priority="urgent",
            tags="green_apple"
        )
        print("Notification sent successfully.")
                        
    

