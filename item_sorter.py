import csv
import re
from html.parser import HTMLParser
from pprint import pprint
import urllib.request

import requests
from bs4 import BeautifulSoup

phrase = r'class="sprite item-sprite"'
href = r'href='
title = r'title='


def get_page(page) -> str:
    fp = urllib.request.urlopen('https://minecraft.gamepedia.com' + page)
    m_bytes = fp.read()
    body = m_bytes.decode('utf8')
    fp.close()
    return body


class Item:
    def __init__(self, title, stackable=None, stacks=None, renewable=None, fuel=None, smeltable=None, compostable=None):
        self.title = title
        self.stackable = stackable
        try:
            self.stacks = int(stacks)
        except TypeError:
            self.stacks = None
        self.renewable = renewable
        self.fuel = fuel
        self.smeltable = smeltable
        self.compostable = compostable

    def __repr__(self):
        return self.title


def get_item(title, link):
    page = get_page(link)
    soup = BeautifulSoup(page, 'html.parser')

    try:
        stackable_str = soup.table.find('th', text=re.compile('Stackable')).parent.p.get_text()
        stackable = boolean_with_versioning(stackable_str)
        if stackable:
            p1 = stackable_str.index('(')
            p2 = stackable_str.index(')')
            stacks = int(stackable_str[p1 + 1: p2])
        else:
            stacks = None
    except AttributeError:
        stackable = None
        stacks = None

    try:
        renewable_text = soup.table.find('a', text='Renewable').parent.parent.p.get_text()
        renewable = boolean_with_versioning(renewable_text)
    except (TypeError, AttributeError):
        renewable = None

    fuel = bool(soup.find(True, text='Fuel'))
    smeltable = bool(soup.find(True, text='Smelting ingredient'))
    compostable = bool(soup.find(True, text='Composting'))

    return Item(title, stackable, stacks, renewable, fuel, smeltable, compostable)


def get_items():
    body = get_page('/Item')
    soup = BeautifulSoup(body, 'html.parser')
    results = []
    for span in soup.find_all('span', 'item-sprite'):
        a = span.parent.a
        print(a.get_text())
        results.append(get_item(a.get_text(), a['href']))

    return results


def boolean_with_versioning(value_str):
    if 'JE' in value_str:
        # I'm grossly assuming here that the JE version will always be the first value in the second half
        return 'Yes' in value_str[len(value_str) // 2:]
    else:
        return 'Yes' in value_str


def get_blocks():
    html = get_page('/Blocks')
    soup = BeautifulSoup(html, 'html.parser')
    cells = soup.table.find_all('td')

    results = []
    for cell in cells:
        all_a = cell.find_all('a')
        try:
            a = all_a[1]
        except IndexError:
            a = all_a[0]
        block_title = a.string
        block_link = a['href']

        print(block_title)

        results.append(get_item(block_title, block_link))

    return results


def get_results_from_file():
    with open('items.csv', newline='') as csv_file:
        reader = csv.reader(csv_file)
        # Skip header line
        next(reader)
        return [Item(*result) for result in reader]


def save_to_file(items):
    table = [list(item.__dict__.values()) for item in items]
    pprint(table)
    with open('items.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        # Header for convenience
        writer.writerow(list(items[0].__dict__.keys()))
        for row in table:
            writer.writerow(row)


if __name__ == '__main__':
    try:
        results = get_results_from_file()
    except FileNotFoundError:
        results = get_blocks() + get_items()
        save_to_file(results)

    print()
    print(f'All items: {len(results)}')
    print(f'Renewable: {len(list(filter(lambda item: item.renewable, results)))}')
    non_renewables = list(filter(lambda item: not item.renewable, results))
    print(f'Non-renewable: {len(non_renewables)}')
    print(non_renewables)
    print(f'Stackable: {len(list(filter(lambda item: item.stackable, results)))}')
    print(f'Non-stackable: {len(list(filter(lambda item: not item.stackable, results)))}')
    print('16 stacking items:')
    print(f'Total: {len(list(filter(lambda item: item.stacks == 16, results)))}')
    print(f'Renewable: {len(list(filter(lambda item: item.stacks == 16 and item.renewable, results)))}')
    print(f'Non-renewable: {len(list(filter(lambda item: item.stacks == 16 and not item.renewable, results)))}')
    print('64 stacking items:')
    print(f'Total: {len(list(filter(lambda item: item.stacks == 64, results)))}')
    print(f'Renewable: {len(list(filter(lambda item: item.stacks == 64 and item.renewable, results)))}')
    print(f'Non-renewable: {len(list(filter(lambda item: item.stacks == 64 and not item.renewable, results)))}')
