import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd

# Set up the WebDriver using WebDriver Manager
service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Define the URL of the page to scrape
url = 'https://www.ouedkniss.com/immobilier/1'

# Load the page with Selenium
driver.get(url)

# Use explicit wait to wait for the listings to load
try:
    # Wait for the specific element to be present
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'v-card'))
    )
except Exception as e:
    print(f"An error occurred: {e}")
    driver.quit()

# Parse the loaded content with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Print the page source for debugging
print(soup.prettify())

# Find the elements containing the data you want to scrape
listings = soup.find_all('div', class_='v-card o-announ-card')

print(f"Number of listings found: {len(listings)}")  # Debugging print

data = []

for listing in listings:
    try:
        # Extract the name
        name = listing.find('h3', class_='o-announ-card-title').text.strip()
        
        # Extract the price
        price_divs = listing.find('span', class_='price').find_all('div')
        price = " ".join([div.text.strip() for div in price_divs])
        
        # Extract the area
        area = listing.find('span', class_='v-chip').text.strip()
        
        # Extract the location
        location = listing.find('div', class_='mb-1 d-flex flex-column flex-gap-1 line-height-1').find('span').text.strip()
        
        data.append({'Name': name, 'Price': price, 'Area': area, 'Location': location})
    except AttributeError as e:
        print(f"Error processing a listing: {e}")

# for item in data:
#     print(item)

df = pd.DataFrame(data)
df.to_csv('ouedkniss_housing.csv', index=False)
print('Data has been scraped and saved to ouedkniss_housing.csv')

# Close the browser
driver.quit()
