import os
import requests
import markdownify
from bs4 import BeautifulSoup
from Scraper import RequestsScraper, SeleniumScraper
from DownloadList import DownloadList

# 目标网站的根URL
target_url = "https://ascript.cn"

# 下载清单对象
download_list = DownloadList()

def crawl_documentation():
    # 使用SeleniumScraper获取页面内容
    driver = SeleniumScraper()

    # 初始URL列表
    url_list = [target_url + "/docs/android/intro", target_url + "/docs/android/guide/"]

    # 存储所有文档内容（如果需要）
    all_documents = []

    while url_list:
        new_url_list = []
        for url in url_list:
            # 检查是否已下载
            if download_list.get(url, {}).get('is_downloaded', False):
                continue

            try:
                # 获取页面内容
                _, html = driver.get_page(url)
                soup = BeautifulSoup(html, 'html.parser')

                # 获取主体内容并处理
                main_content = get_main_content(html)
                if main_content:
                    file_path = generate_file_path(url, soup.find('title').text)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(markdownify.markdownify(main_content))
                    download_list.mark_downloaded(url)

                # 获取目录项链接并添加到新的URL列表
                toc_items = get_toc_items(html)
                for href, text in toc_items:
                    full_url = target_url + href
                    if full_url not in download_list:
                        download_list.add_task(full_url, text)
                        new_url_list.append(full_url)
            except Exception as e:
                print(f"Error fetching {url}: {e}")

        url_list = new_url_list

    driver.close()

def get_toc_items(html_content):
    """
    该函数用于从给定的HTML内容中获取目录项的链接和文本。
    解析思想：
    - 首先使用BeautifulSoup解析HTML内容。
    - 然后遍历所有的<a>标签，因为目录项通常是以链接形式存在的。
    考虑因素：
    - 为了获取准确的目录链接，需要根据特定的条件进行筛选。只选择以/docs/android开头的链接，
      这是因为文档中与Android相关的目录链接都具有此特征，可以排除其他不相关的链接。
    - 同时，链接不以/结尾且不包含#，以进一步排除不符合目录链接格式的情况。
    返回值：
    - 一个包含元组的列表，每个元组包含目录项的链接和文本。
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    toc_items = []
    for a in soup.find_all('a'):
        href = a.get('href')
        if href and href.startswith('/docs/android') and not href.endswith('/') and '#' not in href:
            text = a.text
            toc_items.append((href, text))
    return toc_items

def get_main_content(html_content):
    """
    该函数用于从给定的HTML内容中获取主体内容部分。
    解析思想：
    - 使用BeautifulSoup解析HTML内容，然后查找具有特定类名的<main>标签，
      因为文档的主体内容通常包含在这个标签内。
    返回值：
    - 如果找到<main>标签，则返回其文本内容，以换行符分隔不同的段落；如果未找到，则返回空字符串。
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    main_content = soup.find('main', class_='docMainContainer_TBSr')
    return main_content.get_text(separator='\n') if main_content else ""

def generate_file_path(url, title):
    """
    根据给定的URL和标题生成文件路径
    """
    relative_path = url.replace(target_url, "")
    parts = relative_path.split('/')
    dir_path = os.path.join("/content/docs/项目名", *parts[:-1])
    file_name = parts[-1] if parts[-1] else title
    os.makedirs(dir_path, exist_ok=True)
    return os.path.join(dir_path, file_name + ".md")

if __name__ == "__main__":
    crawl_documentation()
    download_list.save_to_file("download_list.json")
