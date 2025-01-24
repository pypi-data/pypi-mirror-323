#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Time : 2024/10/17 上午午10:40
# @Author : shancx
# @File : __init__.py
# @email : shanhe12@163.com
import matplotlib.pyplot as plt
def getimg(img, cmap='gray', title='Image',path="."):
    img = img.squeeze()  # 去掉 batch 维度并转换为 numpy 数组
    plt.imshow(img, cmap='gray')
    plt.title(f"Image ")
    plt.axis('off')  # 不显示坐标轴
    plt.savefig(f"./test.png")