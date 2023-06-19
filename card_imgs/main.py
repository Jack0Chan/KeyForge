"""_summary_

Returns:
    _type_: _description_
"""
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List
from bs4 import BeautifulSoup
import requests
from rich.progress import Progress


def mk_dir(dir_name: str):
    """创建文件夹目录

    Args:
        dir_name (str): _description_
    """
    if os.path.exists(dir_name):
        # print(f"{dir_name} exists")
        pass
    else:
        os.mkdir(dir_name)
        # print(f'{dir_name} created')


class CardArticle:
    """_summary_
    """

    def __init__(self, article_title: str, article_link: str):
        """_summary_

        Args:
            article_title (str): _description_
            article_link (str): _description_
        """
        # 文章名，也是种族名，比如“暗潮汹涌——海渊全牌表”
        self.article_title: str = article_title
        self.article_link: str = article_link
        self.img_urls: List[str] = []
        self.__get_img_urls()

    def __get_img_urls(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        resp = requests.get(self.article_link, timeout=10)
        page = BeautifulSoup(resp.text, 'html.parser')
        imgs = page.find("div", {"class": "rich_media_content"})
        imgs = imgs.find_all("img")
        self.img_urls = [i.get("data-src") for i in imgs]

    def download_imgs(self, progress, task_id):
        """_summary_
        """
        mk_dir(self.article_title)
        for i, img_url in enumerate(self.img_urls):
            r = requests.get(img_url, timeout=10)
            with open(f"{self.article_title}/{i}.jpeg", 'wb') as f:
                f.write(r.content)
            progress.update(task_id, advance=1)


class ImageSpider:
    """_summary_
    """

    def __init__(self):
        self.card_articles: List[CardArticle] = []

    def get_articles(self):
        """_summary_
        """
        # 微信公众号文章主页
        cookies = {
            'RK': 'NBpZ/UZLEm',
            'ptcz': 'e5c79d45cd27f6950dbabca4ace3cb95c159d63cb83e7503610d9c712409f8b7',
            'pgv_pvid': '1291344370',
            'rewardsn': '',
            'wxtokenkey': '777',
        }

        headers = {
            'authority': 'mp.weixin.qq.com',
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            # 'content-length': '0',
            # 'cookie': 'RK=NBpZ/UZLEm; ptcz=e5c79d45cd27f6950dbabca4ace3cb95c159d63cb83e7503610d9c712409f8b7; pgv_pvid=1291344370; rewardsn=; wxtokenkey=777',
            'origin': 'https://mp.weixin.qq.com',
            'referer': 'https://mp.weixin.qq.com/mp/homepage?__biz=MzU1Nzc2OTgyOA==&hid=1&sn=85d914e5725066b3d150f051b0f229fc&scene=18',
            'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }

        url = 'https://mp.weixin.qq.com/mp/homepage?__biz=MzU1Nzc2OTgyOA==&hid=1&sn=85d914e5725066b3d150f051b0f229fc&scene=18&cid=1&begin=0&count=999&action=appmsg_list&f=json&r=0.16883265625084487&appmsg_token='

        response = requests.post(
            url,
            cookies=cookies,
            headers=headers,
            timeout=10
        )
        # print(response.text)
        article_list = response.json()['appmsg_list']
        # print(article_list)
        for article_info in article_list:
            card_article = CardArticle(
                article_title=article_info['title'],
                article_link=article_info['link'])
            self.card_articles.append(card_article)

    def download_imgs(self):
        """_summary_
        """
        progress = Progress()
        with progress:
            with ThreadPoolExecutor(max_workers=4) as pool:
                for article in self.card_articles:
                    task_id = progress.add_task(
                        f"[cyan]Downloading {article.article_title}...", total=len(article.img_urls))
                    pool.submit(article.download_imgs, progress, task_id)


if __name__ == "__main__":
    spider = ImageSpider()
    spider.get_articles()
    # for s in spider.card_articles:
    #     print(s.article_title)
    #     print(s.article_link)
    spider.download_imgs()
