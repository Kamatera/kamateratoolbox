import os

SERVER_BASE_URL = os.environ.get('KAMATERA_API_SERVER_BASE_URL', 'https://console.kamatera.com')
KAMATERA_API_DEBUG = os.environ.get('KAMATERA_API_DEBUG') == 'yes'
