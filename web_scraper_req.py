#!/home/mikoaj/anaconda3/envs/pyton38/bin/python 

from bs4 import BeautifulSoup
from urllib.request import urlopen as ureq
import re
import pandas as pd
import progressbar

def get_links():
	print("================================ Getting links ================================")
	# wydobywanie informacji z konkretnego pola html soup.find()
	result = soup.find(
		"div", {"class": "col-sm-12 col-md-6 col-lg-7 search-content"})
	tab = []
	# filtrowanie html aby wydobyc odpowiednie linki
	for link in result.findAll('a', attrs={'href': re.compile("^https://sjp.pwn.pl/sjp/")}):
		filter = re.search('lista', link.get('href'))
		if not filter:
			tab.append(link.get('href'))
	return tab


def get_limit(letter):
	print("================================ Getting limit ================================")
	result = soup.find(
		"div", {"class": "col-sm-12 col-md-6 col-lg-7 search-content"})
	number = 0
	for link in result.findAll('a', attrs={'href': re.compile("^https://sjp.pwn.pl/sjp/lista/"+letter)}):
		filter = re.search('\d+', link.get('href'))
		if filter:
			# regex \d+ zwraca cyfry w liście które wystąpiły w stringu conajmniej raz
			digits = int(re.findall(r'\d+', link.get('href'))[0])
			if number < digits:
				number = digits
	print(number, "pages detected for letter", letter)
	return number


def get_word(link, words, definitions):
	try:
		uClient = ureq(link)
		html = uClient.read()
		uClient.close()
		soup = BeautifulSoup(html, 'html.parser')
		data = soup.find("div", {"class": "ribbon-element type-187126"})
		pattern_word = '(?<=\>)(.*?)(?=\<)'
		patternregex = re.compile(pattern_word)
		word = patternregex.search(str(data)).group(0)
		definition = re.sub('<.*?>', '', str(data))
		patternregex= re.compile('(?<=\«)(.*?)(?=\»)')
		definition=patternregex.search(definition).group(0)
		words.append(word)
		definitions.append(definition[len(word)+1:])
	except Exception as e:
		print(e)


def save_as_csv(words,definitions):
	print("================================ Saving DataFrame ================================")
	name_dict = {
				'word': [words],
				'definition': [definitions]
			  }
	df = pd.DataFrame(data=name_dict)
	df.to_csv('data.csv')
	words=[]
	definitions=[]


alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L',
			'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
words = []  # List to store words
definitions = []  # List to store definitions of words above
linki = []
htmls = []
print('Starting webscraper')
try:
	with progressbar.ProgressBar(max_value=len(alphabet)) as bar:
		j=0
		for letter in alphabet:
			j+=1
			bar.update()
			pwnurl = 'https://sjp.pwn.pl/sjp/lista/'+letter+'.html'
			uClient = ureq(pwnurl)
			html = uClient.read()
			uClient.close()
			soup = BeautifulSoup(html, 'html.parser')
			limit = get_limit(letter)
			with progressbar.ProgressBar(max_value=limit) as bar2:
				for page in range(limit):
					bar2.update(page)
					if page != 0:
						pwnurl = 'https://sjp.pwn.pl/sjp/lista/'+letter+';'+str(page)+'.html'
						uClient = ureq(pwnurl)
						html = uClient.read()
						uClient.close()
						soup = BeautifulSoup(html, 'html.parser')
						linki = get_links()
						with progressbar.ProgressBar(max_value=len(linki)) as bar3:
							print('======================== Downloading words from page',page,'========================')
							i=0
							for link in linki:
								bar3.update(i)
								i+=1
								get_word(link, words, definitions)
							bar3.finish()
						save_as_csv(words,definitions)
				bar2.finish()
except Exception as e:
	raise(e)
except KeyboardInterrupt:
	print(letter,page,link)
finally:
	for pair in zip(words, definitions):
		print(pair)