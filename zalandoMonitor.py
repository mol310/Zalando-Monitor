import requests
import time
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook
from discord_webhook import DiscordEmbed
import json
import random as r

f = open("proxiesBig.txt","r")
proxies = f.readlines()

class Monitor:
	def __init__(self, url, webhook_url):
		self.url = url
		self.webhook = webhook_url
		self.runBool = True
		self.headers = {
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
		}
		self.sizeStockList = []
		self.firstLoad = True
		self.delay = 1
		self.Title = ""
		self.desc = ""
		self.price = ""
		self.img = ""
		self.released = False
	def sendWebhook(self, sizes, pid):
		#if Stock greater then 10 it might be even 100 (so its just >= 10)

		webhook = DiscordWebhook(url=self.webhook, username="ZALANDO Monitor")
		embed = DiscordEmbed(
					title="_" + self.Title + ': ' + self.desc + "_", description="Restock Detected", color=2815121
				)
		embed.set_author(
					name="EtherealNotify",
					url="https://twitter.com/EtherealNotify",
					icon_url="https://pbs.twimg.com/profile_images/1371907819113418752/5i7Jab6A_400x400.jpg",
				)
		embed.set_timestamp()
				# Set `inline=False` for the embed field to occupy the whole line
		embed.add_embed_field(name="Product Link", value="[Click Here!]"+ "(" + self.url + "?cache=false" + ")", inline=False)
		embed.add_embed_field(name="PID", value=pid, inline=True)
		embed.add_embed_field(name="Price", value=str(self.price), inline=True)
		if( sizes != None):
			embed.add_embed_field(name="Size [Stock]", value=str(sizes[0]) + " ["+ str(sizes[1]) + "]", inline=False)

		embed.set_thumbnail(url=str(self.img))

		webhook.add_embed(embed)
		response = webhook.execute()

	def checkStock(self):

		response = requests.get(self.url,headers=self.headers,proxies={"http":getProxie()})
		status = response.status_code
		content = response.content
		if status == 200:
			soup = BeautifulSoup(content,'html.parser')
			script = json.loads(str(soup.find(id="z-vegas-pdp-props")).replace('<script id="z-vegas-pdp-props" type="application/json"><![CDATA[',"").replace("]]></script>",""))
			relevantJson = script["model"]["articleInfo"]["units"]
			self.img = soup.find_all(class_="_6uf91T z-oVg8 u-6V88 ka2E9k uMhVZi FxZV-M _2Pvyxl JT3_zV EKabf7 mo6ZnF _1RurXL mo6ZnF PZ5eVw")[0]["src"]
			self.Title = soup.find(class_="OEhtt9 ka2E9k uMhVZi uc9Eq5 pVrzNP _5Yd-hZ").text
			self.desc = soup.find(class_="EKabf7 R_QwOV").text
			self.price = relevantJson[0]["displayPrice"]["price"]["formatted"]
			if(self.firstLoad == False):
				for i in range(0,len(relevantJson)-1):
					if(relevantJson[i]["stock"] != self.sizeStockList[i][1]):
							if(self.sizeStockList[i][1] == 0):
								self.sendWebhook([relevantJson[i]["size"]["local"],relevantJson[i]["stock"]],relevantJson[i]["id"])
							self.sizeStockList[i][1] = relevantJson[i]["stock"]

			else:
				for i in range(0,len(relevantJson)-1):
					self.sizeStockList.append([relevantJson[i]["size"]["manufacturer"],relevantJson[i]["stock"]])
				self.firstLoad = False

	def release(self):
		response = requests.get(self.url,headers=self.headers,proxies={"http":getProxie()})
		status = response.status_code
		content = response.content
		if(status == 200):
			self.released = True
			soup = BeautifulSoup(content,'html.parser')
			script_soup = soup.find(id="z-vegas-pdp-props")
			print("200")
			if script_soup != None :
				print("!= None")
				script = json.loads(str(script_soup).replace('<script id="z-vegas-pdp-props" type="application/json"><![CDATA[',"").replace("]]></script>",""))
				relevantJson = script["model"]["articleInfo"]["units"]
				self.img = soup.find_all(class_="_6uf91T z-oVg8 u-6V88 ka2E9k uMhVZi FxZV-M _2Pvyxl JT3_zV EKabf7 mo6ZnF _1RurXL mo6ZnF PZ5eVw")[0]["src"]
				self.Title = soup.find(class_="OEhtt9 ka2E9k uMhVZi uc9Eq5 pVrzNP _5Yd-hZ").text
				self.desc = soup.find(class_="OEhtt9 ka2E9k uMhVZi z-oVg8 pVrzNP w5w9i_ _1PY7tW _9YcI4f").text
				self.price = relevantJson[0]["displayPrice"]["price"]["formatted"]
				pid = script["model"]["articleInfo"]["id"]
				self.sendWebhook(None,pid)

def getProxie():
	randint = r.randint(0,len(proxies)-1)
	proxie = proxies[randint]
	splittedProxy = proxie.split(':')

	user = splittedProxy[2]
	password = splittedProxy[3].replace("\n","")
	host = splittedProxy[0]
	port = splittedProxy[1]

	return "http://" + user + ":" + password + "@" + host + ":" + port

Monitors = [Monitor("https://www.zalando.de/nike-sportswear-air-force-1-sneaker-low-white-ni114d0ht-a11.html","https://discordapp.com/api/webhooks/825156226580742175/ycGSDK0cq28m10_uVAZM1A-zx0_5aHaRJIZQJxvipNo3kMhL6o17bqvagVsVSXBrYd10")]
while True:
	for m in Monitors:
		# if m.released == False:
		# 	m.release()
		m.checkStock()
	time.sleep(0.01)