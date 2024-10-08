'''
@Project ：spider 
@File    ：同花顺逆向.py
@Author  ：dp
@Date    ：2024/9/26 14:51 
'''

import requests
import subprocess
from lxml import etree


class th_spider:
    def __init__(self):
        pass

    def get_info(self):
        for i in range(1):
            url = f'https://q.10jqka.com.cn/index/index/board/all/field/zdf/order/desc/page/{i}/ajax/1/'
            print(url)
            resp = self.resp(url)
            self.clear_data(resp)


    def clear_data(self,resp):
        print(resp.text)
        html = etree.HTML(resp.text)
        data = {
            '代码': html.xpath('/html/body/table/tbody//tr/td[2]/a/text()'),
            '名称': html.xpath('/html/body/table/tbody//tr/td[3]/a/text()'),
        }
        for i in html.xpath('/html/body/table/tbody//tr'):
            info = i.xpath('.//td/text()')
            print(info)
        print(data)


    def resp(self,url=''):
        result = subprocess.run(['node', '同花顺逆向.js'], capture_output=True, text=True)
        output = result.stdout.strip()
        payload = {}
        headers = {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Cookie': 'u_ukey=A10702B8689642C6BE607730E11E6E4A; u_uver=1.0.0; u_dpass=BSQGyq171ZUMyz%2BFPwPt0JtXRQpBapFMfLp6TH1E4xoniqa%2B7stLxrqeJ3krcxZIHi80LrSsTFH9a%2B6rtRvqGg%3D%3D; u_did=848D82FB4D104616AFE7EDAEA0F06379; u_ttype=WEB; v=A7N3LAPL0a4N3J17VIX6dJe2QrzY6EedAX2L0mVQDDgIZN2i7bjX-hFMGyl2',
            'Pragma': 'no-cache',
            'Referer': 'https://q.10jqka.com.cn/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
            'X-Requested-With': 'XMLHttpRequest',
            'hexin-v': output,
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        return response


if __name__ == '__main__':
    spider = th_spider()
    spider.get_info()

