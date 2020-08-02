import scrap as sc
from bs4 import BeautifulSoup
import time
from tqdm.auto import tqdm
import re
import sys
import pickle


def get_links(html):
    """Returns only links from passed html"""
    links = set()
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        links.add(link.get('href'))
    return links


def get_parts(set_of_urls, regex, limits):
    """Splits finds all urls matching regex and than returns parts of url defined by limits, the idea is to use the return value to generate links
    e.g.
    urls:
            {https://sjp.pwn.pl/sjp/obmowic-sie;2491744.html,
            https://sjp.pwn.pl/sjp/obowiazywac;2491817.html}
    regex:
            'https:\/\/sjp\.pwn\.pl\/sjp\/[a-zA-Z \-zżźćńółęąśŻŹĆĄŚĘŁÓŃ]*;\d*\.html'
    limits:
            [29,-5]

    will return set consisting of: 
    {obmowic-sie;2491744,obowiazywac;2491817}

    this can be used for generator to save memory in case of large amount of urls, in other words returns set containing difference between urls  
    https://sjp.pwn.pl/sjp/ {generated value } .html 
    """
    pattern = re.compile(regex)
    parts = {limit[limits[0]:limits[1]]
             for limit in filter(pattern.match, set_of_urls)}
    return parts


def generate_limits(parts):
    """Generates missing pairs
    e.g.
            A;49
    will return set:
            A 1
            A 2
            .
            .
            .
            A 49
    """
    limits = list()
    parts = [part.split(';') for part in parts]
    parts = [(part[0], (int(part[1]))) for part in parts]
    for part in parts:
        for limit in range(1, part[1]+1):
            limits.append([part[0], limit])
    return limits


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


if __name__ == '__main__':
    start_time = time.time()
    words = []
    definitions = []
    chunk_size = 1000
    alphabet = ['A', 'Ą', 'B', 'C', 'Ć', 'D', 'E', 'Ę', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'Ł',
                'M', 'N', 'Ń', 'O', 'Ó', 'P', 'Q', 'R', 'S', 'Ś', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'Ź', 'Ż']
    sites = [f'https://sjp.pwn.pl/sjp/lista/{letter}.html' for letter in alphabet]
    htmls = list
    start_time = time.time()

    # gets all the pages that starts with letter
    with sc.Scraper(sites) as crap:
        sites = set()
        htmls = crap.html_list
        for html in htmls:
            site = get_links(html)
            for address in site:
                sites.add(address)
        parts = get_parts(
            sites, 'https:\/\/sjp\.pwn\.pl\/sjp\/lista\/[A-ZzżźćńółęąśŻŹĆĄŚĘŁÓŃ];\d{2,3}.html', [29, -5])
        limits = generate_limits(parts)
        sites = [f'https://sjp.pwn.pl/sjp/lista/{limit[0]};{limit[1]}.html' for limit in limits]

    # gets links to every letter
    with sc.Scraper(sites) as crap:
        sites = set()
        htmls = crap.html_list
        for html in htmls:
            site = get_links(html)
            for address in site:
                sites.add(address)
        regex = re.compile(
            'https:\/\/sjp\.pwn\.pl\/sjp\/[a-zA-Z \-zżźćńółęąśŻŹĆĄŚĘŁÓŃ]*;\d*\.html')
        sites = set(filter(regex.match, sites))
    lista = chunks(list(sites), chunk_size)

    # downloads the words
    for lis in tqdm(lista, desc='Overall progress'):
        with sc.Scraper(lis) as crap:
            attribute_errors = 0
            var = None
            for html in tqdm(crap.html_list, desc='Processing htmls'):
                try:
                    soup = BeautifulSoup(html, 'html.parser')
                    data = soup.find(
                        "div", {"class": "ribbon-element type-187126"})
                    pattern_word = '(?<=\>)(.*?)(?=\<)'
                    patternregex = re.compile(pattern_word)
                    word = patternregex.search(str(data)).group(0)
                    definition = re.sub('<.*?>', '', str(data))
                    patternregex = re.compile('(?<=\«)(.*?)(?=\»)')
                    definition = patternregex.search(definition).group(0)
                    if word != None and definition != None:
                        words.append(word)
                        definitions.append(definition)
                except AttributeError:
                    attribute_errors += 1
                except Exception as e:
                    print(e)
            print(f'Caught {attribute_errors} words that do not match the criteria')
        entry = zip(words, definitions)

    with open("entries.pkl", "wb+") as f:
        pickle.dump(entry, f)
    print("--- %s seconds ---" % (time.time() - start_time))
