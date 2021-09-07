![Hypertools logo](images/hypercube.png)


"_To deal with hyper-planes in a 14 dimensional space, visualize a 3D space and say 'fourteen' very loudly.  Everyone does it._" - Geoff Hinton


![Hypertools example](images/hypertools.gif)

## Overview
HyperTools是为了促进基于[降维](https://en.wikipedia.org/wiki/Dimensionality_reduction)的高维度据的可视化探索而设计的。 
其基本pipeline是输入一个高维度据集（或一系列高维度据集），并在一个单一的函数调用中，降低数据集的维度并创建一个图。 
该软件包建立在许多熟悉的工具之上，包括[matplotlib](https://matplotlib.org/)、[scikit-learn](http://scikit-learn.org/)和[seaborn](https://seaborn.pydata.org/) 。 
我们的软件包最近在[Kaggle的No Free Hunch博客](http://blog.kaggle.com/2017/04/10/exploring-the-structure-of-high-dimensional-data-with-hypertools-in-kaggle-kernels/)
上得到了介绍。 
如果想了解总体情况，你可能会发现[这个讲座](https://www.youtube.com/watch?v=hb_ER9RGtOM)很有用，[MIND暑期学校](https://summer-mind.github.io)。


## Try it!

单击badge以启动带有样本用途的Binder实例：
[![Binder](http://mybinder.org/badge.svg)](http://mybinder.org:/repo/contextlab/hypertools-paper-notebooks)

或者

Jupyter notebooks [repo](https://github.com/ContextLab/hypertools-paper-notebooks)
论文[paper](https://arxiv.org/abs/1701.08290).

## 安装

安装最新版本

`pip install hypertools`

要直接从GitHub安装最新的不稳定版本，请运行：

`pip install -U git+https://github.com/ContextLab/hypertools.git`

或者，将repository克隆到本地计算机：

`git clone https://github.com/ContextLab/hypertools.git`

然后，导航到文件夹并键入：

`pip install -e .`

注意：如果你一直在使用0.5.0的开发版本，请清除你的数据缓存（/Users/yourusername/hypertools_data）。

## Requirements

+ python 2.7, 3.5+
+ PPCA>=0.0.2
+ scikit-learn>=0.18.1
+ pandas>=0.18.0
+ seaborn>=0.8.1
+ matplotlib>=1.5.1
+ scipy>=0.17.1
+ numpy>=1.10.4
+ future
+ requests
+ deepdish
+ pytest (for development)
+ ffmpeg (for saving animations)

如果从github安装（而不是pip），你也必须安装需求。
`pip install -r requirements.txt`

### Troubleshooting
如果你在MacOS系统上遇到与安装deepdish(hdf5)有关的错误，请尝试使用[homebrew](https://brew.sh/)直接安装hdf5。
```
$ brew tap homebrew/science
$ brew install hdf5
```
and then re-start the installation.

## 文档

请查看我们的[readthedocs](http://hypertools.readthedocs.io/en/latest/)页面，了解更多的文档、完整的API细节和更多的例子。

## Citing

We wrote a short JMLR paper about HyperTools, which you can read [here](http://jmlr.org/papers/v18/17-434.html), or you can check out a (longer) preprint [here](https://arxiv.org/abs/1701.08290). We also have a repository with example notebooks from the paper [here](https://github.com/ContextLab/hypertools-paper-notebooks).

Please cite as:

`Heusser AC, Ziman K, Owen LLW, Manning JR (2018) HyperTools: A Python toolbox for gaining geometric insights into high-dimensional data.  Journal of Machine Learning Research, 18(152): 1--6.`

Here is a bibtex formatted reference:

```
@ARTICLE {,
    author  = {Andrew C. Heusser and Kirsten Ziman and Lucy L. W. Owen and Jeremy R. Manning},    
    title   = {HyperTools: a Python Toolbox for Gaining Geometric Insights into High-Dimensional Data},    
    journal = {Journal of Machine Learning Research},
    year    = {2018},
    volume  = {18},	
    number  = {152},	
    pages   = {1-6},	
    url     = {http://jmlr.org/papers/v18/17-434.html}	
}
```

## Contributing

[![Join the chat at https://gitter.im/hypertools/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/hypertools/Lobby)

If you'd like to contribute, please first read our [Code of Conduct](https://www.mozilla.org/en-US/about/governance/policies/participation/).

For specific information on how to contribute to the project, please see our [Contributing](https://github.com/ContextLab/hypertools/blob/master/CONTRIBUTING.md) page.
## Testing

[![Build Status](https://travis-ci.org/ContextLab/hypertools.svg?branch=master)](https://travis-ci.org/ContextLab/hypertools)


To test HyperTools, install pytest (`pip install pytest`) and run `pytest` in the HyperTools folder

## 示例

See [here](http://hypertools.readthedocs.io/en/latest/auto_examples/index.html) for more examples.

## 绘图

```
import hypertools as hyp
hyp.plot(list_of_arrays, '.', group=list_of_labels)
```

![Plot example](images/plot.gif)

## 对齐

```
import hypertools as hyp
hyp.plot(list_of_arrays, align='hyper')
```

### BEFORE

![Align before example](images/align_before.gif)

### AFTER</center>

![Align after example](images/align_after.gif)


## 聚类

```
import hypertools as hyp
hyp.plot(array, '.', n_clusters=10)
```

![Cluster Example](images/cluster_example.png)


## Describe

```
import hypertools as hyp
hyp.tools.describe(list_of_arrays, reduce='PCA', max_dims=14)
```
![Describe Example](images/describe_example.png)
