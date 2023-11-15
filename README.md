# 小红书主推品识别

采用doccano平台进行数据标注，基于百度飞桨平台paddlenlp的information_extraction做训练，得到适用于小红书文章的信息提取模型。模型可以有效从一千字以内的文本中提取出美妆相关的“品牌”和“产品”信息。

经过测试，模型召回率达到97.78%（2195/2245）。

## 实现功能

小红书主推品识别

输出数据会保存到所在目录/data文件夹下。

## 环境配置

    python版本:3.8.17
```
pip install -r requirement.txt
```
## 进入指令
```
screen -r streamlit
```
## 网址

http://192.168.1.155:8501

## 开启
```
screen -S streamlit
conda activate my_paddlenlp
streamlit run temp.py
```
## 关闭
```
 screen -X -S streamlit quit
```
