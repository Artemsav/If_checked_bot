import requests
import pprint
import json
import telegram

url = 'https://dvmn.org/api/long_polling/'
headers = {'Authorization': 'Token a10f022e97faba6a70f03d00e003607761df93bf'}
'''def works_on_review (url, headers):
    r = requests.get(url, headers=headers)
    return r.text'''
payload = {'timestamp_to_request': ''}

if __name__ == '__main__':
    #works_on_review(url, headers)
    #print(works_on_review(url, headers))
    while True:
        try:
                r = requests.get(url, headers=headers, params=payload)
                pprint.pprint(r.text, indent = 4, depth = 4)
                review_status = r.json()
                timestamp_to_request = review_status.get('timestamp_to_request')
                print(timestamp_to_request)
                pprint.pprint(review_status, indent = 4, depth = 4)
                payload = {'timestamp_to_request':timestamp_to_request}
        except ConnectionError:
            pass
        except requests.exceptions.ReadTimeout:
            pass