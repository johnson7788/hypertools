#!/usr/bin/env python
# coding: utf-8
# # Mushroom 数据集 Hypertools
import matplotlib.pyplot as plt
import pandas as pd
import hypertools as hyp

def read_data():
    # ### 使用pandas读取数据
    data = pd.read_csv('data/mushrooms.csv')
    data.head()
    # ### 弹出 poisonous/non-poisonous 的类别列
    class_labels = data.pop('class')
    return data, class_labels

def plot_simple():
    # ### 现在让我们把高维度据转换为一个numpy数组并传递给hyperplot，在低维空间中绘制高维度据。
    geo = hyp.plot(data, fmt='.',show=True) # 如果特征的数量大于3，默认为3D绘图。
    # ### 从上面的图中可以看出，这个数据中有多个集合。除了描述性特征外，这个数据集还包含了蘑菇是否有毒。 这些集合对蘑菇是否有毒有影响吗？ 让我们尝试根据蘑菇是否有毒来给这些点着色，以了解这一点。
    geo = hyp.plot(data, '.', group=class_labels, legend=list(set(class_labels)))
    plt.show()

def plot_cluster23():
    # ##从上面的图中可以看出，蘑菇的集群带有关于它们是否有毒的信息（红色是指无毒的，蓝色是指有毒的）。看起来也有一些明显的集群是有毒/无毒的。
    #
    # ###让我们使用hypertools的 "聚类 "特征，用k-means拟合程序发现这些类别。

    # 聚类出23个，然后绘图
    geo = hyp.plot(data, '.', n_clusters=23)

    # 获取这些类别
    cluster_labels = hyp.cluster(data, n_clusters=23)

    # hyp.plot(data, 'o', point_colors=cluster_labels, ndims=2)

def plot_cluster2():
    # 聚类出2个，然后绘图
    # geo = hyp.plot(data, '.', n_clusters=2)

    # 获取这些类别
    cluster_labels = hyp.cluster(data, n_clusters=2)
    # ### 题外话：我们可以使用调色板参数来改变调色板。 Hypertools支持matplotlib和seaborn的调色板。
    geo = hyp.plot(data, '.', group=cluster_labels, palette="deep")
    plt.show()


def plot_reduce_dim():
    # ### Hypertools默认使用PCA来降低维度，但也有其他方法来进行降维。 让我们尝试用各种技术进行降维，但保持集群标签不变。
    # ## ICA降维
    geo_ica = hyp.plot(data, '.', group=class_labels, legend=list(set(class_labels)), reduce='FastICA',  ndims=3)
    # ## t-SNE降维
    geo_tsne = hyp.plot(data, '.', group=class_labels, legend=list(set(class_labels)), reduce='TSNE', ndims=3)
    # ### 现在，这是一些有趣的结构......让我们把所有三个plot相互比较，以对比它们的效果，看看什么是
    geo = hyp.plot(data, '.', group=cluster_labels, reduce='PCA', title='PCA')
    geo_ica.plot(group=cluster_labels, legend=None, title='ICA')
    geo_tsne.plot(group=cluster_labels, legend=None, title='TSNE')

def plot_diff_cluster():
    # ### PCA投影具有不同的k值
    geo = hyp.plot(data, '.', reduce='PCA', title='PCA')
    # ## ICA降维
    geo_ica = hyp.plot(data, '.', group=class_labels, legend=list(set(class_labels)), reduce='FastICA',  ndims=3)
    # ## t-SNE降维
    geo_tsne = hyp.plot(data, '.', group=class_labels, legend=list(set(class_labels)), reduce='TSNE', ndims=3)
    ks = [3,6,9,12,15]
    for k in ks:
        geo.plot(n_clusters=k, title='k=' + str(k))
        plt.show()
    # ### ICA projection with different k values
    for k in ks:
        geo_ica.plot(n_clusters=k, title='k=' + str(k))
        plt.show()
    # ### t-SNE projection with different k values
    for k in ks:
        geo_tsne.plot(n_clusters=k, title='k=' + str(k))
        plt.show()

if __name__ == '__main__':
    data, class_labels = read_data()
    # plot_simple()
    # plot_diff_cluster()
    plot_cluster2()