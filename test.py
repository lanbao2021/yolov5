import os
import re
import pymysql

def getIPv6Address():
    output = os.popen("ipconfig /all").read()
    # print(output)
    result = re.findall(r"(([a-f0-9]{1,4}:){7}[a-f0-9]{1,4})", output, re.I)
    return result[0][0]


def updateIPv6():
    # 远程连接mysql数据库
    con = pymysql.connect(
        host='106.54.72.189',
        port=3306,
        database='weixin',
        user='root',
        password='lantongxue',
        charset='utf8')

    # 创建一个cursor用于执行sql语句
    cur = con.cursor()
    ipv6 = getIPv6Address()
    update = "UPDATE keyword SET reply='" + ipv6 + "' WHERE getkey='ipv6';"
    cur.execute(update)
    cur.close()


if __name__ == "__main__":
    # print(getIPv6Address()
    updateIPv6()

