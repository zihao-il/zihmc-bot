import configparser
import json
import requests

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}
path = 'fkbb.ini'

config = configparser.ConfigParser()
config.read(path, encoding='utf-8')

def mcbv():

    try:
        releasej = requests.get(
            'https://minecraftfeedback.zendesk.com/api/v2/help_center/en-us/sections/360001186971/articles?per_page=5',
            headers=headers, timeout=3).text
        releasej = json.loads(releasej)
        betaj = requests.get(
            'https://minecraftfeedback.zendesk.com/api/v2/help_center/en-us/sections/360001185332/articles?per_page=5',
            headers=headers, timeout=3).text
        betaj = json.loads(betaj)
        fbr = releasej["articles"][0]["name"]
        fbb = betaj["articles"][0]["name"]
    except:
        return
    with open(path, mode='w', encoding='utf-8') as f:
        if config.get('版本记录', 'frelease') != fbr:
            print(f'Minecraft Feedback 发布了新的文章：\n\n标题：\n{fbr}\n\n链接：\n{releasej["articles"][0]["html_url"]}')
            config['版本记录']['frelease'] = fbr
        if config.get('版本记录', 'fbeta') != fbb:
            print(f'Minecraft Feedback 发布了新的文章：\n\n标题：\n{fbb}\n\n链接：\n{betaj["articles"][0]["html_url"]}')
            config['版本记录']['fbeta'] = fbb
        config.write(f)

mcbv()
