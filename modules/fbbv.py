from graia.saya import Channel
import json
import requests
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.scheduler import timers
from graia.scheduler.saya import SchedulerSchema

channel = Channel.current()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}
sections = [{'name': 'Beta',
             'url': 'https://minecraftfeedback.zendesk.com/api/v2/help_center/en-us/sections/360001185332/articles?per_page=5'},
            {'name': 'Release',
             'url': 'https://minecraftfeedback.zendesk.com/api/v2/help_center/en-us/sections/360001186971/articles?per_page=5'}]

path = "data/mcfb.json"

qqgroup = [933238308, 855150997, 562664290, 196619774]

@channel.use(SchedulerSchema(timers.every_custom_minutes(1)))
async def mcbv(app: Ariadne):


    with open(path, "r") as b:
        mcfb_data = json.load(b)

    for sv in sections:
        try:
            mcfb = requests.get(sv["url"], headers=headers, timeout=5)
            mcfb_json = json.loads(mcfb.text)
        except:
            return
        fb_name = mcfb_json["articles"][0]["name"]
        if mcfb_data[sv['name']] != fb_name:
            for g in qqgroup:
                await app.sendGroupMessage(g, MessageChain.create(
                    f'Minecraft Feedback 发布了新的文章：\n\n标题：\n{fb_name}\n\n链接：\n{mcfb_json["articles"][0]["html_url"]}'))
            mcfb_data[sv['name']] = fb_name
            with open(path, "w") as m:
                json.dump(mcfb_data, m)






# 计划失败
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# def get_fbimg(url):
#     options = webdriver.ChromeOptions()
#     options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"')
#     options.add_argument("headless")
#     driver = webdriver.Chrome(options=options)
#     driver.get(url)
#     img_url = driver.find_element(By.CSS_SELECTOR, "p.wysiwyg-text-align-center").find_element(By.CSS_SELECTOR, "img").get_attribute("src")
#     return img_url
