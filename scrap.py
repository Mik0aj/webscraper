import asyncio
import aiohttp
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

class Scraper:
	def __init__(self,link_list):
		self.link_list=link_list
		self.html_list=list()

	async def download_site(self,session, url):
		try:
			async with session.get(url) as response:
				self.html_list.append(await response.text())
		except Exception as e:
			print(e)

	async def download_all_sites(self):
		async with aiohttp.ClientSession() as session:
			tasks =[]
			for url in tqdm(self.link_list):
				task = asyncio.ensure_future(self.download_site(session, url))
				tasks.append(task)
			await asyncio.gather(*tasks, return_exceptions=True)

	def get_links(self):
		links=set()
		for html in tqdm(self.html_list):
			soup = BeautifulSoup(html, 'html.parser')
			for link in soup.find_all('a'):
				links.add(link.get('href'))
		return links

	def main(self):
		asyncio.get_event_loop().run_until_complete(self.download_all_sites())

