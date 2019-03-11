# 导入函数库
import jqdata               #导入聚宽函数库
from six import StringIO    #使用聚宽readfile函数

import numpy as np
import pandas as pd

from datetime import timedelta,date
from random import randint

import statsmodels.api as sm

import random

import warnings
warnings.filterwarnings("ignore")

# 初始化函数，设定基准等等
def initialize(context):
    # 设定基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 输出内容到日志 log.info()
    log.info('初始函数开始运行且全局只运行一次')
    # 过滤掉order系列API产生的比error级别低的log
    # log.set_level('order', 'error')

    ### 设置账户类型 ###

    ## 设置五个账户，各账户资金为策略总资金的五分之一
    init_cash = context.portfolio.starting_cash/5

    set_subportfolios([SubPortfolioConfig(cash=init_cash, type='stock'),\
                       SubPortfolioConfig(cash=init_cash, type='stock'),\
                       SubPortfolioConfig(cash=init_cash, type='stock'),\
                       SubPortfolioConfig(cash=init_cash, type='stock'),\
                       SubPortfolioConfig(cash=init_cash, type='stock')])

    ### 股票、期货、融资融券相关设定使用默认设置，这里暂不做设定 ###
    # 确定相应的轮次顺序
    # 用于控制操作仓位
    g.account_num = 0

    run_daily(Choose_Account,time='before_open', reference_security='000300.XSHG')

    # 设置全局变量
    # 用于控制底部资源池的变量
    body = read_file("Pair_config0.csv")
    g.pairs_info0 = pd.read_csv(StringIO(body))
    # 设置全局变量
    body = read_file("Pair_config1.csv")
    g.pairs_info1 = pd.read_csv(StringIO(body))
    # 设置全局变量
    body = read_file("Pair_config2.csv")
    g.pairs_info2 = pd.read_csv(StringIO(body))
    # 设置全局变量
    body = read_file("Pair_config3.csv")
    g.pairs_info3 = pd.read_csv(StringIO(body))
    # 设置全局变量
    body = read_file("Pair_config4.csv")
    g.pairs_info4 = pd.read_csv(StringIO(body))

    g.buy_list = []
    g.sell_list = []


    # 每日收盘手根据生成购买股票列表
    run_daily(after_market_close,time='after_close', reference_security='000300.XSHG')

    # 每日交易
    run_daily(rebalance, time='09:45', reference_security='000300.XSHG') 
    
    # 更新信息
    run_daily(Update_Pairs, time='09:40', reference_security='000300.XSHG') 
    

def Choose_Account(context):
    # 确定交易的序号，按照序号选择相应的账户进行交易
    g.account_num += 1 

    if g.account_num >= 5:
        g.account_num = 0

    # 平均仓位
    account_avg(context)
    
def account_avg(context):
    # 对不同的子账户进行金额平均分配
    value_total = context.portfolio.subportfolios[0].total_value + \
                    context.portfolio.subportfolios[1].total_value + \
                    context.portfolio.subportfolios[2].total_value + \
                    context.portfolio.subportfolios[3].total_value + \
                    context.portfolio.subportfolios[4].total_value
    
    value_avg = value_total / 5
    transfer_cash(0,1,context.portfolio.subportfolios[0].total_value - value_avg)
    transfer_cash(1,2,context.portfolio.subportfolios[1].total_value - value_avg)
    transfer_cash(2,3,context.portfolio.subportfolios[2].total_value - value_avg)
    transfer_cash(3,4,context.portfolio.subportfolios[3].total_value - value_avg)
    transfer_cash(4,0,context.portfolio.subportfolios[4].total_value - value_avg)


## 收盘后运行函数  
def after_market_close(context):
    # 生成购买股票列表
    
    g.buy_list = []
    g.sell_list = []

    # 通过g.account_num获取需要操作的底层数据
    g.buy_list,g.sell_list  = get_balance_list(context,g.account_num)
    

