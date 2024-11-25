from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接配置
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# 创建数据库连接URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 创建数据库引擎
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# 声明基类
Base = declarative_base()

class StockAnalysis(Base):
    """股票分析结果表"""
    __tablename__ = 'stock_analysis'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    stock_code = Column(String(10), nullable=False)
    stock_name = Column(String(50), nullable=False)
    latest_amount = Column(Float, nullable=False)  # 最新成交额
    avg_amount_30 = Column(Float, nullable=False)  # 30日均额
    avg_amount_60 = Column(Float, nullable=False)  # 60日均额
    ratio_30 = Column(Float, nullable=False)      # 相对30日均额倍数
    ratio_60 = Column(Float, nullable=False)      # 相对60日均额倍数
    current_price = Column(Float, nullable=False)  # 当前价格
    change_percent = Column(Float, nullable=False) # 涨跌幅
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'date': self.date.strftime('%Y-%m-%d'),
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'latest_amount': self.latest_amount,
            'avg_amount_30': self.avg_amount_30,
            'avg_amount_60': self.avg_amount_60,
            'ratio_30': self.ratio_30,
            'ratio_60': self.ratio_60,
            'current_price': self.current_price,
            'change_percent': self.change_percent
        }

def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
