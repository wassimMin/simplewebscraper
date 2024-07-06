from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time

# Initialize the WebDriver with WebDriver Manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

url = 'https://www.ouedkniss.com/immobilier-location-appartement/1'
driver.get(url)

# Allow time for the JavaScript to load
time.sleep(10)

# Scroll and load all listings
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to the bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(10)  # Wait for new content to load

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

soup = BeautifulSoup(driver.page_source, 'html.parser')

data = []
for listing in soup.find_all('div', class_='mx-2'):
    try:
        title = listing.find('h3', class_='o-announ-card-title').text.strip()
        
        # Extract price
        price_elem = listing.find('span', class_='price').find('span', class_='d-inline-flex')
        price_value = price_elem.find('div', dir='ltr').text.strip() if price_elem.find('div', dir='ltr') else 'N/A'
        price_unit = price_elem.find('div', class_='').text.strip() if price_elem.find('div', class_='') else 'N/A'
        price_info = f"{price_value} {price_unit}"
        
        # Extract size
        size_info = listing.find('div', class_='col py-0 px-0 my-1').find('span', class_='v-chip').text.strip()
        
        # Extract location
        location_info = listing.find('div', class_='mb-1 d-flex flex-column flex-gap-1 line-height-1').find('span').text.strip()
        
        data.append({
            'Title': title,
            'Price': price_info,
            'Size': size_info,
            'Location': location_info
        })
    except Exception as e:
        print(f"Error extracting listing: {e}")

driver.quit()

# Create DataFrame and save to CSV
df = pd.DataFrame(data)
df.to_csv('ouedkniss_apartments.csv', index=False)
print(df.head())
