import csv
from html.parser import HTMLParser
from pprint import pprint

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
    def __init__(self, title, link, stackable=None, stacks=None, renewable=None):
        self.title = title
        self.link = link
        print(self.title + ':' + self.link)
        self.stackable = stackable
        try:
            self.stacks = int(stacks)
        except ValueError:
            self.stacks = None
        self.renewable = renewable
        if self.stackable is None or self.renewable is None:
            try:
                self.page = get_page(self.link[1:].replace('%27', "'"))
                stackable_index = self.page.index('Stackable')
                stackable_str = find_element(self.page, 'p', stackable_index)[:-1]
                self.stackable = 'Yes' in stackable_str
                if self.stackable:
                    p1 = stackable_str.index('(')
                    p2 = stackable_str.index(')')
                    self.stacks = int(stackable_str[p1 + 1: p2])
                else:
                    self.stacks = None
                self.stackable = None
                self.stacks = None
                renewable_index = self.page.index('Renewable')
                renewable_str = find_element(self.page, 'p', renewable_index)[:-1]
                self.renewable = 'Yes' in renewable_str
            except (KeyError, ValueError) as e:
                print(e)

    def __repr__(self):
        return self.title


def get_results_from_wiki():
    global results
    body = get_page('Item')
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

    return results


def get_results_from_file():
    results = []

    with open('items.csv', newline='') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)
        for result in reader:
            results.append(Item(result[0], result[1], result[2], result[3], result[4]))

    return results


def save_to_file():
    table = [[item.title, item.link, item.stackable, item.stacks, item.renewable] for item in results]
    pprint(table)
    with open('items.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['title', 'link', 'stackable', 'stacks', 'renewable'])
        for row in table:
            writer.writerow(row)


if __name__ == '__main__':
    results = get_results_from_file()
    # if not results:
    #     results = get_results_from_wiki()
    #     save_to_file()

    print(f'Total items: {len(results)}')
    print('16 stacking items:')
    print(f'Total: {len(list(filter(lambda item: item.stacks == 16, results)))}')
    print(f'Renewable: {len(list(filter(lambda item: item.stacks == 16 and item.renewable, results)))}')
    print(f'Non-renewable: {len(list(filter(lambda item: item.stacks == 16 and not item.renewable, results)))}')
    print('64 stacking items:')
    print(f'Total: {len(list(filter(lambda item: item.stacks == 64, results)))}')
    print(f'Renewable: {len(list(filter(lambda item: item.stacks == 64 and item.renewable, results)))}')
    print(f'Non-renewable: {len(list(filter(lambda item: item.stacks == 64 and not item.renewable, results)))}')
