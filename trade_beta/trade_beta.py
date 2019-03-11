# ���뺯����
import jqdata               #����ۿ�����
from six import StringIO    #ʹ�þۿ�readfile����

import numpy as np
import pandas as pd

from datetime import timedelta,date
from random import randint

import statsmodels.api as sm

import random

import warnings
warnings.filterwarnings("ignore")

# ��ʼ���������趨��׼�ȵ�
def initialize(context):
    # �趨��׼
    set_benchmark('000300.XSHG')
    # ������̬��Ȩģʽ(��ʵ�۸�)
    set_option('use_real_price', True)
    # ������ݵ���־ log.info()
    log.info('��ʼ������ʼ������ȫ��ֻ����һ��')
    # ���˵�orderϵ��API�����ı�error����͵�log
    # log.set_level('order', 'error')

    ### �����˻����� ###

    ## ��������˻������˻��ʽ�Ϊ�������ʽ�����֮һ
    init_cash = context.portfolio.starting_cash/5

    set_subportfolios([SubPortfolioConfig(cash=init_cash, type='stock'),\
                       SubPortfolioConfig(cash=init_cash, type='stock'),\
                       SubPortfolioConfig(cash=init_cash, type='stock'),\
                       SubPortfolioConfig(cash=init_cash, type='stock'),\
                       SubPortfolioConfig(cash=init_cash, type='stock')])

    ### ��Ʊ���ڻ���������ȯ����趨ʹ��Ĭ�����ã������ݲ����趨 ###
    # ȷ����Ӧ���ִ�˳��
    # ���ڿ��Ʋ�����λ
    g.account_num = 0

    run_daily(Choose_Account,time='before_open', reference_security='000300.XSHG')

    # ����ȫ�ֱ���
    # ���ڿ��Ƶײ���Դ�صı���
    body = read_file("Pair_config0.csv")
    g.pairs_info0 = pd.read_csv(StringIO(body))
    # ����ȫ�ֱ���
    body = read_file("Pair_config1.csv")
    g.pairs_info1 = pd.read_csv(StringIO(body))
    # ����ȫ�ֱ���
    body = read_file("Pair_config2.csv")
    g.pairs_info2 = pd.read_csv(StringIO(body))
    # ����ȫ�ֱ���
    body = read_file("Pair_config3.csv")
    g.pairs_info3 = pd.read_csv(StringIO(body))
    # ����ȫ�ֱ���
    body = read_file("Pair_config4.csv")
    g.pairs_info4 = pd.read_csv(StringIO(body))

    g.buy_list = []
    g.sell_list = []


    # ÿ�������ָ������ɹ����Ʊ�б�
    run_daily(after_market_close,time='after_close', reference_security='000300.XSHG')

    # ÿ�ս���
    run_daily(rebalance, time='09:45', reference_security='000300.XSHG') 
    
    # ������Ϣ
    run_daily(Update_Pairs, time='09:40', reference_security='000300.XSHG') 
    

def Choose_Account(context):
    # ȷ�����׵���ţ��������ѡ����Ӧ���˻����н���
    g.account_num += 1 

    if g.account_num >= 5:
        g.account_num = 0

    # ƽ����λ
    account_avg(context)
    
def account_avg(context):
    # �Բ�ͬ�����˻����н��ƽ������
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


## ���̺����к���  
def after_market_close(context):
    # ���ɹ����Ʊ�б�
    
    g.buy_list = []
    g.sell_list = []

    # ͨ��g.account_num��ȡ��Ҫ�����ĵײ�����
    g.buy_list,g.sell_list  = get_balance_list(context,g.account_num)
    

def get_balance_list(context,account_num):
    
    # ��������Ҫ�����ĵײ�����
    pairs_info = pd.DataFrame()

    # ȷ�������Ŀռ�
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
    
    # ���ص�����
    sell_list = []
    buy_list = []
    
    day_count = 200
    end_date =  context.current_dt.strftime('%Y-%m-%d')

    # �洢��Ʊ�ļ۸�ԭʼ����
    for i in range(0,pairs_info.shape[0]):
        s1 = pairs_info.iloc[i,:]['P1']
        s2 = pairs_info.iloc[i,:]['P2']
        stocks = [s1,s2]

        df_stocks = pd.DataFrame()

        # ��ʼ��ȡ���̼���Ϣ�����н���
        for stock_name in stocks:
            stock_price = get_price(stock_name, count = day_count, end_date=end_date, frequency='daily', fields='close',fq = "pre")
            stock_price_pd = pd.DataFrame(data = np.array(stock_price['close']),columns = [stock_name])
            df_stocks = pd.concat([df_stocks,stock_price_pd],axis = 1)
        
        # ����һ��ratio����Ϊ�۸�ı���
        df_stocks['ratio'] = None 
        df_stocks['ratio'] = np.array(df_stocks[s1])/np.array(df_stocks[s2])
        
        # ����z_score
        df_stocks['z_score'] = None 
        df_stocks['z_score'] = (pd.rolling_mean(df_stocks['ratio'], 2) - pd.rolling_mean(df_stocks['ratio'], 60))/pd.rolling_std(df_stocks['ratio'], 60)

        # ��ʼ�жϼ��������б�
        if df_stocks.iloc[-1,:]['z_score'] < -1:
            buy_list.append(s1)
        elif df_stocks.iloc[-1,:]['z_score'] > 1:
            buy_list.append(s2)

        # ��ʼ�жϼ��������б�
        if df_stocks.iloc[-1,:]['z_score'] > -0.8:
            sell_list.append(s1)
        elif df_stocks.iloc[-1,:]['z_score'] < 0.8:
            sell_list.append(s2)
            
    return buy_list,sell_list
 
 
def rebalance(context):
    if len(g.sell_list) != 0:
        for sec in g.sell_list:
            log.info("$$������Ʊ��%s"%(str(sec)))
            order_target_value(sec, 0,side='long', pindex=g.account_num)
    
    # ���������Ʊ�б��µ�
    if len(g.buy_list) != 0:
        per_share =  context.portfolio.subportfolios[g.account_num].total_value/5
        for sec in g.buy_list:
            log.info("$$�����Ʊ��%s"%(str(sec)))
            order_target_value(sec,per_share, side='long', pindex=g.account_num)   


def Update_Pairs(context):
    
    pairs_info = pd.DataFrame()
    read_pairs_pd = pd.DataFrame()
    
    # ȷ�������Ŀռ�
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

        
    # ���������һ�£�˵�������и��£����¸�ֵ���������
    if pairs_info.shape[0] != read_pairs_pd.shape[0]:
        # ȷ�������Ŀռ�
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
            log.info("$$�����Ϣ���£���ֹ�Ʊ��%s"%(str(sec)))
            order_target_value(sec, 0)
            
            
            
            
