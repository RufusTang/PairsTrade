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

结果：
csv文件，其中包含配对信息、相关系数、Pvalue、残差


## step3

文件名：Fill_Info.ipynb
运行环境：joinquant 研究环境
功能：使用聚宽函数对相应的股票进行行业的划分，并添加名字
提示：为了节约时间，可以提前删除一些不相关的配对信息

结果：
csv文件，其中行业信息

## step4

手工对step3的数据进行筛选
筛选标准：
1、相关性大于0.8
2、Pvalue小于0.05
3、同行业
4、其他相关性要求

结果：
生成具有同行业强相关性的配对交易配置文件

配置文件格式：
两列，一列为P1，一列为P2
同时每个行业选择一对即可，避免行业风险

## step5
文件名：Trade.py
运行环境：joinquant 交易环境
功能：使用聚宽平台进行模拟交易

结果：
交易结果信息


## Algorithm Upgrade
文件命：Trade_Beta.py
附件：pair_config0.csv ~ pair_config5.csv

运行环境：joinquant 交易环境
功能：使用聚宽平台进行模拟交易
优化点：
1. 分组分为5组，分类进行管理，以2-3周为周期性进行更新
2. 每天进行交易，提升效率
