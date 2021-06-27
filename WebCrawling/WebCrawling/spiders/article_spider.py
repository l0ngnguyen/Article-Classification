import scrapy
from datetime import date, timedelta
from bs4 import BeautifulSoup


def get_dates_between(start_date, end_date):
    delta = end_date - start_date       # as timedelta

    dates = []
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        day = f'{day.day}-{day.month}-{day.year}'
        dates.append(day)
    
    return dates

START_DATE = date(2018, 1, 1)
END_DATE = date(2021, 6, 12)


categories = [
    'the-thao',
    'thoi-su',
    'the-gioi',
    'phap-luat',
    'kinh-doanh',
    'van-hoa',
    'suc-khoe',
    'khoa-hoc',
    'giai-tri',
    'giao-duc',
    'xe'
]

class ArticleSpider(scrapy.Spider):
    name = 'article'

    def start_requests(self):
        for date in get_dates_between(START_DATE, END_DATE):
            urls = [f'https://tuoitre.vn/{cat}/xem-theo-ngay/{date}.html' for cat in categories]
            for url in urls:
                yield scrapy.Request(url, callback=self.parse_links)
            

    def parse_links(self, response):
        yield from response.follow_all(css='h3.title-news a', callback=self.parse_details)

    def parse_details(self, response):
        url = response.url
        category = response.css('div.bread-crumbs > ul > li:nth-child(1) > a::text').get()

        summary_title = response.css('h2.sapo::text').get()

        paragraphs = response.css('#main-detail-body > p').getall()
        paragraphs = [BeautifulSoup(p, features='lxml').get_text() for p in paragraphs]
        
        all_text_content = summary_title + '\n' + '\n'.join(paragraphs) if summary_title else '\n'.join(paragraphs)

        yield {
            'category': category,
            'text': all_text_content,
            'url': url 
        }
