## Private Label工具集

- FBM Tracking抓取及上传
  + 确保操作系统上安装有Python3，双击init.bat初始化
  + python update_fba_tracking.py -u ${seller.email} -i ${fba.order.ids} -o ${tracking.output}
  + 首次使用需要手工登录、输入两步验证码
  + 输入文件格式：${confirm.date yyyy-MM-dd} {fba.order.id} {source.order.id}，分隔符可以是空格、制表符等