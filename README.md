## Private Label工具集

- 确保操作系统上安装有Python3，双击init.bat初始化

- FBM Tracking抓取及上传
  + python update_fba_tracking.py -u ${seller.email} -i ${fba.order.ids} -o ${tracking.output}
  + 首次使用需要手工登录、输入两步验证码
  + 输入文件格式：${confirm.date yyyy-MM-dd} {fba.order.id} {source.order.id}，分隔符可以是空格、制表符等

- FBM下单
  + python fulfill_fba_orders.py -u ${seller.email} -s ${sku} -i ${fba.orders} -o ${fulfill.results}
  + 首次使用需要手工登录、输入两步验证码
  + 输入文件格式： FBA单号、Quantity、客人姓名、客人地址1、客人地址2、城市、州、邮编、国家（只处理US）、电话。用制表符分割，因为姓名、地址中均可能包含空格