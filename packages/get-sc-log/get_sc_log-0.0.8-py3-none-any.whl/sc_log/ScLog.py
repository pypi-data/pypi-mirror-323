import re
import requests
import time
from datetime import datetime, timedelta,timezone
import json

def get_original_log(data):
    """默认查询最近5d,返回最原始的日记信息"""
    # 从输入数据中提取参数
    project = data["project"]
    logStore = data["logStore"]
    url = "https://xjp-logger-service-s-backend-sysop.inshopline.com/api/getLogs"
    headers = {"Content-Type": "application/json"}
    line = data.get("line", 2)
    offset = data.get("offset", 0)
    # 计算时间范围
    time_15_minutes_ago = datetime.now() - timedelta(days=5)
    timestamp_15_minutes_ago = int(time_15_minutes_ago.timestamp())
    start_time = timestamp_15_minutes_ago
    end_time = int(time.time())
    # 覆盖默认时间范围，如果提供了自定义时间
    start_time = data.get("from",start_time)
    end_time = data.get("to", end_time)
    # 设置请求参数
    params = {"project": project, "logStore": logStore, "from": start_time, "to": end_time,"line":line,"offset":offset}
    # 添加查询条件
    if "query" in data:
        query = data["query"]
        params["query"] = query
    response = requests.get(url, params=params, headers=headers).json()
    return response


def get_msg_log(data):
    """处理返回的日记，"""
    response = get_original_log(data)
    logs = response["data"]["logs"]
    # print("logs",logs)
    m_contents = [log["mLogItem"]["mContents"] for log in logs]
    # print(json.dumps(m_contents))
    log_msg_list = []
    for cotent in m_contents:
        log_msg = {}
        for t in cotent:
            if t["mKey"]=="msg":
                log_msg["msg"] = t["mValue"]
            elif t["mKey"]=="traceId":
                log_msg["traceId"] = t["mValue"]
        log_msg_list.append(log_msg)
    return log_msg_list

def get_http_data(http_data):
    fields = {}
    patterns = {
        'method': r'(?<=method: )\s*(\w+)',
        'uri': r'(?<=uri: )\s*(?P<uri>.+)',
        'requestHeader': r'(?<=requestHeader: )\s*(\{.*?\})',
        'requestParams': r'(?<=requestParams: )\s*(\{.*?\})',
        'requestBody': r'(?<=requestBody: )(\{[^}]+\})[\s\S]*?(?=responseCode)',
        'responseCode': r'(?<=responseCode: )\s*(\d+)',
        'responseHeader': r'(?<=responseHeader: )\s*(\{.*?\})',
        'responseBody': r'(?<=responseBody: )\s*(\{.*?\})[\s\S]*?(?=error)'
    }
    for i in patterns.keys():
        # print(i)
        match = re.search(patterns[i], http_data)
        if match:
            result = match.group(0)
            fields[i] = result
            # print("%s:"%i,result)
    # print(json.dumps(fields))
    #JSON 字符串进行序列化
    # print(fields["requestBody"])
    fields['requestHeader'] = json.loads(fields['requestHeader'])
    fields['requestParams'] = json.loads(fields['requestParams'])
    fields['requestBody'] = json.loads(fields['requestBody'])
    fields['responseHeader'] = json.loads(fields['responseHeader'])
    fields['responseBody'] = json.loads(fields['responseBody'])
    return fields



def sc_assert(data):
    #data = 格式如下
    # assert_data = [{"actual": "123", "expect": "123", "type": "eq"}, {"actual": "1234", "expect": "123", "type": "in"},
    #                {"actual": "123", "expect": "123"}]
    for i in data:
        actual = i["actual"]
        expect = i["expect"]
        type= i.get("type","eq")
        # data_type = i.get("data_type","str")
        if type=="eq":
            try:
                assert actual==expect
            except AssertionError:
                return "实际值:%s,期望值：%s，断言失败"%(actual,expect)
        elif type == "neq":
            try:
                assert actual != expect
            except AssertionError:
                return "实际值:%s,期望值：%s，断言失败" % (actual, expect)
        elif type=="in":
            try:
                assert actual in expect or expect in actual
            except AssertionError:
                return "实际值:%s,期望值：%s，断言失败" % (actual, expect)
        elif type == "notin":
            try:
                assert actual not in expect or expect not in actual
            except AssertionError:
                return "实际值:%s,期望值：%s，断言失败" % (actual, expect)
        elif type == "gt":
            try:
                assert actual>expect
            except AssertionError:
                return "实际值:%s,期望值：%s，断言失败" % (actual, expect)
        elif type == "egt":
            try:
                assert actual >= expect
            except AssertionError:
                return "实际值:%s,期望值：%s，断言失败" % (actual, expect)
        elif type == "lt":
            try:
                assert actual < expect
            except AssertionError:
                return "实际值:%s,期望值：%s，断言失败" % (actual, expect)
        elif type == "elt":
            try:
                assert actual <= expect
            except AssertionError:
                return "实际值:%s,期望值：%s，断言失败" % (actual, expect)



