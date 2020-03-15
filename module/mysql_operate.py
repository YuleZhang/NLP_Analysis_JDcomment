'''
@Author: YuleZhang
@Description: 完成将dataframe数据类型存储到数据库中
@Date: 2020-03-10 08:44:47
'''
# 一个根据pandas自动识别type来设定table的type
import pandas as pd
import pymysql

def make_table_sql(df):
    df['用户ID'] = df['用户ID'].apply(str)
    columns = df.columns.tolist()
    types = df.ftypes
    # 添加id 制动递增主键模式
    make_table = []
    
    for item in columns:
        if 'int' in types[item]:
            char = item + ' INT'
        elif 'float' in types[item]:
            char = item + ' FLOAT'
        elif 'object' in types[item]:
            char = item + ' VARCHAR(255)'           
        elif 'datetime' in types[item]:
            char = item + ' DATETIME'            
        make_table.append(char)
    print(','.join(make_table))
    return ','.join(make_table)

# csv 格式输入 mysql 中

def csv2mysql(user,password,db_name, table_name, df):
    """这个函数用来批量插入数据
    Arguments:
        user {str} -- 登陆用户名
        password {str} -- 登陆密码
        db_name {str} -- 数据库名称
        table_name {str} -- 数据库名称
        df {dataframe} -- 要存的数据
    """
    print("开始将数据导入数据库中")
    # 连接database
    conn = pymysql.connect(host="localhost", user=user,password=password)
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    try:
        # 创建database
        cursor.execute('CREATE DATABASE IF NOT EXISTS {}'.format(db_name))
        # 选择连接database
        conn.select_db(db_name)
        # 创建table
        cursor.execute('DROP TABLE IF EXISTS {}'.format(table_name))
        cursor.execute('CREATE TABLE {}({})'.format(table_name,make_table_sql(df)))
        # 提取数据转list 这里有与pandas时间模式无法写入因此换成str 此时mysql上格式已经设置完成
        values = df.values.tolist()
        # 根据columns个数
        s = ','.join(['%s' for _ in range(len(df.columns))])
        # executemany批量操作 插入数据 批量操作比逐个操作速度快很多
        insert_sql = 'INSERT INTO {} VALUES ({})'.format(table_name,s)
        cursor.executemany(insert_sql, values)
        conn.commit()
        conn.close()
        print("数据插入成功")
    except Exception as e:
        print("数据库存入错误，请检查连接")
        print(e)

#运行测试
if __name__ == "__main__":
    path = r"data//test_result.csv"
    test_df = pd.read_csv(path,encoding='utf-8',header=0)
    test_df.columns = test_df.columns.str.strip(' ')#去除列名中的空格
    csv2mysql('root','','jd_comment','product_info',test_df)