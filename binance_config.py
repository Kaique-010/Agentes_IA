"""
Configurações específicas para o agente Binance
"""

# Pares de moedas mais populares para monitoramento
POPULAR_PAIRS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT",
    "SOLUSDT", "DOTUSDT", "DOGEUSDT", "AVAXUSDT", "MATICUSDT"
]

# Indicadores técnicos disponíveis
TECHNICAL_INDICATORS = {
    "RSI": "Relative Strength Index",
    "MACD": "Moving Average Convergence Divergence", 
    "BB": "Bollinger Bands",
    "SMA": "Simple Moving Average",
    "EMA": "Exponential Moving Average",
    "STOCH": "Stochastic Oscillator"
}

# Timeframes disponíveis
TIMEFRAMES = {
    "1m": "1 minuto",
    "5m": "5 minutos", 
    "15m": "15 minutos",
    "30m": "30 minutos",
    "1h": "1 hora",
    "4h": "4 horas",
    "1d": "1 dia",
    "1w": "1 semana"
}

# Tipos de ordem
ORDER_TYPES = {
    "MARKET": "Ordem a mercado",
    "LIMIT": "Ordem limitada",
    "STOP_LOSS": "Stop Loss",
    "TAKE_PROFIT": "Take Profit",
    "STOP_LOSS_LIMIT": "Stop Loss Limitado",
    "TAKE_PROFIT_LIMIT": "Take Profit Limitado"
}

# Estratégias de trading pré-definidas
TRADING_STRATEGIES = {
    "scalping": {
        "name": "Scalping",
        "timeframe": "1m",
        "indicators": ["RSI", "MACD"],
        "description": "Operações rápidas de curto prazo"
    },
    "swing": {
        "name": "Swing Trading", 
        "timeframe": "4h",
        "indicators": ["SMA", "BB"],
        "description": "Operações de médio prazo"
    },
    "trend_following": {
        "name": "Seguidor de Tendência",
        "timeframe": "1d", 
        "indicators": ["EMA", "MACD"],
        "description": "Segue tendências de longo prazo"
    }
}

# Configurações de risco padrão
RISK_MANAGEMENT = {
    "max_position_size": 0.02,  # 2% do capital por operação
    "stop_loss_percentage": 0.02,  # 2% de stop loss
    "take_profit_ratio": 2,  # 1:2 risk/reward ratio
    "max_daily_loss": 0.05,  # 5% de perda máxima diária
    "max_open_positions": 5  # Máximo de 5 posições abertas
}