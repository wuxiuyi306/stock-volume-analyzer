from flask import Flask, render_template
import efinance as ef
import pandas as pd
from datetime import datetime
import schedule
import time
import threading
from models import StockAnalysis, init_db, get_db
from sqlalchemy.orm import Session
from typing import Generator

app = Flask(__name__)

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
        
        # 获取数据库会话
        db: Session = next(get_db())
        current_date = current_time.date()
        
        try:
            print("开始分析每只股票的成交额...")
            for _, stock in stocks.iterrows():
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
                        # 创建数据库记录
                        analysis = StockAnalysis(
                            date=current_date,
                            stock_code=stock_code,
                            stock_name=stock['股票名称'],
                            latest_amount=latest_amount,
                            avg_amount_30=avg_amount_30,
                            avg_amount_60=avg_amount_60,
                            ratio_30=latest_amount / avg_amount_30,
                            ratio_60=latest_amount / avg_amount_60,
                            current_price=float(stock['最新价']),
                            change_percent=float(stock['涨跌幅'])
                        )
                        db.add(analysis)
                        
                except Exception as e:
                    print(f"处理股票 {stock_code} 时出错: {str(e)}")
                    continue
            
            # 提交所有更改
            db.commit()
            print("分析完成，数据已保存到数据库")
            return True
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error in analyze_stock: {str(e)}")
        return False

@app.route('/')
def index():
    db: Session = next(get_db())
    try:
        # 获取所有分析日期
        dates = db.query(StockAnalysis.date).distinct().order_by(StockAnalysis.date.desc()).all()
        dates = [date[0].strftime('%Y-%m-%d') for date in dates]
        return render_template('index.html', dates=dates)
    finally:
        db.close()

@app.route('/result/<date>')
def result(date):
    db: Session = next(get_db())
    try:
        # 获取指定日期的分析结果
        analysis_date = datetime.strptime(date, '%Y-%m-%d').date()
        results = db.query(StockAnalysis).filter(StockAnalysis.date == analysis_date).all()
        return render_template('result.html', date=date, data=[r.to_dict() for r in results])
    finally:
        db.close()

def run_schedule():
    """运行定时任务"""
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    print("初始化数据库...")
    init_db()
    
    print("启动定时任务...")
    # 设置每天12:00运行分析任务
    schedule.every().day.at("12:00").do(analyze_stock)
    
    # 在新线程中运行定时任务
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.daemon = True
    schedule_thread.start()
    
    print("启动Web服务器...")
    app.run(host='0.0.0.0', port=5000)
