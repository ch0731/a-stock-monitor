#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测引擎模块
"""

class BacktestEngine:
    """简化回测引擎"""
    
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = {}
        self.trades = []
    
    def buy(self, code, price, quantity, date):
        """买入"""
        cost = price * quantity * 1.0003  # 手续费
        if self.capital >= cost:
            self.capital -= cost
            if code not in self.positions:
                self.positions[code] = {'quantity': 0, 'avg_price': 0}
            
            old_qty = self.positions[code]['quantity']
            old_price = self.positions[code]['avg_price']
            new_qty = old_qty + quantity
            
            self.positions[code] = {
                'quantity': new_qty,
                'avg_price': (old_qty * old_price + price * quantity) / new_qty
            }
            
            self.trades.append({
                'date': date, 'type': 'buy', 'code': code,
                'price': price, 'quantity': quantity
            })
            return True
        return False
    
    def sell(self, code, price, quantity, date):
        """卖出"""
        if code in self.positions and self.positions[code]['quantity'] >= quantity:
            self.positions[code]['quantity'] -= quantity
            self.capital += price * quantity * 0.9997
            
            self.trades.append({
                'date': date, 'type': 'sell', 'code': code,
                'price': price, 'quantity': quantity
            })
            return True
        return False
    
    def get_portfolio_value(self, prices):
        """获取组合市值"""
        value = self.capital
        for code, pos in self.positions.items():
            if code in prices:
                value += pos['quantity'] * prices[code]
        return value
    
    def run_backtest(self, signals, prices_data, start_date, end_date):
        """运行回测"""
        results = {
            'trades': self.trades,
            'final_value': self.capital,
            'return': 0
        }
        return results
