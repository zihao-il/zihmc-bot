import configparser
import json
import re
import requests

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"}

path = 'mcbb.ini'

config = configparser.ConfigParser()
config.read(path, encoding='utf-8')

def mcbv():
    try:
        mcr = requests.get("https://bugs.mojang.com/rest/api/2/project/10200/versions", headers=headers)
        data = json.loads(mcr.text)
        release = []
        beta = []
        preview = []
        for v in data:
            if not v['archived'] and v['released']:
                if re.match(r".*Beta$", v["name"]):
                    beta.append(v["name"].split(" ")[0])
                elif re.match(r".*Preview$", v["name"]):
                    preview.append(v["name"].split(" ")[0])
                else:
                    release.append(v["name"].split(" ")[0])
        release = release[-1]
        beta = beta[0]
        preview = preview[0]
    except:
        return
    with open(path, mode='w', encoding='utf-8') as f:
        if config.get('版本记录', 'release') != release:
            print(f'你有新的正式版请注意查收：\n版本号：{release}')
            config['版本记录']['release'] = release
        if config.get('版本记录', 'beta') != beta:
            print(f'你有新的测试版请注意查收：\n版本号：{beta}')
            config['版本记录']['beta'] = beta
        if config.get('版本记录', 'preview') != preview:
            print(f'你有新的预览版请注意查收：\n版本号：{preview}')
            config['版本记录']['preview'] = preview
        config.write(f)
mcbv()


