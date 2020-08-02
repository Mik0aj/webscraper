import scrap as sc
import concurrent.futures
from bs4 import BeautifulSoup
import time
from tqdm.auto import tqdm
import re
import sys
import pickle


def get_links(html_list):
	links = set()
	soup = BeautifulSoup(html, 'html.parser')
	for link in soup.find_all('a'):
		links.add(link.get('href'))
	return links

def get_parts(set_of_urls,regex,limits):
	pattern = re.compile(regex)
	parts= {limit[limits[0]:limits[1]] for limit in filter(pattern.match, set_of_urls)}
	return parts

def get_limits(parts):
	limits=list()
	parts= [part.split(';') for part in parts]
	parts=[(part[0],(int(part[1]))) for part in parts]
	for part in parts:
		for limit in range(1,part[1]+1):
			limits.append([part[0],limit])
	return limits

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

alphabet=['A','Ą','B', 'C', 'Ć', 'D', 'E', 'Ę', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'Ł', 'M', 'N', 'Ń', 'O', 'Ó', 'P', 'Q', 'R', 'S', 'Ś', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'Ź', 'Ż']
sites=[f'https://sjp.pwn.pl/sjp/lista/{letter}.html' for letter in alphabet]
htmls=list
start_time = time.time()
with sc.Scraper(sites) as crap:
	sites=set()
	htmls=crap.html_list
	for html in htmls:
		site=get_links(html)
		for address in site:
			sites.add(address)
	print("getting parts")
	parts=get_parts(sites,'https:\/\/sjp\.pwn\.pl\/sjp\/lista\/[A-ZzżźćńółęąśŻŹĆĄŚĘŁÓŃ];\d{2,3}.html',[29,-5])
	print("generating limits")
	limits=get_limits(parts)
	sites=[f'https://sjp.pwn.pl/sjp/lista/{limit[0]};{limit[1]}.html' for limit in limits]

with sc.Scraper(sites) as crap:
	sites=set()
	htmls=crap.html_list
	for html in htmls:
		site=get_links(html)
		for address in site:
			sites.add(address)
	regex=re.compile('https:\/\/sjp\.pwn\.pl\/sjp\/[a-zA-Z \-zżźćńółęąśŻŹĆĄŚĘŁÓŃ]*;\d*\.html')
	sites=set(filter(regex.match,sites))
words=[]
definitions=[]
start_time = time.time()

lista=chunks(list(sites),1000)
for lis in lista:
	with sc.Scraper(lis) as crap:
		for html in tqdm(crap.html_list):
			try:
				soup = BeautifulSoup(html, 'html.parser')
				data = soup.find("div", {"class": "ribbon-element type-187126"})
				pattern_word = '(?<=\>)(.*?)(?=\<)'
				patternregex = re.compile(pattern_word)
				word = patternregex.search(str(data)).group(0)
				definition = re.sub('<.*?>', '', str(data))
				patternregex= re.compile('(?<=\«)(.*?)(?=\»)')
				definition=patternregex.search(definition).group(0)
				if word != None and definition != None:
					words.append(word)
					definitions.append(definition)
			except Exception as e:
				print(e,word,definition)
	entry = zip(words,definitions)
print("--- %s seconds ---" % (time.time() - start_time))

with open("entries.pkl", "wb+") as f:
	pickle.dump(entry, f)

 