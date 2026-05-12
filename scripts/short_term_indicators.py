#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短线技术指标模块
"""

import pandas as pd
import numpy as np


def calculate_rsi(prices, period=14):
    """计算RSI指标"""
    if len(prices) < period:
        return 50
    
    deltas = pd.Series(prices).diff()
    gain = deltas.where(deltas > 0, 0)
    loss = -deltas.where(deltas < 0, 0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """计算MACD指标"""
    if len(prices) < slow:
        return {'dif': 0, 'dea': 0, 'macd': 0}
    
    ema_fast = pd.Series(prices).ewm(span=fast).mean()
    ema_slow = pd.Series(prices).ewm(span=slow).mean()
    
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal).mean()
    macd = 2 * (dif - dea)
    
    return {
        'dif': dif.iloc[-1],
        'dea': dea.iloc[-1],
        'macd': macd.iloc[-1]
    }


def calculate_kdj(high, low, close, period=9):
    """计算KDJ指标"""
    if len(close) < period:
        return {'k': 50, 'd': 50, 'j': 50}
    
    low_min = pd.Series(low).rolling(window=period).min()
    high_max = pd.Series(high).rolling(window=period).max()
    
    rsv = 100 * (pd.Series(close) - low_min) / (high_max - low_min)
    
    k = rsv.ewm(com=2).mean()
    d = k.ewm(com=2).mean()
    j = 3 * k - 2 * d
    
    return {
        'k': k.iloc[-1],
        'd': d.iloc[-1],
        'j': j.iloc[-1]
    }


def calculate_bollinger(prices, period=20, std_dev=2):
    """计算布林带"""
    if len(prices) < period:
        return {'upper': 0, 'middle': 0, 'lower': 0}
    
    middle = pd.Series(prices).rolling(window=period).mean()
    std = pd.Series(prices).rolling(window=period).std()
    
    upper = middle + std_dev * std
    lower = middle - std_dev * std
    
    return {
        'upper': upper.iloc[-1],
        'middle': middle.iloc[-1],
        'lower': lower.iloc[-1]
    }


def calculate_ma(prices, period):
    """计算移动平均线"""
    if len(prices) < period:
        return 0
    return pd.Series(prices).rolling(window=period).mean().iloc[-1]


def get_short_term_signal(code, prices, highs, lows, volumes):
    """获取短线信号"""
    signals = {'rsi': 0, 'macd': 0, 'kdj': 0, 'bollinger': 0, 'volume': 0}
    
    # RSI
    rsi = calculate_rsi(prices)
    if rsi < 30:
        signals['rsi'] = 1  # 超买
    elif rsi > 70:
        signals['rsi'] = -1  # 超卖
    
    # MACD
    macd = calculate_macd(prices)
    if macd['macd'] > 0:
        signals['macd'] = 1
    elif macd['macd'] < 0:
        signals['macd'] = -1
    
    # KDJ
    kdj = calculate_kdj(highs, lows, prices)
    if kdj['k'] < 20:
        signals['kdj'] = 1
    elif kdj['k'] > 80:
        signals['kdj'] = -1
    
    # 布林带
    bb = calculate_bollinger(prices)
    if prices[-1] < bb['lower']:
        signals['bollinger'] = 1
    elif prices[-1] > bb['upper']:
        signals['bollinger'] = -1
    
    # 量价
    if len(volumes) >= 5:
        avg_vol = np.mean(volumes[-5:])
        if volumes[-1] > avg_vol * 1.5:
            signals['volume'] = 1
    
    return signals


def score_short_term_stock(code, prices, highs, lows, volumes):
    """短线评分"""
    signals = get_short_term_signal(code, prices, highs, lows, volumes)
    
    score = 0
    score += signals['rsi'] * 20
    score += signals['macd'] * 15
    score += signals['kdj'] * 20
    score += signals['bollinger'] * 15
    score += signals['volume'] * 15
    
    # 基础分
    if len(prices) >= 1:
        change = (prices[-1] - prices[-2]) / prices[-2] * 100 if len(prices) > 1 else 0
        score += 25 + change  # 0-50分
    
    return max(0, min(100, score))
