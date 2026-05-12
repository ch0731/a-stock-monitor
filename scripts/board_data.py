#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热点板块数据获取 - 使用腾讯财经接口
"""

import os
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'

import requests
from typing import List, Dict


def get_hot_stocks(min_pct: float = 3.0) -> List[Dict]:
    """
    获取热点股票（涨幅>3%）
    
    Args:
        min_pct: 最小涨幅
    
    Returns:
        股票列表
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 获取所有A股代码
    codes = []
    for i in range(600000, 604000):
        codes.append(f'sh{i}')
    for i in range(4000):
        codes.append(f'sz{i:06d}')
    
    all_stocks = []
    
    # 批量获取
    for i in range(0, min(500, len(codes)), 50):
        batch = codes[i:i+50]
        try:
            r = requests.get(f'https://qt.gtimg.cn/q={",".join(batch)}', 
                           proxies={'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}, 
                           headers=headers, timeout=10)
            
            for line in r.text.split('\n'):
                if '=' not in line:
                    continue
                data = line.split('=')[1].strip('";\n\r').split('~')
                if len(data) >= 6:
                    try:
                        pct = float(data[5])
                        if abs(pct) > min_pct:
                            all_stocks.append({
                                'code': data[2],
                                'name': data[1],
                                'price': data[3],
                                'pct': pct
                            })
                    except:
                        pass
        except:
            pass
    
    return all_stocks


def get_hot_sectors() -> Dict[str, List[Dict]]:
    """获取热点板块及核心标的"""
    
    stocks = get_hot_stocks(min_pct=3.0)
    
    # 定义板块关键词
    sector_keywords = {
        'AI科技': ['科技', '芯', '光', '软件', '智', 'AI', '数', '云', '网', '算'],
        '新能源车': ['新能', '锂', '电', '车', '汽', '能', '源'],
        '医药医疗': ['药', '医', '疗', '生', '康'],
        '军工': ['军', '航', '防', '装'],
        '有色金属': ['金', '铜', '铝', '稀土', '矿'],
        '电力电网': ['电', '网'],
    }
    
    sectors = {k: [] for k in sector_keywords}
    
    for stock in stocks:
        for sector, keywords in sector_keywords.items():
            if any(kw in stock['name'] for kw in keywords):
                sectors[sector].append(stock)
                break
    
    # 排序
    for sector in sectors:
        sectors[sector] = sorted(sectors[sector], key=lambda x: x['pct'], reverse=True)
    
    return sectors


def format_sectors_for_ai() -> str:
    """格式化输出给AI分析"""
    sectors = get_hot_sectors()
    
    lines = []
    for sector, stocks in sectors.items():
        if stocks:
            lines.append(f"\n### {sector} ({len(stocks)}只)")
            for s in stocks[:10]:
                lines.append(f"- {s['name']} {s['code']} {s['pct']:+.2f}%")
    
    return '\n'.join(lines)


if __name__ == '__main__':
    print(format_sectors_for_ai())
