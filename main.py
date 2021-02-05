import asyncio
import pyppeteer
from pyppeteer.errors import NetworkError
import time
import telebot
from config import token
import pymongo
import bot_stats
from datetime import date

# MongoDB
cluster = pymongo.MongoClient(
	'mongodb+srv://spaceshinobi:d.sh.2001@cluster0-7ga1d.mongodb.net/test?retryWrites=true&w=majority')
db4 = cluster["stats"]
statsData = db4["stats"]
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start', 'help'])
def welcome(message):
	bot.send_message(message.chat.id, "Just simply send me an URL and wait 5-10 seconds \U0001F60C".encode('utf-8'))
	bot_stats.send_stats(message, statsData, "start", date.isoformat(date.today()), bot)


@bot.message_handler(content_types=['text'])
def checksite(message):
	bot.reply_to(message, "Proccessing...")
	url = message.text
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)

	async def main(url):
		browser = await pyppeteer.launch(
			args=['--no-sandbox'],
			handleSIGINT=False,
			handleSIGTERM=False,
			handleSIGHUP=False)
		page = await browser.newPage()
		await page.goto(url)
		await page.setViewport(dict(width=1920, height=1080))
		time.sleep(2)
		await page.screenshot(path="screenshot.png", fullPage=True)
		await browser.close()
	try:
		loop.run_until_complete(main(url))
		screen = open("screenshot.png", "rb")
		bot.send_message(message.chat.id, "And here you go \U0001F609".encode("utf-8"))
		bot.send_document(message.chat.id, screen)
		bot_stats.send_stats(message, statsData, "check", date.isoformat(date.today()), bot)
		screen.close()
	except NetworkError:
		bot.send_message(message.chat.id, "ERROR: Invalid link.")
		bot_stats.send_stats(message, statsData, "invalid", date.isoformat(date.today()), bot)


bot.polling(none_stop=True)
