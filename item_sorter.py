import mwclient
import pprint
import requests

# site = mwclient.Site('minecraft.gamepedia.com', path='/')
#
# response = site.api('parse',
#                     page='Item',
#                     format='json',
#                     # prop='text'
#                     )
#
# pprint.pprint(response['parse']['text']['*'])

S = requests.Session()

URL = "https://minecraft.gamepedia.com/api.php"

PARAMS = {
    "action": "parse",
    "page": "Item",
    "format": "json"
}

R = S.get(url=URL, params=PARAMS)
DATA = R.json()

body: str = DATA["parse"]["text"]["*"]

phrase = r'class="sprite item-sprite"'
href = r'href='
title = r'title='


def find_quote(span: str, start):
    first_index = span.index('"', start)
    second_index = span.index('"', first_index + 1)
    return span[first_index + 1: second_index]


begin = 0
result = []
phrase_count = 0
while phrase in body[begin:]:
    next_index = body.index(phrase, begin)
    # href_index = body.index(href, next_index)
    # title_index = body.index(title, next_index)
    #
    # href = find_quote(body, href_index)
    # title = find_quote(body, title_index)
    # result.append(title)
    begin = next_index + 1

    phrase_count += 1

print(phrase_count)
print(result)
