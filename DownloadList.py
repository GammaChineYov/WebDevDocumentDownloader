import json

class DownloadList(dict):
    """
    下载清单类，继承字典类，以 href 为键，包含 text, is_downloaded, is_in_download_queue 作为值。
    支持持久化存储和加载，并支持程序恢复和清除未完成任务标记。
    
    结构:
    - href (str): 作为字典的键，唯一标识下载链接。
    - 值 (dict):
      - text (str): 链接的文本描述。
      - is_downloaded (bool): 是否已下载。
      - is_in_download_queue (bool): 是否在下载队列中。
      
    使用方法:
    - add_task: 添加下载任务。
    - mark_downloaded: 标记任务为已下载。
    - save_to_file: 将当前任务列表保存到文件。
    - load_from_file: 从文件加载任务列表。
    - cleanup_queue: 清除未下载的任务标记，恢复程序时调用。
    - reset: 重置所有任务状态。
    """

    def add_task(self, href, text):
        """添加新的下载任务到清单."""
        self[href] = {
            'text': text,
            'is_downloaded': False,
            'is_in_download_queue': True
        }

    def mark_downloaded(self, href):
        """标记指定的下载任务为已下载."""
        if href in self:
            self[href]['is_downloaded'] = True
            self[href]['is_in_download_queue'] = False

    def save_to_file(self, file_path):
        """将下载清单保存到指定文件路径."""
        with open(file_path, 'w') as file:
            json.dump(self, file, indent=4)
    
    def load_from_file(self, file_path):
        """从指定文件路径加载下载清单."""
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                self.clear()  # 清空现有数据
                for href, details in data.items():
                    self[href] = details
        except FileNotFoundError:
            print(f"{file_path} 文件不存在。")
        except json.JSONDecodeError:
            print(f"{file_path} 文件格式错误，无法解析。")
    
    def cleanup_queue(self):
        """清除未下载且在队列中的任务标记，适合程序恢复时调用."""
        for href, details in self.items():
            if details['is_in_download_queue'] and not details['is_downloaded']:
                details['is_in_download_queue'] = False
    
    def reset(self):
        """重置所有任务状态，将所有任务设为未下载且不在队列中。"""
        for details in self.values():
            details['is_downloaded'] = False
            details['is_in_download_queue'] = False

    def add_download_list(self, a_tags, condition_list, exclude_list):
        """
        批量添加符合条件的下载任务。
        
        参数:
        - a_tags (list): 需过滤的 <a> 标签列表。
        - condition_list (list): 包含条件的字符串列表。
        - exclude_list (list): 排除条件的字符串列表。
        """
        filtered_a_tags = [
            a_tag for a_tag in a_tags
            if any(condition in a_tag.get('href', '') for condition in condition_list)
            and not any(exclude in a_tag.get('href', '') for exclude in exclude_list)
        ]
        
        for a_tag in filtered_a_tags:
            href = a_tag.get('href')
            text = a_tag.get_text()
            if href not in self:
                self.add_task(href, text)
                print(f"添加任务 - href: {href}, text: {text}")
                
if __name__ == "__main__":
  # 初始化下载清单
  download_list = DownloadList()

  # 添加下载任务
  download_list.add_task("http://example.com/file1", "文件1")
  download_list.add_task("http://example.com/file2", "文件2")

  # 标记任务为已下载
  download_list.mark_downloaded("http://example.com/file1")

  # 保存到文件，模拟程序终止
  download_list.save_to_file("download_list.json")

  # 重新加载下载清单，模拟程序恢复
  download_list.load_from_file("download_list.json")

  # 清除未完成的队列标记
  download_list.cleanup_queue()

  # 重置所有任务状态
  download_list.reset()

  # 保存结果
  download_list.save_to_file("download_list.json") # 测试
  print(download_list)
