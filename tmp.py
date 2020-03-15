# -*- coding:utf-8 -*-
import sys
import os
# 添加本地module包路径
sys.path.append(os.path.abspath('module'))
from collections import defaultdict
from cacu_sentiment_score import sentiment_caculate
from mysql_operate import csv2mysql
from optparse import OptionParser
import pandas as pd
import jieba
import shutil
import re

def read_csv(path):
    # 读取csv文件
    df = pd.read_csv(path,encoding='utf-8')
    df.columns = df.columns.str.strip(' ')#去除列名中的空格
    print(df.columns)
    return df

def data_preprocess(df):
    # 数据预处理
    df = df.drop_duplicates()  #去重
    df['评论内容'] = df['评论内容'].fillna('99999') #将空值所在行填充为99999 
    df['手机型号'] = df['手机型号'].fillna('99999') 
    row_comment_index = df[df.评论内容=='99999'].index.tolist()  #找出评论空值所在行索引
    row_type_index = df[df.手机型号=='99999'].index.tolist()   #找出手机型号所在行索引
    df["手机型号"]=df.apply(lambda x:format_phone_name(x['手机型号'],' '),axis=1)
    row_index = row_comment_index + row_type_index
    df = df.drop(row_index)
    print("预处理结束")
    return df

def format_phone_name(full_name,sub):
    """格式化手机名称
    将手机原名称'Apple iPhone 11 (A2223) 128GB 黑色 移动联通电信4G手机 双卡双待'
    转化为'Apple_iPhone_11'的格式，以便于后续存储和处理
    """
    full_name = str(full_name)
    index = full_name.find(sub)   #第一次出现的位置
    index2=full_name.find(sub,index+1)  #第二次出现的位置
    index3=full_name.find(sub,index2+1)  #第三次出现的位置
    new_name = full_name[:index3].translate(str.maketrans('/ \\','___'))
    return new_name


def merge_comment(df,path):
    # 合并同款手机的评论内容
    try:
        shutil.rmtree(path)
        print(path+"目录已经清空")
    except:
        print(path+"目录不存在，进行创建")
    os.mkdir(path)
    file_name = ''
    phone_name = df.loc[0,'手机型号']
    try:
        for index,row in df.iterrows():
            if phone_name != row['手机型号']:
                df.loc[index,'手机型号'] = phone_name
                print(phone_name+"写入成功")
                phone_name = row['手机型号']
            file_name = path+os.sep+phone_name+'.txt'
            file = open(file_name, 'a', encoding='utf-8')
            file.write(row['评论内容'])
            file.close()
    except Exception as e:
        print("手机评论写入文件出错，原因是： "+e)
    
    
def cacu_comment_score(path_sti,path_com,df):
    # 读取合并的txt文本，将其分词处理，计算总得分（内置在setiment_score函数中）
    print("开始计算得分")
    sti_cacu = sentiment_caculate(path_sti)
    content_path=path_com
    filenames = os.listdir(content_path)
    df = df.drop_duplicates(subset=['手机型号'],keep='first')#手机型号去重
    df['评论得分'] = 0 #初始化自增列

    for filename in filenames:
        phone_name = os.path.splitext(filename)[0]
        file_path = content_path+os.sep+filename
        with open(file_path,encoding='utf-8') as f:
            read_data=f.read()
            score = sti_cacu.setiment_score(read_data)
            print('index:  '+str(df.index[df['手机型号'] == phone_name]))
            df.loc[df.index[df['手机型号'] == phone_name], '评论得分'] = score
        print(filename+"计算完毕")

    tmp_df = df.drop(['评论内容','会员级别','点赞数','回复数','得分','购买时间'],axis=1)
    print("处理过后的数据前五行如下：")
    print(tmp_df.head())
    return tmp_df

def save_to_csv(path,df):
    # 文件保存到csv表中
    df.to_csv(path,na_rep='NULL',sep = ',',index=False,header = True,encoding = 'utf_8_sig')
    print(path+"保存成功")

def save_to_mysql(user,pas,dbname,dbtable,df):
    # 文件保存到数据库
    
    print("已保存到数据库")

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-u","--jobs", default="root", dest="user", help="mysql用户名，默认为root")
    parser.add_option("-p", "--pass", default="",dest="password", help="mysql密码，默认为空")
    parser.add_option("-d", "--Database", default="jd_comment",type="string",dest="database",help="数据库名称")
    parser.add_option("-t", "--table", default="product_info",type="string",dest="table",help="表名")
    parser.add_option("-o", "--output", default='data//result.csv', help="保存路径，默认为data//result.csv")
    
    (options,args) = parser.parse_args()
    db_user = options.user
    db_password = options.password
    db_name = options.database
    db_table = options.table
    save_path = options.output 

    sti_path = r'motion_analysis'
    source_path = r"data//tmp_test_data.csv"
    comment_path = r"input_comment"
    comment_df = read_csv(source_path)
    format_comment = data_preprocess(comment_df)
    merge_comment(format_comment,comment_path)
    ans_df = cacu_comment_score(sti_path,comment_path,format_comment)
    # 文件保存到csv
    ans_df.to_csv(save_path,na_rep='NULL',sep = ',',index=False,header = True,encoding = 'utf_8_sig')
    # 文件保存到数据库
    csv2mysql(db_user,db_password,db_name,db_table,ans_df)
    print("保存成功")