# ChannelTool
<b>地震分量选择工具</b>
>基于pyQT的分量选择工具

### Installation
>需要python3.6及以上

    1. 安装依赖： pip install -r requirements.txt
    
### ussage
>1.根据台网名和经纬度范围，爬取台站列表
    
    示例见download_iris.py，结果会保存为xlsx格式

>2.使用可视化工具选取分量
        
    选择1中保存的xlsx文件，点击开始下载，程序将爬取各个站点的分量信息。
    爬取结果会存为json，使用数据加载按钮可直接加载爬取的数据。
    选择完成后，结果会保存为csv文件。可对接SeisDQ模块从iris申请数据