def get_current_utc_time():
    # 获取当前 UTC 时间
    current_utc_time = datetime.now(timezone.utc)
    # 格式化为 YYYY-MM-DDTHH:MM
    formatted_time = current_utc_time.strftime('%Y-%m-%dT%H:%M')
    return formatted_time


def str_to_stamp(time_string,format="%Y-%m-%dT%H:%M:%S.%fZ"):
    # 解析时间字符串为 datetime 对象
    # 使用 strptime 方法并指定格式
    if "Z" in time_string:
        dt_utc = datetime.strptime(time_string, format).replace(tzinfo=timezone.utc)
        # 格式化为所需的字符串格式
        time_string = dt_utc.strftime(format)[:-3] + '+00:00'
        # dt = datetime.strptime(time_string, format)
        # # 转换为时间戳
        # timestamp = int(dt.timestamp()*1000)
        # return timestamp
    elif "+" in time_string:
        #fromisoformat 只支持三位数字（即毫秒）
        time_string = time_string[:-7]  # 去掉最后的时区偏移
        time_string = time_string+"+00:00"  # 加上时区偏移
        # print(time_string)

    dt = datetime.fromisoformat(time_string)
    return int(dt.timestamp() * 1000)




def get_stamp_time(data):
    #拿到指定时间的时间戳
    num = data.get("num",5)
    time_type = data.get("time_type","add")
    unit = data.get("unit","minutes")
    # 获取当前 UTC 时间
    now = datetime.now()
    if time_type not in {"add", "sub"}:
        raise ValueError("Invalid time_type. Use 'add' or 'sub'.")
    # if time_type=="sub":
    #     num=-num
    #     print(num)
    stamp_time = now+timedelta(**{unit:num if time_type=="add" else -num})
    return int(stamp_time.timestamp()*1000)









if __name__=="__main__":
    # data = {"project":"sl-aquaman-sl-user-center-sz","logStore":"sl-aquaman-sl-user-center_test"}
    # data["query"] = 'af63259b535e60f4aaf358fed72b5811 and http and msg: "completed." and msg: open_host and msg: jobs '
    # log_msg = get_msg_log(data)
    # fields = get_http_data(log_msg[1]["msg"])
    # print(fields)
    # assert_data = [{'actual': 'POST', 'expect': 'POST'}, {'actual': 'application/json', 'expect': 'application/json'}, {'actual': 'app_token', 'expect': 'app_token'}, {'actual': '200', 'expect': "200"}, {'actual': 'app_token', 'expect': 'app_token'}, {'actual': 'report', 'expect': 'report'}, {'actual': {"en":"Export Product Sales Report","th":"รายงานสินค้าที่ขาย","vi":"Báo cáo doanh số sản phẩm","zh-cn":"汇出商品销售报表","zh-hant":"匯出商品銷售報表"}, 'expect': {"en":"Export Product Sales Report","th":"รายงานสินค้าที่ขาย","vi":"Báo cáo doanh số sản phẩm","zh-cn":"汇出商品销售报表","zh-hant":"匯出商品銷售報表"}}, {'actual': 'in_progress', 'expect': 'in_progress'}, {'actual': 'system', 'expect': 'system'}, {'actual': 1, 'expect': 0, 'type': 'gt'}, {'actual': '2025-01-20T01:59:42.711Z', 'expect': '2025-01-20T02:00', 'type': 'in'}, {'actual': 'PUT', 'expect': 'PUT', 'type': 'in'}, {'actual': 'PUT', 'expect': 'PUT', 'type': 'eq'}, {'actual': 'done', 'expect': 'done', 'type': 'eq'}, {'actual': '2025-01-20T01:59:48.531Z', 'expect': '2025-01-20T02:00', 'type': 'in'}, {'actual': 10, 'expect': 0, 'type': 'gt'}, {'actual': 0, 'expect': 0, 'type': 'eq'}, {'actual': ['https://dev-img-shoplineapp-com.s3-ap-southeast-1.amazonaws.com/post/6229a7baea70642a8b65ebda_product_sales_1737338383590.csv'], 'expect': [], 'type': 'neq'}, {'actual': '678dae0f34faf5003cc5f9b4', 'expect': '678dae0f34faf5003cc5f9b4', 'type': 'eq'}]
    # assert_data = [{'actual': '2025-01-20T01:59:42.711Z', 'expect': '2025-01-20T01:58',"type":"gt","data_type":"time"},{'actual': '2025-01-20T01:59:42.711Z', 'expect': '2025-01-20T02:05',"type":"lt","data_type":"time"}]
    # res = sc_assert(assert_data)
    # print(res)
    time_str = '2025-01-24T07:55:33.8350+00:00'
    # time_str = "2025-01-24T07:14:42.711"
    actual = str_to_stamp(time_str)
    data = {"num":10,"time_type":"add","unite":"minutes"}
    expect_future = get_stamp_time(data)
    data["time_type"] = "sub"
    expect_before = get_stamp_time(data)
    print("actual",actual)
    print("expect_before",expect_before)
    assert_data = [{'actual': actual, 'expect': expect_future,"type":"lt"},{'actual': actual, 'expect': expect_before,"type":"gt"}]
    res = sc_assert(assert_data)
    print(res)





