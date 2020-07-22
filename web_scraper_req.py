from bs4 import BeautifulSoup
from urllib.request import urlopen as ureq 
import re
import csv  

#firefox sie nie wylłącza przez co zajmuje niepotrzebnie pamięć ram, w skrajnym wypadku zajmuje całą i zawiesza komputer
#trzeba najlepiej dodać funkję main a w niej try exept finnaly gdzie finally będzie wyłączeniem firefoxa
#skrypt działa dość wolno najdłużej zajmuje metoda get_word
#wydaje mi sie że jest to spowodowane "klikaniem" w link i dopiero przechodzeniem na strone
#możnaby to załatwić inaczej pobrać wszystkie linki i dopiero użyć get_word
# selenium okazał sie modułem do pisania botów a nie webscraperów wiec zmarnowałem tylko czas


def get_links():
	print("====getting links====")
	result = soup.find("div",{"class":"col-sm-12 col-md-6 col-lg-7 search-content"})
	tab=[]
	for link in result.findAll('a', attrs={'href': re.compile("^https://sjp.pwn.pl/sjp/")}):
		filter=re.search('lista',link.get('href'))
		if not filter:	
		    tab.append(link.get('href'))
	return tab

def get_limit(letter):
	print("====getting limit====")
	result = soup.find("div",{"class":"col-sm-12 col-md-6 col-lg-7 search-content"})
	number=0
	for link in result.findAll('a', attrs={'href': re.compile("^https://sjp.pwn.pl/sjp/lista/"+letter)}):
		filter=re.search('\d+',link.get('href'))
		if filter:
			#regex \d+ zwraca cyfry w liście które wystąpiły w stringu conajmniej raz	
			digits = int(re.findall(r'\d+', link.get('href'))[0]) 
			if number < digits:
				number=digits
	print(number,"pages detected for letter",letter)
	return number

def get_word(link,words,definitions):
	try:
		uClient=ureq(link)
		html=uClient.read()
		uClient.close()
		soup=BeautifulSoup(html,'html.parser')
		data=soup.find("div",{"class":"ribbon-element type-187126"})
		pattern_word = '>[a-zA-Z0-9 ]+<'
		pattern_clear = '[a-zA-Z0-9 ]+'
		patternregex = re.compile(pattern_word)
		word=patternregex.search(str(data)).group(0)
		patternregex = re.compile(pattern_clear)
		word=patternregex.search(word).group(0)
		if word is not ' ':
			words.append(word)
			definition=re.sub('<.*?>', '', str(data))
			definitions.append(definition[len(word)+1:])
	except Exception as e:
		print("funtcion def_word(), error, propably invalid characters in word")

def save_as_csv(data):
	print('save funtcion')
	#fields=['word','definition']
	file_name='data.csv'
	f=open(file_name,"w")
	f.write(list(data[0]),'	',list(data[1]))
	f.close

alphabet=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z' ]
words=[] #List to store words 
definitions=[] #List to store definitions of words above
linki=[]
htmls=[]
try:
	for letter in alphabet:
		pwnurl='https://sjp.pwn.pl/sjp/lista/'+letter+'.html'
		uClient=ureq(pwnurl)
		html=uClient.read()
		uClient.close()
		soup=BeautifulSoup(html,'html.parser')
		limit=get_limit(letter)
		for page in range(limit): 
			pwnurl='https://sjp.pwn.pl/sjp/lista/'+letter+';'+str(page)+'.html'
			uClient=ureq(pwnurl)
			html=uClient.read()
			uClient.close()
			soup=BeautifulSoup(html,'html.parser')
			linki=get_links()
			for link in linki:
				print(link)
			for link in linki:
				get_word(link,words,definitions)
				save_as_csv(zip(words,definitions))	

except Exception as e:
	raise(e)
finally:
	for pair in zip(words,definitions):
		print(pair)