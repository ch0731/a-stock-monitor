#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热点板块API
"""

import os
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from board_data import get_hot_sectors, format_sectors_for_ai
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/api/hot/sectors')
def hot_sectors_api():
    """获取热点板块"""
    try:
        sectors = get_hot_sectors()
        # 转换为列表格式
        result = []
        for sector_name, stocks in sectors.items():
            if stocks:
                result.append({
                    'name': sector_name,
                    'count': len(stocks),
                    'stocks': stocks[:10]  # 每板块只返回前10只
                })
        return jsonify({'status': 'success', 'data': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/hot/sectors/display')
def hot_sectors_display():
    """获取热点板块（用于展示）"""
    try:
        text = format_sectors_for_ai()
        return f'<pre>{text}</pre>'
    except Exception as e:
        return f'Error: {e}'

if __name__ == '__main__':
    print("启动热点板块API服务...")
    print("访问 http://localhost:5001/api/hot/sectors")
    app.run(port=5001, debug=False)
