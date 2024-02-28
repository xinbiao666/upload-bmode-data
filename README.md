### 用于解析b超数据并将数据以json格式发送给服务端

1、安装项目依赖 pip install -r requirements.txt<br />
2、启动前先运行init_structure.py生成文件结构<br />
3、生成成功后运行main.py启动程序<br />

### 关于配置文件

例如：stxgy = http://197.198.199.221:9288
key为卫生院拼音缩写，value为对应所要配置的值
在current内切换配置当前程序所要运行的卫生院
