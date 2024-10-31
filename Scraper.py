import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor, as_completed

# 通用手机端请求头
default_headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile; rv:89.0) Gecko/89.0 Firefox/89.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",  # 不跟踪请求
    "Accept-Encoding": "gzip, deflate, br"
}


class RequestsScraper:
    """
    使用 requests 模块获取页面内容。
    支持多线程和生成器逐条返回 HTML 内容。
    """
    def __init__(self, headers):
        self.headers = headers

    def get_page(self, url):
        """单个请求页面的 HTML 内容"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return url, response.text
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return url, None

    def get_pages(self, url_list, max_workers=5):
        """
        使用多线程获取页面内容，逐条生成 URL 与 HTML 内容。

        参数:
        - url_list (list): URL 列表。
        - max_workers (int): 最大线程数。

        返回:
        - generator: 每次返回 (url, html) 元组。
        """
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            futures = {executor.submit(self.get_page, url): url for url in url_list}
            # 逐条返回每个页面的内容
            for future in as_completed(futures):
                yield future.result()


class SeleniumScraper:
    """
    使用 Selenium 模块获取页面内容。
    支持多线程和生成器逐条返回 HTML 内容。
    """
    def __init__(self, headers:dict={}):
        if not headers:
          self.headers = default_headers
        else:
          self.headers = headers

    def get_page(self, url):
        """使用 Selenium 获取单个页面 HTML 内容"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f"user-agent={self.headers['User-Agent']}")

        driver = webdriver.Chrome(options=options)
        try:
            driver.get(url)
            html = driver.page_source
            return url, html
        except Exception as e:
            print(f"Selenium 请求失败: {e}")
            return url, None
        finally:
            driver.quit()

    def get_pages(self, url_list, max_workers=2):
        """
        使用多线程获取页面内容，逐条生成 URL 与 HTML 内容。

        参数:
        - url_list (list): URL 列表。
        - max_workers (int): 最大线程数。

        返回:
        - generator: 每次返回 (url, html) 元组。
        """
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.get_page, url): url for url in url_list}
            for future in as_completed(futures):
                yield future.result()
    def close(self):
      pass



# 使用示例
if __name__ == "__main__":
    url_list = ["https://example.com/page1", "https://example.com/page2"]
    headers = default_headers
    # 使用 RequestsScraper 批量获取页面
    requests_scraper = RequestsScraper(headers)
    print("Requests 获取页面内容:")
    for url, content in requests_scraper.get_pages(url_list):
        print(f"{url}: {content[:200]}")  # 仅显示部分内容

    # 使用 SeleniumScraper 批量获取页面
    selenium_scraper = SeleniumScraper(headers)
    print("Selenium 获取页面内容:")
    for url, content in selenium_scraper.get_pages(url_list):
        print(f"{url}: {content[:200]}")  # 仅显示部分内容
