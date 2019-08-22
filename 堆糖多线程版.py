import os
import json
import re
import requests
from urllib import request
import threading
from queue import Queue

dir_path = 'D://堆糖2/'
if not os.path.exists(dir_path):
    os.mkdir(dir_path)

class Procuder(threading.Thread):
    def __init__(self,page_queue,img_queue,*args,**kwargs):
        super(Procuder,self).__init__(*args,**kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.page_queue.empty():
                break
            url = self.page_queue.get()  # 先进先出模式，第一个是start=0
            self.parse_page(url)

    def parse_page(self,url):
        web = requests.get(url)
        # web.encoding='gbk'
        html = web.text
        my_dict = json.loads(html)
        # for i in my_dict['data']['object_list']:
        #     img_url = i['photo']['path']
        #     filename = img_url.split('/')[-1]
        #     self.img_queue.put((img_url,filename))
        img_list = re.findall(r'"path":"(.+?)"',html)
        for img in img_list:
            filename = img.split('/')[-1]
            self.img_queue.put((img,filename))

class Consumer(threading.Thread):
    def __init__(self,page_queue,img_queue,*args,**kwargs):
        super(Consumer,self).__init__(*args,**kwargs)
        self.page_queue = page_queue
        self.img_queue = img_queue

    def run(self):
        while True:
            if self.page_queue.empty() and self.img_queue.empty():
                break
            img_url, filename = self.img_queue.get()
            request.urlretrieve(img_url, dir_path + filename)


def main(keyword):
    page_queue = Queue(10)
    img_queue = Queue(200)
    for page in range(0,10):
        url = 'https://www.duitang.com/napi/blog/list/by_search/?kw=%s&type=feed&start=%d' % (keyword, 24*page)
        page_queue.put(url)  # 将URL添加到线程队列去

    for i in range(3):
        t = Procuder(page_queue,img_queue)
        t.start()

    for i in range(10):
        t = Consumer(page_queue,img_queue)
        t.start()

if __name__ == '__main__':
    keyword = input('请输入需要查找的关键字，如：fate：')
    main(keyword)