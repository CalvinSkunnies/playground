import requests
import csv

API_KEY = '002a0b3be23cd822f63f8b8d72278ea8bc7e5873046e1b0a141cebb7e73a'
BASE_URL = 'https://api.cryptorank.io/v2/currencies/publicsales'

HEADERS = {
    'Authorization': f'Bearer {API_KEY}'
}

def fetch_data(category):
    all_projects = []
    page = 1
    while True:
        params = {'limit': 100, 'page': page}
        response = requests.get(f"{BASE_URL}/{category}", headers=HEADERS, params=params)
        data = response.json()

        if not data.get('data'):
            break

        all_projects.extend(data['data'])

        if len(data['data']) < 100:
            break
        page += 1
    return all_projects

def save_to_csv(data, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        header = ['name', 'ticker', 'category', 'startDate', 'endDate', 'platform', 'raise']
        writer.writerow(header)
        for item in data:
            writer.writerow([
                item.get('name'),
                item.get('token', {}).get('symbol', ''),
                item.get('category'),
                item.get('startDate'),
                item.get('endDate'),
                item.get('platform', {}).get('name', ''),
                item.get('raise', {}).get('total', {}).get('USD', '')
            ])

# Fetch all three categories
upcoming = fetch_data('upcoming')
ongoing = fetch_data('ongoing')
ended = fetch_data('ended')

# Combine and save
all_data = upcoming + ongoing + ended
save_to_csv(all_data, 'cryptorank_ico_data.csv')
