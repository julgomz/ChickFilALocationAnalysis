import re
import pandas as pd
import requests
import openpyxl
from bs4 import BeautifulSoup


def is_phone_number(text):
    trimmed_text = text.strip()
    pattern = re.compile(r'\(\d{3}\)\s*\d{3}-\d{4}')
    return pattern.match(text) is not None


def extract_zip_code(address):
    pattern = re.compile(r'\b\d{5}(?:-\d{4})?$')
    match = pattern.search(address)
    if match:
        return match.group()
    return None


base_url = 'http://www.chick-fil-a.com'
main_url = f"{base_url}/locations/browse"
response = requests.get(main_url)
soup = BeautifulSoup(response.text, 'html.parser')

state_links = []
state_links = soup.find_all('a', href=lambda href: href and 'locations/browse/' in href)

# Usage to confirm existence of all Territories.
print(state_links)
# Usage to confirm 48 states including Washington DC with chick fil a presence. (None in Hawaii, Alaska, or Vermont)
print(f"{len(state_links)} Territories Confirmed On Website")

location_count = 0
locations_data = []
for state_link in state_links:
    state_href = state_link['href']
    state_name = state_link.getText()
    full_url = f'{base_url}{state_href}'  # construction of full URL for state page.
    # print(full_url) URL TESTING

    # request the state specific page
    state_response = requests.get(full_url)
    state_soup = BeautifulSoup(state_response.text, 'html.parser')

    locations = state_soup.find_all('div', class_='location')
    for location in locations:
        location_name = location.find('h2').get_text(strip=True)
        location_details = location.find('p').get_text(separator='\n', strip=True).split('\n')

        if is_phone_number(location_details[-1]):
            phone = location_details.pop(-1)
        else:
            phone = 'N/A'

        address = ', '.join(location_details)

        zip_code = extract_zip_code(address)

        print(f"Location: {location_name}, Address: {address}, zip_code: {zip_code}, Phone: {phone}")
        locations_data.append({"Location Name": location_name, "Zip Code": zip_code})
        location_count += 1

df = pd.DataFrame(locations_data)
df.to_excel("chick_fil_a_locations.xlsx", index=False)

print(f"{location_count} Locations Confirmed") # Original Result of 3057 locations across 48 Territories (47 States + Washington DC)
'''Chick-fil-A claims 3059 locations Across all US Territories, but I will be disregarding Puerto Rico and only focusing on mainland USA'''
