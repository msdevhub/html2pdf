import requests
import json
from datetime import datetime
import calendar
import pytz

# 设置请求头
headers = {
    'Accept-Language': 'zh-CN,zh',
    'content-type': 'application/json;charset=utf8',
}
now = datetime.now()

def get_holidays(start_date):
 
  query = start_date.strftime('%Y年%-m月')

  # 设置请求参数
  params = {
      'query': query,
      'co': '',
      'resource_id': 39043,
      't': datetime.timestamp(now)*1000,  # JavaScript的Date.now()返回的是毫秒级时间戳
      'ie': 'utf8',
      'oe': 'utf8',
      # 'cb': 'op_aladdin_callback',
      'format': 'json',
      'tn': 'wisetpl',
      # 'cb': 'here'
  }
  print(params)

  # 发送GET请求
  response = requests.get('https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php', headers=headers, params=params)

  # 提取并处理数据
  data = response.json()
  # print(response.text)
  almanac_data = data['data'][0]['almanac']

  # 获取almanac_data中的status等于1的数据，还需要判断没有status的情况
  holidays = [a for a in almanac_data if 'status' in a and a['status'] == '1']


  # 创建时区对象
  utc = pytz.utc
  local_tz = pytz.timezone('Asia/Shanghai')  # 将此处替换为你需要的时区

  for a in holidays:
      # 解析日期时间字符串
      date = datetime.strptime(a['oDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
      # 将其设置为UTC时区
      date = date.replace(tzinfo=utc)
      # 转换为本地时区
      date = date.astimezone(local_tz)

      a['key'] = date.strftime('%Y.%m.%d')

  # print('holidays', [[a['month'],a['day'],a['key']] for a in holidays])
  return holidays