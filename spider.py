"""
@QQ_VX:   240942649
@Date:    2019.08.09
@Author:  小伟科技工作室
@Project: 农产品交易
"""

import re
import execjs
import requests
from lxml import etree
from retry import retry
from openpyxl import Workbook
from loguru import logger
from gevent import monkey, pool
from gevent.lock import Semaphore
monkey.patch_socket()

sem = Semaphore(1)


class LongSpider(object):
    """
    农产品交易
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36'
                          ' (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            # 'Cookie': 'YwnBCHQI8xgWI5a=KMITdgVuivvmbO9tpasiosENKZeKWKc8DNGpo9B.dpWZ0H5hL45Bo03jKp6e5yCPqmLf88MFbafEblBLLmLNGJSxJw16SFG4vWNGlmr_OaHIN'
        }
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(['项目编号', '项目名称', '交易地点', '公式日期', '流转方式', '流转期限', '是否续租', '流转用途',
                        '交易面积', '交易方式', '成交价'])
        self.pool = pool.Pool(10)

        with open('script/js.js', 'r', encoding='utf-8') as file:
            js = file.read()

        self.ctx = execjs.compile(js)

    @staticmethod
    def extract_first(values):
        for value in values:
            if value != '' and value is not None:
                return re.sub(r'\s', '', value)

        return '\t'

    @retry(ValueError, tries=10)
    def search_list(self, page):
        """
        搜索列表
        :return:
        """
        url = 'http://www.jsnc.gov.cn/nccqjy/portal.do?method=province_cj_gg_list'
        post_data = {
            'unitId': '1',
            'page': str(page),
            'selectName': '江苏省',
            'unitID': '',
            'proType': '40286f8147d283fc0147d2a637c00001',
            'proArea': '',
            'proCode': '',
            'startTime': '2018-01-01',
            'endTime': '2018-12-31',
        }
        response = requests.post(url, data=post_data, headers=self.headers)
        print(response.status_code)

        if 'JLyKZlWgYjpTkAsEt9LnA' in response.text:
            self.set_cooke()

            raise ValueError('刷新cookie')

        html = etree.HTML(response.content)
        items = html.xpath('//table[@class="show_data"]/tr')[1:]
        for item in items:
            p_id = self.extract_first(item.xpath('./td[1]/text()'))
            name = self.extract_first(item.xpath('./td[2]/a/text()'))
            address = self.extract_first(item.xpath('./td[3]/span/text()'))
            date = self.extract_first(item.xpath('./td[4]/text()'))

            # 处理链接
            link = self.extract_first(item.xpath('./td[2]/a/@onclick'))

            link = 'http://www.jsnc.gov.cn' + re.findall(r"'(.+?)'", link)[0]
            line = [p_id, name, address, date]
            # self.get_info(link, line)
            self.pool.spawn(self.get_info, link, line)

        self.wb.save('info.xlsx')

    @retry(ValueError, tries=10)
    def get_info(self, link, s_line):
        """
        获取详情
        :param link:
        :return:
        """
        response = requests.get(link, headers=self.headers)

        if 'JLyKZlWgYjpTkAsEt9LnA' in response.text:
            self.set_cooke()
            raise ValueError('刷新cookie')

        html = etree.HTML(response.text)
        # 流转方式
        flow_way = self.extract_first(html.xpath('//td[contains(text(), "流转方式")]/following-sibling::td[1]/text()'))
        # 流转期限
        flow_limit = self.extract_first(html.xpath('//td[contains(text(), "流转期限")]/following-sibling::td[1]/text()'))

        # 是否续租
        is_zu = self.extract_first(html.xpath('//span[contains(text(), "是否续租")]/../text()'))
        # 流转用途
        desc = self.extract_first(html.xpath('//span[contains(text(), "流转用途")]/../text()'))
        # 交易面积
        trad_area = self.extract_first(html.xpath('//span[contains(text(), "交易面积")]/../text()'))
        # 交易方式
        trad_way = self.extract_first(html.xpath('//span[contains(text(), "交易方式")]/../text()'))
        # 成交价
        price = self.extract_first(html.xpath('//span[contains(text(), "成交价")]/../text()'))

        line = s_line + [flow_way, flow_limit, is_zu, desc, trad_area, trad_way, price]
        self.ws.append(line)
        logger.info(f'【INFO】获取数据: {line[1]}')

    def set_cooke(self):
        """
        设置cookie
        :return:
        """
        js_url = 'http://www.jsnc.gov.cn/mRnE3GFBhtb7/MXC5cdd/a6a1a7'
        response = requests.get(js_url, headers=self.headers)
        go = re.findall(r'function _\$g0\(\){return "(.+?)"', response.text)
        if go:

            cookie = self.ctx.call('get_cookie', go[0])
            cookie = f'YwnBCHQI8xgWI5a={cookie}'
            logger.info(f'【INFO】设置cookie={cookie}')
            self.headers['Cookie'] = cookie
        else:
            raise ValueError('cookie 设置失败')

    def crawl(self):
        self.set_cooke()
        for page in range(1, 1340):
            logger.info(f'【INFO】 当前页数: {page}')
            self.search_list(page)

        self.pool.join()
        self.wb.save('info.xlsx')


if __name__ == '__main__':
    spider = LongSpider()
    spider.crawl()
