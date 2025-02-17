import time
from datetime import date

import requests

from utils import (HEADERS, add_to_cache, cache_hit, get_env, load_cache,
                   load_env, notify, to_karen_readable_date)

def department_match_or_zero(product_features: dict) -> int:
    """
    The dict is of this form: {"product_features": [{"id": string; "id_feature_value": string}]}
    eg: {"product_features": [{id:"200", "id_feature_value":"2114"}, {"id":"300", "id_feature_value":"3057"}, {"id":"305","id_feature_value":"3682"}...]
    -- Department feature id is "300"
    """
    expected_values = set(get_env('department_features', {}).keys())

    product_attribute = next((feature['id_feature_value'] for feature in product_features if feature['id'] == '300'), None)
    if not product_attribute:
        return False

    product_attribute = int(product_attribute)
    return get_env('department_features', {}).get(product_attribute) if product_attribute in expected_values else 0


def fetch_products():
    BASE_URL = 'https://portail-culture-et-loisirs.ccas.fr/api/products'
    TODAY = date.today().isoformat()
    LIMIT = 50
    OFFSET = 0

    while True:
        print(f'[{OFFSET}..{OFFSET+LIMIT}] Fetching products')
        params = {
            'display': 'full', # Looking for [id,base_name,manufacturer_name,representation_date], but `associations` is only displayed in 'full' 
            'output_format': 'JSON',
            'filter[representation_date]': f'>[{TODAY}]',
            'limit': f'{OFFSET},{LIMIT}'
        }

        response = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=60)
        response.raise_for_status()
        data = response.json()

        if 'products' not in data: # No more products returned, meaning an empty []
            break

        for product in data['products']:
            department = department_match_or_zero(product.get('associations', {}).get('product_features', {}))
            if not department:
                continue

            product_id = str(product.get('id'))
            if cache_hit(product_id):
                continue

            what = product.get('base_name')
            location = product.get('manufacturer_name')
            day, _ = product.get('representation_date').split(' ')
            link = f"https://portail-culture-et-loisirs.ccas.fr/spectacles/{product_id}-{product.get('link_rewrite')}.html"

            notify(
                f'*({department})* [{what}]({link}), {location}, on {to_karen_readable_date(day)}', '🎫'
            )
            add_to_cache(product_id)

        OFFSET += LIMIT
        time.sleep(10)

if __name__ == '__main__':
    load_env(['telegram', 'department_features'])
    load_cache()
    fetch_products()