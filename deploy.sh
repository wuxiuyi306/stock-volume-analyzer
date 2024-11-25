#!/bin/bash

# 安装依赖
pip3 install -r requirements.txt

# 创建systemd服务
cat > /etc/systemd/system/stock-analyzer.service << EOL
[Unit]
Description=Stock Analyzer Service
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/stock-analyzer
Environment=PYTHONPATH=/var/www/stock-analyzer
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# 重新加载systemd配置
systemctl daemon-reload

# 启用并启动服务
systemctl enable stock-analyzer
systemctl restart stock-analyzer

echo "部署完成！"
