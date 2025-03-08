import scrapy
from baiTap1.items import Baitap1Item
from scrapy_playwright.page import PageMethod

class SpiderbaitapSpider(scrapy.Spider):
    # name = "spiderBaiTap"
    # allowed_domains = ["dichvucong.gov.vn"]
    # start_urls = ["https://dichvucong.gov.vn/p/home/dvc-cau-hoi-pho-bien.html"]

    name = 'spiderBaiTap'
    # allow_domain = 'www.dichvucong.gov.vn'
    # start_urls = ['https://dichvucong.gov.vn/p/home/sdvc-cau-hoi-pho-bien.html']

    def start_requests(self):
        yield scrapy.Request('https://dichvucong.gov.vn/p/home/dvc-cau-hoi-pho-bien.html', meta= dict(
            playwright = True,
            playwright_include_page = True,
            playwright_page_methods = [
                PageMethod('wait_for_selector', 'div.tab-content')
                ]
        ))

    async def parse(self, response):
        # yield{
        #     'text': response.text
        # }
        for item in response.css('div.tab-pane.active#tatCa > div.list-document.-question > a.item'):
            yield{
                'title' : item.css("a::text").get()
            }
            question_text = item.css("a::text").get()
            question_url = item.css('a::attr(href)').get()
            # 'traloi' :  response('url' : item.css('a::attr(href)').get())

            yield response.follow(
                    question_url,
                    self.parse_details,
                    meta={"playwright": True, "question": question_text},
                )
            
        next_button = response.css("li.next > a")
        if next_button and next_button.attrib.get("href") == "javascript:;":
            
            # Get the Playwright page
            page = response.meta["playwright_page"]

            # Click the next button
            await page.click("li.next > a")

            # Wait for content to load
            await page.wait_for_selector("div.tab-pane.active#tatCa", timeout=5000)

            # Get new page content
            new_content = await page.content()
            new_response = response.replace(body=new_content)

            # Call parse again with new content
            async for result in self.parse(new_response):
                yield result
        

        
    # def parse_cauhoi(self, response):
    #     item = Bai1Item()
    #     #item['cauhoi'] = response.css('h1.main-title-sub::text').get()
    #     item['cauhoi'] = "1"
    #     #item["traloi"] = " ".join(response.css("div.article p::text").getall()).strip()
    #     yield item

    async def parse_details(self, response):
        """Extracts the answer from the detail page."""
        question = response.meta["question"]
        answer = " ".join(response.css("div.article p::text").getall()).strip()

        yield {
            "cauhoi": question,
            "traloi": answer.strip() if answer else "No answer found",
        }
