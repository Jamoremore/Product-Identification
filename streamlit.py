import streamlit as st
from paddlenlp import Taskflow
import os
import shutil
import pandas as pd
from pandas import isnull
import datetime
from io import BytesIO

# schema = ['主推产品']
# my_ie = Taskflow("information_extraction", schema=schema, task_path='./model')

#
# @st.cache_resource
# def get_my_ie():
#
#     return my_ie


def remove_non_gb2312(text):
    res = []
    for char in text:
        try:
            char.encode('GB2312')
            res.append(char)
        except UnicodeEncodeError:
            pass
    return ''.join(res)


def get_opt(text):
    # 删除错误文件
    model_path = "./model/static"
    if os.path.exists(model_path):
        shutil.rmtree(model_path)
    schema = ['主推产品']
    my_ie = Taskflow("information_extraction", schema=schema, task_path='./model')
    opt = "########原文########\n"+text+"\n\n########输出结果########\n"

    cnt = 1

    # my_ie = get_my_ie()
    # 删除特殊符号
    text = remove_non_gb2312(text)
    temp = my_ie(text)
    if '主推产品' in temp[0]:
        for j in temp[0]['主推产品']:
            # 删除低概率的判定结果
            if j['probability'] >= 0.5:
                opt = opt + "id:" + str(cnt) + "\n    text:" + j['text'] + "\n    prob:" + str(j['probability']) + '\n'
                cnt = cnt + 1
    print(opt)
    with open('data/logs.txt', 'a', encoding='utf-8') as ins_test_file:
        current_time = datetime.datetime.now()
        ins_test_file.write(current_time.strftime("%Y/%m/%d %H:%M:%S\n") + opt + '\n\n')

    return opt


def process_text(title, content):
    text = title + '\n' + content
    return get_opt(text)


def get_label(r1, r2, my_ie):
    if pd.isnull(r1):
        r1 = ""
    if pd.isnull(r2):
        r2 = ""
    text = remove_non_gb2312(r1+'\n'+r2)
    temp = my_ie(text)
    opt = ""
    cnt = 1
    if '主推产品' in temp[0]:
        for j in temp[0]['主推产品']:
            # 删除低概率的判定结果
            if j['probability'] >= 0.5 and len(j['text']) < 50:
                opt = opt + "text" + str(cnt) + ":" + j['text'] + ";\n"
                cnt = cnt + 1
    return opt


def process_file(df):
    # 删除错误文件
    model_path = "./model/static"
    if os.path.exists(model_path):
        shutil.rmtree(model_path)
    schema = ['主推产品']
    my_ie = Taskflow("information_extraction", schema=schema, task_path='./model')

    # .read() 会返回 bytes, 所以我们要把它转换成字符串
    # 逐行读取第一列和第二列的内容，计算f(col1, col2)，并将结果保存到第三列
    df[2] = df.apply(lambda row: get_label(row[0], row[1], my_ie), axis=1)

    # 保存结果到本地
    current_time = datetime.datetime.now()
    df.to_excel('data/' + current_time.strftime("%Y_%m_%d %H_%M_%S") + '.xlsx', index=False)
    # 绘制结果
    st.write(df)

    # 将DataFrame转化为Excel并存储在BytesIO对象中
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)
    # 重置指针位置
    excel_file.seek(0)

    # 使用st.download_button创建一个可以下载Excel文件的按钮
    st.download_button(
        label="下载Excel文件",
        data=excel_file,
        file_name='output.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    return ""


# 创建文本框，用户可以输入长篇文章
user_input1 = st.text_input("请输入您的文章标题")
# 创建文本框，用户可以输入长篇文章
user_input2 = st.text_area("请输入您的文章")

# 创建文件上传功能，允许用户上传.xlsx文件
uploaded_file = st.file_uploader("请选择要上传的文件（按照第一行为列名，第一列为标题，第二列为内容的格式）", type="xlsx")

# 检查是否有文件上传
if uploaded_file is not None:
    # file_contents = uploaded_file.read()
    file_contents = pd.read_excel(uploaded_file)

# 创建两个结果显示区域
result_from_text = st.empty()
result_from_file = st.empty()

# 创建两个按钮，分别处理文本输入和文件上传
if (user_input1 != "" or user_input2 != "") and st.button('处理输入的文本'):
    result_from_text.text("text processing... please wait.")
    result_from_text.text(process_text(user_input1, user_input2))   # 假设process_text函数会返回处理结果

if uploaded_file is not None and st.button('处理上传的文件'):
    result_from_file.text("doc processing... please wait.")
    result_from_file.text(process_file(file_contents)) # 假设process_file函数会返回处理结果
