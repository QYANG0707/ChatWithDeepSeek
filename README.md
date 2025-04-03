# Sublime插件,DeekSeek多轮对话功能
  *
  *
  *
  
## 安装方法
将ChatWithDeepSeek文件夹添加到 sublime安装目录/data/Packages 目录中即可

## 功能描述
* 创建临时对话,对话内容不进行记录
  <br><br>
* 创建记录对话,在对话结束后,关闭对话视图后,对话内容会自动保存<br>
  保存路径为 sublime安装目录/data/Packages/ChatWithDeepSeek/temp 目录中
  <br><br>
* 导入对话,对话内容以json数据格式保存并导入
  ```json
  {
    "data":
    [
        {
            "role": "user",
            "content": "简易回答,世界上最高的山",
            "time": "2025-04-03 14:54:02"
        },
        {
            "role": "assistant",
            "content": "珠穆朗玛峰（海拔8848.86米）。",
            "time": "2025-04-03 14:54:08"
        },
        {
            "role": "user",
            "content": "简易回答,第二高的",
            "time": "2025-04-03 14:54:11"
        },
        {
            "role": "assistant",
            "content": "乔戈里峰（K2，海拔8611米）。",
            "time": "2025-04-03 14:54:17"
        }
    ]
  }
##  配置
首选项-Package Settings-ChatWithDeepSeek-setting
* api_key:前往DeepSeek官网,注册账号-充值金额-创建apikey,将创建的apikey复制到配置文件即可
* name:在对话时显示的用户名称
* ai_name:在对话时显示的ai名称
* interval:对话时用户和ai对话时之前的空行数量
* show_line_number:是否显示对话行号
* prefix:每一次对话时的自定义前缀,该语句将被添加到每一次提问的最前方

