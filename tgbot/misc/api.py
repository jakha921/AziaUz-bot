import json
import requests
from pprint import pprint
from requests.structures import CaseInsensitiveDict


urls = {
    'verify-number': 'https://asia-uz.herokuapp.com/customers/verify-number',
    'verify-code': 'https://asia-uz.herokuapp.com/customers/verify-code',
    'news': 'https://asia-uz.herokuapp.com/news',
    'cards': 'https://asia-uz.herokuapp.com/loyalty/cards',
    'feedbacks': 'https://asia-uz.herokuapp.com/feedbacks',
    'customers': 'https://asia-uz.herokuapp.com/customers'
}


def auth_token(token: str):
    """Create correct token form for auth"""
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["Authorization"] = "Bearer " + token
    return headers


def contact_verify(number):
    """Verify contact & get token"""
    res_numb = requests.post(urls['verify-number'], data={"number": f'{number}'})
    if res_numb.status_code == 200:
        msg = True
    else:
        msg = False
    return msg


def confirm_contact(number: str, code: str):
    """Get confirmation of contact number"""
    customer_code = {"number": number, "code": code}
    res_code = requests.post(urls['verify-code'], customer_code)
    try:
        verify = json.loads(res_code.text)
        print(f'{number} is verify')
    except:
        verify = "Error is verified"
    return verify


def parse_news(token: str):
    """Get last 3 news"""
    try:
        headers = auth_token(token)
        res = requests.get(urls['news'], headers=headers)
        data = json.loads(res.text)

        last_news = {}
        for count, i in enumerate(data[:3]):
            last_news[count] = {'type': i['type'],
                                'title': i['title'],
                                'description': i['description'],
                                'image': i['image'],
                                # 'createdAt': i['createdAt'],
                                # 'updatedAt': i['updatedAt'],
                                }
    except:
        print('error on parsing news')
    return last_news


def loyal_cards(token: str):
    """Get card number, total balance & etc"""
    try:
        headers = auth_token(token)
        res = requests.get(urls['cards'], headers=headers)
        data = json.loads(res.text)
        card = {
            'total_balance': data[0]['total_balance'],
            'card_encrypted': int(data[0]['card_encrypted']) % 10000,
            'is_physical': data[0]['is_physical'],
        }
    except:
        card = {}
        print('error on loyal cards')
    return card


def post_feedbacks(token: str, msg: str, type='feedback', platform='Telegram'):
    """Send msg from user to db by api"""
    headers = auth_token(token)
    data = {
        "type": type,
        "message": msg,
        "platform": platform
    }
    res = requests.post(urls['feedbacks'], headers=headers, data=data)
    return res.text


def post_user_details(token: str, info: dict):
    """get from user info and send to api"""
    headers = auth_token(token)
    res = requests.post(urls['customers'], headers=headers, data=info)
    return res.text



def test(token):
    for numb, char in enumerate(token):
        return numb, char

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtb2JpbGVfcGhvbmUiOiIrOTk4OTAwMDEwMTAxIiwic3ViIjoiNjI3ZGUwZTVmNWE5ZWVmMGY5ZWJhMmJlIiwiaWF0IjoxNjU4ODM5MjcwfQ.ftvBFFqaLQaseOgb282CxY1v9hS-zYKt48faYRBxw-g'
# token_card = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtb2JpbGVfcGhvbmUiOiIrOTk4OTg0NjA1Njg2Iiwic3ViIjoiNjJkYjk3MGE0M2VhOTA3MzBhODFkYjE5IiwiaWF0IjoxNjU4OTMyMTYzfQ.mCHuBAYUC2XLT8WHh5Yq8N0OZopB6-l--cF_5N6HSv8'


if __name__ == '__main__':
    # pprint(contact_verify('+998913339636'))
    # pprint(confirm_contact('+998913339636', '9876'))
    # pprint(parse_news(token))
    # pprint(loyal_cards(token_card))
    # print(post_feedbacks(token, 'jakha'))
    # print(post_user_details(token_card, data))
    pprint(test(token))
