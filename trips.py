import re
import time

import requests
from bs4 import BeautifulSoup

from utils import (HEADERS, add_to_cache, cache_hit, load_cache, load_env,
                   notify)


def fetch_trips():
    BASE_URL = 'https://gdscatalogueur.ccas.fr'

    response = requests.get(f'{BASE_URL}/search?typesej[]=rouge', headers=HEADERS, timeout=60)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')

    trips = soup.find_all('article')

    for trip in trips:
        id = trip.find('strong').get_text(strip=True) # Located before the <strong> for the dates

        # Check if trip is cached
        if cache_hit(id):
            continue

        title = trip.find('h2').get_text(strip=True).split(' ')[0]
        link = f"{BASE_URL}{trip.select_one('.offre_sejour')['href']}"

        subtitle = trip.find('h3').get_text(strip=True)
        season = subtitle.split(' ')[0].strip()
        
        description = trip.select_one('.descrip').get_text()
        startdate, enddate = re.findall(r'(\d{2}/\d{2}/\d{4})', description)

        time.sleep(4) # Sleep before getting trip details to prevent spam
        trip_detail = requests.get(link, headers=HEADERS, timeout=60).text
        is_full = bool(re.search(r'complet', trip_detail))
        reference_price = re.search(r'([\d|\s?]+€)', trip_detail).group()

        if not is_full:
            notify(
                f'*{title}*, {startdate} to {enddate} ({season}) \n[Ref]({link}): {reference_price}', '🌍'
            )
        add_to_cache(id)


if __name__ == '__main__':
    load_env(['telegram'])
    load_cache()
    fetch_trips()