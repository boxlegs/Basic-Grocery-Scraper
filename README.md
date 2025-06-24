# Woolies Salescraper
A basic Woolies grocery sale scraper, since who buys anything at full price nowadays?

This isn't _really_ a scraper, since it uses a publicly available API. However this API doesn't have much in the way of public documentation so it's about as haphazard. This uses the `/ui/product/detail` endpoint to grab general price data for specific items. Using just the item's code (shown in the URL when online shopping) we can poll this data without any form of API key - which is weird, since the internet says you need one. 

## Usage
Using this tool is pretty easy. You just need to clone the repository and supply the file containing the item codes (see format below), as well as the desired ntfy.sh server+endpoint if you have one. 

```sh
git clone https://github.com/boxlegs/WooliesSalescraper.git
cd WooliesSalescraper
python3 scrape.py -u http://ntfy.sh/sale codes.txt
```
