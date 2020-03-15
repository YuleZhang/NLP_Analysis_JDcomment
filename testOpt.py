'''
@Author: YuleZhang
@Description: 测试命令行
@Date: 2020-03-15 10:00:30
'''
from optparse import OptionParser

if __name__ == "__main__":
    parser =OptionParser()

    parser.add_option("-D", "--Database", action="store",type="string",dest="database",help="请输入测试数据库名称")

    parser.add_option("-T", "--Table",action="store",type="string",dest="table",help="Please input test table")

    parser.add_option("-C", "--Column",action="store",type="string",dest="column",help="Please input test column")

    parser.add_option("-U" ,"--Url", action="store",type="string",dest="url",help="Please input test url")

    (options,args) = parser.parse_args()

    print(options)