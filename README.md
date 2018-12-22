# PairsTrade



## step1

文件名：Get_Data.ipynb
运行环境：joinquant 研究环境
功能：从平台中取出数据，存入csv中，待下一步研究

结果：
csv文件，其中包含价格信息，列名为股票编码，行名为日期


## step2

文件名：PickPairs.ipynb
运行环境：jupyter notebook
功能：利用step1中提出的数据进行配对分析，主要通过Pvalue、Correlation检查序列相关性

结果
csv文件，其中包含配对信息、相关系数、Pvalue、残差