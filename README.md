# 成交额异常筛选系统

这是一个用于筛选A股市场中成交额异常股票的Web应用系统。系统每天晚上22:00自动运行，分析所有A股数据，找出成交额显著放大的股票。

## 功能特点

- 自动分析所有A股数据
- 筛选市值大于30亿的股票
- 分析最近60天的成交额数据
- 识别成交额异常放大的股票（相对30天或60天平均值）
- Web界面展示分析结果
- 每日自动更新

## 安装要求

- Python 3.8+
- 依赖包：见 requirements.txt

## 安装步骤

1. 克隆代码库：
```bash
git clone https://github.com/wuxiuyi306/stock-volume-analyzer.git
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
python app.py
```

## 使用说明

1. 访问 http://localhost:5000 查看主页
2. 点击日期卡片查看当天的分析结果
3. 在结果页面可以查看详细的股票信息
4. 点击"详情"按钮查看单个股票的具体数据

## 自动化部署

系统配置为每天晚上22:00自动运行分析程序，并更新结果。结果会自动保存在data目录下，按日期命名。

## 技术栈

- 后端：Python + Flask
- 数据分析：efinance
- 前端：Bootstrap + DataTables
- 定时任务：APScheduler

## 注意事项

- 确保系统时间正确设置为北京时间
- 需要稳定的网络连接以获取股票数据
- 建议在服务器上部署时使用进程管理工具（如Supervisor）

## 许可证

MIT License
