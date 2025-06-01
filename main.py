import requests
from bs4 import BeautifulSoup
import re
import time
import json
import logging

# Load configuration
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Set up logging
logging.basicConfig(
    filename=config["main.log"],
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s:%(message)s"
)

def main(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    adverts = soup.find_all(class_="wf-cell")
    print(f"Adverts: {len(adverts)}")

    adverts_data = []

    for advert in adverts:
        # Title and link
        h4_element = advert.find("h4")
        if h4_element and h4_element.find("a"):
            title = h4_element.find("a").get("title")
            link = h4_element.find("a").get("href")
        else:
            title = None
            link = None

        # Image
        img_element = advert.find("img")
        image = img_element.get("src") if img_element else None

        # Price
        price_element = advert.find("span", class_="woocommerce-Price-amount")
        price = price_element.get_text(strip=True) if price_element else None

        # Details and Contacts (from advert page)
        details = []
        contacts = []
        if link:
            try:
                advert_response = requests.get(link)
                advert_soup = BeautifulSoup(advert_response.content, "html.parser")
                # Details extraction
                for h2 in advert_soup.find_all("h2"):
                    h2_text = "".join(h2.stripped_strings)
                    div = h2.find_next_sibling("div")
                    div_text = " ".join(div.stripped_strings) if div else ""
                    combined_one = f"{h2_text} {div_text}".strip()
                    cleaned = re.sub(r"\s+", " ", combined_one)
                    details.append(cleaned)
                # Contacts extraction
                for p in advert_soup.select(".has-text-align-center"):
                    combined_two = " ".join(p.stripped_strings)
                    cleaned = re.sub(r"\s+", " ", combined_two)
                    contacts.append(cleaned)
            except Exception as e:
                print(f"Failed to fetch details for {link}: {e}")

        # Save advert data
        adverts_data.append({
            "title": title,
            "image": image,
            "price": price,
            "link": link,
            "details": details,
            "contacts": contacts
        })

    print(f"Successfully scraped {len(adverts_data)} vehicles from {url}")
    return adverts_data

if __name__ == '__main__':
    all_adverts = []

    first_page = "https://dealsonwheels.lt/isigykite-naudota-automobili-internetu/"
    print("Scraping page 1...")
    all_adverts.extend(main(first_page))
    time.sleep(1)

    base_url = "https://dealsonwheels.lt/isigykite-naudota-automobili-internetu/page/{}/"
    for page_number in range(2, 7):
        print(f"Scraping page {page_number}...")
        url = base_url.format(page_number)
        all_adverts.extend(main(url))
        time.sleep(1)

    with open("DOW_adverts.json", "w", encoding="utf-8") as file:
        json.dump(all_adverts, file, indent=4, ensure_ascii=False)

    with open("DOW_adverts.json", "r", encoding="utf-8") as file:
        data = json.load(file)

    print("The scraping successfully completed")
