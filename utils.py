from datetime import datetime
from pathlib import Path

import requests
import yaml

PRODUCTS_FILE = Path(__file__).with_name('.cache')
PRODUCTS_CACHE = set()
ENV_FILE = Path(__file__).with_name('env.yaml')
ENV = set()

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
}


# Utility Functions
def notify(text: str, emoji: str):
    token = get_env('telegram').get('token')
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {
            'text': f'{emoji} {text}',
            'chat_id': get_env('telegram').get('chatID'),
            'parse_mode': 'markdown',
            'disable_web_page_preview': True,
        }
    requests.post(url, json=data)


def load_env(required_keys: list):
    global ENV
    if not ENV_FILE.exists():
        raise FileNotFoundError('Missing env.yaml file')

    with open(ENV_FILE, 'r', encoding='utf-8') as f:
        ENV = yaml.safe_load(f) or {}

    if not all(key in ENV for key in required_keys):
        raise KeyError(f'Missing one of the following keys : {required_keys}')


def get_env(key: str, default=None):
    return ENV.get(key, default)


def to_karen_readable_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d/%m/%Y')

# Cache Functions
def load_cache():
    global PRODUCTS_CACHE
    if PRODUCTS_FILE.exists():
        with open(PRODUCTS_FILE, 'r') as cache:
            PRODUCTS_CACHE = {line.strip() for line in cache}


def update_cache():
    with open(PRODUCTS_FILE, 'w') as cache:
        if PRODUCTS_CACHE:
            cache.write('\n'.join(PRODUCTS_CACHE))


def cache_hit(product: str) -> bool:
    return product in PRODUCTS_CACHE


def add_to_cache(product: str):
    PRODUCTS_CACHE.add(product)
    update_cache()


def del_from_cache(product: str):
    PRODUCTS_CACHE.discard(product)
    update_cache()