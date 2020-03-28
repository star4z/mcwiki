import urllib.request

from bs4 import BeautifulSoup


def read_from_site():
    fp = urllib.request.urlopen('https://minecraftitemids.com/')
    mybytes = fp.read()
    mystr = mybytes.decode('utf8')
    fp.close()

    # with open('mcitem0.html', 'w') as f:
    #     f.write(mystr)

    return mystr


def read_from_file():
    html = ''
    with open('mcitem0.html') as f:
        for line in f:
            html += line

    return html


class Item:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


if __name__ == '__main__':
    html = read_from_site()

    soup = BeautifulSoup(html, features='html.parser')
    rows = soup.find_all('tr', 'tsr')
    items = []
    for row in rows:
        item_name = row.find_all('td')[1].string
        item_link = row.a['href']
        items.append(Item(item_name))

    print(items)
    print(len(items))
