from html.parser import HTMLParser

import requests

phrase = r'class="sprite item-sprite"'
href = r'href='
title = r'title='


def get_page(page) -> str:
    S = requests.Session()

    URL = "https://minecraft.gamepedia.com/api.php"

    PARAMS = {
        "action": "parse",
        "page": page,
        "format": "json"
    }

    R = S.get(url=URL, params=PARAMS)
    DATA = R.json()

    body = DATA["parse"]["text"]["*"]

    if 'redirectMsg' in body:
        href_index = body.index(href)
        next_href = find_quote(body, href_index)

        return get_page(next_href[1:])

    return body


body = get_page('Item')


def find_element(body, element, start_index):
    opening_tag = f'<{element}>'
    closing_tag = f'</{element}>'

    opening_index = body.index(opening_tag, start_index)
    closing_index = body.index(closing_tag, opening_index + len(opening_tag))

    return body[opening_index + len(opening_tag): closing_index]


def find_quote(span: str, start):
    first_index = span.index('"', start)
    second_index = span.index('"', first_index + 1)
    return span[first_index + 1: second_index]


class MyHTMLParser(HTMLParser):
    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        print("Num ent  :", c)


class Item:
    def __init__(self, title, link):
        self.title = title
        self.link = link
        print(self.title + ':' + self.link)
        try:
            self.page = get_page(self.link[1:].replace('%27', "'"))
            stackable_index = self.page.index('Stackable')
            stackable_str = find_element(self.page, 'p', stackable_index)[:-1]
            self.stackable = 'No' not in stackable_str
        except (KeyError, ValueError) as e:
            # print("Error with " + self.title)
            print(e)
            self.stackable = None

    def __repr__(self):
        return self.title


begin = 0
results = []
while phrase in body[begin:]:
    next_index = body.index(phrase, begin)
    href_index = body.index(href, next_index)
    title_index = body.index(title, next_index)

    next_href = find_quote(body, href_index)
    next_title = find_quote(body, title_index)
    results.append(Item(next_title, next_href))
    begin = next_index + 1

print([result.stackable for result in results])

item0 = results[0]
