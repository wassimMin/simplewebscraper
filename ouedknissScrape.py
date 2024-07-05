import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd

def scrape_data():
    url = 'https://www.ouedkniss.com/immobilier/1'

    options = Options()
    options.add_argument('--headless')  
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)

    def scroll_down(driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for the content to load

        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Adjust the sleep time as necessary
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    scroll_down(driver)

    with open('ouedkniss_page.html', 'w', encoding='utf-8') as file:
        file.write(driver.page_source)

    driver.quit()

    with open('ouedkniss_page.html', 'r', encoding='utf-8') as file:
        page_content = file.read()

    soup = BeautifulSoup(page_content, 'html.parser')

    name_listings = []
    price_listings = []
    area_listings = []
    location_listings = []

    name_elements = soup.find_all('h3', class_='o-announ-card-title')
    price_elements = soup.find_all('div', class_='d-flex flex-wrap flex-gap-1 align-center mb-1')
    area_elements = soup.find_all('div', class_='col py-0 px-0 my-1')
    location_elements = soup.find_all('div', class_='mb-1 d-flex flex-column flex-gap-1 line-height-1')

    for name_elem in name_elements:
        name_listings.append(name_elem.text.strip())

    for price_elem in price_elements:
        price_text = price_elem.find('div', dir='ltr')
        price_value = price_text.text.strip() if price_text else 'N/A'
        price_unit = price_elem.find('div', class_='')
        price_unit_text = price_unit.text.strip() if price_unit else 'N/A'
        price_listings.append(f"{price_value} {price_unit_text}")

    for area_elem in area_elements:
        area_text = area_elem.find('span')
        area_listings.append(area_text.text.strip() if area_text else 'N/A')

    for location_elem in location_elements:
        location_spans = location_elem.find_all('span')
        location = location_spans[0].text.strip() if location_spans else 'N/A'
        location_listings.append(location)




    data = [{'Name': name, 'Price': price, 'Area': area, 'Location': location} 
            for name, price, area, location in zip(name_listings, price_listings, area_listings, location_listings)]

    try:
        existing_df = pd.read_csv('ouedkniss_housing.csv')
        existing_data = existing_df.to_dict(orient='records')
    except FileNotFoundError:
        existing_data = []

    existing_data_set = set((d['Name'], d['Price'], d['Area'], d['Location']) for d in existing_data)

    new_data = [d for d in data if (d['Name'], d['Price'], d['Area'], d['Location']) not in existing_data_set]

    if new_data:
        new_df = pd.DataFrame(new_data)
        new_df.to_csv('ouedkniss_housing.csv', mode='a', header=False, index=False)
        print(f'{len(new_data)} new listings have been added to ouedkniss_housing.csv')
    else:
        print('No new data to save.')

for _ in range(50):  
    scrape_data()  

    print('Completed a scrape cycle.')
    time.sleep(1)  
