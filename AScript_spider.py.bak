import os
import requests
import markdownify  # 用于将HTML转换为Markdown
from bs4 import BeautifulSoup
from Scraper import *
# 下载网页
urls = ["https://ascript.cn/docs/android/intro","https://ascript.cn/docs/android/guide/"]

file_path = ".temp/output.html"
os.makedirs(os.path.dirname(file_path), exist_ok=True)
file_content = ""
driver = Scraper.SeleniumScraper()
for url, html in driver.get_pages(urls):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)
    break;
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



html_path = ".temp/output.html"
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

toc_items = get_toc_items(html_content)
main_content = get_main_content(html_content)

print("Table of Contents:")
for href, text in toc_items:
    print(f"- [{text}]({href})")

print("\nMain Content:")
print(main_content)