"""
Configurações específicas para o agente Bet365
"""

# Esportes suportados
SPORTS = {
    "futebol": {
        "name": "Futebol",
        "leagues": ["Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Brasileirão"],
        "markets": ["1X2", "Over/Under", "Both Teams to Score", "Asian Handicap"]
    },
    "basquete": {
        "name": "Basquete", 
        "leagues": ["NBA", "Euroliga", "NBB", "NCAA"],
        "markets": ["Moneyline", "Point Spread", "Total Points", "Player Props"]
    },
    "tenis": {
        "name": "Tênis",
        "tournaments": ["ATP", "WTA", "Grand Slams", "Masters 1000"],
        "markets": ["Match Winner", "Set Betting", "Total Games", "Handicap"]
    },
    "esports": {
        "name": "E-Sports",
        "games": ["CS:GO", "League of Legends", "Dota 2", "Valorant"],
        "markets": ["Match Winner", "Map Winner", "Total Maps", "First Blood"]
    }
}

# Tipos de apostas
BET_TYPES = {
    "simples": "Aposta em um único evento",
    "multipla": "Combinação de várias apostas",
    "sistema": "Combinações parciais de apostas",
    "ao_vivo": "Apostas durante o evento",
    "longo_prazo": "Apostas de temporada/campeonato"
}

# Estratégias de bankroll
BANKROLL_STRATEGIES = {
    "flat": {
        "name": "Flat Betting",
        "description": "Apostar sempre o mesmo valor",
        "risk": "Baixo",
        "recommended_stake": "1-3% do bankroll"
    },
    "kelly": {
        "name": "Kelly Criterion",
        "description": "Stake baseado na vantagem matemática",
        "risk": "Médio",
        "recommended_stake": "Calculado pela fórmula Kelly"
    },
    "progressive": {
        "name": "Progressiva",
        "description": "Aumentar stake após perdas",
        "risk": "Alto",
        "recommended_stake": "Não recomendado para iniciantes"
    }
}

# Indicadores de análise
ANALYSIS_INDICATORS = {
    "form": "Forma recente da equipe/jogador",
    "h2h": "Histórico de confrontos diretos",
    "home_away": "Performance em casa vs fora",
    "injuries": "Lesões e suspensões",
    "motivation": "Motivação (posição na tabela, objetivos)",
    "weather": "Condições climáticas",
    "referee": "Histórico do árbitro"
}

# Mercados populares por esporte
POPULAR_MARKETS = {
    "futebol": [
        "Resultado Final (1X2)",
        "Dupla Chance",
        "Ambas Marcam",
        "Total de Gols",
        "Handicap Asiático",
        "Primeiro/Último Gol"
    ],
    "basquete": [
        "Vencedor da Partida",
        "Handicap de Pontos",
        "Total de Pontos",
        "Margem de Vitória",
        "Pontos por Quarter",
        "Props de Jogadores"
    ],
    "tenis": [
        "Vencedor da Partida",
        "Handicap de Sets",
        "Total de Games",
        "Set Exato",
        "Tiebreak no Set",
        "Props de Jogadores"
    ]
}

# Configurações de risco
RISK_MANAGEMENT = {
    "max_stake_percentage": 5,  # Máximo 5% do bankroll por aposta
    "max_daily_loss": 10,  # Máximo 10% de perda diária
    "min_odds": 1.5,  # Odds mínimas recomendadas
    "max_odds": 10.0,  # Odds máximas recomendadas
    "max_selections_multiple": 5,  # Máximo de seleções em múltipla
    "stop_loss_streak": 5  # Parar após 5 perdas consecutivas
}

# Ligas e competições principais
MAJOR_COMPETITIONS = {
    "futebol": {
        "internacional": ["Copa do Mundo", "Eurocopa", "Copa América", "Champions League", "Europa League"],
        "nacional": ["Premier League", "La Liga", "Serie A", "Bundesliga", "Brasileirão", "Copa do Brasil"]
    },
    "basquete": {
        "internacional": ["FIBA World Cup", "Olympics", "Eurobasket"],
        "nacional": ["NBA", "Euroliga", "NBB", "NCAA March Madness"]
    },
    "tenis": {
        "grand_slams": ["Wimbledon", "US Open", "French Open", "Australian Open"],
        "masters": ["Indian Wells", "Miami Open", "Monte Carlo", "Madrid Open"]
    }
}