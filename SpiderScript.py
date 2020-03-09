from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from queue import Queue
import threading
import time
import requests
import json
import csv

'''
1. 创建 URL队列, 响应队列, 数据队列 在init方法中
2. 在生成URL列表中方法中,把URL添加URL队列中
3. 在请求页面的方法中,从URL队列中取出URL执行,把获取到的响应数据添加响应队列中
4. 在处理数据的方法中,从响应队列中取出页面内容进行解析, 把解析结果存储数据队列中
5. 在保存数据的方法中, 从数据队列中取出数据,进行保存
6. 开启几个线程来执行上面的方法
'''

def run_forever(func):
    def wrapper(obj):
        while True:
            func(obj)
    return wrapper


class QiubaiSpider(object):

    def __init__(self,csv_path):
        ua=UserAgent()
        self.headers = {
            'Accept': '*/*',
            'User-Agent':ua.random,
            'Referer':"https://item.jd.com/100000177760.html#comment"
        }
        self.product_page_Num = 10
        self.path = csv_path
        self.sale_url = 'https://club.jd.com/comment/productCommentSummaries.action?my=pinglun&referenceIds={}'
        self.price_url = 'https://p.3.cn/prices/mgets?skuIds=J_{}'
        self.product_url = 'https://list.jd.com/list.html?cat=9987,653,655&page={}&sort=sort_rank_asc&trans=1&JL=6_0_0&ms=10#J_main'
        self.comment_url = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&&productId={0}&score=0&sortType=5&page={1}&pageSize=10&isShadowSku=0&fold=1'
        #self.url_pattern = 'https://www.qiushibaike.com/8hr/page/{}/'
        # url 队列
        self.url_queue = Queue()
        # 响应队列
        self.page_queue = Queue()
        # 数据队列
        self.data_queue = Queue()


    def add_url_to_queue(self,product_page):
        # 把URL添加url队列中,先选择前10页，600款手机
        for i in range(1, product_page):
            response = requests.get(url=self.product_url.format(i), headers=self.headers)
            soup = BeautifulSoup(response.text, "lxml")
            sum_good = soup.find(id="plist")
            try:
                for li in sum_good.find_all('li'):
                    good_name = li.find_all('div',class_='p-name')
                    if len(good_name):
                        href = good_name[0].find('a').get('href')
                        tmp = href.rfind('/')
                        productId = href[tmp+1:-5] #截取完整的productId
                        #先访问第0页获取最大页数，再进行循环遍历
                        max_page = self.get_comment_pages_num(productId)
                        max_page = min(50,max_page)#每种商品取50条
                        if(max_page==-1):
                            continue
                        print("每种商品爬%s页数据"%max_page)
                        for pageNum in range(0,int(max_page)):
                            #print(self.comment_url.format(productId,pageNum))
                            self.url_queue.put(self.comment_url.format(productId,pageNum))
                            #break
                    #break
                time.sleep(1)
            except Exception as e:
                print("错误原因："+e)
                print("5s后重试")
                time.sleep(5)

    def get_comment_pages_num(self,product):
        max_page = -1
        try:
            tmp_url = self.comment_url.format(product,0)
            print(tmp_url)
            response = requests.get(url=tmp_url, headers=self.headers)
            jsonData = response.text
            startLoc = jsonData.find('{')
            jsonData = jsonData[startLoc:-2]
            jsonData = json.loads(jsonData)
            max_page = int(jsonData['maxPage'])
        except Exception as e:
            print("获取评论页数出错，错误原因是")
            print(e)
        return max_page

    @run_forever
    def add_page_to_queue(self):
        ''' 发送请求获取数据 '''
        url = self.url_queue.get()
        response = requests.get(url, headers=self.headers)
        time.sleep(1)
        print("请求页面: "+url)
        #print('响应码: '+response.status_code)
        if response.status_code != 200:
            self.url_queue.put(url)
        else:
            self.page_queue.put(response.text)
        # 完成当前URL任务
        self.url_queue.task_done()

    @run_forever
    def add_dz_to_queue(self):
        '''根据页面内容使用bs4解析数据, 获取段子列表'''
        jsonData = self.page_queue.get()
        sig_comment = []
        proId = ""
        price = ""
        sale = ""
        pageLen = ""
        startLoc = jsonData.find('{')
        jsonData = jsonData[startLoc:-2]
        jsonData = json.loads(jsonData)
        try:
            #为了获取价格需要单独请求特殊url，参数为productId
            proId = jsonData['productCommentSummary']['productId']
            #print("productId = %s"%proId)
            #print("请求url为：%s"%self.price_url.format(proId))
            # 获取产品价格
            response = requests.get(self.price_url.format(proId), headers=self.headers)
            priceInfo = json.loads(response.text)
            price = priceInfo[0]['p']
            # 获取产品销量
            response = requests.get(url=self.sale_url.format(proId), headers=self.headers)
            salesInfo = json.loads(response.text)
            sale = salesInfo['CommentsCount'][0]['CommentCount']
            pageLen = len(jsonData['comments'])
        except Exception as e:
            time.sleep(2)
            print("页面信息分析错误,错误原因：%s"%e)
            return
        for j in range(0,pageLen):
            #userId = jsonData['comments'][j]['id']#用户ID
            content = jsonData['comments'][j]['content'].strip()#评论内容
            levelName = jsonData['comments'][j]['plusAvailable']#会员级别
            voteCount = jsonData['comments'][j]['usefulVoteCount']#点赞数
            replyCount = jsonData['comments'][j]['replyCount']#回复数目
            starStep = jsonData['comments'][j]['score']#得分
            creationTime = jsonData['comments'][j]['creationTime']#购买时间
            referenceName = jsonData['comments'][j]['referenceName'].strip()#手机型号
            sig_comment.append(proId)#每一行数据
            sig_comment.append(content)
            sig_comment.append(levelName)
            sig_comment.append(voteCount)
            sig_comment.append(replyCount)
            sig_comment.append(starStep)
            sig_comment.append(price)
            sig_comment.append(creationTime)
            sig_comment.append(referenceName)
            sig_comment.append(sale)
            self.data_queue.put(sig_comment)
            sig_comment = []
        self.page_queue.task_done()

    @run_forever
    def save_dz_list(self):
        '''把段子信息保存到文件中'''
        dz_list = self.data_queue.get()
        file = open(path,'a',newline = '',encoding='utf-8-sig')
        writer = csv.writer(file)
        writer.writerow(dz_list)
        file.close()
        self.data_queue.task_done()
        #print('存入成功')

    def run_use_more_task(self, func, count=1):
        '''把func放到线程中执行, count:开启多少线程执行'''
        for i in range(0, count):
            t = threading.Thread(target=func)
            t.setDaemon(True)
            t.start()

    def run(self):
        # 开启线程执行上面的几个方法
        url_t = threading.Thread(target=self.add_url_to_queue,args=(self.product_page_Num,))
        url_t.setDaemon(True)
        url_t.start()

        time.sleep(5)
        self.run_use_more_task(self.save_dz_list, 2)
        self.run_use_more_task(self.add_dz_to_queue, 2)
        self.run_use_more_task(self.add_page_to_queue, 2)
        

        # 使用队列join方法,等待队列任务都完成了才结束
        self.url_queue.join()
        self.page_queue.join()
        self.data_queue.join()

def init_csv(file_name,head):
    file = open(file_name,'a',newline = '',encoding='utf-8-sig')
    writer = csv.writer(file)
    writer.writerow(head)
    file.close()

if __name__ == '__main__':
    path = 'data/JDComment_data.csv'
    csv_head = ['用户ID','评论内容','会员级别','点赞数','回复数','得分','价格','购买时间','手机型号','销量']
    init_csv(path,csv_head)
    qbs = QiubaiSpider(path)
    qbs.run()
