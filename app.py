from flask import Flask, render_template
import efinance as ef
import pandas as pd
from datetime import datetime
import json
import os
from tqdm import tqdm
import schedule
import time
import threading

app = Flask(__name__)

# 确保数据目录存在
if not os.path.exists('data'):
    os.makedirs('data')

def analyze_stock():
    try:
        current_time = datetime.now()
        print(f"开始执行股票分析... 当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("开始获取A股实时行情...")
        # 获取所有A股实时行情
        stocks = ef.stock.get_realtime_quotes()
        
        print("筛选市值大于30亿的股票...")
        # 将总市值转换为数值类型
        stocks['总市值'] = pd.to_numeric(stocks['总市值'], errors='coerce')
        # 筛选市值大于30亿的股票
        stocks = stocks[stocks['总市值'] > 3000000000]
        print(f"共找到 {len(stocks)} 只满足条件的股票")
        
        result_list = []
        
        print("开始分析每只股票的成交额...")
        for _, stock in tqdm(stocks.iterrows(), total=len(stocks)):
            try:
                stock_code = stock['股票代码']
                
                # 获取历史数据
                history = ef.stock.get_quote_history(stock_code)
                if len(history) < 60:
                    continue
                    
                # 计算最近60天和30天的平均成交额
                last_60_days = history.tail(60)
                last_30_days = history.tail(30)
                
                avg_amount_60 = last_60_days['成交额'].mean()
                avg_amount_30 = last_30_days['成交额'].mean()
                latest_amount = history.iloc[-1]['成交额']
                
                # 判断是否符合条件
                if latest_amount > avg_amount_30 * 3 or latest_amount > avg_amount_60 * 3:
                    result_list.append({
                        '股票代码': stock_code,
                        '股票名称': stock['股票名称'],
                        '最新成交额': latest_amount,
                        '30日均额': avg_amount_30,
                        '60日均额': avg_amount_60,
                        '相对30日均额倍数': latest_amount / avg_amount_30,
                        '相对60日均额倍数': latest_amount / avg_amount_60,
                        '当前价格': stock['最新价'],
                        '涨跌幅': stock['涨跌幅']
                    })
            except Exception as e:
                print(f"处理股票 {stock_code} 时出错: {str(e)}")
                continue
        
        print("分析完成，保存结果...")
        # 保存结果
        if result_list:
            current_date = datetime.now().strftime('%Y-%m-%d')
            with open(f'data/{current_date}.json', 'w', encoding='utf-8') as f:
                json.dump(result_list, f, ensure_ascii=False, indent=2)
            print(f"找到 {len(result_list)} 只成交额异常的股票")
        else:
            print("没有找到符合条件的股票")
            
        return True
    except Exception as e:
        print(f"Error in analyze_stock: {str(e)}")
        return False

@app.route('/')
def index():
    # 获取所有结果文件
    result_dates = []
    if os.path.exists('data'):
        for file in os.listdir('data'):
            if file.endswith('.json'):
                date = file.replace('.json', '')
                result_dates.append(date)
    result_dates.sort(reverse=True)
    return render_template('index.html', dates=result_dates)

@app.route('/result/<date>')
def result(date):
    try:
        with open(f'data/{date}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return render_template('result.html', date=date, data=data)
    except:
        return "数据不存在"

@app.route('/detail/<date>/<code>')
def detail(date, code):
    try:
        with open(f'data/{date}.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        stock_data = next((item for item in data if item['股票代码'] == code), None)
        if stock_data:
            return render_template('detail.html', stock=stock_data, date=date)
        return "股票数据不存在"
    except:
        return "数据不存在"

def run_schedule():
    """运行定时任务"""
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    print("启动定时任务...")
    # 设置每天22点运行分析任务
    schedule.every().day.at("22:00").do(analyze_stock)
    
    # 在新线程中运行定时任务
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.daemon = True
    schedule_thread.start()
    
    print("启动Web服务器...")
    app.run(host='0.0.0.0', port=5000)
