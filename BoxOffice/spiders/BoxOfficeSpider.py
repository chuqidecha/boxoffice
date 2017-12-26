# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest, Selector
import logging

from BoxOffice.items import BoxOfficeItem

null_str = lambda x: x if x is not None else ""


class BoxofficespiderSpider(scrapy.Spider):
    name = 'BoxOfficeSpider'
    start_urls = ['http://58921.com/user/login']
    post_headers = {
        "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36",
        "Referer": "http://58921.com/user/login",
    }

    custom_settings = {
        'ITEM_PIPELINES': {
            'BoxOffice.pipelines.CsvPipeline': 500,
        }
    }

    # 重写了爬虫类的方法, 实现了自定义请求, 运行成功后会调用callback回调函数
    def start_requests(self):
        return [Request(url, meta={'cookiejar': 1}, callback=self.post_login) for url in self.start_urls]

    # 使用FormRequeset模拟表单提交
    def post_login(self, response):
        # 先去拿隐藏的表单参数
        form_id = response.xpath('//*[@id="user_login_form"]/input[1]/@value').extract_first()
        logging.info('form_id = ' + form_id)
        form_token = response.xpath('//*[@id="user_login_form"]/input[2]/@value').extract_first()
        logging.info('form_token = ' + form_token)
        # 登陆成功后, 会调用after_login回调函数，如果url跟Request页面的一样就省略掉
        return [FormRequest.from_response(response,
                                          url="http://58921.com/user/login/ajax?ajax=submit&__q=user/login",
                                          meta={'cookiejar': response.meta['cookiejar']},
                                          headers=self.post_headers,  # 注意此处的headers
                                          formdata={
                                              'mail': u'初沏的茶',
                                              'pass': '**********',
                                              'form_id': form_id,
                                              'form_token': form_token,
                                              "submit": u'登录'
                                          },
                                          callback=self.after_login,
                                          dont_filter=True
                                          )]

    def after_login(self, response):
        logging.info("logging sucess!")
        yield Request("http://58921.com/alltime", meta={'cookiejar': 1}, callback=self.parse)

    def parse(self, response):
        logging.info(response.url)
        selector = Selector(response=response)
        next = selector.xpath('//*[@id="content"]/div[4]/ul/li[11]/a/@href').extract_first()
        if next:
            yield Request("http://58921.com" + next, meta={'cookiejar': 1}, callback=self.parse)
        tb_body = selector.xpath('//*[@id="content"]/div[3]/table/tbody/tr')
        for tr in tb_body:
            try:
                detail = tr.xpath('./td[3]/a/@href').extract_first()
                film_name = tr.xpath('./td[3]/a/text()').extract_first()
                yield Request("http://58921.com" + detail,
                              meta={
                                  'cookiejar': 1,
                                  'film_name': film_name
                              },
                              callback=self.parse_detail)
            except:
                logging.error(response.url)

    def parse_detail(self, response):
        logging.info(response.url)
        selector = Selector(response=response)
        href = selector.xpath('//*[@id="content_page_tabs"]/li[2]/a/@href').extract_first()
        detail_ul = selector.xpath('//div[@class="content_view content_film_view"]/div[2]/div/ul')[0]
        director = detail_ul.xpath(u'./li/strong[text()="导演："]/following-sibling::a/text()').extract()
        actors = detail_ul.xpath(u'./li/strong[text()="主演："]/following-sibling::a/text()').extract()
        broadcast_time = detail_ul.xpath(u'./li/strong[text()="上映时间："]/../text()').extract_first()
        country = detail_ul.xpath(u'./li/strong[text()="制作国家/地区："]/following-sibling::a/text()').extract_first()
        time_span = detail_ul.xpath(u'./li/strong[text()="片长："]/../text()').extract_first()
        category = detail_ul.xpath(u'./li/strong[text()="类型："]/following-sibling::a/text()').extract()
        language = detail_ul.xpath(u'./li/strong[text()="语言："]/following-sibling::a/text()').extract()

        yield Request("http://58921.com" + href,
                      meta={
                          'cookiejar': 1,
                          'film_name': response.meta['film_name'],
                          'director': ','.join(director),
                          'actors': ','.join(actors),
                          'broadcast_time': null_str(broadcast_time),
                          'country': null_str(country),
                          'time_span': null_str(time_span),
                          'category': ','.join(category),
                          'language': ','.join(language)
                      },
                      callback=self.parse_box_office)

    def parse_box_office(self, response):
        box_office = response.xpath('//*[@id="2"]/div[1]/h3/text()').extract_first().split(' ')[-1].replace(')',
                                                                                                            '').strip()
        yield BoxOfficeItem(
            film_name=(response.meta['film_name']),
            director=(response.meta['director']),
            actors=(response.meta['actors']),
            broadcast_time=(response.meta['broadcast_time']),
            country=(response.meta['country']),
            time_span=(response.meta['time_span']),
            category=(response.meta['category']),
            language=(response.meta['language']),
            box_office=(box_office)
        )
