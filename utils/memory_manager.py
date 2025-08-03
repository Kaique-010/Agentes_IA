from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
import sqlite3
import json
from datetime import datetime, timedelta
import os
import aiosqlite
from typing import Dict, Any, Optional, List

class MemoryManager:
    def __init__(self, db_path="agent_memory.db"):
        self.db_path = db_path
        self.init_database()  # Corrigido de init_db() para init_database()
    
    def init_database(self):
        """Inicializa o banco de dados para memória persistente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela para conversas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT UNIQUE,
                user_id TEXT,
                agent_type TEXT,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        # Tabela para contexto de longo prazo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS long_term_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT,
                agent_type TEXT,
                context_type TEXT,
                content TEXT,
                importance_score INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (thread_id) REFERENCES conversations (thread_id)
            )
        ''')
        
        # Tabela para preferências do usuário
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                agent_type TEXT,
                preference_key TEXT,
                preference_value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela para sessões de agentes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                agent_type TEXT,
                user_id TEXT,
                thread_id TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela para performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_type TEXT,
                user_id TEXT,
                metric_type TEXT,
                metric_value REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_sqlite_saver(self, agent_type="default"):
        """Retorna uma instância de checkpointer para o tipo de agente especificado"""
        try:
            # Usar MemorySaver como solução temporária mais estável
            from langgraph.checkpoint.memory import MemorySaver
            return MemorySaver()
            
        except Exception as e:
            print(f"⚠️ Erro ao criar checkpointer: {e}")
            # Fallback básico
            from langgraph.checkpoint.memory import MemorySaver
            return MemorySaver()
    
    def save_conversation_context(self, thread_id: str, context: Dict[str, Any], agent_type: str = "default"):
        """Salva contexto importante da conversa"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO long_term_context 
            (thread_id, agent_type, context_type, content, importance_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            thread_id,
            agent_type,
            context.get('type', 'general'),
            json.dumps(context.get('content', {})),
            context.get('importance', 1)
        ))
        
        conn.commit()
        conn.close()
    
    def get_conversation_context(self, thread_id: str, agent_type: str = "default", limit: int = 10) -> List[Dict]:
        """Recupera contexto relevante da conversa"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT context_type, content, importance_score, created_at
            FROM long_term_context
            WHERE thread_id = ? AND agent_type = ?
            ORDER BY importance_score DESC, created_at DESC
            LIMIT ?
        ''', (thread_id, agent_type, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'type': row[0],
                'content': json.loads(row[1]),
                'importance': row[2],
                'created_at': row[3]
            })
        
        conn.close()
        return results
    
    def save_user_preference(self, user_id: str, key: str, value: str, agent_type: str = "default"):
        """Salva preferência do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences 
            (user_id, agent_type, preference_key, preference_value, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, agent_type, key, value, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_user_preferences(self, user_id: str, agent_type: str = "default") -> Dict[str, str]:
        """Recupera preferências do usuário"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT preference_key, preference_value
            FROM user_preferences
            WHERE user_id = ? AND agent_type = ?
        ''', (user_id, agent_type))
        
        preferences = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return preferences
    
    def create_session(self, user_id: str, agent_type: str) -> str:
        """Cria uma nova sessão de agente"""
        session_id = hashlib.md5(f"{user_id}_{agent_type}_{datetime.now()}".encode()).hexdigest()
        thread_id = f"{agent_type}_{session_id[:8]}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO agent_sessions 
            (session_id, agent_type, user_id, thread_id)
            VALUES (?, ?, ?, ?)
        ''', (session_id, agent_type, user_id, thread_id))
        
        conn.commit()
        conn.close()
        return thread_id
    
    def update_session_activity(self, thread_id: str):
        """Atualiza a última atividade da sessão"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE agent_sessions 
            SET last_activity = ?
            WHERE thread_id = ?
        ''', (datetime.now(), thread_id))
        
        conn.commit()
        conn.close()
    
    def save_performance_metric(self, agent_type: str, user_id: str, metric_type: str, value: float):
        """Salva métricas de performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_metrics 
            (agent_type, user_id, metric_type, metric_value)
            VALUES (?, ?, ?, ?)
        ''', (agent_type, user_id, metric_type, value))
        
        conn.commit()
        conn.close()
    
    def get_performance_metrics(self, agent_type: str, user_id: str, days: int = 30) -> List[Dict]:
        """Recupera métricas de performance"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT metric_type, metric_value, timestamp
            FROM performance_metrics
            WHERE agent_type = ? AND user_id = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        ''', (agent_type, user_id, since_date))
        
        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                'type': row[0],
                'value': row[1],
                'timestamp': row[2]
            })
        
        conn.close()
        return metrics
    
    def cleanup_old_data(self, days: int = 90):
        """Remove dados antigos para manter o banco otimizado"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Remove contexto antigo de baixa importância
        cursor.execute('''
            DELETE FROM long_term_context 
            WHERE created_at < ? AND importance_score < 3
        ''', (cutoff_date,))
        
        # Remove métricas antigas
        cursor.execute('''
            DELETE FROM performance_metrics 
            WHERE timestamp < ?
        ''', (cutoff_date,))
        
        conn.commit()
        conn.close()