def get_balance_list(context,account_num):
    
    # 函数内需要操作的底层数据
    pairs_info = pd.DataFrame()

    # 确定操作的空间
    if account_num == 0:
        pairs_info = g.pairs_info0
    elif account_num == 1:        
        pairs_info = g.pairs_info1
    elif account_num == 2:        
        pairs_info = g.pairs_info2
    elif account_num == 3:        
        pairs_info = g.pairs_info3
    elif account_num == 4:        
        pairs_info = g.pairs_info4
    
    # 返回的数据
    sell_list = []
    buy_list = []
    
    day_count = 200
    end_date =  context.current_dt.strftime('%Y-%m-%d')

    # 存储股票的价格原始数据
    for i in range(0,pairs_info.shape[0]):
        s1 = pairs_info.iloc[i,:]['P1']
        s2 = pairs_info.iloc[i,:]['P2']
        stocks = [s1,s2]

        df_stocks = pd.DataFrame()

        # 开始获取收盘价信息，按列进行
        for stock_name in stocks:
            stock_price = get_price(stock_name, count = day_count, end_date=end_date, frequency='daily', fields='close',fq = "pre")
            stock_price_pd = pd.DataFrame(data = np.array(stock_price['close']),columns = [stock_name])
            df_stocks = pd.concat([df_stocks,stock_price_pd],axis = 1)
        
        # 新增一列ratio，作为价格的比例
        df_stocks['ratio'] = None 
        df_stocks['ratio'] = np.array(df_stocks[s1])/np.array(df_stocks[s2])
        
        # 计算z_score
        df_stocks['z_score'] = None 
        df_stocks['z_score'] = (pd.rolling_mean(df_stocks['ratio'], 2) - pd.rolling_mean(df_stocks['ratio'], 60))/pd.rolling_std(df_stocks['ratio'], 60)

        # 开始判断加入买卖列表
        if df_stocks.iloc[-1,:]['z_score'] < -1:
            buy_list.append(s1)
        elif df_stocks.iloc[-1,:]['z_score'] > 1:
            buy_list.append(s2)

        # 开始判断加入买卖列表
        if df_stocks.iloc[-1,:]['z_score'] > -0.8:
            sell_list.append(s1)
        elif df_stocks.iloc[-1,:]['z_score'] < 0.8:
            sell_list.append(s2)
            
    return buy_list,sell_list
 
 
def rebalance(context):
    if len(g.sell_list) != 0:
        for sec in g.sell_list:
            log.info("$$卖出股票：%s"%(str(sec)))
            order_target_value(sec, 0,side='long', pindex=g.account_num)
    
    # 按照买入股票列表下单
    if len(g.buy_list) != 0:
        per_share =  context.portfolio.subportfolios[g.account_num].total_value/5
        for sec in g.buy_list:
            log.info("$$买入股票：%s"%(str(sec)))
            order_target_value(sec,per_share, side='long', pindex=g.account_num)   


def Update_Pairs(context):
    
    pairs_info = pd.DataFrame()
    read_pairs_pd = pd.DataFrame()
    
    # 确定操作的空间
    if g.account_num == 0:
        pairs_info = g.pairs_info0
        body = read_file("Pair_config0.csv")
        read_pairs_pd = pd.read_csv(StringIO(body))
    elif g.account_num == 1:        
        pairs_info = g.pairs_info1
        body = read_file("Pair_config1.csv")
        read_pairs_pd = pd.read_csv(StringIO(body))
    elif g.account_num == 2:        
        pairs_info = g.pairs_info2
        body = read_file("Pair_config2.csv")
        read_pairs_pd = pd.read_csv(StringIO(body))
    elif g.account_num == 3:        
        pairs_info = g.pairs_info3
        body = read_file("Pair_config3.csv")
        read_pairs_pd = pd.read_csv(StringIO(body))
    elif g.account_num == 4:        
        pairs_info = g.pairs_info4
        body = read_file("Pair_config4.csv")
        read_pairs_pd = pd.read_csv(StringIO(body))

        
    # 如果行数不一致，说明数据有更新，重新赋值，并且清仓
    if pairs_info.shape[0] != read_pairs_pd.shape[0]:
        # 确定操作的空间
        if g.account_num == 0:
            g.pairs_info0 = read_pairs_pd
        elif g.account_num == 1:        
            g.pairs_info1 = read_pairs_pd
        elif g.account_num == 2:        
            g.pairs_info2 = read_pairs_pd
        elif g.account_num == 3:        
            g.pairs_info3 = read_pairs_pd
        elif g.account_num == 4:        
            g.pairs_info4 = read_pairs_pd
        
        
        
        for sec in context.portfolio.subportfolios[g.account_num].positions.keys():
            log.info("$$配对信息更新，清仓股票：%s"%(str(sec)))
            order_target_value(sec, 0)
            
            
            
            
