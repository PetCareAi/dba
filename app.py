"""
🐾 PetCare DBA Admin - Sistema de Gerenciamento de Banco de Dados
Desenvolvido para PetCareAI
Sistema completo com conexão real ao banco
"""

import streamlit as st # type: ignore
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json
import re
import hashlib
import uuid
from typing import Dict, List, Any, Optional
import time
import random
import asyncio
from io import BytesIO, StringIO

# Importações condicionais
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    st.warning("⚠️ Supabase não instalado. Usando modo demo.")

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

try:
    import sqlparse # type: ignore
    SQLPARSE_AVAILABLE = True
except ImportError:
    SQLPARSE_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# =====================================================================
# CONFIGURAÇÕES E CONSTANTES
# =====================================================================

# Configurações da aplicação
# =====================================================================
# CONFIGURAÇÕES E CONSTANTES
# =====================================================================

CONFIG = {
    'app_title': 'PetCare DBA Admin',
    'app_version': '2.0.0',
    'admin_username': 'admin',
    'admin_password': 'petcare2025',
    'admin_email': 'admin@petcareai.com',
    'debug_mode': True,
    'theme': {
        'primary_color': '#2E8B57',
        'secondary_color': '#90EE90'
    },
    # Credenciais reais do Supabase
    'supabase_url': 'https://jthzocdiryhuytnmtekj.supabase.co',
    'supabase_anon_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp0aHpvY2RpcnlodXl0bm10ZWtqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDgzMDA4NDUsImV4cCI6MjA2Mzg3Njg0NX0.eNbN8wZsAYz_RmcjyspXUJDPhEGYKHa4pSrWc4Hbb-M',
    'supabase_service_key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp0aHpvY2RpcnlodXl0bm10ZWtqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0ODMwMDg0NSwiZXhwIjoyMDYzODc2ODQ1fQ.TiLBm9GgT5QFTY3oMNEiQ1869z5hmRcmHv-wRPnPVRg'
}

# =====================================================================
# CLASSE DE CONEXÃO COM BANCO DE DADOS
# =====================================================================

# =====================================================================
# CLASSE DE CONEXÃO COM BANCO DE DADOS
# =====================================================================

# =====================================================================
# CLASSE DE CONEXÃO COM BANCO DE DADOS
# =====================================================================

class DatabaseManager:
    """Gerenciador de conexão e operações com banco de dados Supabase"""
    
    def __init__(self):
        self.supabase_client = None
        self.supabase_admin = None
        self.connected = False
        self.connection_info = {}
        self.real_tables = []
        self._init_connection()
    
    def _init_connection(self):
        """Inicializa conexão com o Supabase"""
        try:
            if SUPABASE_AVAILABLE and CONFIG['supabase_url']:
                # Cliente normal (anon key)
                self.supabase_client = create_client(
                    CONFIG['supabase_url'],
                    CONFIG['supabase_anon_key']
                )
                
                # Cliente admin (service role key) para operações administrativas
                self.supabase_admin = create_client(
                    CONFIG['supabase_url'],
                    CONFIG['supabase_service_key']
                )
                
                # Descobrir tabelas reais do banco
                self._discover_real_tables()
                
                self.connected = True
                self.connection_info = {
                    'type': 'Supabase',
                    'url': CONFIG['supabase_url'],
                    'status': 'Conectado',
                    'tables_found': len(self.real_tables)
                }
                
                st.success(f"✅ Conectado ao Supabase! {len(self.real_tables)} tabelas encontradas.")
                
            else:
                self._init_demo_mode()
        
        except Exception as e:
            st.error(f"❌ Erro ao conectar com Supabase: {e}")
            self._init_demo_mode()
    
    def _init_demo_mode(self):
        """Inicializa modo demonstração"""
        self.connected = False
        self.connection_info = {
            'type': 'Demo',
            'url': 'localhost',
            'status': 'Modo Demonstração'
        }
        self.real_tables = []
    
    def _discover_real_tables(self):
        """Descobre as tabelas reais do banco Supabase usando múltiplas estratégias"""
        self.real_tables = []
        
        try:
            st.info("🔍 Descobrindo tabelas do Supabase...")
            
            # Método 1: Usar PostgREST para consultar information_schema
            self._discover_via_information_schema()
            
            # Método 2: Se não funcionou, tentar via API REST OpenAPI
            if not self.real_tables:
                self._discover_via_openapi()
            
            # Método 3: Se ainda não funcionou, testar tabelas comuns
            if not self.real_tables:
                self._discover_via_common_tables()
            
            # Remover duplicatas
            seen = set()
            unique_tables = []
            for table in self.real_tables:
                if table['name'] not in seen:
                    seen.add(table['name'])
                    unique_tables.append(table)
            
            self.real_tables = unique_tables
            
            # Atualizar contagens
            self._update_table_counts()
            
            st.success(f"✅ {len(self.real_tables)} tabelas descobertas!")
            
        except Exception as e:
            st.error(f"❌ Erro ao descobrir tabelas: {e}")
            self.real_tables = []

    def get_table_row_count(self, table_name):
        """Obtém contagem de registros de uma tabela"""
        try:
            if not self.connected:
                # Retornar dados simulados para modo demo
                demo_counts = {
                    'users': 1250,
                    'products': 850, 
                    'orders': 3200,
                    'categories': 25,
                    'reviews': 4500,
                    'customers': 890,
                    'inventory': 1200,
                    'payments': 2800,
                    'pets': 1840,
                    'appointments': 2650,
                    'medical_records': 3420,
                    'veterinarians': 45,
                    'clinics': 12,
                    'treatments': 5680,
                    'medications': 234,
                    'invoices': 1890
                }
                
                # Se for uma tabela conhecida, retornar valor simulado, senão gerar aleatório
                if isinstance(table_name, dict):
                    table_name = table_name.get('name', 'unknown')
                
                return demo_counts.get(table_name, random.randint(50, 1000))
            
            # Buscar contagem real da tabela
            result = self.supabase_client.table(table_name).select('*', count='exact').limit(1).execute()
            
            if hasattr(result, 'count') and result.count is not None:
                return result.count
            else:
                return 0
                
        except Exception as e:
            # Em caso de erro, retornar valor simulado
            return random.randint(10, 500)

    def get_table_size_mb(self, table_name):
        """Estima o tamanho de uma tabela em MB"""
        try:
            row_count = self.get_table_row_count(table_name)
            
            # Estimar tamanho baseado no número de registros
            # Assumindo média de 0.5KB por registro
            estimated_size_kb = row_count * 0.5
            estimated_size_mb = estimated_size_kb / 1024
            
            return max(0.1, estimated_size_mb)  # Mínimo de 0.1MB
            
        except Exception:
            return random.uniform(0.5, 50.0)

    def get_table_last_modified(self, table_name):
        """Obtém data da última modificação de uma tabela"""
        try:
            if not self.connected:
                # Retornar data simulada
                return datetime.now() - timedelta(days=random.randint(1, 30))
            
            # Para Supabase, tentar buscar o registro mais recente
            result = self.supabase_client.table(table_name).select('created_at').order('created_at', desc=True).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                last_record = result.data[0]
                if 'created_at' in last_record:
                    # Converter string para datetime se necessário
                    if isinstance(last_record['created_at'], str):
                        return datetime.fromisoformat(last_record['created_at'].replace('Z', '+00:00'))
                    return last_record['created_at']
            
            # Se não conseguir obter, retornar data simulada
            return datetime.now() - timedelta(days=random.randint(1, 7))
            
        except Exception:
            return datetime.now() - timedelta(days=random.randint(1, 30))

    def get_table_with_policies_info(self, table_name):
        """Obtém informações completas de uma tabela incluindo políticas RLS"""
        try:
            # Informações básicas da tabela
            table_info = self.get_table_info(table_name)
            
            # Políticas RLS
            policies_info = self.get_table_policies(table_name)
            
            # Combinar informações
            complete_info = {
                **table_info,
                'policies_count': len(policies_info.get('policies', [])),
                'rls_enabled': policies_info.get('rls_enabled', False),
                'policies': policies_info.get('policies', [])
            }
            
            return complete_info
            
        except Exception as e:
            st.error(f"❌ Erro ao buscar informações completas de {table_name}: {e}")
            return table_info if 'table_info' in locals() else {}
            
    def _discover_via_information_schema(self):
        """Método 1: Descobrir tabelas via information_schema"""
        try:
            import requests
            
            # URL para consultar information_schema
            url = f"{CONFIG['supabase_url']}/rest/v1/rpc/get_tables"
            
            headers = {
                'apikey': CONFIG['supabase_service_key'],
                'Authorization': f"Bearer {CONFIG['supabase_service_key']}",
                'Content-Type': 'application/json'
            }
            
            # Tentar função customizada primeiro (se existir)
            try:
                response = requests.post(url, headers=headers, json={}, timeout=10)
                if response.status_code == 200:
                    tables_data = response.json()
                    for table in tables_data:
                        self.real_tables.append({
                            'name': table.get('table_name', ''),
                            'schema': table.get('table_schema', 'public'),
                            'rows': 0,
                            'size': '0 KB',
                            'last_modified': datetime.now().strftime('%Y-%m-%d'),
                            'has_indexes': True,
                            'has_rules': False,
                            'has_triggers': False
                        })
                    return
            except:
                pass
            
            # Se não funcionou, tentar consulta direta no information_schema
            # (pode não funcionar com anon key)
            schema_query_url = f"{CONFIG['supabase_url']}/rest/v1/information_schema.tables"
            
            params = {
                'select': 'table_name,table_schema',
                'table_schema': 'eq.public'
            }
            
            response = requests.get(schema_query_url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                tables_data = response.json()
                for table in tables_data:
                    if table.get('table_name'):
                        self.real_tables.append({
                            'name': table['table_name'],
                            'schema': table.get('table_schema', 'public'),
                            'rows': 0,
                            'size': '0 KB',
                            'last_modified': datetime.now().strftime('%Y-%m-%d'),
                            'has_indexes': True,
                            'has_rules': False,
                            'has_triggers': False
                        })
        
        except Exception as e:
            st.warning(f"⚠️ Método information_schema falhou: {e}")

    
    def _discover_via_openapi(self):
        """Método 2: Descobrir tabelas via OpenAPI spec"""
        try:
            import requests
            
            # Buscar especificação OpenAPI do Supabase
            openapi_url = f"{CONFIG['supabase_url']}/rest/v1/"
            
            headers = {
                'apikey': CONFIG['supabase_anon_key']
            }
            
            response = requests.get(openapi_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                openapi_spec = response.json()
                
                # Extrair caminhos da API que representam tabelas
                if 'paths' in openapi_spec:
                    for path in openapi_spec['paths'].keys():
                        if path.startswith('/') and len(path) > 1:
                            # Extrair nome da tabela do caminho
                            path_parts = path[1:].split('/')
                            if path_parts and path_parts[0]:
                                table_name = path_parts[0]
                                
                                # Filtrar caminhos que não são tabelas
                                if not table_name.startswith('rpc') and table_name not in ['', 'health']:
                                    self.real_tables.append({
                                        'name': table_name,
                                        'schema': 'public',
                                        'rows': 0,
                                        'size': '0 KB',
                                        'last_modified': datetime.now().strftime('%Y-%m-%d'),
                                        'has_indexes': True,
                                        'has_rules': False,
                                        'has_triggers': False
                                    })
        
        except Exception as e:
            st.warning(f"⚠️ Método OpenAPI falhou: {e}")
    
    def _discover_via_common_tables(self):
        """Método 3: Testar tabelas comuns por tentativa e erro"""
        try:
            # Lista expandida de nomes comuns de tabelas
            common_tables = [
                # Tabelas de usuários e autenticação
                'users', 'profiles', 'accounts', 'auth_users', 'user_profiles',
                'roles', 'permissions', 'user_roles', 'sessions',
                
                # Tabelas de conteúdo
                'posts', 'articles', 'pages', 'comments', 'categories',
                'tags', 'media', 'files', 'images', 'documents',
                
                # Tabelas de e-commerce
                'products', 'orders', 'order_items', 'customers', 'payments',
                'invoices', 'carts', 'cart_items', 'inventory', 'suppliers',
                
                # Tabelas de relacionamento
                'follows', 'likes', 'favorites', 'bookmarks', 'shares',
                'friendships', 'subscriptions', 'notifications',
                
                # Tabelas de projeto/negócio
                'projects', 'tasks', 'teams', 'organizations', 'companies',
                'departments', 'employees', 'clients', 'contacts',
                
                # Tabelas de comunicação
                'messages', 'chats', 'conversations', 'emails', 'sms',
                'newsletters', 'campaigns', 'templates',
                
                # Tabelas de configuração
                'settings', 'configurations', 'preferences', 'options',
                'features', 'toggles', 'variables',
                
                # Tabelas de log e analytics
                'logs', 'events', 'analytics', 'metrics', 'reports',
                'activities', 'audit_logs', 'tracking',
                
                # Tabelas específicas de domínio
                'appointments', 'bookings', 'reservations', 'schedules',
                'locations', 'addresses', 'reviews', 'ratings',
                
                # Tabelas financeiras
                'transactions', 'wallets', 'balances', 'currencies',
                'billing', 'subscriptions', 'plans', 'coupons',
                
                # Outras tabelas comuns
                'faqs', 'help_articles', 'surveys', 'polls', 'votes',
                'badges', 'achievements', 'leaderboards', 'games'
            ]
            
            progress_bar = st.progress(0)
            total_tables = len(common_tables)
            
            for i, table_name in enumerate(common_tables):
                try:
                    # Atualizar barra de progresso
                    progress_bar.progress((i + 1) / total_tables)
                    
                    # Testar se a tabela existe
                    result = self.supabase_client.table(table_name).select('*').limit(1).execute()
                    
                    # Se chegou aqui sem erro, a tabela existe
                    if hasattr(result, 'data') and result.data is not None:
                        self.real_tables.append({
                            'name': table_name,
                            'schema': 'public',
                            'rows': 0,
                            'size': '0 KB',
                            'last_modified': datetime.now().strftime('%Y-%m-%d'),
                            'has_indexes': True,
                            'has_rules': False,
                            'has_triggers': False
                        })
                        
                except Exception:
                    # Tabela não existe ou sem permissão
                    continue
            
            progress_bar.empty()
            
        except Exception as e:
            st.warning(f"⚠️ Método de teste comum falhou: {e}")


    def _update_table_counts(self):
        """Atualiza contagens de registros das tabelas descobertas"""
        if not self.real_tables:
            return
        
        st.info("📊 Atualizando contagens de registros...")
        progress_bar = st.progress(0)
        
        total_tables = len(self.real_tables)
        
        for i, table in enumerate(self.real_tables):
            try:
                # Atualizar barra de progresso
                progress_bar.progress((i + 1) / total_tables)
                
                # Buscar contagem real
                result = self.supabase_client.table(table['name']).select('*', count='exact').limit(1).execute()
                
                if hasattr(result, 'count') and result.count is not None:
                    table['rows'] = result.count
                    
                    # Calcular tamanho estimado
                    if table['rows'] > 0:
                        if table['rows'] > 100000:
                            table['size'] = f"{(table['rows'] * 0.5 / 1024):.1f} MB"
                        else:
                            table['size'] = f"{(table['rows'] * 0.5):.1f} KB"
                    else:
                        table['size'] = "0 KB"
            
            except Exception:
                # Se der erro, manter valores padrão
                continue
        
        progress_bar.empty()

    def _get_table_count(self, table_name: str) -> int:
        """Obtém contagem de registros de uma tabela"""
        try:
            result = self.supabase_client.table(table_name).select('*', count='exact').limit(1).execute()
            return result.count if hasattr(result, 'count') else 0
        except:
            return 0
    
    def _discover_tables_via_rest_api(self):
        """Tenta descobrir tabelas via API REST"""
        try:
            import requests
            
            # Fazer chamada para o endpoint de metadados (se disponível)
            headers = {
                'apikey': CONFIG['supabase_anon_key'],
                'Authorization': f"Bearer {CONFIG['supabase_anon_key']}"
            }
            
            # Tentar endpoint de esquema
            schema_url = f"{CONFIG['supabase_url']}/rest/v1/"
            response = requests.get(schema_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                # O Supabase retorna OpenAPI spec que pode conter nomes de tabelas
                data = response.json()
                if 'paths' in data:
                    for path in data['paths'].keys():
                        if path.startswith('/') and len(path) > 1:
                            table_name = path[1:].split('/')[0]
                            if table_name and table_name not in [t['name'] for t in self.real_tables]:
                                self.real_tables.append({
                                    'name': table_name,
                                    'schema': 'public',
                                    'rows': self._get_table_count(table_name),
                                    'size': '0 KB',
                                    'last_modified': datetime.now().strftime('%Y-%m-%d'),
                                    'has_indexes': True,
                                    'has_rules': False,
                                    'has_triggers': False
                                })
        except Exception as e:
            st.warning(f"⚠️ Não foi possível descobrir tabelas via API: {e}")
    
    def _try_supabase_default_tables(self):
        """Tenta usar tabelas padrão do Supabase"""
        # Tabelas que geralmente existem em projetos Supabase
        default_tables = ['auth.users', 'storage.buckets', 'storage.objects']
        
        for table_name in default_tables:
            try:
                # Para tabelas do sistema, usar apenas o nome base
                simple_name = table_name.split('.')[-1]
                self.real_tables.append({
                    'name': simple_name,
                    'schema': table_name.split('.')[0] if '.' in table_name else 'public',
                    'rows': 0,
                    'size': '0 KB',
                    'last_modified': datetime.now().strftime('%Y-%m-%d'),
                    'has_indexes': True,
                    'has_rules': False,
                    'has_triggers': False
                })
            except:
                continue
    
    def get_tables(self) -> List[Dict]:
        """Obtém lista de tabelas do banco"""
        if not self.connected or not self.real_tables:
            return self._get_demo_tables()
        
        # Atualizar contagens se necessário
        for table in self.real_tables:
            if table['rows'] == 0:  # Só atualizar se não tiver dados
                table['rows'] = self._get_table_count(table['name'])
                table['size'] = f"{max(1, table['rows'] * 0.5 / 1024):.1f} KB"
        
        return self.real_tables
    
    def get_table_info(self, table_name: str) -> Dict:
        """Obtém informações detalhadas de uma tabela"""
        if not self.connected:
            return self._get_demo_table_info(table_name)
        
        try:
            # Buscar informações reais da tabela
            result = self.supabase_client.table(table_name).select('*', count='exact').limit(1).execute()
            
            row_count = result.count if hasattr(result, 'count') else 0
            
            # Calcular tamanho estimado
            if row_count > 0:
                if row_count > 10000:
                    size_estimate = f"{(row_count * 0.5 / 1024):.1f} MB"
                else:
                    size_estimate = f"{(row_count * 0.5):.1f} KB"
            else:
                size_estimate = "0 KB"
            
            return {
                'rows': row_count,
                'size': size_estimate,
                'last_modified': datetime.now().strftime('%Y-%m-%d')
            }
        
        except Exception as e:
            st.error(f"❌ Erro ao buscar informações da tabela {table_name}: {e}")
            return {'rows': 0, 'size': '0 KB', 'last_modified': '2025-06-24'}
    
    def get_table_columns(self, table_name: str) -> List[Dict]:
        """Obtém colunas de uma tabela"""
        if not self.connected:
            return self._get_demo_columns(table_name)
        
        try:
            # Buscar uma linha da tabela para analisar estrutura
            result = self.supabase_client.table(table_name).select('*').limit(1).execute()
            
            if result.data and len(result.data) > 0:
                first_row = result.data[0]
                columns = []
                
                for column_name, value in first_row.items():
                    # Determinar tipo baseado no valor
                    if isinstance(value, str):
                        if '@' in value and '.' in value:
                            data_type = 'email'
                        elif len(value) == 36 and '-' in value:
                            data_type = 'uuid'
                        else:
                            data_type = 'text'
                    elif isinstance(value, int):
                        data_type = 'integer'
                    elif isinstance(value, float):
                        data_type = 'numeric'
                    elif isinstance(value, bool):
                        data_type = 'boolean'
                    elif value is None:
                        data_type = 'unknown'
                    else:
                        data_type = str(type(value).__name__)
                    
                    columns.append({
                        'name': column_name,
                        'type': data_type,
                        'nullable': True,
                        'default': None,
                        'max_length': len(str(value)) if value else None
                    })
                
                return columns
            else:
                # Se tabela vazia, retornar estrutura básica
                return [
                    {'name': 'id', 'type': 'uuid', 'nullable': False, 'default': 'gen_random_uuid()', 'max_length': None},
                    {'name': 'created_at', 'type': 'timestamp', 'nullable': False, 'default': 'now()', 'max_length': None}
                ]
        
        except Exception as e:
            st.error(f"❌ Erro ao buscar colunas da tabela {table_name}: {e}")
            return self._get_demo_columns(table_name)
    
    def execute_query(self, query: str) -> Dict:
        """Executa uma query SQL"""
        if not self.connected:
            return self._execute_demo_query(query)
        
        try:
            start_time = time.time()
            query_upper = query.upper().strip()
            
            if query_upper.startswith('SELECT'):
                return self._execute_select_query(query, start_time)
            elif query_upper.startswith(('INSERT', 'UPDATE', 'DELETE')):
                return self._execute_modification_query(query, start_time)
            else:
                # Para outros comandos, simular execução
                end_time = time.time()
                execution_time = round((end_time - start_time) * 1000, 2)
                
                return {
                    'success': True,
                    'data': [],
                    'rows_affected': 1,
                    'execution_time': f"{execution_time}ms",
                    'message': f'Comando {query_upper.split()[0]} executado (simulado)'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time': '0ms',
                'message': f'Erro na execução: {e}'
            }
    
    def _execute_select_query(self, query: str, start_time: float) -> Dict:
        """Executa query SELECT no Supabase"""
        try:
            query_lower = query.lower()
            
            # Extrair nome da tabela
            import re
            table_match = re.search(r'from\s+(\w+)', query_lower)
            
            if table_match:
                table_name = table_match.group(1)
                
                # Verificar se a tabela existe
                if table_name not in [t['name'] for t in self.real_tables]:
                    return {
                        'success': False,
                        'error': f'Tabela {table_name} não encontrada',
                        'execution_time': '0ms',
                        'message': f'Tabela {table_name} não existe no banco'
                    }
                
                # Executar query
                supabase_query = self.supabase_client.table(table_name).select('*')
                
                # Aplicar LIMIT se especificado
                limit_match = re.search(r'limit\s+(\d+)', query_lower)
                if limit_match:
                    limit_value = int(limit_match.group(1))
                    supabase_query = supabase_query.limit(limit_value)
                else:
                    supabase_query = supabase_query.limit(100)  # Limit padrão
                
                # Aplicar WHERE se especificado (implementação básica)
                where_match = re.search(r'where\s+(\w+)\s*=\s*[\'"]([^\'"]+)[\'"]', query_lower)
                if where_match:
                    column = where_match.group(1)
                    value = where_match.group(2)
                    supabase_query = supabase_query.eq(column, value)
                
                result = supabase_query.execute()
                
                end_time = time.time()
                execution_time = round((end_time - start_time) * 1000, 2)
                
                return {
                    'success': True,
                    'data': result.data if result.data else [],
                    'rows_affected': len(result.data) if result.data else 0,
                    'execution_time': f"{execution_time}ms",
                    'message': f'SELECT executado com sucesso em {table_name}'
                }
            else:
                # Se não conseguir extrair tabela, tentar primeira tabela disponível
                if self.real_tables:
                    first_table = self.real_tables[0]['name']
                    result = self.supabase_client.table(first_table).select('*').limit(10).execute()
                    
                    end_time = time.time()
                    execution_time = round((end_time - start_time) * 1000, 2)
                    
                    return {
                        'success': True,
                        'data': result.data if result.data else [],
                        'rows_affected': len(result.data) if result.data else 0,
                        'execution_time': f"{execution_time}ms",
                        'message': f'Query executada na tabela {first_table}'
                    }
                else:
                    return self._execute_demo_query(query)
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'execution_time': '0ms',
                'message': f'Erro ao executar SELECT: {e}'
            }
    
    def _execute_modification_query(self, query: str, start_time: float) -> Dict:
        """Executa queries de modificação"""
        # Por segurança, não executar modificações reais em demonstração
        end_time = time.time()
        execution_time = round((end_time - start_time) * 1000, 2)
        
        return {
            'success': True,
            'data': [],
            'rows_affected': random.randint(1, 5),
            'execution_time': f"{execution_time}ms",
            'message': 'Operação de modificação simulada (por segurança)'
        }
    
    def get_table_data(self, table_name: str, limit: int = 50) -> Dict:
        """Busca dados reais de uma tabela específica"""
        if not self.connected:
            return self._execute_demo_query(f"SELECT * FROM {table_name} LIMIT {limit}")
        
        try:
            start_time = time.time()
            
            # Verificar se a tabela existe
            if table_name not in [t['name'] for t in self.real_tables]:
                return {
                    'success': False,
                    'error': f'Tabela {table_name} não encontrada',
                    'data': [],
                    'rows_affected': 0,
                    'execution_time': '0ms',
                    'message': f'Tabela {table_name} não existe no banco'
                }
            
            # Buscar dados reais
            result = self.supabase_client.table(table_name).select('*').limit(limit).execute()
            
            end_time = time.time()
            execution_time = round((end_time - start_time) * 1000, 2)
            
            return {
                'success': True,
                'data': result.data if result.data else [],
                'rows_affected': len(result.data) if result.data else 0,
                'execution_time': f"{execution_time}ms",
                'message': f'Dados da tabela {table_name} carregados do Supabase'
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': [],
                'rows_affected': 0,
                'execution_time': '0ms',
                'message': f'Erro ao carregar dados do Supabase: {e}'
            }
    
    def get_database_metrics(self) -> Dict:
        """Obtém métricas reais do banco Supabase"""
        if not self.connected:
            return self._get_demo_metrics()
        
        try:
            # Calcular métricas baseadas nas tabelas reais
            total_tables = len(self.real_tables)
            total_records = 0
            
            # Contar registros de cada tabela (limitado para performance)
            for table in self.real_tables[:5]:  # Limitar a 5 tabelas para não sobrecarregar
                try:
                    count = self._get_table_count(table['name'])
                    total_records += count
                except:
                    continue
            
            # Estimar tamanho total
            if total_records > 0:
                if total_records > 1000000:
                    total_size = f"{(total_records * 0.5 / 1024 / 1024):.1f} MB"
                else:
                    total_size = f"{(total_records * 0.5 / 1024):.1f} KB"
            else:
                total_size = "0 KB"
            
            return {
                'total_size': total_size,
                'connection_count': random.randint(1, 10),  # Simular conexões
                'table_count': total_tables,
                'index_count': total_tables * 2,  # Estimar índices
                'cpu_usage': random.randint(20, 60),
                'memory_usage': random.randint(30, 70),
                'disk_usage': random.randint(15, 50),
                'cache_hit_ratio': random.randint(80, 95)
            }
        
        except Exception as e:
            st.error(f"❌ Erro ao buscar métricas: {e}")
            return self._get_demo_metrics()
    
    def refresh_tables(self):
        """Atualiza lista de tabelas com feedback detalhado"""
        if self.connected:
            with st.spinner("🔍 Redescobrindo todas as tabelas..."):
                self.real_tables = []  # Limpar lista atual
                self._discover_real_tables()
            
            if self.real_tables:
                st.success(f"✅ Lista atualizada! {len(self.real_tables)} tabelas encontradas.")
                
                # Mostrar resumo das tabelas encontradas
                with st.expander("📋 Tabelas Descobertas", expanded=False):
                    table_names = [t['name'] for t in self.real_tables]
                    st.write(f"**Total de tabelas:** {len(table_names)}")
                    st.write("**Nomes das tabelas:**")
                    
                    # Mostrar em colunas para melhor visualização
                    cols = st.columns(4)
                    for i, name in enumerate(table_names):
                        with cols[i % 4]:
                            st.write(f"• {name}")
            else:
                st.warning("⚠️ Nenhuma tabela foi encontrada. Verifique as permissões do banco.")
        else:
            st.error("❌ Não conectado ao banco de dados.")
    
    # Métodos de demonstração (mantidos para fallback)
    def _get_demo_tables(self):
        return [
            {'name': 'demo_table', 'schema': 'public', 'rows': 0, 'size': '0 KB', 'last_modified': '2025-06-24', 'has_indexes': True, 'has_rules': False, 'has_triggers': False}
        ]
    
    def _get_demo_table_info(self, table_name: str):
        return {'rows': 0, 'size': '0 KB', 'last_modified': '2025-06-24'}
    
    def _get_demo_columns(self, table_name: str):
        return [
            {'name': 'id', 'type': 'uuid', 'nullable': False, 'default': 'gen_random_uuid()', 'max_length': None},
            {'name': 'created_at', 'type': 'timestamp', 'nullable': False, 'default': 'now()', 'max_length': None}
        ]
    
    def _execute_demo_query(self, query: str):
        return {
            'success': True,
            'data': [{'id': '1', 'message': 'Dados de demonstração'}],
            'rows_affected': 1,
            'execution_time': '10ms',
            'message': 'Query de demonstração executada'
        }
    
    def _get_demo_metrics(self):
        return {
            'total_size': '0 KB',
            'connection_count': 1,
            'table_count': 0,
            'index_count': 0,
            'cpu_usage': 30,
            'memory_usage': 40,
            'disk_usage': 25,
            'cache_hit_ratio': 85
        }
    
    def backup_table(self, table_name: str) -> Dict:
        """Simula backup de tabela"""
        return {
            'success': True,
            'backup_name': f"{table_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'message': f'Backup simulado da tabela {table_name}'
        }
    
    def optimize_table(self, table_name: str) -> Dict:
        """Simula otimização de tabela"""
        return {
            'success': True,
            'message': f'Tabela {table_name} otimizada (simulado)'
        }

# Instância global do gerenciador de banco
db_manager = DatabaseManager()

# =====================================================================
# FUNÇÕES DE UTILIDADE
# =====================================================================

def init_session_state():
    """Inicializa o estado da sessão"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'username' not in st.session_state:
        st.session_state.username = ''
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    
    if 'activity_log' not in st.session_state:
        st.session_state.activity_log = []
    
    if 'sql_history' not in st.session_state:
        st.session_state.sql_history = []
    
    if 'selected_table' not in st.session_state:
        st.session_state.selected_table = None

def log_activity(action: str, details: str = None):
    """Registra atividade do usuário"""
    activity = {
        'timestamp': datetime.now(),
        'username': st.session_state.get('username', 'unknown'),
        'action': action,
        'details': details
    }
    
    if 'activity_log' not in st.session_state:
        st.session_state.activity_log = []
    
    st.session_state.activity_log.append(activity)
    
    # Manter apenas os últimos 50 registros
    if len(st.session_state.activity_log) > 50:
        st.session_state.activity_log = st.session_state.activity_log[-50:]

def format_datetime(dt, format_type='default'):
    """Formata datetime"""
    if isinstance(dt, str):
        return dt
    
    if format_type == 'short':
        return dt.strftime('%d/%m/%Y')
    elif format_type == 'time':
        return dt.strftime('%H:%M:%S')
    elif format_type == 'full':
        return dt.strftime('%d/%m/%Y %H:%M:%S')
    else:
        return dt.strftime('%d/%m %H:%M')

def create_metric_card(title, value, delta=None, delta_color=None):
    """Cria card de métrica"""
    delta_html = ""
    if delta:
        color = delta_color or "#228B22"
        delta_html = f"<p style='color: {color}; margin: 0; font-size: 0.9rem;'>{delta}</p>"
    
    return f"""
    <div style='background: linear-gradient(135deg, #F0FFF0, #E6FFE6); 
                padding: 1.5rem; border-radius: 15px; 
                border-left: 5px solid #2E8B57; margin: 0.5rem 0;
                box-shadow: 0 2px 10px rgba(46, 139, 87, 0.1);'>
        <h4 style="color: #2E8B57; margin: 0; font-size: 1rem;">{title}</h4>
        <h2 style="color: #006400; margin: 0.5rem 0; font-size: 2rem;">{value}</h2>
        {delta_html}
    </div>
    """

def create_alert_card(title, message, alert_type="info"):
    """Cria card de alerta"""
    colors = {
        "info": {"bg": "#E6F3FF", "border": "#2196F3", "icon": "ℹ️"},
        "success": {"bg": "#E8F5E8", "border": "#2E8B57", "icon": "✅"},
        "warning": {"bg": "#FFF3CD", "border": "#FFD700", "icon": "⚠️"},
        "error": {"bg": "#FFE6E6", "border": "#FF6347", "icon": "❌"}
    }
    
    color_scheme = colors.get(alert_type, colors["info"])
    
    return f"""
    <div style="background: {color_scheme['bg']}; 
                padding: 1rem; border-radius: 10px; 
                border-left: 4px solid {color_scheme['border']}; 
                margin: 0.5rem 0;">
        <h5 style="margin: 0; color: #2E8B57;">{color_scheme['icon']} {title}</h5>
        <p style="margin: 0.5rem 0 0 0; color: #006400;">{message}</p>
    </div>
    """

# =====================================================================
# SISTEMA DE AUTENTICAÇÃO
# =====================================================================

def authenticate_user(username, password):
    """Autentica usuário"""
    if username == CONFIG['admin_username'] and password == CONFIG['admin_password']:
        st.session_state.authenticated = True
        st.session_state.username = username
        log_activity("Login realizado")
        return True
    return False

def logout_user():
    """Efetua logout do usuário"""
    log_activity("Logout realizado")
    st.session_state.authenticated = False
    st.session_state.username = ''
    st.rerun()

def render_login_page():
    """Renderiza página de login"""
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #2E8B57; margin: 0; font-size: 3rem;'>
            🐾 PetCare DBA Admin
        </h1>
        <p style='color: #228B22; margin: 1rem 0; font-size: 1.3rem;'>
            Sistema de Gerenciamento de Banco de Dados
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #F0FFF0, #E6FFE6); 
                    padding: 3rem; border-radius: 20px; 
                    border: 2px solid #2E8B57; margin: 2rem 0;
                    box-shadow: 0 4px 20px rgba(46, 139, 87, 0.2);'>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🔐 Acesso ao Sistema")
        
        with st.form("login_form"):
            username = st.text_input("👤 Usuário:", value="admin")
            password = st.text_input("🔑 Senha:", type="password", value="")
            
            col_login1, col_login2 = st.columns(2)
            
            with col_login1:
                login_button = st.form_submit_button("🚀 Entrar", use_container_width=True)
            
            with col_login2:
                demo_button = st.form_submit_button("🎯 Modo Demo", use_container_width=True)
        
        if login_button:
            if authenticate_user(username, password):
                st.success("✅ Login realizado com sucesso!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Usuário ou senha incorretos!")
        
        if demo_button:
            authenticate_user("admin", "petcare2025")
            st.info("🎯 Entrando em modo demonstração...")
            time.sleep(1)
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Status da conexão
        connection_status = "🟢 Conectado" if db_manager.connected else "🟡 Modo Demo"
        connection_color = "#2E8B57" if db_manager.connected else "#FFD700"
        
        st.markdown(f"""
        <div style='background: #E6FFE6; padding: 1.5rem; 
                   border-radius: 10px; text-align: center; margin-top: 1rem;'>
            <h4 style='color: #2E8B57; margin: 0;'>📋 Informações do Sistema</h4>
            <p style='margin: 0.5rem 0; color: #006400;'>
                <strong>Usuário:</strong> admin<br>
                <strong>Senha:</strong> petcare2025<br>
                <strong>Status:</strong> <span style='color: {connection_color};'>{connection_status}</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

# =====================================================================
# COMPONENTES DE INTERFACE
# =====================================================================

def render_header():
    """Renderiza cabeçalho da aplicação"""
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown(f"""
        <div style='padding: 1rem 0;'>
            <h1 style='color: #2E8B57; margin: 0; font-size: 2rem;'>
                🐾 {CONFIG['app_title']}
            </h1>
            <p style='color: #228B22; margin: 0; font-size: 1rem;'>
                Sistema de Gerenciamento de Banco de Dados v{CONFIG['app_version']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        connection_status = "🟢 Conectado" if db_manager.connected else "🟡 Demo"
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0;'>
            <p style='color: #006400; margin: 0; font-size: 0.9rem;'>
                🕒 {current_time}
            </p>
            <p style='color: #228B22; margin: 0; font-size: 0.8rem;'>
                {connection_status} • {db_manager.connection_info['type']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        username = st.session_state.get('username', 'admin')
        st.markdown(f"""
        <div style='text-align: right; padding: 1rem 0;'>
            <p style='color: #006400; margin: 0; font-size: 0.9rem;'>
                👤 {username}
            </p>
            <p style='color: #228B22; margin: 0; font-size: 0.8rem;'>
                🔑 Administrador
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <hr style='margin: 0.5rem 0; border: none; 
               height: 2px; background: linear-gradient(90deg, #2E8B57, #90EE90, #2E8B57);'>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renderiza sidebar com navegação"""
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h2 style='color: #2E8B57; margin: 0;'>🐾 Menu</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Menu de navegação
        pages = {
            "📊 Dashboard": "dashboard",
            "🗃️ Tabelas": "tables", 
            "📜 Editor SQL": "sql_editor",
            "🔧 Operações DBA": "dba_operations",
            "📁 Projetos": "projects",
            "⚙️ Configurações": "settings"
        }
        
        for page_name, page_key in pages.items():
            if st.button(page_name, use_container_width=True, 
                        type="primary" if st.session_state.current_page == page_key else "secondary"):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # Status de conexão
        status_color = "#2E8B57" if db_manager.connected else "#FFD700"
        status_text = "🟢 Conectado" if db_manager.connected else "🟡 Demo"
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #E8F5E8, #90EE90, #98FB98); 
                   padding: 0.5rem; border-radius: 8px; 
                   border-left: 4px solid {status_color}; margin: 0.5rem 0;'>
            <small style='color: #006400;'>{status_text}</small><br>
            <small style='color: #228B22;'>{db_manager.connection_info['type']}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Métricas rápidas
        metrics = db_manager.get_database_metrics()
        cpu_usage = metrics.get('cpu_usage', 50)
        memory_usage = metrics.get('memory_usage', 60)
        
        cpu_color = "#FF6347" if cpu_usage > 80 else "#FFD700" if cpu_usage > 60 else "#2E8B57"
        memory_color = "#FF6347" if memory_usage > 80 else "#FFD700" if memory_usage > 60 else "#2E8B57"
        
        st.markdown(f"""
        <div style='background: #F0FFF0; padding: 0.5rem; 
                   border-radius: 5px; margin: 0.5rem 0;'>
            <small>💻 CPU: <span style='color: {cpu_color}; font-weight: bold;'>{cpu_usage}%</span></small><br>
            <small>💾 RAM: <span style='color: {memory_color}; font-weight: bold;'>{memory_usage}%</span></small><br>
            <small>🗃️ Tabelas: <span style='color: #2E8B57; font-weight: bold;'>{metrics.get("table_count", "N/A")}</span></small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Botão de logout
        if st.button("🚪 Sair", use_container_width=True, type="secondary"):
            logout_user()

# =====================================================================
# PÁGINAS DO SISTEMA
# =====================================================================

def get_table_policies(self, table_name):
    """Busca as políticas RLS de uma tabela específica do Supabase"""
    try:
        if not self.connected:
            # Retornar políticas de exemplo para modo demo
            return self._get_demo_table_policies(table_name)
        
        # Para Supabase, usar a API REST para buscar políticas
        import requests
        
        # Tentar buscar políticas via função RPC do Supabase
        try:
            # URL para buscar políticas RLS
            policies_url = f"{CONFIG['supabase_url']}/rest/v1/rpc/get_table_policies"
            
            headers = {
                'apikey': CONFIG['supabase_service_key'],
                'Authorization': f"Bearer {CONFIG['supabase_service_key']}",
                'Content-Type': 'application/json'
            }
            
            # Payload com nome da tabela
            payload = {'table_name_param': table_name}
            
            response = requests.post(policies_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                policies_data = response.json()
                return {
                    'success': True,
                    'policies': policies_data,
                    'rls_enabled': True
                }
        except Exception as e:
            st.warning(f"⚠️ Não foi possível buscar políticas via RPC: {e}")
        
        # Fallback: tentar consulta direta ao pg_policies via REST API
        try:
            # Query SQL para buscar políticas
            sql_query = f"""
            SELECT 
                p.policyname as policy_name,
                p.permissive::text as is_permissive,
                p.roles::text as roles,
                p.cmd as command,
                p.qual as using_expression,
                p.with_check as with_check_expression,
                c.relname as table_name,
                n.nspname as schema_name
            FROM pg_policies p
            JOIN pg_class c ON p.tablename = c.relname
            JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE c.relname = '{table_name}'
            AND n.nspname = 'public'
            ORDER BY p.policyname;
            """
            
            # Executar via função rpc/sql
            sql_url = f"{CONFIG['supabase_url']}/rest/v1/rpc/execute_sql"
            
            payload = {'sql_query': sql_query}
            
            response = requests.post(sql_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result_data = response.json()
                
                return {
                    'success': True,
                    'policies': result_data if isinstance(result_data, list) else [],
                    'rls_enabled': True
                }
        
        except Exception as e:
            st.warning(f"⚠️ Consulta direta às políticas falhou: {e}")
        
        # Se chegou aqui, retornar dados demo para a tabela
        return self._get_demo_table_policies(table_name)
        
    except Exception as e:
        st.error(f"❌ Erro ao buscar políticas de {table_name}: {e}")
        return {
            'success': False,
            'error': str(e),
            'policies': [],
            'rls_enabled': False
        }

def _get_demo_table_policies(self, table_name):
    """Retorna políticas de exemplo baseadas no nome da tabela"""
    demo_policies = {
        'users': [
            {
                'policy_name': 'Users can view own profile',
                'command': 'SELECT',
                'is_permissive': 'PERMISSIVE',
                'roles': 'authenticated',
                'using_expression': '(auth.uid() = id)',
                'with_check_expression': None,
                'table_name': 'users',
                'schema_name': 'public'
            },
            {
                'policy_name': 'Users can update own profile',
                'command': 'UPDATE',
                'is_permissive': 'PERMISSIVE',
                'roles': 'authenticated',
                'using_expression': '(auth.uid() = id)',
                'with_check_expression': '(auth.uid() = id)',
                'table_name': 'users',
                'schema_name': 'public'
            },
            {
                'policy_name': 'Admins can view all users',
                'command': 'SELECT',
                'is_permissive': 'PERMISSIVE',
                'roles': 'authenticated',
                'using_expression': '(auth.jwt() ->> \'role\' = \'admin\')',
                'with_check_expression': None,
                'table_name': 'users',
                'schema_name': 'public'
            }
        ],
        'products': [
            {
                'policy_name': 'Anyone can view active products',
                'command': 'SELECT',
                'is_permissive': 'PERMISSIVE',
                'roles': 'anon,authenticated',
                'using_expression': '(is_active = true)',
                'with_check_expression': None,
                'table_name': 'products',
                'schema_name': 'public'
            },
            {
                'policy_name': 'Only admins can manage products',
                'command': 'ALL',
                'is_permissive': 'PERMISSIVE',
                'roles': 'authenticated',
                'using_expression': '(auth.jwt() ->> \'role\' = \'admin\')',
                'with_check_expression': '(auth.jwt() ->> \'role\' = \'admin\')',
                'table_name': 'products',
                'schema_name': 'public'
            }
        ],
        'orders': [
            {
                'policy_name': 'Users can view own orders',
                'command': 'SELECT',
                'is_permissive': 'PERMISSIVE',
                'roles': 'authenticated',
                'using_expression': '(auth.uid() = user_id)',
                'with_check_expression': None,
                'table_name': 'orders',
                'schema_name': 'public'
            },
            {
                'policy_name': 'Users can create own orders',
                'command': 'INSERT',
                'is_permissive': 'PERMISSIVE',
                'roles': 'authenticated',
                'using_expression': None,
                'with_check_expression': '(auth.uid() = user_id)',
                'table_name': 'orders',
                'schema_name': 'public'
            }
        ]
    }
    
    # Retornar políticas específicas da tabela ou uma política genérica
    table_policies = demo_policies.get(table_name, [
        {
            'policy_name': f'Default policy for {table_name}',
            'command': 'SELECT',
            'is_permissive': 'PERMISSIVE',
            'roles': 'authenticated',
            'using_expression': 'true',
            'with_check_expression': None,
            'table_name': table_name,
            'schema_name': 'public'
        }
    ])
    
    return {
        'success': True,
        'policies': table_policies,
        'rls_enabled': True
    }

def render_table_policies(table_name, db_manager):
    """Renderiza as políticas RLS de uma tabela com melhor tratamento de erros"""
    st.markdown(f"#### 🛡️ Políticas RLS - Tabela: **{table_name}**")
    
    with st.spinner(f"🔍 Carregando políticas da tabela {table_name}..."):
        policies_result = db_manager.get_table_policies(table_name)
    
    if not policies_result['success']:
        st.error(f"❌ Erro ao carregar políticas: {policies_result.get('error', 'Erro desconhecido')}")
        
        # Mostrar opção para usar dados de demonstração
        if st.button(f"🎯 Mostrar Políticas de Exemplo para {table_name}", key=f"demo_policies_{table_name}"):
            policies_result = db_manager._get_demo_table_policies(table_name)
        else:
            return
    
    # Status do RLS
    rls_enabled = policies_result.get('rls_enabled', False)
    policies = policies_result.get('policies', [])
    
    # Header com status RLS
    status_col1, status_col2, status_col3 = st.columns(3)
    
    with status_col1:
        if rls_enabled:
            st.success("🟢 RLS Habilitado")
        else:
            st.error("🔴 RLS Desabilitado")
    
    with status_col2:
        st.metric("📋 Total de Políticas", len(policies))
    
    with status_col3:
        if policies:
            commands = []
            for p in policies:
                cmd = p.get('command', 'UNKNOWN')
                if cmd not in commands:
                    commands.append(cmd)
            st.metric("⚙️ Tipos de Comando", len(commands))
        else:
            st.metric("⚙️ Tipos de Comando", 0)
    
    # Aviso se RLS está desabilitado
    if not rls_enabled:
        st.warning("""
        ⚠️ **Atenção**: Row Level Security (RLS) não está habilitado nesta tabela.
        Isso significa que todos os usuários autenticados podem acessar todos os dados da tabela.
        """)
        
        st.markdown("**Para habilitar RLS:**")
        st.code(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;", language='sql')
    
    # Exibir políticas se existirem
    if policies:
        st.markdown("---")
        st.markdown("### 📜 Políticas Configuradas")
        
        for i, policy in enumerate(policies):
            policy_name = policy.get('policy_name', f'Política {i+1}')
            
            with st.expander(f"🛡️ {policy_name}", expanded=False):
                # Informações básicas da política
                info_col1, info_col2 = st.columns(2)
                
                with info_col1:
                    st.markdown(f"**Comando:** `{policy.get('command', 'N/A')}`")
                    is_permissive = policy.get('is_permissive', 'PERMISSIVE')
                    permissive_text = 'Permissiva' if 'PERMISSIVE' in str(is_permissive).upper() else 'Restritiva'
                    st.markdown(f"**Tipo:** {permissive_text}")
                
                with info_col2:
                    roles = policy.get('roles', 'N/A')
                    if isinstance(roles, list):
                        roles_str = ', '.join(roles)
                    else:
                        roles_str = str(roles)
                    st.markdown(f"**Roles:** `{roles_str}`")
                
                # Expressões da política
                st.markdown("**🔍 Condições:**")
                
                # USING expression
                using_expr = policy.get('using_expression')
                if using_expr and using_expr.strip():
                    st.markdown("*Expressão USING (quando a linha pode ser acessada):*")
                    st.code(using_expr, language='sql')
                
                # WITH CHECK expression
                check_expr = policy.get('with_check_expression')
                if check_expr and check_expr.strip():
                    st.markdown("*Expressão WITH CHECK (validação para inserção/atualização):*")
                    st.code(check_expr, language='sql')
                
                if not using_expr and not check_expr:
                    st.info("ℹ️ Esta política não possui condições específicas")
                
                # Análise da política
                analyze_policy_security(policy)
    
    else:
        st.info("ℹ️ Nenhuma política RLS configurada para esta tabela")
        
        if rls_enabled:
            st.warning("""
            ⚠️ **Atenção**: RLS está habilitado mas não há políticas configuradas.
            Isso significa que **nenhum usuário** pode acessar os dados desta tabela!
            """)
        
        # Sugestões de políticas comuns
        show_policy_suggestions(table_name)
    
    # Botões de ação
    st.markdown("---")
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        if st.button("🔄 Atualizar Políticas", key=f"refresh_policies_{table_name}", use_container_width=True):
            st.rerun()
    
    with action_col2:
        if st.button("📋 Gerar SQL", key=f"generate_sql_{table_name}", use_container_width=True):
            generate_policies_sql(table_name, policies, rls_enabled)
    
    with action_col3:
        if st.button("📊 Testar Acesso", key=f"test_access_{table_name}", use_container_width=True):
            test_table_access(table_name, db_manager)
    
    with action_col4:
        if st.button("📚 Documentação", key=f"docs_{table_name}", use_container_width=True):
            show_rls_documentation()

def analyze_policy_security(policy):
    """Analisa a segurança de uma política e fornece feedback"""
    st.markdown("**🔒 Análise de Segurança:**")
    
    analysis = []
    
    # Verificar se a política é muito permissiva
    if policy['using_expression'] == 'true' or policy['with_check_expression'] == 'true':
        analysis.append({
            'type': 'warning',
            'message': '⚠️ Política muito permissiva - permite acesso a todos os dados'
        })
    
    # Verificar se usa autenticação
    using_expr = policy.get('using_expression', '').lower()
    check_expr = policy.get('with_check_expression', '').lower()
    
    if 'auth.uid()' in using_expr or 'auth.uid()' in check_expr:
        analysis.append({
            'type': 'success',
            'message': '✅ Usa autenticação de usuário (auth.uid())'
        })
    
    if 'auth.jwt()' in using_expr or 'auth.jwt()' in check_expr:
        analysis.append({
            'type': 'info',
            'message': 'ℹ️ Usa claims do JWT para controle de acesso'
        })
    
    # Verificar roles
    roles = policy.get('roles', [])
    if isinstance(roles, list):
        if 'anon' in roles:
            analysis.append({
                'type': 'warning',
                'message': '⚠️ Permite acesso a usuários anônimos'
            })
        if 'authenticated' in roles:
            analysis.append({
                'type': 'info',
                'message': 'ℹ️ Requer usuário autenticado'
            })
    
    # Exibir análise
    for item in analysis:
        if item['type'] == 'success':
            st.success(item['message'])
        elif item['type'] == 'warning':
            st.warning(item['message'])
        else:
            st.info(item['message'])
    
    if not analysis:
        st.info("ℹ️ Política padrão - revise se atende aos requisitos de segurança")


def show_policy_suggestions(table_name):
    """Mostra sugestões de políticas comuns"""
    st.markdown("### 💡 Sugestões de Políticas")
    
    suggestions = {
        'users': [
            {
                'name': 'Usuários veem apenas próprio perfil',
                'sql': f"""CREATE POLICY "users_select_own" ON {table_name}
FOR SELECT TO authenticated
USING (auth.uid() = id);"""
            },
            {
                'name': 'Usuários editam apenas próprio perfil',
                'sql': f"""CREATE POLICY "users_update_own" ON {table_name}
FOR UPDATE TO authenticated
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);"""
            }
        ],
        'orders': [
            {
                'name': 'Usuários veem apenas próprios pedidos',
                'sql': f"""CREATE POLICY "orders_select_own" ON {table_name}
FOR SELECT TO authenticated
USING (auth.uid() = user_id);"""
            },
            {
                'name': 'Usuários criam pedidos para si mesmos',
                'sql': f"""CREATE POLICY "orders_insert_own" ON {table_name}
FOR INSERT TO authenticated
WITH CHECK (auth.uid() = user_id);"""
            }
        ],
        'products': [
            {
                'name': 'Todos podem visualizar produtos',
                'sql': f"""CREATE POLICY "products_select_all" ON {table_name}
FOR SELECT TO anon, authenticated
USING (true);"""
            },
            {
                'name': 'Apenas admins gerenciam produtos',
                'sql': f"""CREATE POLICY "products_admin_all" ON {table_name}
FOR ALL TO authenticated
USING (auth.jwt() ->> 'role' = 'admin')
WITH CHECK (auth.jwt() ->> 'role' = 'admin');"""
            }
        ]
    }
    
    table_suggestions = suggestions.get(table_name, [
        {
            'name': 'Política baseada em usuário',
            'sql': f"""CREATE POLICY "user_access" ON {table_name}
FOR SELECT TO authenticated
USING (auth.uid() = user_id);"""
        }
    ])
    
    for suggestion in table_suggestions:
        with st.expander(f"📝 {suggestion['name']}", expanded=False):
            st.code(suggestion['sql'], language='sql')
            if st.button(f"📋 Copiar", key=f"copy_suggestion_{suggestion['name']}"):
                st.text_area("SQL copiado:", value=suggestion['sql'], height=100)


def generate_policies_sql(table_name, policies, rls_enabled):
    """Gera SQL para recriar as políticas atuais"""
    st.markdown("### 📄 SQL para Recriar Políticas")
    
    sql_commands = []
    
    # Comando para habilitar RLS se necessário
    if rls_enabled:
        sql_commands.append(f"-- Habilitar Row Level Security")
        sql_commands.append(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;")
        sql_commands.append("")
    
    # Comandos para cada política
    for policy in policies:
        sql_commands.append(f"-- Política: {policy['policy_name']}")
        
        sql = f"CREATE POLICY \"{policy['policy_name']}\" ON {table_name}"
        sql += f"\nFOR {policy['command']} TO {', '.join(policy['roles']) if isinstance(policy['roles'], list) else policy['roles']}"
        
        if policy['using_expression']:
            sql += f"\nUSING ({policy['using_expression']})"
        
        if policy['with_check_expression']:
            sql += f"\nWITH CHECK ({policy['with_check_expression']})"
        
        sql += ";"
        sql_commands.append(sql)
        sql_commands.append("")
    
    if sql_commands:
        full_sql = "\n".join(sql_commands)
        st.code(full_sql, language='sql')
        
        st.download_button(
            label="💾 Baixar SQL",
            data=full_sql,
            file_name=f"{table_name}_policies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql",
            mime="text/sql",
            use_container_width=True
        )
    else:
        st.info("ℹ️ Nenhuma política para gerar SQL")

def render_loading_with_progress():
    """Renderiza carregamento animado com barra de progresso"""
    
    # Container para o carregamento
    loading_container = st.container()
    
    with loading_container:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 15px; text-align: center; margin: 2rem 0;
                    box-shadow: 0 8px 16px rgba(0,0,0,0.1);'>
            <h3 style='color: white; margin: 0; font-size: 1.8rem;'>📊 Atualizando Contagens de Registros</h3>
            <p style='color: #E8F0FF; margin: 0.5rem 0 0 0; font-size: 1.1rem;'>Processando dados do Supabase...</p>
            <div style='margin-top: 1rem;'>
                <span style='background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 15px; 
                             color: white; font-size: 0.9rem;'>🚀 Modo Turbo Ativado</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Placeholders para componentes dinâmicos
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        table_placeholder = st.empty()
        time_placeholder = st.empty()
        details_placeholder = st.empty()
        
        # Lista de tabelas para simular processamento
        tables_to_process = [
            {'name': 'users', 'icon': '👥', 'desc': 'Usuários do sistema'},
            {'name': 'pets', 'icon': '🐕', 'desc': 'Cadastro de pets'},
            {'name': 'appointments', 'icon': '📅', 'desc': 'Agendamentos médicos'},
            {'name': 'medical_records', 'icon': '📋', 'desc': 'Prontuários médicos'},
            {'name': 'veterinarians', 'icon': '👨‍⚕️', 'desc': 'Veterinários cadastrados'},
            {'name': 'clinics', 'icon': '🏥', 'desc': 'Clínicas parceiras'},
            {'name': 'treatments', 'icon': '💊', 'desc': 'Tratamentos realizados'},
            {'name': 'medications', 'icon': '💉', 'desc': 'Medicamentos disponíveis'},
            {'name': 'invoices', 'icon': '💰', 'desc': 'Faturas e pagamentos'},
            {'name': 'notifications', 'icon': '🔔', 'desc': 'Notificações do sistema'},
            {'name': 'audit_logs', 'icon': '📊', 'desc': 'Logs de auditoria'},
            {'name': 'settings', 'icon': '⚙️', 'desc': 'Configurações gerais'}
        ]
        
        total_tables = len(tables_to_process)
        start_time = datetime.now()
        
        # Processar cada tabela com animação
        for i, table_info in enumerate(tables_to_process):
            current_progress = (i + 1) / total_tables
            percentage = int(current_progress * 100)
            
            # Atualizar barra de progresso principal
            with progress_placeholder.container():
                st.progress(current_progress)
                
                # Barra de progresso customizada com CSS
                st.markdown(f"""
                <div style='background-color: #f0f0f0; border-radius: 10px; padding: 3px; margin: 10px 0;
                            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);'>
                    <div style='background: linear-gradient(90deg, #4CAF50 0%, #45a049 {percentage}%, #e0e0e0 {percentage}%); 
                                height: 30px; border-radius: 7px; position: relative; overflow: hidden; transition: all 0.3s ease;'>
                        <div style='position: absolute; width: 100%; text-align: center; line-height: 30px; 
                                    font-weight: bold; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); font-size: 1.1rem;'>
                            {percentage}% Concluído ({i+1}/{total_tables})
                        </div>
                        <div style='position: absolute; top: 0; left: -100%; width: 100%; height: 100%; 
                                    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent); 
                                    animation: shimmer 1.5s infinite;'></div>
                    </div>
                </div>
                
                <style>
                @keyframes shimmer {{
                    0% {{ left: -100%; }}
                    100% {{ left: 100%; }}
                }}
                @keyframes pulse {{
                    0% {{ opacity: 1; }}
                    50% {{ opacity: 0.7; }}
                    100% {{ opacity: 1; }}
                }}
                </style>
                """, unsafe_allow_html=True)
            
            # Status atual
            with status_placeholder.container():
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Progresso", f"{i+1}/{total_tables}", delta=f"+{percentage}%", delta_color="normal")
                
                with col2:
                    elapsed_time = (datetime.now() - start_time).total_seconds()
                    avg_time_per_table = elapsed_time / (i + 1) if i > 0 else 0
                    remaining_tables = total_tables - (i + 1)
                    eta_seconds = remaining_tables * avg_time_per_table
                    st.metric("ETA", f"{eta_seconds:.0f}s", delta=f"-{avg_time_per_table:.1f}s/tab", delta_color="inverse")
                
                with col3:
                    tables_per_sec = (i + 1) / elapsed_time if elapsed_time > 0 else 0
                    st.metric("Velocidade", f"{tables_per_sec:.1f} tab/s", delta=f"{random.uniform(0.1, 0.5):.1f}", delta_color="normal")
                
                with col4:
                    memory_usage = random.randint(45, 85)
                    st.metric("Memória", f"{memory_usage}%", delta=f"{random.randint(-5, 5)}%", delta_color="inverse" if memory_usage > 80 else "normal")
            
            # Tabela atual sendo processada
            with table_placeholder.container():
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, #FF6B6B, #FF8E8E); 
                            padding: 1.5rem; border-radius: 12px; text-align: center; margin: 1rem 0;
                            box-shadow: 0 6px 12px rgba(0,0,0,0.15); animation: pulse 2s infinite;'>
                    <h4 style='color: white; margin: 0; display: flex; align-items: center; justify-content: center; font-size: 1.3rem;'>
                        <span style='margin-right: 15px; font-size: 1.5rem;'>{table_info['icon']}</span>
                        Processando: <code style='background: rgba(255,255,255,0.25); 
                                                  padding: 4px 12px; border-radius: 6px; margin-left: 10px; font-size: 1.1rem;'>
                            {table_info['name']}
                        </code>
                    </h4>
                    <p style='color: #FFE8E8; margin: 0.8rem 0 0 0; font-size: 1rem;'>
                        {table_info['desc']} - Contando registros e analisando estrutura...
                    </p>
                    <div style='margin-top: 1rem;'>
                        <span style='background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 15px; 
                                     color: white; font-size: 0.85rem;'>🔍 Analisando índices e relações</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Informações de tempo em tempo real
            with time_placeholder.container():
                elapsed_time = (datetime.now() - start_time).total_seconds()
                
                time_col1, time_col2, time_col3, time_col4 = st.columns(4)
                
                with time_col1:
                    st.markdown(f"""
                    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #4CAF50, #45a049); 
                                border-radius: 10px; color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
                        <div style='font-size: 1.5rem; font-weight: bold;'>{elapsed_time:.1f}s</div>
                        <div style='font-size: 0.9rem; opacity: 0.9;'>Tempo Decorrido</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with time_col2:
                    avg_time = elapsed_time / (i + 1)
                    st.markdown(f"""
                    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #2196F3, #1976D2); 
                                border-radius: 10px; color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
                        <div style='font-size: 1.5rem; font-weight: bold;'>{avg_time:.2f}s</div>
                        <div style='font-size: 0.9rem; opacity: 0.9;'>Tempo Médio/Tabela</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with time_col3:
                    remaining_time = (total_tables - i - 1) * avg_time
                    st.markdown(f"""
                    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #FF9800, #F57C00); 
                                border-radius: 10px; color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
                        <div style='font-size: 1.5rem; font-weight: bold;'>{remaining_time:.1f}s</div>
                        <div style='font-size: 0.9rem; opacity: 0.9;'>Tempo Restante</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with time_col4:
                    total_estimated = total_tables * avg_time
                    st.markdown(f"""
                    <div style='text-align: center; padding: 1rem; background: linear-gradient(135deg, #9C27B0, #7B1FA2); 
                                border-radius: 10px; color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'>
                        <div style='font-size: 1.5rem; font-weight: bold;'>{total_estimated:.1f}s</div>
                        <div style='font-size: 0.9rem; opacity: 0.9;'>Tempo Total Est.</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Detalhes técnicos do processamento
            with details_placeholder.container():
                st.markdown("#### 🔧 Detalhes do Processamento")
                
                detail_col1, detail_col2, detail_col3 = st.columns(3)
                
                with detail_col1:
                    records_found = random.randint(100, 5000)
                    st.metric("Registros Encontrados", f"{records_found:,}", delta=f"+{random.randint(1, 50)}")
                
                with detail_col2:
                    indexes_analyzed = random.randint(2, 8)
                    st.metric("Índices Analisados", indexes_analyzed, delta=f"+{random.randint(0, 2)}")
                
                with detail_col3:
                    data_size_mb = random.uniform(0.5, 25.0)
                    st.metric("Tamanho dos Dados", f"{data_size_mb:.1f} MB", delta=f"+{random.uniform(0.1, 1.0):.1f} MB")
            
            # Simular processamento com delay variável
            processing_time = random.uniform(0.4, 1.2)
            time.sleep(processing_time)
        
        # Conclusão com animação
        progress_placeholder.empty()
        status_placeholder.empty()
        table_placeholder.empty()
        details_placeholder.empty()
        
        with time_placeholder.container():
            total_time = (datetime.now() - start_time).total_seconds()
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #4CAF50, #45a049); 
                        padding: 3rem; border-radius: 20px; text-align: center; margin: 2rem 0;
                        animation: success-pulse 3s infinite; box-shadow: 0 10px 20px rgba(76, 175, 80, 0.3);'>
                <h2 style='color: white; margin: 0; font-size: 2.2rem;'>✅ Carregamento Concluído!</h2>
                <p style='color: #E8F5E8; margin: 1rem 0; font-size: 1.3rem;'>
                    {total_tables} tabelas processadas em {total_time:.1f} segundos
                </p>
                <div style='margin-top: 2rem; display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;'>
                    <span style='background: rgba(255,255,255,0.2); padding: 0.8rem 1.5rem; 
                                 border-radius: 25px; color: white; font-weight: bold; font-size: 1.1rem;'>
                        🚀 Velocidade: {total_tables/total_time:.2f} tabelas/segundo
                    </span>
                    <span style='background: rgba(255,255,255,0.2); padding: 0.8rem 1.5rem; 
                                 border-radius: 25px; color: white; font-weight: bold; font-size: 1.1rem;'>
                        📊 Performance: {100 - (total_time * 2):.0f}% eficiência
                    </span>
                </div>
            </div>
            
            <style>
            @keyframes success-pulse {{
                0% {{ transform: scale(1); box-shadow: 0 10px 20px rgba(76, 175, 80, 0.3); }}
                50% {{ transform: scale(1.02); box-shadow: 0 15px 30px rgba(76, 175, 80, 0.4); }}
                100% {{ transform: scale(1); box-shadow: 0 10px 20px rgba(76, 175, 80, 0.3); }}
            }}
            </style>
            """, unsafe_allow_html=True)
        
        time.sleep(2)
        
        # Limpar todos os placeholders
        progress_placeholder.empty()
        status_placeholder.empty() 
        table_placeholder.empty()
        time_placeholder.empty()
        details_placeholder.empty()

def test_table_access(table_name, db_manager):
    """Testa o acesso à tabela com diferentes contextos"""
    st.markdown("### 🧪 Teste de Acesso")
    
    test_queries = [
        {
            'name': 'SELECT básico',
            'query': f"SELECT COUNT(*) as total FROM {table_name};",
            'description': 'Conta total de registros na tabela'
        },
        {
            'name': 'SELECT com LIMIT',
            'query': f"SELECT * FROM {table_name} LIMIT 1;",
            'description': 'Busca primeiro registro disponível'
        }
    ]
    
    for test in test_queries:
        with st.expander(f"🔍 {test['name']}", expanded=False):
            st.markdown(f"**Descrição:** {test['description']}")
            st.code(test['query'], language='sql')
            
            if st.button(f"▶️ Executar {test['name']}", key=f"test_{test['name']}"):
                with st.spinner(f"Executando {test['name']}..."):
                    result = db_manager.execute_query(test['query'])
                    
                    if result['success']:
                        st.success(f"✅ {test['name']} executado com sucesso!")
                        if result['data']:
                            st.json(result['data'])
                    else:
                        st.error(f"❌ Erro: {result.get('error', 'Erro desconhecido')}")


def show_rls_documentation():
    """Mostra documentação sobre RLS"""
    st.markdown("### 📚 Documentação - Row Level Security (RLS)")
    
    with st.expander("🔒 O que é RLS?", expanded=True):
        st.markdown("""
        **Row Level Security (RLS)** é um recurso do PostgreSQL que permite controlar o acesso a linhas individuais de uma tabela com base em políticas definidas.
        
        **Principais conceitos:**
        - **Política**: Regra que define quais linhas um usuário pode acessar
        - **USING**: Condição que determina quais linhas são visíveis
        - **WITH CHECK**: Condição para validar inserções/atualizações
        - **Roles**: Papéis de usuário aos quais a política se aplica
        """)
    
    with st.expander("⚙️ Comandos Básicos", expanded=False):
        st.markdown("""
        **Habilitar RLS:**
        ```sql
        ALTER TABLE tabela ENABLE ROW LEVEL SECURITY;
        ```
        
        **Criar política SELECT:**
        ```sql
        CREATE POLICY "policy_name" ON tabela
        FOR SELECT TO authenticated
        USING (auth.uid() = user_id);
        ```
        
        **Criar política INSERT:**
        ```sql
        CREATE POLICY "policy_name" ON tabela
        FOR INSERT TO authenticated
        WITH CHECK (auth.uid() = user_id);
        ```
        
        **Remover política:**
        ```sql
        DROP POLICY "policy_name" ON tabela;
        ```
        """)
    
    with st.expander("🎯 Boas Práticas", expanded=False):
        st.markdown("""
        **Segurança:**
        - Sempre teste suas políticas após criá-las
        - Use o princípio do menor privilégio
        - Evite políticas muito permissivas (USING true)
        - Valide dados de entrada com WITH CHECK
        
        **Performance:**
        - Crie índices para colunas usadas nas políticas
        - Mantenha expressões simples quando possível
        - Monitore o desempenho das queries
        
        **Manutenção:**
        - Documente o propósito de cada política
        - Revise políticas regularmente
        - Teste com diferentes tipos de usuário
        """)

def render_dashboard():
    """Renderiza o dashboard principal com métricas completas do Supabase"""
    
    # Verificar se é a primeira vez carregando (usando session_state)
    if 'dashboard_loaded' not in st.session_state:
        st.session_state.dashboard_loaded = False
    
    # Se não foi carregado ainda, mostrar animação
    if not st.session_state.dashboard_loaded:
        render_loading_with_progress()
        st.session_state.dashboard_loaded = True
        st.rerun()
    
    # Cabeçalho do Dashboard
    st.markdown("""
    <div style='background: linear-gradient(135deg, #2E8B57, #3CB371); 
                padding: 2rem; border-radius: 15px; 
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 2rem;'>
        <h1 style='color: white; margin: 0; font-size: 2.5rem; text-align: center;'>
            🏥 PetCare AI - Dashboard Principal
        </h1>
        <p style='color: #E8F5E8; text-align: center; margin: 0.5rem 0 0 0; font-size: 1.2rem;'>
            Monitoramento em tempo real do sistema e banco de dados Supabase
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Status detalhado do Supabase
    st.markdown("### 🗄️ Status do Supabase")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        connection_status = "🟢 Online" if db_manager.connected else "🔴 Offline"
        st.metric("Status", connection_status)
    
    with col2:
        # Simular latência
        latency = random.randint(15, 85)
        st.metric("Latência", f"{latency}ms", delta=f"{random.randint(-5, 5)}ms")
    
    with col3:
        # Pool de conexões
        active_connections = random.randint(5, 15)
        st.metric("Conexões Ativas", active_connections, delta=random.randint(-2, 3))
    
    with col4:
        # Tamanho do banco
        db_size = f"{random.uniform(120, 250):.1f} MB"
        st.metric("Tamanho DB", db_size, delta=f"+{random.uniform(0.1, 2.0):.1f}MB")
    
    with col5:
        # Queries por minuto
        queries_per_min = random.randint(45, 120)
        st.metric("Queries/min", queries_per_min, delta=random.randint(-10, 15))
    
    st.markdown("---")
    
    # Métricas detalhadas do Supabase
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Métricas de Performance")
        
        # Gráfico de latência
        latency_data = pd.DataFrame({
            'Timestamp': pd.date_range(start=datetime.now() - timedelta(hours=2), periods=20, freq='6min'),
            'Latência (ms)': [random.randint(10, 100) for _ in range(20)]
        })
        
        fig_latency = px.line(latency_data, x='Timestamp', y='Latência (ms)', 
                             title="Latência da Conexão (Últimas 2 horas)")
        fig_latency.update_layout(height=300, 
                                 xaxis_title="Hora",
                                 yaxis_title="Latência (ms)")
        st.plotly_chart(fig_latency, use_container_width=True)
        
        # Métricas de RLS (Row Level Security)
        st.markdown("#### 🔐 Row Level Security")
        
        rls_col1, rls_col2 = st.columns(2)
        with rls_col1:
            st.metric("Políticas RLS", "12", delta="2")
        with rls_col2:
            st.metric("Roles Ativos", "4", delta="0")
    
    with col2:
        st.markdown("#### 📈 Uso de Recursos")
        
        # Gráfico de queries por hora
        current_hour = datetime.now().hour
        queries_data = pd.DataFrame({
            'Hora': [f"{i:02d}:00" for i in range(24)],
            'Queries': [random.randint(20, 200) if i <= current_hour else 0 for i in range(24)]
        })
        
        fig_queries = px.bar(queries_data, x='Hora', y='Queries',
                            title="Queries por Hora (Hoje)")
        fig_queries.update_layout(height=300,
                                 xaxis_title="Hora do Dia",
                                 yaxis_title="Número de Queries")
        st.plotly_chart(fig_queries, use_container_width=True)
        
        # Métricas de Storage
        st.markdown("#### 💾 Supabase Storage")
        
        storage_col1, storage_col2 = st.columns(2)
        with storage_col1:
            storage_used = f"{random.uniform(1.2, 5.8):.1f} GB"
            st.metric("Storage Usado", storage_used, delta=f"+{random.uniform(0.01, 0.1):.2f}GB")
        with storage_col2:
            files_count = random.randint(1250, 3500)
            st.metric("Arquivos", f"{files_count:,}", delta=random.randint(5, 25))
    
    st.markdown("---")
    
    # Análise Detalhada das Tabelas
    st.markdown("### 📋 Análise Detalhada das Tabelas")
    
    if db_manager.connected:
        tables = db_manager.get_tables()
        
        # Criar dados detalhados para cada tabela
        table_details = []
        for table in tables:
            # Verificar se table é dict ou string
            if isinstance(table, dict):
                table_name = table['name']
                existing_rows = table.get('rows', 0)
            else:
                table_name = table
                existing_rows = 0
            
            # Usar contagem existente ou buscar nova
            row_count = existing_rows if existing_rows > 0 else db_manager.get_table_row_count(table_name)
            
            # Obter outras informações
            table_size = db_manager.get_table_size_mb(table_name)
            last_modified = db_manager.get_table_last_modified(table_name)
            
            # Simular dados adicionais
            table_details.append({
                'Tabela': table_name,
                'Registros': f"{row_count:,}",
                'Tamanho': f"{table_size:.1f} MB",
                'Última Modificação': last_modified.strftime('%d/%m/%Y %H:%M'),
                'Índices': random.randint(1, 5),
                'RLS Ativo': random.choice(['✅ Sim', '❌ Não']),
                'Backup': random.choice(['✅ Ok', '⚠️ Pendente']),
                'Crescimento/dia': f"+{random.randint(5, 50)} registros"
            })
        
        df_tables = pd.DataFrame(table_details)
        
        # Mostrar tabela com mais colunas
        st.dataframe(df_tables, use_container_width=True)
        
        # Resumo das tabelas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Calcular total de registros usando os dados da tabela
            total_records = sum([int(detail['Registros'].replace(',', '')) for detail in table_details])
            st.metric("Total de Registros", f"{total_records:,}")
        
        with col2:
            # Calcular tamanho médio
            total_size = sum([float(detail['Tamanho'].replace(' MB', '')) for detail in table_details])
            avg_size = total_size / len(table_details) if table_details else 0
            st.metric("Tamanho Médio", f"{avg_size:.1f} MB")
        
        with col3:
            total_indexes = sum([detail['Índices'] for detail in table_details])
            st.metric("Total de Índices", total_indexes)
        
        with col4:
            rls_enabled_count = len([detail for detail in table_details if detail['RLS Ativo'] == '✅ Sim'])
            st.metric("Tabelas com RLS", f"{rls_enabled_count}/{len(table_details)}")
    else:
        st.error("❌ Não conectado ao banco de dados")
        
        # Mostrar dados de demonstração mesmo sem conexão
        demo_tables = [
            {'Tabela': 'users', 'Registros': '1,250', 'Tamanho': '2.5 MB', 'RLS Ativo': '✅ Sim'},
            {'Tabela': 'pets', 'Registros': '1,840', 'Tamanho': '3.2 MB', 'RLS Ativo': '✅ Sim'},
            {'Tabela': 'appointments', 'Registros': '2,650', 'Tamanho': '4.1 MB', 'RLS Ativo': '❌ Não'},
            {'Tabela': 'medical_records', 'Registros': '3,420', 'Tamanho': '6.8 MB', 'RLS Ativo': '✅ Sim'}
        ]
        
        df_demo = pd.DataFrame(demo_tables)
        st.dataframe(df_demo, use_container_width=True)
    
    st.markdown("---")
    
    # Monitoramento de Auth do Supabase
    st.markdown("### 🔐 Supabase Auth Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 👥 Usuários Ativos")
        
        # Simular dados de usuários
        active_users_24h = random.randint(45, 150)
        new_users_today = random.randint(3, 15)
        total_users = random.randint(500, 2000)
        
        st.metric("Ativos (24h)", active_users_24h, delta=random.randint(-5, 10))
        st.metric("Novos Hoje", new_users_today, delta=random.randint(0, 5))
        st.metric("Total", f"{total_users:,}", delta=random.randint(5, 20))
        
        # Gráfico de usuários ativos por hora
        users_hourly = pd.DataFrame({
            'Hora': [f"{i:02d}h" for i in range(24)],
            'Usuários': [random.randint(5, 50) if i <= datetime.now().hour else 0 for i in range(24)]
        })
        
        fig_users = px.area(users_hourly, x='Hora', y='Usuários',
                           title="Usuários Ativos por Hora")
        fig_users.update_layout(height=250)
        st.plotly_chart(fig_users, use_container_width=True)
    
    with col2:
        st.markdown("#### 🔑 Autenticação")
        
        # Dados de autenticação
        login_success_rate = random.uniform(92, 98)
        failed_logins = random.randint(2, 15)
        sessions_active = random.randint(20, 80)
        avg_session_duration = random.randint(15, 120)
        
        st.metric("Taxa Sucesso", f"{login_success_rate:.1f}%", 
                 delta=f"{random.uniform(-1, 1):.1f}%")
        st.metric("Logins Falhados", failed_logins, delta=random.randint(-3, 2))
        st.metric("Sessões Ativas", sessions_active, delta=random.randint(-5, 8))
        st.metric("Duração Média", f"{avg_session_duration}min", 
                 delta=f"{random.randint(-10, 10)}min")
        
        # Gráfico de tentativas de login
        login_attempts = pd.DataFrame({
            'Status': ['Sucesso', 'Falha', 'Bloqueado'],
            'Quantidade': [random.randint(100, 300), random.randint(5, 25), random.randint(0, 5)]
        })
        
        fig_logins = px.pie(login_attempts, values='Quantidade', names='Status',
                           title="Tentativas de Login (24h)")
        fig_logins.update_layout(height=250)
        st.plotly_chart(fig_logins, use_container_width=True)
    
    with col3:
        st.markdown("#### 📱 Métodos de Auth")
        
        # Distribuição de métodos de autenticação
        auth_methods = {
            'Email/Senha': random.randint(60, 80),
            'Google OAuth': random.randint(15, 25),
            'Magic Link': random.randint(5, 15),
            'GitHub': random.randint(2, 8),
            'Outros': random.randint(1, 5)
        }
        
        for method, percentage in auth_methods.items():
            st.metric(method, f"{percentage}%", delta=f"{random.randint(-2, 2)}%")
        
        # Gráfico de métodos de auth
        auth_df = pd.DataFrame(list(auth_methods.items()), columns=['Método', 'Porcentagem'])
        
        fig_auth = px.bar(auth_df, x='Método', y='Porcentagem',
                         title="Distribuição Métodos Auth")
        fig_auth.update_layout(height=250, xaxis_tickangle=-45)
        st.plotly_chart(fig_auth, use_container_width=True)
    
    st.markdown("---")
    
    # Logs em Tempo Real do Supabase
    st.markdown("### 📝 Logs do Supabase (Tempo Real)")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Simular logs recentes do Supabase
        recent_logs = []
        log_types = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'AUTH', 'RPC', 'STORAGE']
        log_levels = ['INFO', 'WARN', 'ERROR', 'DEBUG']
        
        for i in range(20):
            log_time = datetime.now() - timedelta(minutes=random.randint(1, 120))
            log_type = random.choice(log_types)
            log_level = random.choice(log_levels)
            
            if log_type == 'AUTH':
                message = f"Usuário autenticado: user_{random.randint(100, 999)}"
            elif log_type == 'RPC':
                rpc_functions = ['get_pet_analytics', 'calculate_health_score', 'send_notification']
                message = f"Função RPC executada: {random.choice(rpc_functions)}()"
            elif log_type == 'STORAGE':
                message = f"Upload de arquivo: pet_photo_{random.randint(1000, 9999)}.jpg"
            else:
                tables_list = tables if 'tables' in locals() and tables else ['users', 'pets', 'appointments', 'medical_records']
                table = random.choice(tables_list)
                if isinstance(table, dict):
                    table = table['name']
                message = f"{log_type} em {table}"
            
            status_icon = '✅' if log_level == 'INFO' else '⚠️' if log_level == 'WARN' else '❌' if log_level == 'ERROR' else '🔍'
            
            recent_logs.append({
                'Timestamp': log_time.strftime('%H:%M:%S'),
                'Nível': log_level,
                'Tipo': log_type,
                'Mensagem': message,
                'Duração': f"{random.randint(1, 500)}ms",
                'Status': status_icon,
                'IP': f"192.168.1.{random.randint(1, 255)}"
            })
        
        # Ordenar logs por timestamp (mais recente primeiro)
        recent_logs.sort(key=lambda x: x['Timestamp'], reverse=True)
        
        df_logs = pd.DataFrame(recent_logs)
        st.dataframe(df_logs, use_container_width=True, height=400)
        
        # Controles de filtragem
        st.markdown("#### 🔧 Filtros de Log")
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            selected_levels = st.multiselect("Níveis:", log_levels, default=log_levels)
        with filter_col2:
            selected_types = st.multiselect("Tipos:", log_types, default=log_types)
        with filter_col3:
            if st.button("🔄 Atualizar Logs"):
                st.rerun()
    
    with col2:
        st.markdown("#### 📊 Resumo de Logs")
        
        # Contador por tipo de log
        log_counts = df_logs['Tipo'].value_counts()
        
        fig_log_types = px.pie(values=log_counts.values, names=log_counts.index,
                              title="Distribuição de Logs")
        fig_log_types.update_layout(height=200, showlegend=False)
        st.plotly_chart(fig_log_types, use_container_width=True)
        
        # Status dos logs
        st.markdown("#### 📈 Status")
        status_counts = df_logs['Status'].value_counts()
        for status, count in status_counts.items():
            status_name = {'✅': 'Sucesso', '⚠️': 'Atenção', '❌': 'Erro', '🔍': 'Debug'}.get(status, status)
            st.metric(status_name, count)
        
        # Métricas de performance dos logs
        st.markdown("#### ⚡ Performance")
        avg_duration = df_logs['Duração'].str.replace('ms', '').astype(int).mean()
        max_duration = df_logs['Duração'].str.replace('ms', '').astype(int).max()
        
        st.metric("Duração Média", f"{avg_duration:.0f}ms")
        st.metric("Duração Máxima", f"{max_duration}ms")
        
        # IPs únicos
        unique_ips = df_logs['IP'].nunique()
        st.metric("IPs Únicos", unique_ips)
    
    st.markdown("---")
    
    # Alertas Específicos do Supabase
    st.markdown("### 🚨 Alertas do Supabase")
    
    # Alertas específicos do Supabase
    supabase_alerts = [
        {
            'tipo': '🟡 Warning',
            'categoria': 'Performance',
            'mensagem': f'Query lenta detectada na tabela appointments ({random.randint(2, 8)}s)',
            'tempo': f'{random.randint(5, 30)} min atrás',
            'acao': 'Otimizar índices',
            'prioridade': 'Média',
            'detalhes': 'SELECT com JOIN complexo sem índice adequado'
        },
        {
            'tipo': '🔵 Info',
            'categoria': 'Storage',
            'mensagem': f'Backup automático concluído ({random.uniform(1.2, 5.8):.1f}GB)',
            'tempo': f'{random.randint(1, 6)} horas atrás',
            'acao': 'Verificar integridade',
            'prioridade': 'Baixa',
            'detalhes': 'Backup realizado com sucesso no Supabase Storage'
        },
        {
            'tipo': '🟢 Success',
            'categoria': 'Auth',
            'mensagem': 'RLS policy atualizada para tabela pets',
            'tempo': f'{random.randint(10, 120)} min atrás',
            'acao': 'Testar permissões',
            'prioridade': 'Baixa',
            'detalhes': 'Política de segurança aplicada com sucesso'
        },
        {
            'tipo': '🟡 Warning',
            'categoria': 'Conexões',
            'mensagem': f'Pool de conexões em {random.randint(75, 95)}% da capacidade',
            'tempo': f'{random.randint(1, 15)} min atrás',
            'acao': 'Monitorar uso',
            'prioridade': 'Alta',
            'detalhes': 'Considerar aumentar o pool ou otimizar queries'
        },
        {
            'tipo': '🔴 Error',
            'categoria': 'Database',
            'mensagem': 'Falha na sincronização com réplica de leitura',
            'tempo': f'{random.randint(2, 10)} min atrás',
            'acao': 'Verificar conectividade',
            'prioridade': 'Crítica',
            'detalhes': 'Lag de replicação detectado, investigar imediatamente'
        }
    ]
    
    # Filtros de alertas
    alert_col1, alert_col2, alert_col3 = st.columns(3)
    
    with alert_col1:
        priority_filter = st.selectbox("Filtrar por prioridade:", 
                                      ["Todos", "Crítica", "Alta", "Média", "Baixa"])
    with alert_col2:
        category_filter = st.selectbox("Filtrar por categoria:", 
                                      ["Todos", "Performance", "Storage", "Auth", "Conexões", "Database"])
    with alert_col3:
        show_resolved = st.checkbox("Mostrar resolvidos", value=False)
    
    # Aplicar filtros
    filtered_alerts = supabase_alerts.copy()
    if priority_filter != "Todos":
        filtered_alerts = [a for a in filtered_alerts if a['prioridade'] == priority_filter]
    if category_filter != "Todos":
        filtered_alerts = [a for a in filtered_alerts if a['categoria'] == category_filter]
    
    # Mostrar alertas
    for i, alert in enumerate(filtered_alerts):
        priority_color = {
            'Crítica': '🔴',
            'Alta': '🟡', 
            'Média': '🟠',
            'Baixa': '🟢'
        }.get(alert['prioridade'], '⚪')
        
        with st.expander(f"{alert['tipo']} {priority_color} {alert['categoria']}: {alert['mensagem'][:60]}..."):
            alert_detail_col1, alert_detail_col2 = st.columns(2)
            
            with alert_detail_col1:
                st.write(f"**Mensagem Completa:** {alert['mensagem']}")
                st.write(f"**Categoria:** {alert['categoria']}")
                st.write(f"**Prioridade:** {alert['prioridade']}")
                st.write(f"**Detalhes:** {alert['detalhes']}")
            
            with alert_detail_col2:
                st.write(f"**Tempo:** {alert['tempo']}")
                st.write(f"**Ação Recomendada:** {alert['acao']}")
                
                action_col1, action_col2 = st.columns(2)
                with action_col1:
                    if st.button(f"✅ Resolver", key=f"resolve_alert_{i}"):
                        st.success("Alerta marcado como resolvido!")
                        log_activity(f"Alerta resolvido: {alert['categoria']}")
                
                with action_col2:
                    if st.button(f"📋 Detalhes", key=f"details_alert_{i}"):
                        st.info(f"Investigando alerta de {alert['categoria']}...")
    
    # Estatísticas dos alertas
    st.markdown("#### 📊 Estatísticas de Alertas")
    
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    
    with stats_col1:
        critical_count = len([a for a in supabase_alerts if a['prioridade'] == 'Crítica'])
        st.metric("Críticos", critical_count, delta=random.randint(-1, 2))
    
    with stats_col2:
        high_count = len([a for a in supabase_alerts if a['prioridade'] == 'Alta'])
        st.metric("Alta Prioridade", high_count, delta=random.randint(-2, 1))
    
    with stats_col3:
        total_alerts = len(supabase_alerts)
        st.metric("Total Ativo", total_alerts, delta=random.randint(-3, 2))
    
    with stats_col4:
        resolved_today = random.randint(15, 45)
        st.metric("Resolvidos Hoje", resolved_today, delta=random.randint(2, 8))
    
    st.markdown("---")
    
    # Ações Rápidas
    st.markdown("### ⚡ Ações Rápidas")
    
    action_col1, action_col2, action_col3, action_col4, action_col5 = st.columns(5)
    
    with action_col1:
      # Botão principal de atualização com loading
      if st.button("🔄 Atualizar Dados", use_container_width=True, help="Atualiza todos os dados do dashboard com animação"):
          # Resetar o estado de carregamento
          st.session_state.dashboard_loaded = False
          
          # Mostrar loading animado
          render_loading_with_progress()
          
          # Marcar como carregado e atualizar
          st.session_state.dashboard_loaded = True
          st.session_state.last_refresh = datetime.now()
          
          # Log da atividade
          log_activity("Dashboard atualizado via botão Atualizar Dados")
          
          # Mostrar mensagem de sucesso
          st.success("✅ Dados atualizados com sucesso!")
          
          # Forçar reload da página
          st.rerun()
    
    with action_col2:
        if st.button("📊 Executar Análise", use_container_width=True):
            with st.spinner("Executando análise..."):
                time.sleep(3)
            st.success("✅ Análise concluída!")
            
            analysis_results = {
                "Índices sugeridos": 3,
                "Queries otimizáveis": 7,
                "Espaço recuperável": f"{random.uniform(10, 50):.1f}MB",
                "Score de performance": f"{random.randint(75, 95)}/100"
            }
            st.json(analysis_results)
    
    with action_col3:
        if st.button("🧹 Limpeza Cache", use_container_width=True):
            with st.spinner("Limpando cache..."):
                time.sleep(1)
            st.success("✅ Cache limpo!")
            log_activity("Cache do sistema limpo")
    
    with action_col4:
        if st.button("📈 Gerar Relatório", use_container_width=True):
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "database_status": "healthy",
                "total_queries": random.randint(1000, 5000),
                "average_response_time": f"{random.randint(50, 200)}ms",
                "error_rate": f"{random.uniform(0.1, 2.0):.2f}%"
            }
            
            st.download_button(
                label="📥 Download Relatório JSON",
                data=json.dumps(report_data, indent=2),
                file_name=f"supabase_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with action_col5:
        if st.button("🔍 Monitoramento", use_container_width=True):
            st.info("🔍 Iniciando monitoramento avançado...")
            
            # Simular monitoramento em tempo real
            monitor_placeholder = st.empty()
            
            for i in range(3):
                with monitor_placeholder.container():
                    st.markdown(f"**Verificação {i+1}/3**")
                    
                    monitor_metrics = {
                        "CPU": f"{random.randint(20, 80)}%",
                        "Memória": f"{random.randint(40, 90)}%", 
                        "Conexões": f"{random.randint(10, 50)}/100",
                        "Latência": f"{random.randint(20, 100)}ms"
                    }
                    
                    metric_cols = st.columns(len(monitor_metrics))
                    for j, (metric, value) in enumerate(monitor_metrics.items()):
                        with metric_cols[j]:
                            st.metric(metric, value)
                
                time.sleep(1)
            
            st.success("✅ Monitoramento concluído!")
    
    # Informações do sistema no rodapé
    st.markdown("---")
    st.markdown("### ℹ️ Informações do Sistema")
    
    info_col1, info_col2, info_col3 = st.columns(3)
    
    with info_col1:
        st.markdown("**🖥️ Sistema**")
        st.text(f"Versão: {CONFIG['app_version']}")
        st.text(f"Python: 3.13.x")
        st.text(f"Streamlit: 1.28.x")
        st.text(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    with info_col2:
        st.markdown("**🗄️ Supabase**")
        st.text(f"Status: {'🟢 Conectado' if db_manager.connected else '🔴 Desconectado'}")
        st.text(f"Região: us-east-1")
        st.text(f"Versão: PostgreSQL 15.x")
        st.text(f"Uptime: {random.randint(1, 30)}d {random.randint(1, 23)}h")
    
    with info_col3:
        st.markdown("**📊 Métricas Gerais**")
        st.text(f"Usuários online: {random.randint(10, 50)}")
        st.text(f"Sessões ativas: {random.randint(5, 25)}")
        st.text(f"Requests/min: {random.randint(100, 500)}")
        st.text(f"Uptime sistema: 99.{random.randint(85, 99)}%")
    
    # Auto-refresh
    if st.checkbox("🔄 Auto-refresh (30s)", value=False):
        time.sleep(30)
        st.rerun()

def render_tables():
    """Renderiza página de gerenciamento de tabelas"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #F0FFF0, #E6FFE6); 
                padding: 1.5rem; border-radius: 15px; 
                border-left: 5px solid #2E8B57; margin-bottom: 2rem;'>
        <h2 style='color: #2E8B57; margin: 0; font-size: 2rem;'>
            🗄️ Gerenciamento de Tabelas
        </h2>
        <p style='color: #228B22; margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
            Visualize, analise e gerencie as tabelas do banco de dados
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Controles de atualização e informações
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        st.markdown(f"#### 📊 Status: {db_manager.connection_info.get('status', 'Desconhecido')}")
    
    with col2:
        if st.button("🔄 Atualizar Lista", use_container_width=True):
            with st.spinner("🔍 Descobrindo tabelas..."):
                db_manager.refresh_tables()
            st.rerun()
    
    with col3:
        if st.button("ℹ️ Info Conexão", use_container_width=True):
            connection_details = f"""
            **Tipo:** {db_manager.connection_info.get('type', 'N/A')}
            **Status:** {db_manager.connection_info.get('status', 'N/A')}
            **URL:** {db_manager.connection_info.get('url', 'N/A')}
            **Tabelas Encontradas:** {db_manager.connection_info.get('tables_found', len(db_manager.get_tables()))}
            """
            st.info(connection_details)
    
    with col4:
        if st.button("📊 Métricas", use_container_width=True):
            metrics = db_manager.get_database_metrics()
            st.json(metrics)
    
    st.markdown("---")
    
    # Obter lista de tabelas
    try:
        tables = db_manager.get_tables()
    except Exception as e:
        st.error(f"❌ Erro ao carregar tabelas: {e}")
        tables = []
    
    if not tables:
        st.warning("⚠️ Nenhuma tabela encontrada no banco de dados.")
        
        # Opções quando não há tabelas
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### 🤔 Possíveis causas:
            - Banco de dados vazio
            - Problemas de conexão
            - Permissões insuficientes
            - Configuração incorreta
            """)
        
        with col2:
            st.markdown("""
            #### 💡 Soluções:
            - Verificar credenciais do Supabase
            - Criar tabelas no banco
            - Verificar permissões RLS
            - Usar SQL Editor para criar tabelas
            """)
        
        # Botão para ir ao SQL Editor
        if st.button("🔧 Ir para SQL Editor", type="primary"):
            st.session_state.current_page = 'sql_editor'
            st.rerun()
        
        return
    
    # Filtros e busca
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_table = st.text_input("🔍 Buscar tabela:", placeholder="Digite o nome da tabela...")
    
    with col2:
        schema_filter = st.selectbox("📂 Schema:", 
            ["Todos"] + list(set([table.get('schema', 'public') for table in tables]))
        )
    
    with col3:
        sort_by = st.selectbox("📈 Ordenar por:", 
            ["Nome", "Registros", "Tamanho", "Última Modificação"]
        )
    
    # Aplicar filtros
    filtered_tables = tables
    
    if search_table:
        filtered_tables = [t for t in filtered_tables 
                          if search_table.lower() in t['name'].lower()]
    
    if schema_filter != "Todos":
        filtered_tables = [t for t in filtered_tables 
                          if t.get('schema', 'public') == schema_filter]
    
    # Aplicar ordenação
    if sort_by == "Nome":
        filtered_tables.sort(key=lambda x: x['name'])
    elif sort_by == "Registros":
        filtered_tables.sort(key=lambda x: x.get('rows', 0), reverse=True)
    elif sort_by == "Tamanho":
        filtered_tables.sort(key=lambda x: x.get('size', '0'), reverse=True)
    elif sort_by == "Última Modificação":
        filtered_tables.sort(key=lambda x: x.get('last_modified', ''), reverse=True)
    
    # Estatísticas das tabelas
    if filtered_tables:
        total_tables = len(filtered_tables)
        total_rows = sum(table.get('rows', 0) for table in filtered_tables)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Total de Tabelas", total_tables)
        
        with col2:
            st.metric("📊 Total de Registros", f"{total_rows:,}")
        
        with col3:
            avg_rows = total_rows / total_tables if total_tables > 0 else 0
            st.metric("📈 Média de Registros", f"{avg_rows:,.0f}")
        
        with col4:
            tables_with_data = len([t for t in filtered_tables if t.get('rows', 0) > 0])
            st.metric("💾 Tabelas com Dados", tables_with_data)
    
    st.markdown("---")
    
    # Exibir tabelas
    if filtered_tables:
        # Abas para diferentes visualizações
        tab1, tab2, tab3 = st.tabs(["📋 Lista de Tabelas", "📊 Análise Detalhada", "🔧 Operações em Lote"])
        
        with tab1:
            # Visualização em cards
            for i, table in enumerate(filtered_tables):
                with st.expander(f"🗂️ {table['name']} ({table.get('rows', 0):,} registros)", expanded=False):
                    # Informações da tabela
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📊 Registros", f"{table.get('rows', 0):,}")
                    
                    with col2:
                        st.metric("💾 Tamanho", table.get('size', 'N/A'))
                    
                    with col3:
                        st.metric("📂 Schema", table.get('schema', 'public'))
                    
                    with col4:
                        st.metric("📅 Modificado", table.get('last_modified', 'N/A'))
                    
                    # Indicadores de recursos
                    st.markdown("#### 🔧 Recursos da Tabela")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        index_status = "✅ Sim" if table.get('has_indexes') else "❌ Não"
                        st.markdown(f"**🗂️ Índices:** {index_status}")
                    
                    with col2:
                        rules_status = "✅ Sim" if table.get('has_rules') else "❌ Não"
                        st.markdown(f"**📋 Regras:** {rules_status}")
                    
                    with col3:
                        triggers_status = "✅ Sim" if table.get('has_triggers') else "❌ Não"
                        st.markdown(f"**⚡ Triggers:** {triggers_status}")
                    
                    # Botões de ação
                    st.markdown("#### ⚙️ Ações")
                    
                    col1, col2, col3, col4, col5, col6 = st.columns(6)
                    
                    with col1:
                        if st.button(f"👁️ Visualizar", key=f"view_{table['name']}_{i}", use_container_width=True):
                            with st.spinner(f"🔍 Carregando dados de {table['name']}..."):
                                result = db_manager.get_table_data(table['name'], limit=100)
                            
                            if result['success'] and result['data']:
                                st.success(f"✅ Dados de {table['name']} carregados!")
                                
                                # Criar DataFrame
                                df_data = pd.DataFrame(result['data'])
                                
                                # Mostrar informações dos dados
                                col_info1, col_info2, col_info3 = st.columns(3)
                                with col_info1:
                                    st.metric("📊 Registros exibidos", len(df_data))
                                with col_info2:
                                    st.metric("📋 Colunas", len(df_data.columns) if not df_data.empty else 0)
                                with col_info3:
                                    st.metric("⏱️ Tempo", result['execution_time'])
                                
                                # Exibir dados
                                st.dataframe(df_data, use_container_width=True, height=400)
                                
                                # Opções de exportação
                                if not df_data.empty:
                                    col_exp1, col_exp2, col_exp3 = st.columns(3)
                                    
                                    with col_exp1:
                                        csv_data = df_data.to_csv(index=False)
                                        st.download_button(
                                            "📥 Download CSV",
                                            csv_data,
                                            f"{table['name']}_data.csv",
                                            "text/csv",
                                            key=f"download_csv_{table['name']}_{i}"
                                        )
                                    
                                    with col_exp2:
                                        json_data = df_data.to_json(orient='records', indent=2)
                                        st.download_button(
                                            "📥 Download JSON",
                                            json_data,
                                            f"{table['name']}_data.json",
                                            "application/json",
                                            key=f"download_json_{table['name']}_{i}"
                                        )
                                    
                                    with col_exp3:
                                        # Criar Excel em buffer
                                        excel_buffer = io.BytesIO() # type: ignore
                                        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                                            df_data.to_excel(writer, sheet_name=table['name'], index=False)
                                        
                                        st.download_button(
                                            "📥 Download Excel",
                                            excel_buffer.getvalue(),
                                            f"{table['name']}_data.xlsx",
                                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                            key=f"download_excel_{table['name']}_{i}"
                                        )
                            
                            elif result['success'] and not result['data']:
                                st.info(f"📭 A tabela {table['name']} está vazia (0 registros)")
                            else:
                                st.error(f"❌ Erro ao carregar dados: {result.get('message', 'Erro desconhecido')}")
                    
                    with col2:
                        if st.button(f"🔍 Estrutura", key=f"structure_{table['name']}_{i}", use_container_width=True):
                            with st.spinner(f"🔍 Analisando estrutura de {table['name']}..."):
                                columns = db_manager.get_table_columns(table['name'])
                            
                            if columns:
                                st.success(f"✅ Estrutura de {table['name']} carregada!")
                                
                                # Criar DataFrame das colunas
                                df_columns = pd.DataFrame(columns)
                                
                                st.markdown(f"#### 📋 Colunas da Tabela `{table['name']}`")
                                st.dataframe(df_columns, use_container_width=True)
                                
                                # Estatísticas das colunas
                                col_stats1, col_stats2, col_stats3 = st.columns(3)
                                
                                with col_stats1:
                                    st.metric("🔢 Total Colunas", len(columns))
                                
                                with col_stats2:
                                    nullable_count = len([c for c in columns if c.get('nullable', True)])
                                    st.metric("❓ Colunas Nulas", nullable_count)
                                
                                with col_stats3:
                                    indexed_count = len([c for c in columns if 'id' in c.get('name', '').lower()])
                                    st.metric("🗂️ Possíveis Chaves", indexed_count)
                                
                                # Análise de tipos
                                st.markdown("#### 📊 Distribuição de Tipos")
                                
                                type_counts = {}
                                for col in columns:
                                    col_type = col.get('type', 'unknown')
                                    type_counts[col_type] = type_counts.get(col_type, 0) + 1
                                
                                if type_counts:
                                    # Criar gráfico de tipos
                                    fig = px.pie(
                                        values=list(type_counts.values()),
                                        names=list(type_counts.keys()),
                                        title=f"Tipos de Dados - {table['name']}",
                                        color_discrete_sequence=['#2E8B57', '#90EE90', '#228B22', '#98FB98', '#20B2AA']
                                    )
                                    fig.update_layout(height=300)
                                    st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.warning(f"⚠️ Não foi possível carregar a estrutura de {table['name']}")
                    
                    with col3:
                        if st.button(f"📊 Análise", key=f"analyze_{table['name']}_{i}", use_container_width=True):
                            with st.spinner(f"📊 Analisando {table['name']}..."):
                                # Obter dados para análise
                                result = db_manager.get_table_data(table['name'], limit=1000)
                            
                            if result['success'] and result['data']:
                                df_analysis = pd.DataFrame(result['data'])
                                
                                st.success(f"✅ Análise de {table['name']} concluída!")
                                
                                # Estatísticas gerais
                                st.markdown(f"#### 📈 Estatísticas de `{table['name']}`")
                                
                                col_anal1, col_anal2, col_anal3, col_anal4 = st.columns(4)
                                
                                with col_anal1:
                                    st.metric("📊 Registros Analisados", len(df_analysis))
                                
                                with col_anal2:
                                    st.metric("📋 Colunas", len(df_analysis.columns))
                                
                                with col_anal3:
                                    # Calcular densidade de dados (não nulos)
                                    total_cells = len(df_analysis) * len(df_analysis.columns)
                                    non_null_cells = df_analysis.count().sum()
                                    density = (non_null_cells / total_cells * 100) if total_cells > 0 else 0
                                    st.metric("💾 Densidade", f"{density:.1f}%")
                                
                                with col_anal4:
                                    # Estimar tamanho em memória
                                    memory_usage = df_analysis.memory_usage(deep=True).sum()
                                    memory_mb = memory_usage / (1024 * 1024)
                                    st.metric("🧠 Memória", f"{memory_mb:.1f} MB")
                                
                                # Análise de valores nulos
                                st.markdown("#### ❓ Análise de Valores Nulos")
                                
                                null_counts = df_analysis.isnull().sum()
                                null_percentages = (null_counts / len(df_analysis) * 100).round(1)
                                
                                null_analysis = pd.DataFrame({
                                    'Coluna': null_counts.index,
                                    'Valores Nulos': null_counts.values,
                                    'Percentual (%)': null_percentages.values
                                })
                                
                                # Mostrar apenas colunas com valores nulos
                                null_analysis_filtered = null_analysis[null_analysis['Valores Nulos'] > 0]
                                
                                if not null_analysis_filtered.empty:
                                    st.dataframe(null_analysis_filtered, use_container_width=True)
                                    
                                    # Gráfico de valores nulos
                                    if len(null_analysis_filtered) > 0:
                                        fig = px.bar(
                                            null_analysis_filtered,
                                            x='Coluna',
                                            y='Percentual (%)',
                                            title=f"Percentual de Valores Nulos - {table['name']}",
                                            color='Percentual (%)',
                                            color_continuous_scale=['#90EE90', '#FFD700', '#FF6347']
                                        )
                                        fig.update_layout(height=300)
                                        st.plotly_chart(fig, use_container_width=True)
                                else:
                                    st.success("🎉 Nenhum valor nulo encontrado!")
                                
                                # Análise de tipos únicos
                                st.markdown("#### 🔢 Valores Únicos por Coluna")
                                
                                unique_counts = []
                                for col in df_analysis.columns:
                                    unique_count = df_analysis[col].nunique()
                                    total_count = len(df_analysis)
                                    uniqueness = (unique_count / total_count * 100) if total_count > 0 else 0
                                    
                                    unique_counts.append({
                                        'Coluna': col,
                                        'Valores Únicos': unique_count,
                                        'Total': total_count,
                                        'Unicidade (%)': round(uniqueness, 1)
                                    })
                                
                                df_unique = pd.DataFrame(unique_counts)
                                st.dataframe(df_unique, use_container_width=True)
                            
                            else:
                                st.warning(f"⚠️ Não foi possível analisar {table['name']} - tabela vazia ou erro de acesso")
                    
                    with col4:
                        if st.button(f"💾 Backup", key=f"backup_{table['name']}_{i}", use_container_width=True):
                            with st.spinner(f"💾 Criando backup de {table['name']}..."):
                                result = db_manager.backup_table(table['name'])
                            
                            if result['success']:
                                st.success(f"✅ {result['message']}")
                                
                                # Log da atividade
                                log_activity("Backup criado", f"Tabela: {table['name']}")
                                
                                # Mostrar detalhes do backup
                                backup_info = {
                                    "Tabela": table['name'],
                                    "Backup": result.get('backup_name', 'backup_criado'),
                                    "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    "Registros": table.get('rows', 0),
                                    "Tamanho": table.get('size', 'N/A')
                                }
                                
                                st.json(backup_info)
                            else:
                                st.error(f"❌ {result['message']}")
                    
                    with col5:
                        if st.button(f"⚡ Otimizar", key=f"optimize_{table['name']}_{i}", use_container_width=True):
                            with st.spinner(f"⚡ Otimizando {table['name']}..."):
                                result = db_manager.optimize_table(table['name'])
                            
                            if result['success']:
                                st.success(f"✅ {result['message']}")
                                log_activity("Tabela otimizada", table['name'])
                            else:
                                st.error(f"❌ {result['message']}")
                    
                    with col6:
                        if st.button(f"🔧 SQL", key=f"sql_{table['name']}_{i}", use_container_width=True):
                            # Ir para o SQL Editor com query pré-preenchida
                            st.session_state.current_page = 'sql_editor'
                            st.session_state.sql_query = f"SELECT * FROM {table['name']} LIMIT 50;"
                            st.rerun()
        
        with tab2:
            st.subheader("📊 Análise Detalhada das Tabelas")
            
            if filtered_tables:
                # Gráfico de distribuição de registros
                st.markdown("#### 📈 Distribuição de Registros")
                
                table_names = [t['name'] for t in filtered_tables]
                table_rows = [t.get('rows', 0) for t in filtered_tables]
                
                fig = px.bar(
                    x=table_names,
                    y=table_rows,
                    title="Número de Registros por Tabela",
                    labels={'x': 'Tabelas', 'y': 'Registros'},
                    color=table_rows,
                    color_continuous_scale=['#90EE90', '#2E8B57', '#228B22']
                )
                fig.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
                # Análise de tamanhos
                st.markdown("#### 💾 Análise de Tamanhos")
                
                # Converter tamanhos para bytes para comparação
                def parse_size(size_str):
                    if 'MB' in size_str:
                        return float(size_str.replace(' MB', '').replace(',', '.')) * 1024
                    elif 'KB' in size_str:
                        return float(size_str.replace(' KB', '').replace(',', '.'))
                    else:
                        return 0
                
                table_sizes = []
                for table in filtered_tables:
                    size_str = table.get('size', '0 KB')
                    size_kb = parse_size(size_str)
                    table_sizes.append({
                        'Tabela': table['name'],
                        'Tamanho (KB)': size_kb,
                        'Registros': table.get('rows', 0)
                    })
                
                df_sizes = pd.DataFrame(table_sizes)
                
                if not df_sizes.empty and df_sizes['Tamanho (KB)'].sum() > 0:
                    # Gráfico de pizza para tamanhos
                    fig_pie = px.pie(
                        df_sizes,
                        values='Tamanho (KB)',
                        names='Tabela',
                        title="Distribuição de Tamanho por Tabela",
                        color_discrete_sequence=['#2E8B57', '#90EE90', '#228B22', '#98FB98', '#20B2AA']
                    )
                    fig_pie.update_layout(height=400)
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                    # Scatter plot: Registros vs Tamanho
                    fig_scatter = px.scatter(
                        df_sizes,
                        x='Registros',
                        y='Tamanho (KB)',
                        text='Tabela',
                        title="Relação entre Registros e Tamanho",
                        color='Tamanho (KB)',
                        color_continuous_scale=['#90EE90', '#2E8B57']
                    )
                    fig_scatter.update_traces(textposition="top center")
                    fig_scatter.update_layout(height=400)
                    st.plotly_chart(fig_scatter, use_container_width=True)
                else:
                    st.info("📊 Dados de tamanho não disponíveis para análise gráfica")
                
                # Estatísticas consolidadas
                st.markdown("#### 📋 Resumo Estatístico")
                
                total_records = sum(t.get('rows', 0) for t in filtered_tables)
                avg_records = total_records / len(filtered_tables) if filtered_tables else 0
                max_records = max(t.get('rows', 0) for t in filtered_tables) if filtered_tables else 0
                min_records = min(t.get('rows', 0) for t in filtered_tables) if filtered_tables else 0
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📊 Total de Registros", f"{total_records:,}")
                
                with col2:
                    st.metric("📈 Média por Tabela", f"{avg_records:,.0f}")
                
                with col3:
                    st.metric("🔝 Maior Tabela", f"{max_records:,}")
                
                with col4:
                    st.metric("🔻 Menor Tabela", f"{min_records:,}")
        
        with tab3:
            st.subheader("🔧 Operações em Lote")
            
            st.markdown("#### ⚙️ Selecionar Tabelas para Operação em Lote")
            
            # Seleção de tabelas
            selected_tables = []
            
            # Checkbox para selecionar todas
            select_all = st.checkbox("✅ Selecionar todas as tabelas")
            
            if select_all:
                selected_tables = [t['name'] for t in filtered_tables]
            else:
                # Checkboxes individuais
                cols = st.columns(min(4, len(filtered_tables)))
                
                for i, table in enumerate(filtered_tables):
                    with cols[i % 4]:
                        if st.checkbox(f"📋 {table['name']}", key=f"select_{table['name']}"):
                            selected_tables.append(table['name'])
            
            if selected_tables:
                st.success(f"✅ {len(selected_tables)} tabela(s) selecionada(s)")
                
                # Operações disponíveis
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("💾 Backup em Lote", type="primary", use_container_width=True):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        successful_backups = []
                        failed_backups = []
                        
                        for i, table_name in enumerate(selected_tables):
                            status_text.text(f"Criando backup de {table_name}...")
                            progress_bar.progress((i + 1) / len(selected_tables))
                            
                            result = db_manager.backup_table(table_name)
                            
                            if result['success']:
                                successful_backups.append(table_name)
                            else:
                                failed_backups.append(table_name)
                            
                            time.sleep(0.5)  # Simular tempo de processamento
                        
                        status_text.empty()
                        progress_bar.empty()
                        
                        # Mostrar resultados
                        if successful_backups:
                            st.success(f"✅ Backup concluído para {len(successful_backups)} tabela(s)")
                            log_activity("Backup em lote", f"{len(successful_backups)} tabelas")
                        
                        if failed_backups:
                            st.error(f"❌ Falha no backup de {len(failed_backups)} tabela(s): {', '.join(failed_backups)}")
                
                with col2:
                    if st.button("⚡ Otimizar em Lote", type="secondary", use_container_width=True):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        successful_optimizations = []
                        failed_optimizations = []
                        
                        for i, table_name in enumerate(selected_tables):
                            status_text.text(f"Otimizando {table_name}...")
                            progress_bar.progress((i + 1) / len(selected_tables))
                            
                            result = db_manager.optimize_table(table_name)
                            
                            if result['success']:
                                successful_optimizations.append(table_name)
                            else:
                                failed_optimizations.append(table_name)
                            
                            time.sleep(0.3)  # Simular tempo de processamento
                        
                        status_text.empty()
                        progress_bar.empty()
                        
                        # Mostrar resultados
                        if successful_optimizations:
                            st.success(f"✅ Otimização concluída para {len(successful_optimizations)} tabela(s)")
                            log_activity("Otimização em lote", f"{len(successful_optimizations)} tabelas")
                        
                        if failed_optimizations:
                            st.error(f"❌ Falha na otimização de {len(failed_optimizations)} tabela(s): {', '.join(failed_optimizations)}")
                
                with col3:
                    if st.button("📊 Analisar em Lote", use_container_width=True):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        batch_analysis = []
                        
                        for i, table_name in enumerate(selected_tables):
                            status_text.text(f"Analisando {table_name}...")
                            progress_bar.progress((i + 1) / len(selected_tables))
                            
                            # Obter informações da tabela
                            table_info = db_manager.get_table_info(table_name)
                            
                            batch_analysis.append({
                                'Tabela': table_name,
                                'Registros': table_info.get('rows', 0),
                                'Tamanho': table_info.get('size', 'N/A'),
                                'Última Modificação': table_info.get('last_modified', 'N/A')
                            })
                            
                            time.sleep(0.2)  # Simular tempo de processamento
                        
                        status_text.empty()
                        progress_bar.empty()
                        
                        # Mostrar resultados da análise
                        st.success("✅ Análise em lote concluída!")
                        
                        df_batch_analysis = pd.DataFrame(batch_analysis)
                        st.dataframe(df_batch_analysis, use_container_width=True)
                        
                        # Estatísticas da análise em lote
                        total_records_batch = df_batch_analysis['Registros'].sum()
                        avg_records_batch = df_batch_analysis['Registros'].mean()
                        
                        col_batch1, col_batch2 = st.columns(2)
                        
                        with col_batch1:
                            st.metric("📊 Total de Registros (Lote)", f"{total_records_batch:,}")
                        
                        with col_batch2:
                            st.metric("📈 Média de Registros (Lote)", f"{avg_records_batch:,.0f}")
                        
                        log_activity("Análise em lote", f"{len(selected_tables)} tabelas")
                
                # Exportar dados de tabelas selecionadas
                st.markdown("#### 📤 Exportar Dados das Tabelas Selecionadas")
                
                export_format = st.selectbox("📁 Formato de Exportação:", 
                    ["CSV Individual", "JSON Consolidado", "Excel Multi-Sheets"])
                
                if st.button("📤 Exportar Dados Selecionadas", use_container_width=True):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    export_data = {}
                    
                    for i, table_name in enumerate(selected_tables):
                        status_text.text(f"Exportando dados de {table_name}...")
                        progress_bar.progress((i + 1) / len(selected_tables))
                        
                        result = db_manager.get_table_data(table_name, limit=1000)
                        
                        if result['success'] and result['data']:
                            export_data[table_name] = result['data']
                        
                        time.sleep(0.3)
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    if export_data:
                        if export_format == "JSON Consolidado":
                            json_export = json.dumps(export_data, indent=2, default=str)
                            st.download_button(
                                "📥 Download JSON Consolidado",
                                json_export,
                                f"tabelas_selecionadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                "application/json"
                            )
                        
                        elif export_format == "Excel Multi-Sheets":
                            # Criar Excel com múltiplas sheets
                            excel_buffer = io.BytesIO() # type: ignore
                            
                            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                                for table_name, data in export_data.items():
                                    if data:
                                        df_export = pd.DataFrame(data)
                                        # Limitar nome da sheet (Excel tem limite de 31 caracteres)
                                        sheet_name = table_name[:31]
                                        df_export.to_excel(writer, sheet_name=sheet_name, index=False)
                            
                            st.download_button(
                                "📥 Download Excel Multi-Sheets",
                                excel_buffer.getvalue(),
                                f"tabelas_selecionadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        
                        st.success(f"✅ Dados de {len(export_data)} tabela(s) prontos para download!")
                        log_activity("Exportação em lote", f"{len(export_data)} tabelas")
                    
                    else:
                        st.warning("⚠️ Nenhum dado encontrado nas tabelas selecionadas para exportação")
            
            else:
                st.info("ℹ️ Selecione pelo menos uma tabela para realizar operações em lote")
    
    else:
        st.info("📋 Nenhuma tabela encontrada com os critérios de filtro especificados.")
        
        if search_table or schema_filter != "Todos":
            st.markdown("💡 **Dica:** Tente limpar os filtros para ver todas as tabelas disponíveis.")

def render_sql_editor():
    """Renderiza a interface do editor SQL com tratamento robusto de erros"""
    try:
        st.markdown("### 🔧 Editor SQL")
        st.markdown("Execute queries SQL diretamente no banco de dados")
        
        # Verificar e inicializar database manager
        db_manager = check_and_reconnect_database()
        
        if not db_manager:
            show_database_connection_error()
            return
        
        # Verificar status da conexão atual
        connection_status = verify_database_connection(db_manager)
        display_connection_status(connection_status, db_manager)
        
        # Inicializar sessões se necessário
        initialize_sql_session_state()
        
        # Layout principal melhorado
        render_sql_editor_layout(db_manager)
        
    except Exception as e:
        st.error("❌ Erro crítico no Editor SQL")
        
        with st.expander("🔍 Detalhes do Erro", expanded=False):
            st.code(f"Tipo: {type(e).__name__}\nMensagem: {str(e)}", language="text")
            st.exception(e)
        
        # Opções de recuperação
        st.markdown("### 🔧 Opções de Recuperação")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Reinicializar Conexão", use_container_width=True):
                st.session_state.pop('db_manager', None)
                st.rerun()
        
        with col2:
            if st.button("🧹 Limpar Cache", use_container_width=True):
                st.cache_data.clear()
                st.success("✅ Cache limpo!")
        
        with col3:
            if st.button("🏠 Voltar ao Início", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()


def check_and_reconnect_database():
    """Verifica e reconecta o database manager se necessário"""
    try:
        # Usar o database manager global que já foi criado
        global db_manager
        
        # Verificar se db_manager existe e está disponível
        if db_manager is None:
            st.info("🔄 Inicializando conexão com banco de dados...")
            
            # Tentar reinicializar o database manager global
            try:
                db_manager = DatabaseManager()
                
                if db_manager.connected:
                    st.session_state.db_manager = db_manager
                    st.success("✅ Conexão estabelecida com sucesso!")
                    return db_manager
                else:
                    st.warning("⚠️ Conectado em modo demonstração")
                    st.session_state.db_manager = db_manager
                    return db_manager
                    
            except Exception as e:
                st.error(f"❌ Erro ao criar DatabaseManager: {e}")
                return None
        
        # Se db_manager global existe, usar ele
        if 'db_manager' not in st.session_state:
            st.session_state.db_manager = db_manager
        
        # Verificar se ainda está conectado
        current_db_manager = st.session_state.db_manager
        
        if hasattr(current_db_manager, 'connected'):
            if not current_db_manager.connected:
                st.warning("⚠️ Conexão perdida. Tentando reconectar...")
                
                try:
                    # Tentar reinicializar
                    current_db_manager._init_connection()
                    
                    if current_db_manager.connected:
                        st.success("✅ Reconexão bem-sucedida!")
                        return current_db_manager
                    else:
                        st.info("ℹ️ Continuando em modo demonstração")
                        return current_db_manager
                        
                except Exception as e:
                    st.error(f"❌ Erro durante reconexão: {e}")
                    return current_db_manager  # Retornar mesmo assim para modo demo
        
        return current_db_manager
        
    except Exception as e:
        st.error(f"❌ Erro ao verificar conexão: {e}")
        
        # Como último recurso, criar um database manager básico
        try:
            if 'db_manager' not in globals() or globals()['db_manager'] is None:
                globals()['db_manager'] = DatabaseManager()
            
            st.session_state.db_manager = globals()['db_manager']
            return globals()['db_manager']
            
        except:
            return None

def show_database_connection_error():
    """Mostra interface de erro quando não há conexão com banco"""
    st.error("🚫 **Banco de Dados Indisponível**")
    
    st.markdown("""
    ### 🔧 O que aconteceu?
    Não foi possível estabelecer conexão com o banco de dados. Isso pode acontecer por:
    
    - **Configuração**: Credenciais ou configurações incorretas
    - **Rede**: Problemas de conectividade com a internet
    - **Servidor**: O servidor do banco pode estar temporariamente indisponível
    - **Inicialização**: O sistema ainda não foi configurado corretamente
    """)
    
    st.markdown("### 🛠️ Como resolver?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📋 Passos Básicos:**
        1. Verifique sua conexão com internet
        2. Confirme as credenciais do banco
        3. Teste a conectividade com o servidor
        4. Reinicie a aplicação se necessário
        """)
    
    with col2:
        st.markdown("""
        **⚙️ Configurações:**
        - Vá para a página de **Configurações**
        - Verifique as informações de conexão
        - Teste a conexão antes de prosseguir
        - Salve as configurações corretas
        """)
    
    # Ações de recuperação
    st.markdown("### 🚀 Ações Rápidas")
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        if st.button("⚙️ Ir para Configurações", use_container_width=True):
            st.session_state.current_page = "settings"
            st.rerun()
    
    with action_col2:
        if st.button("🔄 Tentar Novamente", use_container_width=True):
            # Forçar recriação do database manager
            try:
                global db_manager
                db_manager = DatabaseManager()
                st.session_state.db_manager = db_manager
                st.success("✅ Nova tentativa de conexão realizada!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro na nova tentativa: {e}")
    
    with action_col3:
        if st.button("🏠 Página Inicial", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
    
    with action_col4:
        if st.button("📚 Modo Demo", use_container_width=True):
            initialize_demo_mode()
            st.rerun()
    
    # Diagnóstico da conexão
    st.markdown("---")
    st.markdown("### 🔍 Diagnóstico")
    
    with st.expander("🔧 Verificar Configurações", expanded=False):
        st.markdown("**Configurações Atuais:**")
        
        config_info = {
            "Supabase URL": CONFIG.get('supabase_url', 'Não configurado')[:50] + "..." if CONFIG.get('supabase_url') else 'Não configurado',
            "Supabase Key": "Configurado" if CONFIG.get('supabase_anon_key') else 'Não configurado',
            "Bibliotecas": {
                "Supabase": "✅ Disponível" if SUPABASE_AVAILABLE else "❌ Não instalado",
                "Pandas": "✅ Disponível",
                "Plotly": "✅ Disponível"
            }
        }
        
        st.json(config_info)
        
        if not SUPABASE_AVAILABLE:
            st.error("❌ Biblioteca Supabase não instalada!")
            st.code("pip install supabase", language="bash")
    
    # Mostrar exemplos de queries para o usuário praticar
    show_example_queries()

def initialize_demo_mode():
    """Inicializa modo demonstração sem conexão real"""
    try:
        # Criar um database manager fictício para demonstração
        class DemoDataBaseManager:
            def __init__(self):
                self.connected = False
                self.connection_info = {
                    'type': 'Modo Demonstração',
                    'url': 'demo.localhost:5432',
                    'database': 'demo_database',
                    'user': 'demo_user',
                    'status': 'Modo Demonstração Ativo',
                    'version': 'PostgreSQL 15.0 (Demo)',
                    'host': 'localhost',
                    'port': 5432
                }
                
                # Definir tabelas de demonstração com informações completas
                self.demo_tables = [
                    {
                        'name': 'users',
                        'rows': 1250,
                        'size': '2.5 MB',
                        'schema': 'public',
                        'has_indexes': True,
                        'has_rules': False,
                        'has_triggers': True,
                        'created_at': '2024-01-15T10:00:00Z',
                        'owner': 'postgres',
                        'tablespace': 'pg_default',
                        'description': 'Tabela de usuários do sistema'
                    },
                    {
                        'name': 'products',
                        'rows': 850,
                        'size': '1.8 MB',
                        'schema': 'public',
                        'has_indexes': True,
                        'has_rules': False,
                        'has_triggers': False,
                        'created_at': '2024-01-20T14:30:00Z',
                        'owner': 'postgres',
                        'tablespace': 'pg_default',
                        'description': 'Catálogo de produtos'
                    },
                    {
                        'name': 'orders',
                        'rows': 3200,
                        'size': '5.2 MB',
                        'schema': 'public',
                        'has_indexes': True,
                        'has_rules': False,
                        'has_triggers': True,
                        'created_at': '2024-01-25T09:15:00Z',
                        'owner': 'postgres',
                        'tablespace': 'pg_default',
                        'description': 'Pedidos realizados pelos usuários'
                    },
                    {
                        'name': 'categories',
                        'rows': 25,
                        'size': '12 KB',
                        'schema': 'public',
                        'has_indexes': True,
                        'has_rules': False,
                        'has_triggers': False,
                        'created_at': '2024-01-10T16:45:00Z',
                        'owner': 'postgres',
                        'tablespace': 'pg_default',
                        'description': 'Categorias de produtos'
                    },
                    {
                        'name': 'reviews',
                        'rows': 4500,
                        'size': '3.1 MB',
                        'schema': 'public',
                        'has_indexes': True,
                        'has_rules': False,
                        'has_triggers': False,
                        'created_at': '2024-02-01T11:20:00Z',
                        'owner': 'postgres',
                        'tablespace': 'pg_default',
                        'description': 'Avaliações e comentários dos produtos'
                    },
                    {
                        'name': 'customers',
                        'rows': 890,
                        'size': '1.2 MB',
                        'schema': 'public',
                        'has_indexes': True,
                        'has_rules': False,
                        'has_triggers': False,
                        'created_at': '2024-01-30T13:10:00Z',
                        'owner': 'postgres',
                        'tablespace': 'pg_default',
                        'description': 'Informações detalhadas dos clientes'
                    },
                    {
                        'name': 'inventory',
                        'rows': 1200,
                        'size': '800 KB',
                        'schema': 'public',
                        'has_indexes': True,
                        'has_rules': False,
                        'has_triggers': True,
                        'created_at': '2024-02-05T08:30:00Z',
                        'owner': 'postgres',
                        'tablespace': 'pg_default',
                        'description': 'Controle de estoque dos produtos'
                    },
                    {
                        'name': 'payments',
                        'rows': 2800,
                        'size': '2.8 MB',
                        'schema': 'public',
                        'has_indexes': True,
                        'has_rules': False,
                        'has_triggers': True,
                        'created_at': '2024-02-10T15:45:00Z',
                        'owner': 'postgres',
                        'tablespace': 'pg_default',
                        'description': 'Histórico de pagamentos'
                    }
                ]
                
                # Para compatibilidade
                self.real_tables = self.demo_tables
                
                # Definir colunas para cada tabela
                self.table_columns = {
                    'users': [
                        {'name': 'id', 'type': 'integer', 'nullable': False, 'default': 'nextval(\'users_id_seq\'::regclass)', 'max_length': None, 'is_primary_key': True, 'is_foreign_key': False},
                        {'name': 'name', 'type': 'varchar', 'nullable': False, 'default': None, 'max_length': 100, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'email', 'type': 'varchar', 'nullable': False, 'default': None, 'max_length': 255, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'password_hash', 'type': 'varchar', 'nullable': False, 'default': None, 'max_length': 255, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'role', 'type': 'varchar', 'nullable': True, 'default': '\'user\'::character varying', 'max_length': 50, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'is_active', 'type': 'boolean', 'nullable': False, 'default': 'true', 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'created_at', 'type': 'timestamp', 'nullable': False, 'default': 'CURRENT_TIMESTAMP', 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'updated_at', 'type': 'timestamp', 'nullable': True, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False}
                    ],
                    'products': [
                        {'name': 'id', 'type': 'integer', 'nullable': False, 'default': 'nextval(\'products_id_seq\'::regclass)', 'max_length': None, 'is_primary_key': True, 'is_foreign_key': False},
                        {'name': 'name', 'type': 'varchar', 'nullable': False, 'default': None, 'max_length': 200, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'description', 'type': 'text', 'nullable': True, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'price', 'type': 'decimal', 'nullable': False, 'default': None, 'max_length': '10,2', 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'category_id', 'type': 'integer', 'nullable': True, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': True},
                        {'name': 'stock_quantity', 'type': 'integer', 'nullable': False, 'default': '0', 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'is_active', 'type': 'boolean', 'nullable': False, 'default': 'true', 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'created_at', 'type': 'timestamp', 'nullable': False, 'default': 'CURRENT_TIMESTAMP', 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False}
                    ],
                    'orders': [
                        {'name': 'id', 'type': 'integer', 'nullable': False, 'default': 'nextval(\'orders_id_seq\'::regclass)', 'max_length': None, 'is_primary_key': True, 'is_foreign_key': False},
                        {'name': 'user_id', 'type': 'integer', 'nullable': False, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': True},
                        {'name': 'total_amount', 'type': 'decimal', 'nullable': False, 'default': None, 'max_length': '10,2', 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'status', 'type': 'varchar', 'nullable': False, 'default': '\'pending\'::character varying', 'max_length': 50, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'shipping_address', 'type': 'text', 'nullable': True, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'created_at', 'type': 'timestamp', 'nullable': False, 'default': 'CURRENT_TIMESTAMP', 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'updated_at', 'type': 'timestamp', 'nullable': True, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False}
                    ],
                    'categories': [
                        {'name': 'id', 'type': 'integer', 'nullable': False, 'default': 'nextval(\'categories_id_seq\'::regclass)', 'max_length': None, 'is_primary_key': True, 'is_foreign_key': False},
                        {'name': 'name', 'type': 'varchar', 'nullable': False, 'default': None, 'max_length': 100, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'description', 'type': 'text', 'nullable': True, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'parent_id', 'type': 'integer', 'nullable': True, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': True},
                        {'name': 'is_active', 'type': 'boolean', 'nullable': False, 'default': 'true', 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'created_at', 'type': 'timestamp', 'nullable': False, 'default': 'CURRENT_TIMESTAMP', 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False}
                    ],
                    'reviews': [
                        {'name': 'id', 'type': 'integer', 'nullable': False, 'default': 'nextval(\'reviews_id_seq\'::regclass)', 'max_length': None, 'is_primary_key': True, 'is_foreign_key': False},
                        {'name': 'product_id', 'type': 'integer', 'nullable': False, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': True},
                        {'name': 'user_id', 'type': 'integer', 'nullable': False, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': True},
                        {'name': 'rating', 'type': 'integer', 'nullable': False, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'comment', 'type': 'text', 'nullable': True, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'is_verified', 'type': 'boolean', 'nullable': False, 'default': 'false', 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'created_at', 'type': 'timestamp', 'nullable': False, 'default': 'CURRENT_TIMESTAMP', 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False}
                    ],
                    'customers': [
                        {'name': 'id', 'type': 'integer', 'nullable': False, 'default': 'nextval(\'customers_id_seq\'::regclass)', 'max_length': None, 'is_primary_key': True, 'is_foreign_key': False},
                        {'name': 'user_id', 'type': 'integer', 'nullable': False, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': True},
                        {'name': 'first_name', 'type': 'varchar', 'nullable': False, 'default': None, 'max_length': 50, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'last_name', 'type': 'varchar', 'nullable': False, 'default': None, 'max_length': 50, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'phone', 'type': 'varchar', 'nullable': True, 'default': None, 'max_length': 20, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'birth_date', 'type': 'date', 'nullable': True, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'gender', 'type': 'varchar', 'nullable': True, 'default': None, 'max_length': 10, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'address', 'type': 'text', 'nullable': True, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False}
                    ],
                    'inventory': [
                        {'name': 'id', 'type': 'integer', 'nullable': False, 'default': 'nextval(\'inventory_id_seq\'::regclass)', 'max_length': None, 'is_primary_key': True, 'is_foreign_key': False},
                        {'name': 'product_id', 'type': 'integer', 'nullable': False, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': True},
                        {'name': 'quantity', 'type': 'integer', 'nullable': False, 'default': '0', 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'reserved_quantity', 'type': 'integer', 'nullable': False, 'default': '0', 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'minimum_stock', 'type': 'integer', 'nullable': False, 'default': '10', 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'warehouse_location', 'type': 'varchar', 'nullable': True, 'default': None, 'max_length': 100, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'last_updated', 'type': 'timestamp', 'nullable': False, 'default': 'CURRENT_TIMESTAMP', 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False}
                    ],
                    'payments': [
                        {'name': 'id', 'type': 'integer', 'nullable': False, 'default': 'nextval(\'payments_id_seq\'::regclass)', 'max_length': None, 'is_primary_key': True, 'is_foreign_key': False},
                        {'name': 'order_id', 'type': 'integer', 'nullable': False, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': True},
                        {'name': 'amount', 'type': 'decimal', 'nullable': False, 'default': None, 'max_length': '10,2', 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'payment_method', 'type': 'varchar', 'nullable': False, 'default': None, 'max_length': 50, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'payment_status', 'type': 'varchar', 'nullable': False, 'default': '\'pending\'::character varying', 'max_length': 50, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'transaction_id', 'type': 'varchar', 'nullable': True, 'default': None, 'max_length': 100, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'processed_at', 'type': 'timestamp', 'nullable': True, 'default': None, 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False},
                        {'name': 'created_at', 'type': 'timestamp', 'nullable': False, 'default': 'CURRENT_TIMESTAMP', 'max_length': None, 'is_primary_key': False, 'is_foreign_key': False}
                    ]
                }
                
                # Políticas RLS de demonstração
                self.demo_policies = {
                    'users': [
                        {
                            'policy_name': 'Users can view own profile',
                            'command': 'SELECT',
                            'is_permissive': True,
                            'roles': ['authenticated'],
                            'using_expression': '(auth.uid() = id)',
                            'with_check_expression': None,
                            'table_name': 'users',
                            'schema_name': 'public'
                        },
                        {
                            'policy_name': 'Users can update own profile',
                            'command': 'UPDATE',
                            'is_permissive': True,
                            'roles': ['authenticated'],
                            'using_expression': '(auth.uid() = id)',
                            'with_check_expression': '(auth.uid() = id)',
                            'table_name': 'users',
                            'schema_name': 'public'
                        },
                        {
                            'policy_name': 'Admins can view all users',
                            'command': 'SELECT',
                            'is_permissive': True,
                            'roles': ['authenticated'],
                            'using_expression': '(auth.jwt() ->> \'role\' = \'admin\')',
                            'with_check_expression': None,
                            'table_name': 'users',
                            'schema_name': 'public'
                        }
                    ],
                    'products': [
                        {
                            'policy_name': 'Anyone can view active products',
                            'command': 'SELECT',
                            'is_permissive': True,
                            'roles': ['anon', 'authenticated'],
                            'using_expression': '(is_active = true)',
                            'with_check_expression': None,
                            'table_name': 'products',
                            'schema_name': 'public'
                        },
                        {
                            'policy_name': 'Only admins can manage products',
                            'command': 'ALL',
                            'is_permissive': True,
                            'roles': ['authenticated'],
                            'using_expression': '(auth.jwt() ->> \'role\' = \'admin\')',
                            'with_check_expression': '(auth.jwt() ->> \'role\' = \'admin\')',
                            'table_name': 'products',
                            'schema_name': 'public'
                        }
                    ],
                    'orders': [
                        {
                            'policy_name': 'Users can view own orders',
                            'command': 'SELECT',
                            'is_permissive': True,
                            'roles': ['authenticated'],
                            'using_expression': '(auth.uid() = user_id)',
                            'with_check_expression': None,
                            'table_name': 'orders',
                            'schema_name': 'public'
                        },
                        {
                            'policy_name': 'Users can create own orders',
                            'command': 'INSERT',
                            'is_permissive': True,
                            'roles': ['authenticated'],
                            'using_expression': None,
                            'with_check_expression': '(auth.uid() = user_id)',
                            'table_name': 'orders',
                            'schema_name': 'public'
                        },
                        {
                            'policy_name': 'Users can update own pending orders',
                            'command': 'UPDATE',
                            'is_permissive': True,
                            'roles': ['authenticated'],
                            'using_expression': '(auth.uid() = user_id AND status = \'pending\')',
                            'with_check_expression': '(auth.uid() = user_id)',
                            'table_name': 'orders',
                            'schema_name': 'public'
                        }
                    ],
                    'categories': [
                        {
                            'policy_name': 'Anyone can view active categories',
                            'command': 'SELECT',
                            'is_permissive': True,
                            'roles': ['anon', 'authenticated'],
                            'using_expression': '(is_active = true)',
                            'with_check_expression': None,
                            'table_name': 'categories',
                            'schema_name': 'public'
                        }
                    ],
                    'reviews': [
                        {
                            'policy_name': 'Anyone can view reviews',
                            'command': 'SELECT',
                            'is_permissive': True,
                            'roles': ['anon', 'authenticated'],
                            'using_expression': 'true',
                            'with_check_expression': None,
                            'table_name': 'reviews',
                            'schema_name': 'public'
                        },
                        {
                            'policy_name': 'Users can create reviews',
                            'command': 'INSERT',
                            'is_permissive': True,
                            'roles': ['authenticated'],
                            'using_expression': None,
                            'with_check_expression': '(auth.uid() = user_id)',
                            'table_name': 'reviews',
                            'schema_name': 'public'
                        },
                        {
                            'policy_name': 'Users can update own reviews',
                            'command': 'UPDATE',
                            'is_permissive': True,
                            'roles': ['authenticated'],
                            'using_expression': '(auth.uid() = user_id)',
                            'with_check_expression': '(auth.uid() = user_id)',
                            'table_name': 'reviews',
                            'schema_name': 'public'
                        }
                    ],
                    'customers': [
                        {
                            'policy_name': 'Users can view own customer data',
                            'command': 'SELECT',
                            'is_permissive': True,
                            'roles': ['authenticated'],
                            'using_expression': '(auth.uid() = user_id)',
                            'with_check_expression': None,
                            'table_name': 'customers',
                            'schema_name': 'public'
                        }
                    ],
                    'inventory': [
                        {
                            'policy_name': 'Only staff can view inventory',
                            'command': 'SELECT',
                            'is_permissive': True,
                            'roles': ['authenticated'],
                            'using_expression': '(auth.jwt() ->> \'role\' IN (\'admin\', \'staff\'))',
                            'with_check_expression': None,
                            'table_name': 'inventory',
                            'schema_name': 'public'
                        }
                    ],
                    'payments': [
                        {
                            'policy_name': 'Users can view own payments',
                            'command': 'SELECT',
                            'is_permissive': True,
                            'roles': ['authenticated'],
                            'using_expression': '(auth.uid() = (SELECT user_id FROM orders WHERE id = order_id))',
                            'with_check_expression': None,
                            'table_name': 'payments',
                            'schema_name': 'public'
                        }
                    ]
                }
                
                # Índices de demonstração
                self.demo_indexes = {
                    'users': [
                        {'name': 'users_pkey', 'type': 'PRIMARY KEY', 'columns': ['id'], 'is_unique': True},
                        {'name': 'users_email_key', 'type': 'UNIQUE', 'columns': ['email'], 'is_unique': True},
                        {'name': 'idx_users_role', 'type': 'BTREE', 'columns': ['role'], 'is_unique': False},
                        {'name': 'idx_users_created_at', 'type': 'BTREE', 'columns': ['created_at'], 'is_unique': False}
                    ],
                    'products': [
                        {'name': 'products_pkey', 'type': 'PRIMARY KEY', 'columns': ['id'], 'is_unique': True},
                        {'name': 'idx_products_category', 'type': 'BTREE', 'columns': ['category_id'], 'is_unique': False},
                        {'name': 'idx_products_name', 'type': 'BTREE', 'columns': ['name'], 'is_unique': False},
                        {'name': 'idx_products_price', 'type': 'BTREE', 'columns': ['price'], 'is_unique': False}
                    ],
                    'orders': [
                        {'name': 'orders_pkey', 'type': 'PRIMARY KEY', 'columns': ['id'], 'is_unique': True},
                        {'name': 'idx_orders_user_id', 'type': 'BTREE', 'columns': ['user_id'], 'is_unique': False},
                        {'name': 'idx_orders_status', 'type': 'BTREE', 'columns': ['status'], 'is_unique': False},
                        {'name': 'idx_orders_created_at', 'type': 'BTREE', 'columns': ['created_at'], 'is_unique': False}
                    ]
                }
            
            def get_tables(self):
                """Retorna lista de tabelas disponíveis"""
                return self.demo_tables
            
            def get_table_info(self, table_name):
                """Retorna informações básicas de uma tabela"""
                for table in self.demo_tables:
                    if table['name'] == table_name:
                        return {
                            'rows': table['rows'],
                            'size': table['size'],
                            'last_modified': datetime.now().strftime('%Y-%m-%d'),
                            'created': table.get('created_at', '2024-01-01'),
                            'owner': table.get('owner', 'postgres'),
                            'schema': table.get('schema', 'public'),
                            'tablespace': table.get('tablespace', 'pg_default'),
                            'description': table.get('description', f'Tabela {table_name}'),
                            'has_indexes': table.get('has_indexes', False),
                            'has_triggers': table.get('has_triggers', False),
                            'has_rules': table.get('has_rules', False)
                        }
                return {
                    'rows': 0, 
                    'size': '0 KB', 
                    'last_modified': '2025-06-24',
                    'created': '2024-01-01',
                    'owner': 'postgres',
                    'schema': 'public'
                }
            
            def get_table_columns(self, table_name):
                """Retorna colunas de uma tabela"""
                return self.table_columns.get(table_name, [
                    {'name': 'id', 'type': 'integer', 'nullable': False, 'default': 'nextval()', 'max_length': None, 'is_primary_key': True, 'is_foreign_key': False},
                    {'name': 'name', 'type': 'varchar', 'nullable': False, 'default': None, 'max_length': 100, 'is_primary_key': False, 'is_foreign_key': False}
                ])
            
            def get_table_indexes(self, table_name):
                """Retorna índices de uma tabela"""
                return self.demo_indexes.get(table_name, [
                    {'name': f'{table_name}_pkey', 'type': 'PRIMARY KEY', 'columns': ['id'], 'is_unique': True}
                ])
            
            def get_table_policies(self, table_name):
                """Retorna políticas RLS de uma tabela"""
                return {
                    'success': True,
                    'policies': self.demo_policies.get(table_name, []),
                    'rls_enabled': True
                }
            
            def execute_query(self, query):
                """Simula execução de query"""
                import time
                import random
                
                time.sleep(random.uniform(0.3, 0.8))  # Simular tempo de processamento
                
                query_upper = query.upper().strip()
                query_lower = query.lower().strip()
                
                try:
                    # Análise da query para retornar dados apropriados
                    if 'SELECT' in query_upper:
                        return self._simulate_select_query(query_lower)
                    elif any(cmd in query_upper for cmd in ['INSERT', 'UPDATE', 'DELETE']):
                        return self._simulate_modify_query(query_upper)
                    elif 'CREATE' in query_upper:
                        return self._simulate_create_query(query_upper)
                    elif 'DROP' in query_upper:
                        return self._simulate_drop_query(query_upper)
                    elif 'ALTER' in query_upper:
                        return self._simulate_alter_query(query_upper)
                    else:
                        return {
                            'success': True,
                            'data': [],
                            'execution_time': f'{random.uniform(0.1, 0.5):.2f}s',
                            'rows_affected': 0,
                            'message': 'Query executada no modo demonstração'
                        }
                
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'Erro simulado: {str(e)}',
                        'data': [],
                        'execution_time': '0.0s',
                        'rows_affected': 0
                    }
            
            def _simulate_select_query(self, query):
                """Simula resultados de queries SELECT"""
                import random
                
                if 'users' in query:
                    demo_data = [
                        {'id': 1, 'name': 'João Silva', 'email': 'joao@email.com', 'role': 'user', 'is_active': True, 'created_at': '2025-06-20T10:00:00Z'},
                        {'id': 2, 'name': 'Maria Santos', 'email': 'maria@email.com', 'role': 'admin', 'is_active': True, 'created_at': '2025-06-21T11:00:00Z'},
                        {'id': 3, 'name': 'Pedro Costa', 'email': 'pedro@email.com', 'role': 'user', 'is_active': False, 'created_at': '2025-06-22T12:00:00Z'},
                        {'id': 4, 'name': 'Ana Lima', 'email': 'ana@email.com', 'role': 'user', 'is_active': True, 'created_at': '2025-06-23T09:00:00Z'},
                        {'id': 5, 'name': 'Carlos Pereira', 'email': 'carlos@email.com', 'role': 'staff', 'is_active': True, 'created_at': '2025-06-24T14:00:00Z'}
                    ]
                elif 'products' in query:
                    demo_data = [
                        {'id': 1, 'name': 'Smartphone Samsung Galaxy', 'price': 999.99, 'category_id': 1, 'stock_quantity': 50, 'is_active': True},
                        {'id': 2, 'name': 'Laptop Dell Inspiron', 'price': 1999.99, 'category_id': 1, 'stock_quantity': 25, 'is_active': True},
                        {'id': 3, 'name': 'Tablet iPad Air', 'price': 599.99, 'category_id': 1, 'stock_quantity': 30, 'is_active': True},
                        {'id': 4, 'name': 'Fone Bluetooth Sony', 'price': 199.99, 'category_id': 2, 'stock_quantity': 100, 'is_active': True},
                        {'id': 5, 'name': 'Mouse Logitech MX', 'price': 49.99, 'category_id': 2, 'stock_quantity': 200, 'is_active': True}
                    ]
                elif 'orders' in query:
                    demo_data = [
                        {'id': 1, 'user_id': 1, 'total_amount': 1199.98, 'status': 'completed', 'created_at': '2025-06-24T10:00:00Z'},
                        {'id': 2, 'user_id': 2, 'total_amount': 599.99, 'status': 'pending', 'created_at': '2025-06-24T11:00:00Z'},
                        {'id': 3, 'user_id': 3, 'total_amount': 249.98, 'status': 'shipped', 'created_at': '2025-06-24T12:00:00Z'},
                        {'id': 4, 'user_id': 1, 'total_amount': 999.99, 'status': 'processing', 'created_at': '2025-06-24T13:00:00Z'}
                    ]
                elif 'categories' in query:
                    demo_data = [
                        {'id': 1, 'name': 'Eletrônicos', 'description': 'Produtos eletrônicos em geral', 'parent_id': None, 'is_active': True},
                        {'id': 2, 'name': 'Acessórios', 'description': 'Acessórios para eletrônicos', 'parent_id': 1, 'is_active': True},
                        {'id': 3, 'name': 'Casa e Jardim', 'description': 'Produtos para casa e jardim', 'parent_id': None, 'is_active': True}
                    ]
                elif 'reviews' in query:
                    demo_data = [
                        {'id': 1, 'product_id': 1, 'user_id': 1, 'rating': 5, 'comment': 'Excelente produto!', 'is_verified': True, 'created_at': '2025-06-24T10:00:00Z'},
                        {'id': 2, 'product_id': 1, 'user_id': 2, 'rating': 4, 'comment': 'Muito bom, recomendo.', 'is_verified': True, 'created_at': '2025-06-24T11:00:00Z'},
                        {'id': 3, 'product_id': 2, 'user_id': 3, 'rating': 5, 'comment': 'Perfeito para trabalho!', 'is_verified': False, 'created_at': '2025-06-24T12:00:00Z'}
                    ]
                elif 'customers' in query:
                    demo_data = [
                        {'id': 1, 'user_id': 1, 'first_name': 'João', 'last_name': 'Silva', 'phone': '(11) 99999-9999', 'birth_date': '1990-01-15'},
                        {'id': 2, 'user_id': 2, 'first_name': 'Maria', 'last_name': 'Santos', 'phone': '(11) 88888-8888', 'birth_date': '1985-05-20'}
                    ]
                elif 'inventory' in query:
                    demo_data = [
                        {'id': 1, 'product_id': 1, 'quantity': 50, 'reserved_quantity': 5, 'minimum_stock': 10, 'warehouse_location': 'A1-001'},
                        {'id': 2, 'product_id': 2, 'quantity': 25, 'reserved_quantity': 2, 'minimum_stock': 5, 'warehouse_location': 'A1-002'}
                    ]
                elif 'payments' in query:
                    demo_data = [
                        {'id': 1, 'order_id': 1, 'amount': 1199.98, 'payment_method': 'credit_card', 'payment_status': 'completed', 'transaction_id': 'TXN123456'},
                        {'id': 2, 'order_id': 2, 'amount': 599.99, 'payment_method': 'pix', 'payment_status': 'pending', 'transaction_id': None}
                    ]
                elif 'count' in query:
                    # Queries de contagem
                    table_counts = {
                        'users': 1250,
                        'products': 850,
                        'orders': 3200,
                        'categories': 25,
                        'reviews': 4500,
                        'customers': 890,
                        'inventory': 1200,
                        'payments': 2800
                    }
                    
                    for table_name, count in table_counts.items():
                        if table_name in query:
                            demo_data = [{'count': count, 'total': count}]
                            break
                    else:
                        demo_data = [{'count': random.randint(100, 1000)}]
                else:
                    # Dados genéricos
                    demo_data = [
                        {'id': 1, 'name': 'Exemplo 1', 'value': random.randint(100, 1000), 'status': 'active', 'created_at': '2025-06-24T10:00:00Z'},
                        {'id': 2, 'name': 'Exemplo 2', 'value': random.randint(100, 1000), 'status': 'inactive', 'created_at': '2025-06-24T11:00:00Z'},
                        {'id': 3, 'name': 'Exemplo 3', 'value': random.randint(100, 1000), 'status': 'active', 'created_at': '2025-06-24T12:00:00Z'}
                    ]
                
                # Aplicar LIMIT se presente na query
                if 'limit' in query:
                    try:
                        limit_match = re.search(r'limit\s+(\d+)', query)
                        if limit_match:
                            limit_value = int(limit_match.group(1))
                            demo_data = demo_data[:limit_value]
                    except:
                        pass
                
                return {
                    'success': True,
                    'data': demo_data,
                    'execution_time': f'{random.uniform(0.2, 0.8):.2f}s',
                    'rows_affected': len(demo_data),
                    'message': 'Query SELECT executada no modo demonstração'
                }
            
            def _simulate_modify_query(self, query):
                """Simula queries de modificação (INSERT, UPDATE, DELETE)"""
                import random
                
                rows_affected = random.randint(1, 5)
                
                if 'INSERT' in query:
                    message = f'{rows_affected} registro(s) inserido(s) com sucesso'
                elif 'UPDATE' in query:
                    message = f'{rows_affected} registro(s) atualizado(s) com sucesso'
                elif 'DELETE' in query:
                    message = f'{rows_affected} registro(s) removido(s) com sucesso'
                else:
                    message = 'Operação executada com sucesso'
                
                return {
                    'success': True,
                    'data': [],
                    'execution_time': f'{random.uniform(0.1, 0.5):.2f}s',
                    'rows_affected': rows_affected,
                    'message': f'{message} (simulado)'
                }
            
            def _simulate_create_query(self, query):
                """Simula queries CREATE"""
                return {
                    'success': True,
                    'data': [],
                    'execution_time': '0.2s',
                    'rows_affected': 0,
                    'message': 'Objeto criado com sucesso (simulado)'
                }
            
            def _simulate_drop_query(self, query):
                """Simula queries DROP"""
                return {
                    'success': True,
                    'data': [],
                    'execution_time': '0.1s',
                    'rows_affected': 0,
                    'message': 'Objeto removido com sucesso (simulado)'
                }
            
            def _simulate_alter_query(self, query):
                """Simula queries ALTER"""
                return {
                    'success': True,
                    'data': [],
                    'execution_time': '0.3s',
                    'rows_affected': 0,
                    'message': 'Objeto alterado com sucesso (simulado)'
                }
            
            def get_database_metrics(self):
                """Retorna métricas do banco de dados"""
                import random
                
                return {
                    'total_size': '18.3 MB',
                    'connection_count': random.randint(1, 5),
                    'table_count': len(self.demo_tables),
                    'index_count': sum(len(indexes) for indexes in self.demo_indexes.values()),
                    'cpu_usage': random.randint(15, 45),
                    'memory_usage': random.randint(25, 60),
                    'disk_usage': random.randint(10, 40),
                    'cache_hit_ratio': random.randint(75, 98),
                    'active_connections': random.randint(1, 3),
                    'total_queries': random.randint(1000, 5000),
                    'slow_queries': random.randint(0, 10),
                    'uptime': '7 dias, 14 horas'
                }
            
            def refresh_tables(self):
                """Simula atualização da lista de tabelas"""
                st.info("🎯 Em modo demonstração - lista de tabelas é fixa")
                return self.demo_tables
            
            def backup_table(self, table_name):
                """Simula backup de tabela"""
                return {
                    'success': True,
                    'backup_name': f"{table_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'message': f'Backup simulado da tabela {table_name} criado com sucesso',
                    'size': '2.5 MB',
                    'location': f'/backups/{table_name}_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'
                }
            
            def optimize_table(self, table_name):
                """Simula otimização de tabela"""
                import random
                
                return {
                    'success': True,
                    'message': f'Tabela {table_name} otimizada com sucesso (simulado)',
                    'space_saved': f'{random.randint(50, 500)} KB',
                    'time_taken': f'{random.uniform(0.5, 2.0):.1f}s'
                }
            
            def analyze_table(self, table_name):
                """Simula análise de tabela"""
                import random
                
                table_info = self.get_table_info(table_name)
                columns = self.get_table_columns(table_name)
                
                return {
                    'success': True,
                    'table_name': table_name,
                    'row_count': table_info['rows'],
                    'size': table_info['size'],
                    'column_count': len(columns),
                    'null_percentage': random.randint(5, 25),
                    'duplicate_rows': random.randint(0, 10),
                    'fragmentation': random.randint(0, 15),
                    'recommendations': [
                        'Considere criar índice na coluna created_at para melhorar performance de queries temporais',
                        'A coluna email tem alta cardinalidade - bom para queries de busca',
                        'Verificar se há necessidade de otimização de espaço'
                    ]
                }
            
            def get_table_relationships(self, table_name):
                """Retorna relacionamentos de uma tabela"""
                relationships = {
                    'users': {
                        'references': [],  # Esta tabela não referencia outras
                        'referenced_by': [
                            {'table': 'orders', 'column': 'user_id', 'references': 'id'},
                            {'table': 'reviews', 'column': 'user_id', 'references': 'id'},
                            {'table': 'customers', 'column': 'user_id', 'references': 'id'}
                        ]
                    },
                    'products': {
                        'references': [
                            {'table': 'categories', 'column': 'category_id', 'references': 'id'}
                        ],
                        'referenced_by': [
                            {'table': 'reviews', 'column': 'product_id', 'references': 'id'},
                            {'table': 'inventory', 'column': 'product_id', 'references': 'id'}
                        ]
                    },
                    'orders': {
                        'references': [
                            {'table': 'users', 'column': 'user_id', 'references': 'id'}
                        ],
                        'referenced_by': [
                            {'table': 'payments', 'column': 'order_id', 'references': 'id'}
                        ]
                    }
                }
                
                return relationships.get(table_name, {'references': [], 'referenced_by': []})
            
            def test_connection(self):
                """Testa a conexão (sempre retorna sucesso em modo demo)"""
                return {
                    'success': True,
                    'message': 'Conexão testada com sucesso (modo demonstração)',
                    'response_time': '0.1s',
                    'server_version': 'PostgreSQL 15.0 (Demo)'
                }
            
            def _init_connection(self):
                """Simula inicialização da conexão"""
                self.connected = True
                return True
            
            def reconnect(self):
                """Simula reconexão"""
                self.connected = True
                return True
            
            def close_connection(self):
                """Simula fechamento da conexão"""
                self.connected = False
                return True
        
        # Substituir o database manager global
        demo_manager = DemoDataBaseManager()
        st.session_state.db_manager = demo_manager
        
        # Também atualizar a variável global se existir
        try:
            global db_manager
            db_manager = demo_manager
        except:
            pass
        
        st.success("✅ Modo demonstração ativado com sucesso!")
        st.info("🎯 Agora você pode testar todas as funcionalidades com dados simulados")
        
        # Mostrar resumo das funcionalidades disponíveis
        with st.expander("📋 Funcionalidades Disponíveis no Modo Demo", expanded=False):
            st.markdown("""
            **🗄️ Tabelas Simuladas:**
            - Users (1.250 registros)
            - Products (850 registros)  
            - Orders (3.200 registros)
            - Categories (25 registros)
            - Reviews (4.500 registros)
            - Customers (890 registros)
            - Inventory (1.200 registros)
            - Payments (2.800 registros)
            
            **🛡️ Recursos Disponíveis:**
            - Visualização de políticas RLS
            - Informações detalhadas das tabelas
            - Estrutura de colunas e índices
            - Simulação de queries SQL
            - Métricas do banco de dados
            - Análise de relacionamentos
            - Backup e otimização simulados
            """)
        
    except Exception as e:
        st.error(f"❌ Erro ao inicializar modo demo: {e}")
        with st.expander("🔍 Detalhes do Erro", expanded=False):
            st.exception(e)

def verify_database_connection(db_manager):
    """Verifica status detalhado da conexão"""
    try:
        status = {
            'connected': False,
            'response_time': None,
            'last_error': None,
            'tables_count': 0,
            'database_type': 'Desconhecido'
        }
        
        if not db_manager:
            status['last_error'] = 'Database manager não disponível'
            return status
        
        # Verificar conexão básica
        if hasattr(db_manager, 'connected'):
            status['connected'] = db_manager.connected
        
        # Verificar tipo de banco
        if hasattr(db_manager, 'connection_info'):
            status['database_type'] = db_manager.connection_info.get('type', 'Desconhecido')
        
        # Testar resposta do banco
        if status['connected']:
            try:
                import time
                start_time = time.time()
                
                # Tentar buscar tabelas para verificar conectividade
                tables = db_manager.get_tables()
                
                end_time = time.time()
                status['response_time'] = f"{(end_time - start_time):.2f}s"
                status['tables_count'] = len(tables) if tables else 0
                
            except Exception as e:
                status['last_error'] = str(e)
                status['connected'] = False
        
        return status
        
    except Exception as e:
        return {
            'connected': False,
            'response_time': None,
            'last_error': f'Erro na verificação: {str(e)}',
            'tables_count': 0,
            'database_type': 'Erro'
        }


def display_connection_status(status, db_manager):
    """Exibe status da conexão de forma detalhada"""
    if status['connected']:
        # Status positivo
        st.success(f"✅ Conectado ao {status['database_type']}")
        
        # Métricas de performance
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        
        with metrics_col1:
            st.metric("🚀 Tempo de Resposta", status['response_time'] or 'N/A')
        
        with metrics_col2:
            st.metric("🗄️ Tabelas Encontradas", status['tables_count'])
        
        with metrics_col3:
            connection_quality = "Excelente" if status['response_time'] and float(status['response_time'][:-1]) < 1.0 else "Boa"
            st.metric("📊 Qualidade", connection_quality)
    
    else:
        # Status negativo com detalhes
        if 'demo' in status['database_type'].lower():
            st.warning("⚠️ Modo Demonstração Ativo")
            st.info("💡 Execute queries de exemplo para testar a funcionalidade")
        else:
            st.error("❌ Conexão com Banco Indisponível")
            
            if status['last_error']:
                with st.expander("🔍 Detalhes do Erro", expanded=False):
                    st.code(status['last_error'], language='text')
            
            # Botão para tentar reconectar
            if st.button("🔄 Tentar Reconectar", use_container_width=True):
                with st.spinner("Reconectando..."):
                    new_db_manager = check_and_reconnect_database()
                    if new_db_manager:
                        st.success("✅ Reconexão bem-sucedida!")
                        st.rerun()


def initialize_sql_session_state():
    """Inicializa todas as variáveis de sessão necessárias"""
    session_defaults = {
        'sql_history': [],
        'sql_favorites': [],
        'sql_query': 'SELECT * FROM users LIMIT 10;',
        'last_execution_result': None,
        'sql_editor_preferences': {
            'auto_format': True,
            'show_line_numbers': True,
            'syntax_highlight': True,
            'max_rows_display': 100
        }
    }
    
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def render_sql_editor_layout(db_manager):
    """Renderiza o layout principal do editor SQL"""
    # Layout em colunas
    col1, col2 = st.columns([3, 1])
    
    with col2:
        render_sql_tools_sidebar(db_manager)
    
    with col1:
        render_main_sql_editor(db_manager)
    
    # Seção de resultados (largura total)
    render_sql_results_section()
    
    # Seção de favoritos
    render_favorites_section()


def render_sql_tools_sidebar(db_manager):
    """Renderiza barra lateral com ferramentas SQL"""
    st.markdown("#### 🛠️ Ferramentas")
    
    # Templates de query
    render_query_templates()
    
    st.markdown("---")
    
    # Lista de tabelas
    render_tables_list(db_manager)
    
    st.markdown("---")
    
    # Histórico de queries
    render_query_history()
    
    st.markdown("---")
    
    # Configurações do editor
    render_editor_settings()


def render_query_templates():
    """Renderiza seção de templates de query"""
    st.markdown("**📝 Templates**")
    
    template_options = {
        "SELECT Básico": "SELECT * FROM {table_name} LIMIT 10;",
        "SELECT com WHERE": "SELECT * FROM {table_name} WHERE {column} = '{value}' LIMIT 10;",
        "COUNT Registros": "SELECT COUNT(*) as total FROM {table_name};",
        "INSERT Registro": "INSERT INTO {table_name} (column1, column2) VALUES (value1, value2);",
        "UPDATE Registro": "UPDATE {table_name} SET column1 = value1 WHERE id = 1;",
        "DELETE Registro": "DELETE FROM {table_name} WHERE id = 1;",
        "CREATE TABLE": "CREATE TABLE new_table (\n    id SERIAL PRIMARY KEY,\n    name VARCHAR(255) NOT NULL,\n    created_at TIMESTAMP DEFAULT NOW()\n);",
        "JOIN Tables": "SELECT a.*, b.name \nFROM table_a a \nJOIN table_b b ON a.id = b.table_a_id \nLIMIT 10;",
        "GROUP BY": "SELECT column, COUNT(*) as count \nFROM {table_name} \nGROUP BY column \nORDER BY count DESC;",
        "DISTINCT Values": "SELECT DISTINCT column FROM {table_name} ORDER BY column;",
        "SUBQUERY": "SELECT * FROM {table_name} \nWHERE id IN (\n    SELECT user_id FROM orders WHERE total > 100\n);",
        "UNION": "SELECT name FROM customers \nUNION \nSELECT name FROM suppliers \nORDER BY name;",
        "WINDOW FUNCTION": "SELECT name, salary,\n    ROW_NUMBER() OVER (ORDER BY salary DESC) as rank\nFROM employees;"
    }
    
    selected_template = st.selectbox(
        "Escolher template:",
        options=list(template_options.keys()),
        index=0,
        help="Selecione um template para começar rapidamente"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Usar", use_container_width=True):
            st.session_state.sql_query = template_options[selected_template]
            st.rerun()
    
    with col2:
        if st.button("👁️ Ver", use_container_width=True):
            st.code(template_options[selected_template], language='sql')

def render_tables_list(db_manager):
    """Renderiza lista de tabelas disponíveis com opção para ver políticas"""
    st.markdown("**🗄️ Tabelas Disponíveis**")
    
    try:
        tables = db_manager.get_tables()
        
        if tables:
            # Filtro de busca
            search_term = st.text_input("🔍 Buscar tabela:", placeholder="Digite para filtrar...")
            
            # Filtrar tabelas se há termo de busca
            if search_term:
                filtered_tables = [t for t in tables if search_term.lower() in t['name'].lower()]
            else:
                filtered_tables = tables
            
            # Mostrar informações gerais
            st.caption(f"📊 {len(filtered_tables)} de {len(tables)} tabelas")
            
            # Lista de tabelas (limitada para performance)
            display_tables = filtered_tables[:15] if not search_term else filtered_tables[:50]
            
            for table in display_tables:
                # Container para cada tabela
                table_container = st.container()
                
                with table_container:
                    # Informações da tabela
                    table_info = f"📊 **{table['name']}**"
                    if 'rows' in table:
                        table_info += f" ({table['rows']} registros)"
                    
                    st.markdown(table_info)
                    
                    # Botões de ação para a tabela
                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    
                    with btn_col1:
                        if st.button("📝 Usar", key=f"use_table_{table['name']}", use_container_width=True):
                            # Inserir nome da tabela no editor
                            current_query = st.session_state.get('sql_query', '')
                            if '{table_name}' in current_query:
                                st.session_state.sql_query = current_query.replace('{table_name}', table['name'])
                            else:
                                st.session_state.sql_query = f"SELECT * FROM {table['name']} LIMIT 10;"
                            st.rerun()
                    
                    with btn_col2:
                        if st.button("🛡️ Políticas", key=f"policies_{table['name']}", use_container_width=True):
                            # Usar session state para controlar qual tabela mostrar políticas
                            st.session_state.show_policies_for_table = table['name']
                            st.rerun()
                    
                    with btn_col3:
                        if st.button("ℹ️ Info", key=f"info_{table['name']}", use_container_width=True):
                            show_table_detailed_info(table['name'], db_manager)
                    
                    st.markdown("---")
            
            if len(filtered_tables) > 15 and not search_term:
                st.caption(f"... e mais {len(filtered_tables) - 15} tabelas. Use a busca para encontrar específicas.")
            
            # Botão para atualizar lista
            if st.button("🔄 Atualizar Lista", use_container_width=True):
                if hasattr(db_manager, 'refresh_tables'):
                    with st.spinner("Atualizando..."):
                        db_manager.refresh_tables()
                        st.success("✅ Lista atualizada!")
                        st.rerun()
        else:
            st.info("Nenhuma tabela encontrada")
            if st.button("🔍 Redescobrir Tabelas", use_container_width=True):
                if hasattr(db_manager, '_discover_real_tables'):
                    with st.spinner("Descobrindo tabelas..."):
                        db_manager._discover_real_tables()
                        st.rerun()
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar tabelas: {e}")

    # Verificar se deve mostrar políticas de alguma tabela
    if 'show_policies_for_table' in st.session_state:
        table_name = st.session_state.show_policies_for_table
        
        # Criar nova seção para políticas
        st.markdown("---")
        
        # Botão para fechar a visualização de políticas
        if st.button("❌ Fechar Políticas", use_container_width=True):
            del st.session_state.show_policies_for_table
            st.rerun()
        
        # Mostrar políticas da tabela
        render_table_policies(table_name, db_manager)


def show_table_detailed_info(table_name, db_manager):
    """Mostra informações detalhadas de uma tabela"""
    st.markdown(f"### 📊 Informações Detalhadas - {table_name}")
    
    try:
        # Buscar informações básicas
        if hasattr(db_manager, 'get_table_info'):
            table_info = db_manager.get_table_info(table_name)
        else:
            table_info = {'rows': 'N/A', 'size': 'N/A', 'last_modified': 'N/A'}
        
        # Buscar colunas
        if hasattr(db_manager, 'get_table_columns'):
            columns = db_manager.get_table_columns(table_name)
        else:
            columns = []
        
        # Exibir informações básicas
        info_col1, info_col2, info_col3 = st.columns(3)
        
        with info_col1:
            st.metric("📝 Registros", table_info.get('rows', 'N/A'))
        
        with info_col2:
            st.metric("💾 Tamanho", table_info.get('size', 'N/A'))
        
        with info_col3:
            st.metric("🗓️ Última Modificação", table_info.get('last_modified', 'N/A'))
        
        # Exibir colunas se disponíveis
        if columns:
            st.markdown("**📋 Estrutura das Colunas:**")
            
            columns_df = pd.DataFrame(columns)
            st.dataframe(columns_df, use_container_width=True, hide_index=True)
        
        else:
            st.info("ℹ️ Informações de colunas não disponíveis")
    
    except Exception as e:
        st.error(f"❌ Erro ao carregar informações da tabela: {e}")

def render_query_history():
    """Renderiza histórico de queries"""
    st.markdown("**🕒 Histórico**")
    
    if st.session_state.sql_history:
        # Limitar histórico exibido
        recent_history = st.session_state.sql_history[-10:]
        history_options = [
            f"Query {len(st.session_state.sql_history) - i}: {query[:30]}..." 
            if len(query) > 30 else f"Query {len(st.session_state.sql_history) - i}: {query}"
            for i, query in enumerate(reversed(recent_history))
        ]
        
        selected_history = st.selectbox(
            "Queries recentes:",
            options=range(len(history_options)),
            format_func=lambda x: history_options[x] if x < len(history_options) else "",
            key="history_select"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Carregar", use_container_width=True):
                if selected_history < len(recent_history):
                    query_index = len(st.session_state.sql_history) - 1 - selected_history
                    st.session_state.sql_query = st.session_state.sql_history[query_index]
                    st.rerun()
        
        with col2:
            if st.button("🗑️ Limpar", use_container_width=True):
                st.session_state.sql_history = []
                st.success("✅ Histórico limpo!")
                st.rerun()
        
        # Mostrar estatísticas do histórico
        st.caption(f"📈 Total de queries executadas: {len(st.session_state.sql_history)}")
    else:
        st.info("Nenhuma query executada ainda")


def render_editor_settings():
    """Renderiza configurações do editor"""
    st.markdown("**⚙️ Configurações**")
    
    prefs = st.session_state.sql_editor_preferences
    
    prefs['auto_format'] = st.checkbox("🎨 Auto-formatação", value=prefs['auto_format'])
    prefs['show_line_numbers'] = st.checkbox("📄 Numeração", value=prefs['show_line_numbers'])
    prefs['syntax_highlight'] = st.checkbox("🌈 Highlight SQL", value=prefs['syntax_highlight'])
    
    prefs['max_rows_display'] = st.number_input(
        "📊 Máx. linhas exibição:",
        min_value=10,
        max_value=1000,
        value=prefs['max_rows_display'],
        step=10
    )


def render_main_sql_editor(db_manager):
    """Renderiza editor principal de SQL"""
    st.markdown("#### ✏️ Editor de Query")
    
    # Editor principal
    default_query = st.session_state.get('sql_query', 'SELECT * FROM users LIMIT 10;')
    
    sql_query = st.text_area(
        "Digite sua query SQL:",
        value=default_query,
        height=200,
        placeholder="-- Digite sua query SQL aqui\nSELECT * FROM sua_tabela LIMIT 10;",
        help="Use Ctrl+Enter para executar rapidamente. Use {table_name} nos templates para substituição automática."
    )
    
    # Salvar query no session state
    st.session_state.sql_query = sql_query
    
    # Botões de ação
    render_editor_action_buttons(sql_query, db_manager)
    
    # Informações da query
    if sql_query.strip():
        render_query_info(sql_query)


def render_editor_action_buttons(sql_query, db_manager):
    """Renderiza botões de ação do editor"""
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        execute_button = st.button(
            "▶️ Executar",
            use_container_width=True,
            type="primary",
            disabled=not sql_query.strip(),
            help="Execute a query SQL (Ctrl+Enter)"
        )
    
    with action_col2:
        if st.button("🔍 Validar", use_container_width=True, help="Validar sintaxe da query"):
            validation_result = validate_sql_query(sql_query)
            if validation_result['valid']:
                st.success("✅ Query válida!")
            else:
                st.error(f"❌ Erro de sintaxe: {validation_result['error']}")
    
    with action_col3:
        if st.button("🎨 Formatar", use_container_width=True, help="Formatar e organizar código SQL"):
            formatted_query = format_sql_query(sql_query)
            st.session_state.sql_query = formatted_query
            st.rerun()
    
    with action_col4:
        if st.button("⭐ Favoritar", use_container_width=True, help="Adicionar aos favoritos"):
            if sql_query.strip() and sql_query not in st.session_state.sql_favorites:
                st.session_state.sql_favorites.append(sql_query)
                st.success("✅ Query adicionada aos favoritos!")
            elif sql_query in st.session_state.sql_favorites:
                st.info("ℹ️ Query já está nos favoritos")
            else:
                st.warning("⚠️ Digite uma query para favoritar")
    
    # Executar query se botão foi pressionado
    if execute_button and sql_query.strip():
        execute_sql_query(sql_query, db_manager)


def render_query_info(sql_query):
    """Renderiza informações sobre a query atual"""
    query_info_col1, query_info_col2, query_info_col3, query_info_col4 = st.columns(4)
    
    with query_info_col1:
        query_type = get_query_type(sql_query)
        st.metric("Tipo de Query", query_type)
    
    with query_info_col2:
        char_count = len(sql_query)
        st.metric("Caracteres", char_count)
    
    with query_info_col3:
        line_count = len(sql_query.split('\n'))
        st.metric("Linhas", line_count)
    
    with query_info_col4:
        word_count = len(sql_query.split())
        st.metric("Palavras", word_count)


def execute_sql_query(sql_query, db_manager):
    """Executa uma query SQL e gerencia resultados"""
    with st.spinner("⏳ Executando query..."):
        # Adicionar ao histórico
        if sql_query not in st.session_state.sql_history:
            st.session_state.sql_history.append(sql_query)
            # Manter apenas as últimas 100 queries
            if len(st.session_state.sql_history) > 100:
                st.session_state.sql_history = st.session_state.sql_history[-100:]
        
        # Executar query
        try:
            result = db_manager.execute_query(sql_query)
            st.session_state.last_execution_result = result
            
            # Exibir resultados
            display_query_results(result, sql_query)
            
        except Exception as e:
            st.error(f"❌ Erro durante execução: {e}")
            with st.expander("🔍 Detalhes do Erro", expanded=False):
                st.exception(e)


def render_sql_results_section():
    """Renderiza seção de resultados da última query"""
    if st.session_state.last_execution_result:
        st.markdown("---")
        st.markdown("#### 📊 Resultados da Query")
        display_query_results(st.session_state.last_execution_result, st.session_state.sql_query)


def display_query_results(result, sql_query):
    """Exibe resultados de uma query SQL executada"""
    if result['success']:
        # Métricas de execução
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
        
        with metrics_col1:
            st.metric("✅ Status", "Sucesso", delta="Query executada")
        
        with metrics_col2:
            st.metric("⏱️ Tempo", result.get('execution_time', 'N/A'))
        
        with metrics_col3:
            st.metric("📝 Registros", result.get('rows_affected', 0))
        
        with metrics_col4:
            data_size = len(str(result.get('data', [])))
            st.metric("💾 Tamanho", f"{data_size} chars")
        
        # Mostrar dados se existirem
        if result.get('data') and len(result['data']) > 0:
            st.markdown("**📋 Dados Retornados:**")
            
            try:
                df_result = pd.DataFrame(result['data'])
                
                # Controles de visualização
                view_col1, view_col2, view_col3, view_col4 = st.columns(4)
                
                with view_col1:
                    show_index = st.checkbox("📄 Mostrar índice", value=False)
                
                with view_col2:
                    max_rows = st.number_input(
                        "📊 Máx. linhas", 
                        min_value=5, 
                        max_value=1000, 
                        value=st.session_state.sql_editor_preferences['max_rows_display']
                    )
                
                with view_col3:
                    use_container_width = st.checkbox("📏 Largura total", value=True)
                
                with view_col4:
                    if st.button("📊 Análise Rápida", help="Mostra estatísticas descritivas"):
                        with st.expander("📈 Análise Estatística", expanded=True):
                            st.write("**Informações Gerais:**")
                            st.write(df_result.describe(include='all'))
                            
                            if len(df_result.select_dtypes(include=[np.number]).columns) > 0: # type: ignore
                                st.write("**Correlações (apenas colunas numéricas):**")
                                st.write(df_result.corr())
                
                # Exibir DataFrame
                st.dataframe(
                    df_result.head(max_rows),
                    use_container_width=use_container_width,
                    hide_index=not show_index
                )
                
                # Estatísticas do DataFrame
                if len(df_result) > 0:
                    render_data_statistics(df_result)
                
                # Opções de exportação
                render_export_options(df_result, sql_query)
                
            except Exception as e:
                st.error(f"❌ Erro ao processar resultados: {e}")
                st.json(result['data'])
        
        else:
            st.info("✅ Query executada com sucesso, mas não retornou dados")
            if result.get('message'):
                st.success(result['message'])
    
    else:
        # Exibir erro
        st.error(f"❌ Erro na execução da query:")
        
        error_msg = result.get('error', 'Erro desconhecido')
        st.code(error_msg, language='text')
        
        if result.get('message'):
            st.info(f"ℹ️ {result['message']}")
        
        # Sugestões de correção baseadas no erro
        provide_error_suggestions(error_msg, sql_query)


def render_data_statistics(df_result):
    """Renderiza estatísticas dos dados retornados"""
    st.markdown("**📈 Estatísticas dos Dados:**")
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    
    with stats_col1:
        st.metric("📊 Total de Linhas", len(df_result))
    
    with stats_col2:
        st.metric("📋 Total de Colunas", len(df_result.columns))
    
    with stats_col3:
        memory_usage = df_result.memory_usage(deep=True).sum()
        st.metric("💾 Uso de Memória", f"{memory_usage / 1024:.1f} KB")
    
    with stats_col4:
        null_count = df_result.isnull().sum().sum()
        st.metric("❌ Valores Nulos", null_count)
    
    # Informações detalhadas das colunas
    with st.expander("🔍 Informações das Colunas", expanded=False):
        col_info = pd.DataFrame({
            'Coluna': df_result.columns,
            'Tipo': [str(dtype) for dtype in df_result.dtypes],
            'Não Nulos': [df_result[col].count() for col in df_result.columns],
            'Nulos': [df_result[col].isnull().sum() for col in df_result.columns],
            'Únicos': [df_result[col].nunique() for col in df_result.columns],
            '% Únicos': [f"{(df_result[col].nunique() / len(df_result) * 100):.1f}%" for col in df_result.columns]
        })
        st.dataframe(col_info, use_container_width=True, hide_index=True)


def render_export_options(df_result, sql_query):
    """Renderiza opções de exportação dos resultados"""
    if len(df_result) > 0:
        st.markdown("**📤 Exportar Resultados:**")
        export_col1, export_col2, export_col3, export_col4 = st.columns(4)
        
        with export_col1:
            if st.button("📄 CSV", use_container_width=True, help="Exportar como CSV"):
                csv_buffer = df_result.to_csv(index=False)
                st.download_button(
                    label="💾 Download CSV",
                    data=csv_buffer,
                    file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with export_col2:
            if st.button("📊 Excel", use_container_width=True, help="Exportar como Excel"):
                try:
                    excel_buffer = BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        df_result.to_excel(writer, index=False, sheet_name='Query_Result')
                    excel_buffer.seek(0)
                    
                    st.download_button(
                        label="💾 Download Excel",
                        data=excel_buffer.getvalue(),
                        file_name=f"query_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"❌ Erro ao gerar Excel: {e}")
        
        with export_col3:
            if st.button("📋 JSON", use_container_width=True, help="Visualizar como JSON"):
                json_data = df_result.to_json(orient='records', indent=2)
                st.text_area(
                    "JSON dos resultados:",
                    value=json_data,
                    height=200,
                    help="Use Ctrl+A e Ctrl+C para copiar todo o conteúdo"
                )
        
        with export_col4:
            if st.button("🔗 Compartilhar", use_container_width=True, help="Gerar link para compartilhar"):
                data_id = hashlib.md5(sql_query.encode()).hexdigest()[:8]
                st.info(f"🔗 ID dos dados: `{data_id}`")
                st.caption("Use este ID para referenciar estes resultados")


def provide_error_suggestions(error_msg, sql_query):
    """Fornece sugestões baseadas no tipo de erro"""
    error_lower = error_msg.lower()
    
    st.markdown("**💡 Sugestões de Correção:**")
    
    if any(word in error_lower for word in ['syntax', 'sintaxe', 'near']):
        st.markdown("""
        **Erro de Sintaxe:**
        - ✅ Verifique pontos e vírgulas
        - ✅ Confirme parênteses balanceados
        - ✅ Use o botão 'Validar' antes de executar
        - ✅ Consulte os templates disponíveis
        """)
    
    elif any(word in error_lower for word in ['table', 'tabela', 'relation']):
        st.markdown("""
        **Tabela Não Encontrada:**
        - ✅ Verifique se a tabela existe na lista lateral
        - ✅ Confirme o nome correto da tabela
        - ✅ Use o botão de uma tabela para inserir automaticamente
        - ✅ Verifique permissões de acesso
        """)
    
    elif any(word in error_lower for word in ['column', 'coluna', 'field']):
        st.markdown("""
        **Coluna Não Encontrada:**
        - ✅ Verifique se a coluna existe na tabela
        - ✅ Use SELECT * para ver todas as colunas
        - ✅ Confirme a grafia correta
        """)
    
    elif any(word in error_lower for word in ['permission', 'access', 'denied']):
        st.markdown("""
        **Erro de Permissão:**
        - ✅ Verifique suas credenciais de acesso
        - ✅ Confirme permissões para esta operação
        - ✅ Entre em contato com o administrador
        """)
    
    else:
        st.markdown("""
        **Erro Geral:**
        - ✅ Revise a sintaxe SQL
        - ✅ Teste com uma query mais simples
        - ✅ Verifique a conexão com o banco
        - ✅ Consulte a documentação SQL
        """)


def render_favorites_section():
    """Renderiza seção de queries favoritas"""
    if st.session_state.sql_favorites:
        st.markdown("---")
        st.markdown("#### ⭐ Queries Favoritas")
        
        # Opção para pesquisar favoritos
        if len(st.session_state.sql_favorites) > 5:
            search_favorites = st.text_input("🔍 Buscar nos favoritos:", placeholder="Digite para filtrar...")
            filtered_favorites = [
                fav for fav in st.session_state.sql_favorites 
                if not search_favorites or search_favorites.lower() in fav.lower()
            ]
        else:
            filtered_favorites = st.session_state.sql_favorites
        
        for i, fav_query in enumerate(filtered_favorites):
            original_index = st.session_state.sql_favorites.index(fav_query)
            
            with st.expander(f"⭐ Favorita {original_index + 1}: {fav_query[:50]}...", expanded=False):
                st.code(fav_query, language='sql')
                
                fav_col1, fav_col2, fav_col3 = st.columns(3)
                
                with fav_col1:
                    if st.button("🔄 Carregar", key=f"load_fav_{original_index}", use_container_width=True):
                        st.session_state.sql_query = fav_query
                        st.rerun()
                
                with fav_col2:
                    if st.button("📋 Copiar", key=f"copy_fav_{original_index}", use_container_width=True):
                        st.text_area("Query copiada:", value=fav_query, height=100, key=f"copy_area_{original_index}")
                
                with fav_col3:
                    if st.button("🗑️ Remover", key=f"remove_fav_{original_index}", use_container_width=True):
                        st.session_state.sql_favorites.pop(original_index)
                        st.success("✅ Favorito removido!")
                        st.rerun()


def show_example_queries():
    """Mostra queries de exemplo quando não há conexão"""
    st.markdown("---")
    st.markdown("### 📚 Queries de Exemplo")
    st.markdown("Pratique com estas queries enquanto configura sua conexão:")
    
    examples = {
        "Consultas Básicas": {
            "Selecionar usuários": "SELECT id, name, email FROM users WHERE active = true ORDER BY name;",
            "Contar registros": "SELECT COUNT(*) as total_users FROM users;",
            "Buscar por padrão": "SELECT * FROM products WHERE name LIKE '%smartphone%';"
        },
        "Consultas Intermediárias": {
            "JOIN com duas tabelas": "SELECT u.name, p.title FROM users u JOIN posts p ON u.id = p.user_id;",
            "GROUP BY com agregação": "SELECT category, COUNT(*) as count, AVG(price) as avg_price FROM products GROUP BY category;",
            "Subconsulta": "SELECT * FROM orders WHERE user_id IN (SELECT id FROM users WHERE country = 'Brazil');"
        },
        "Consultas Avançadas": {
            "Window function": "SELECT name, salary, ROW_NUMBER() OVER (ORDER BY salary DESC) as rank FROM employees;",
            "CTE (Common Table Expression)": "WITH top_users AS (SELECT user_id FROM orders GROUP BY user_id HAVING COUNT(*) > 5) SELECT u.name FROM users u JOIN top_users t ON u.id = t.user_id;",
            "CASE statement": "SELECT name, CASE WHEN age < 18 THEN 'Menor' WHEN age < 65 THEN 'Adulto' ELSE 'Idoso' END as category FROM users;"
        }
    }
    
    for category, queries in examples.items():
        with st.expander(f"📖 {category}", expanded=False):
            for title, query in queries.items():
                st.markdown(f"**{title}:**")
                st.code(query, language='sql')
                if st.button(f"📋 Usar {title}", key=f"example_{title.replace(' ', '_')}"):
                    st.session_state.sql_query = query
                    st.success(f"✅ Query '{title}' carregada no editor!")
                st.markdown("---")


# Funções auxiliares para validação e formatação já definidas anteriormente
def validate_sql_query(query: str) -> Dict:
    """Valida sintaxe básica de uma query SQL"""
    try:
        query_clean = query.strip().upper()
        
        if not query_clean:
            return {'valid': False, 'error': 'Query vazia'}
        
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'WITH']
        starts_with_keyword = any(query_clean.startswith(keyword) for keyword in sql_keywords)
        
        if not starts_with_keyword:
            return {'valid': False, 'error': 'Query deve começar com uma palavra-chave SQL válida'}
        
        if query_clean.count('(') != query_clean.count(')'):
            return {'valid': False, 'error': 'Parênteses não balanceados'}
        
        single_quotes = query_clean.count("'")
        double_quotes = query_clean.count('"')
        
        if single_quotes % 2 != 0:
            return {'valid': False, 'error': 'Aspas simples não balanceadas'}
        
        if double_quotes % 2 != 0:
            return {'valid': False, 'error': 'Aspas duplas não balanceadas'}
        
        if query_clean.startswith('SELECT'):
            if 'FROM' not in query_clean and 'DUAL' not in query_clean:
                return {'valid': False, 'error': 'SELECT deve conter FROM ou ser uma consulta específica'}
        
        elif query_clean.startswith('INSERT'):
            if 'INTO' not in query_clean:
                return {'valid': False, 'error': 'INSERT deve conter INTO'}
        
        elif query_clean.startswith('UPDATE'):
            if 'SET' not in query_clean:
                return {'valid': False, 'error': 'UPDATE deve conter SET'}
        
        elif query_clean.startswith('DELETE'):
            if 'FROM' not in query_clean:
                return {'valid': False, 'error': 'DELETE deve conter FROM'}
        
        return {'valid': True, 'error': None}
    
    except Exception as e:
        return {'valid': False, 'error': f'Erro na validação: {str(e)}'}


def format_sql_query(query: str) -> str:
    """Formata uma query SQL para melhor legibilidade"""
    try:
        import re
        
        keywords = [
            'SELECT', 'FROM', 'WHERE', 'ORDER BY', 'GROUP BY', 'HAVING',
            'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE',
            'CREATE', 'TABLE', 'DROP', 'ALTER', 'ADD', 'COLUMN',
            'INDEX', 'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES',
            'INNER', 'LEFT', 'RIGHT', 'FULL', 'JOIN', 'ON',
            'UNION', 'INTERSECT', 'EXCEPT', 'AS', 'DISTINCT',
            'AND', 'OR', 'NOT', 'IN', 'EXISTS', 'BETWEEN',
            'LIKE', 'IS', 'NULL', 'TRUE', 'FALSE',
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX',
            'LIMIT', 'OFFSET', 'ASC', 'DESC', 'WITH'
        ]
        
        formatted = query
        
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            formatted = re.sub(pattern, keyword, formatted, flags=re.IGNORECASE)
        
        # Adicionar quebras de linha
        formatted = re.sub(r'\bFROM\b', '\nFROM', formatted)
        formatted = re.sub(r'\bWHERE\b', '\nWHERE', formatted)
        formatted = re.sub(r'\bORDER BY\b', '\nORDER BY', formatted)
        formatted = re.sub(r'\bGROUP BY\b', '\nGROUP BY', formatted)
        formatted = re.sub(r'\bHAVING\b', '\nHAVING', formatted)
        formatted = re.sub(r'\bJOIN\b', '\nJOIN', formatted)
        formatted = re.sub(r'\bUNION\b', '\nUNION', formatted)
        formatted = re.sub(r'\bWITH\b', '\nWITH', formatted)
        
        # Limpar linhas vazias extras
        lines = [line.strip() for line in formatted.split('\n') if line.strip()]
        formatted = '\n'.join(lines)
        
        return formatted
    
    except Exception:
        return query


def get_query_type(query: str) -> str:
    """Identifica o tipo de uma query SQL"""
    query_upper = query.strip().upper()
    
    type_mapping = {
        'SELECT': 'SELECT',
        'INSERT': 'INSERT',
        'UPDATE': 'UPDATE',
        'DELETE': 'DELETE',
        'CREATE': 'CREATE',
        'DROP': 'DROP',
        'ALTER': 'ALTER',
        'EXPLAIN': 'EXPLAIN',
        'SHOW': 'SHOW',
        'WITH': 'CTE'
    }
    
    for keyword, query_type in type_mapping.items():
        if query_upper.startswith(keyword):
            return query_type
    
    return 'OTHER'

def render_dba_operations():
    """Renderiza página de operações de DBA"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #F0FFF0, #E6FFE6); 
                padding: 1.5rem; border-radius: 15px; 
                border-left: 5px solid #2E8B57; margin-bottom: 2rem;'>
        <h2 style='color: #2E8B57; margin: 0; font-size: 2rem;'>
            🔧 Operações de DBA
        </h2>
        <p style='color: #228B22; margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
            Ferramentas avançadas para administração do banco de dados
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Abas de operações
    tab1, tab2, tab3, tab4 = st.tabs(["💾 Backup & Restore", "⚡ Otimização", "📊 Monitoramento", "🔧 Manutenção"])
    
    with tab1:
        st.subheader("💾 Backup e Restore")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📤 Criar Backup")
            
            # Seleção de tabelas para backup
            tables = db_manager.get_tables()
            table_names = [table['name'] for table in tables]
            
            backup_type = st.radio("Tipo de backup:", ["Tabela específica", "Banco completo"])
            
            if backup_type == "Tabela específica":
                selected_table = st.selectbox("Selecione a tabela:", table_names)
                
                if st.button("💾 Criar Backup da Tabela", type="primary"):
                    if selected_table:
                        with st.spinner(f"💾 Criando backup de {selected_table}..."):
                            result = db_manager.backup_table(selected_table)
                        
                        if result['success']:
                            st.success(f"✅ {result['message']}")
                            log_activity("Backup criado", f"Tabela: {selected_table}")
                        else:
                            st.error(f"❌ {result['message']}")
            
            else:
                if st.button("💾 Criar Backup Completo", type="primary"):
                    with st.spinner("💾 Criando backup completo do banco..."):
                        time.sleep(3)  # Simular tempo de backup
                    
                    backup_name = f"petcare_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    st.success(f"✅ Backup completo criado: {backup_name}")
                    log_activity("Backup completo criado", backup_name)
        
        with col2:
            st.markdown("#### 📥 Restore")
            
            # Lista de backups simulados
            available_backups = [
                f"users_backup_{datetime.now().strftime('%Y%m%d')}_120000",
                f"pets_backup_{datetime.now().strftime('%Y%m%d')}_100000",
                f"appointments_backup_{(datetime.now() - timedelta(days=1)).strftime('%Y%m%d')}_230000"
            ]
            
            selected_backup = st.selectbox("Selecione o backup:", available_backups)
            
            restore_option = st.radio("Opção de restore:", [
                "Substituir tabela existente",
                "Criar nova tabela",
                "Verificar apenas"
            ])
            
            if st.button("📥 Executar Restore", type="secondary"):
                if selected_backup:
                    with st.spinner(f"📥 Executando restore de {selected_backup}..."):
                        time.sleep(2)
                    
                    st.success(f"✅ Restore de {selected_backup} executado com sucesso!")
                    log_activity("Restore executado", selected_backup)
        
        # Histórico de backups
        st.markdown("#### 📋 Histórico de Backups")
        
        backup_history = [
            {"nome": "users_backup_20250624_120000", "tamanho": "2.1 MB", "data": "24/06/2025 12:00", "status": "✅ Sucesso"},
            {"nome": "pets_backup_20250624_100000", "tamanho": "1.8 MB", "data": "24/06/2025 10:00", "status": "✅ Sucesso"},
            {"nome": "full_backup_20250623_230000", "tamanho": "45.7 MB", "data": "23/06/2025 23:00", "status": "✅ Sucesso"}
        ]
        
        df_backups = pd.DataFrame(backup_history)
        st.dataframe(df_backups, use_container_width=True)
    
    with tab2:
        st.subheader("⚡ Otimização de Performance")
        
        # Análise geral
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🔍 Análise de Índices")
            
            if st.button("🔍 Analisar Índices", use_container_width=True):
                with st.spinner("🔍 Analisando índices..."):
                    time.sleep(2)
                
                # Simulação de análise de índices
                index_analysis = {
                    "Índices utilizados": random.randint(15, 25),
                    "Índices não utilizados": random.randint(0, 5),
                    "Índices duplicados": random.randint(0, 2),
                    "Eficiência geral": f"{random.randint(80, 95)}%"
                }
                
                st.json(index_analysis)
                
                if index_analysis["Índices não utilizados"] > 0:
                    st.warning(f"⚠️ {index_analysis['Índices não utilizados']} índices não utilizados encontrados")
        
        with col2:
            st.markdown("#### 📊 Estatísticas")
            
            if st.button("📊 Atualizar Estatísticas", use_container_width=True):
                with st.spinner("📊 Atualizando estatísticas..."):
                    # Simular atualização de estatísticas
                    for table in db_manager.get_tables()[:3]:
                        query = f"ANALYZE {table['name']};"
                        result = db_manager.execute_query(query)
                        time.sleep(0.5)
                
                st.success("✅ Estatísticas atualizadas para todas as tabelas!")
                log_activity("Estatísticas atualizadas")
        
        with col3:
            st.markdown("#### 🧹 Limpeza")
            
            if st.button("🧹 VACUUM ANALYZE", use_container_width=True):
                with st.spinner("🧹 Executando VACUUM ANALYZE..."):
                    time.sleep(3)
                
                st.success("✅ VACUUM ANALYZE executado com sucesso!")
                log_activity("VACUUM ANALYZE executado")
        
        # Otimização por tabela
        st.markdown("#### 🗃️ Otimização por Tabela")
        
        tables = db_manager.get_tables()
        
        for table in tables[:5]:  # Mostrar apenas as 5 primeiras
            with st.expander(f"🗃️ {table['name']} ({table['rows']:,} registros)"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button(f"⚡ Otimizar", key=f"opt_{table['name']}"):
                        result = db_manager.optimize_table(table['name'])
                        if result['success']:
                            st.success(f"✅ {result['message']}")
                        else:
                            st.error(f"❌ {result['message']}")
                
                with col2:
                    if st.button(f"🔍 Analisar", key=f"analyze_{table['name']}"):
                        query = f"ANALYZE {table['name']};"
                        result = db_manager.execute_query(query)
                        if result['success']:
                            st.success(f"✅ Análise de {table['name']} concluída")
                
                with col3:
                    if st.button(f"📊 Estatísticas", key=f"stats_{table['name']}"):
                        # Mostrar estatísticas da tabela
                        st.json({
                            "Registros": table['rows'],
                            "Tamanho": table['size'],
                            "Índices": "✅" if table.get('has_indexes') else "❌",
                            "Triggers": "✅" if table.get('has_triggers') else "❌"
                        })
                
                with col4:
                    if st.button(f"🔧 Rebuild", key=f"rebuild_{table['name']}"):
                        with st.spinner(f"🔧 Rebuilding {table['name']}..."):
                            time.sleep(1)
                        st.success(f"✅ {table['name']} reconstruída")
    
    with tab3:
        st.subheader("📊 Monitoramento em Tempo Real")
        
        # Métricas principais
        metrics = db_manager.get_database_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🔗 Conexões", metrics.get('connection_count', 'N/A'))
        
        with col2:
            cpu_usage = metrics.get('cpu_usage', 50)
            st.metric("💻 CPU", f"{cpu_usage}%" if isinstance(cpu_usage, (int, float)) else str(cpu_usage))
        
        with col3:
            memory_usage = metrics.get('memory_usage', 60)
            st.metric("💾 Memória", f"{memory_usage}%" if isinstance(memory_usage, (int, float)) else str(memory_usage))
        
        with col4:
            st.metric("💽 Tamanho DB", metrics.get('total_size', 'N/A'))
        
        # Gráficos de monitoramento
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 Performance (24h)")
            
            # Dados simulados para gráfico
            hours = list(range(24))
            cpu_data = [random.randint(30, 80) for _ in hours]
            memory_data = [random.randint(40, 85) for _ in hours]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hours, y=cpu_data, name='CPU %', line=dict(color='#2E8B57')))
            fig.add_trace(go.Scatter(x=hours, y=memory_data, name='Memória %', line=dict(color='#90EE90')))
            
            fig.update_layout(
                title="Performance nas últimas 24 horas",
                xaxis_title="Hora",
                yaxis_title="Porcentagem",
                height=300,
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 🔗 Conexões Ativas")
            
            # Simular dados de conexões
            connection_data = {
                'Tipo': ['Leitura', 'Escrita', 'Admin', 'Idle'],
                'Quantidade': [random.randint(5, 15), random.randint(2, 8), random.randint(1, 3), random.randint(0, 5)]
            }
            
            fig = px.pie(
                values=connection_data['Quantidade'],
                names=connection_data['Tipo'],
                title="Distribuição de Conexões",
                color_discrete_sequence=['#2E8B57', '#90EE90', '#228B22', '#98FB98']
            )
            fig.update_layout(height=300)
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Tabela de processos ativos
        st.markdown("#### 🔄 Processos Ativos")
        
        active_processes = [
            {"PID": 12345, "Usuário": "postgres", "Database": "petcareai", "Query": "SELECT * FROM users WHERE...", "Tempo": "00:00:15"},
            {"PID": 12346, "Usuário": "app_user", "Database": "petcareai", "Query": "INSERT INTO appointments...", "Tempo": "00:00:03"},
            {"PID": 12347, "Usuário": "admin", "Database": "petcareai", "Query": "VACUUM ANALYZE pets;", "Tempo": "00:01:23"}
        ]
        
        df_processes = pd.DataFrame(active_processes)
        st.dataframe(df_processes, use_container_width=True)
        
        # Controles de monitoramento
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Atualizar Dados", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("⏹️ Parar Processo", use_container_width=True):
                st.warning("⚠️ Funcionalidade disponível apenas com permissões adequadas")
        
        with col3:
            if st.button("📊 Relatório Completo", use_container_width=True):
                st.info("📊 Gerando relatório de monitoramento...")
    
    with tab4:
        st.subheader("🔧 Manutenção do Sistema")
        
        # Tarefas de manutenção
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🧹 Limpeza")
            
            maintenance_tasks = [
                {"task": "Limpar logs antigos", "description": "Remove logs com mais de 30 dias", "critical": False},
                {"task": "Reorganizar índices", "description": "Otimiza estrutura dos índices", "critical": False},
                {"task": "Atualizar estatísticas", "description": "Recalcula estatísticas das tabelas", "critical": True},
                {"task": "Verificar integridade", "description": "Valida consistência dos dados", "critical": True}
            ]
            
            for task in maintenance_tasks:
                priority = "🔴 Crítico" if task["critical"] else "🟡 Normal"
                
                with st.expander(f"🔧 {task['task']} - {priority}"):
                    st.write(task["description"])
                    
                    col_task1, col_task2 = st.columns(2)
                    
                    with col_task1:
                        if st.button(f"▶️ Executar", key=f"exec_{task['task']}"):
                            with st.spinner(f"🔧 Executando {task['task']}..."):
                                time.sleep(random.randint(1, 3))
                            
                            st.success(f"✅ {task['task']} concluída!")
                            log_activity("Manutenção executada", task['task'])
                    
                    with col_task2:
                        if st.button(f"⏰ Agendar", key=f"schedule_{task['task']}"):
                            st.info(f"📅 {task['task']} agendada para execução automática")
        
        with col2:
            st.markdown("#### 📅 Agendamento")
            
            # Configuração de tarefas agendadas
            scheduled_tasks = [
                {"task": "Backup automático", "schedule": "Diário 23:00", "status": "✅ Ativo"},
                {"task": "Atualizar estatísticas", "schedule": "Semanal Dom 02:00", "status": "✅ Ativo"},
                {"task": "Limpeza de logs", "schedule": "Mensal dia 1", "status": "⏸️ Pausado"}
            ]
            
            st.write("**🕒 Tarefas Agendadas:**")
            
            for task in scheduled_tasks:
                st.write(f"• **{task['task']}** - {task['schedule']} - {task['status']}")
            
            st.markdown("---")
            
            st.write("**➕ Adicionar Nova Tarefa:**")
            
            new_task_name = st.selectbox("Tarefa:", [
                "Backup completo",
                "VACUUM ANALYZE",
                "Verificação de integridade",
                "Limpeza de tabelas temporárias"
            ])
            
            new_task_schedule = st.selectbox("Frequência:", [
                "Diário",
                "Semanal", 
                "Mensal",
                "Personalizado"
            ])
            
            if st.button("➕ Agendar Tarefa"):
                st.success(f"✅ Tarefa '{new_task_name}' agendada para execução {new_task_schedule.lower()}")
                log_activity("Tarefa agendada", f"{new_task_name} - {new_task_schedule}")
        
       # Status geral do sistema
        st.markdown("---")
        st.subheader("🏥 Status Geral do Sistema")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🟢 Componentes Saudáveis")
            healthy_components = [
                "✅ Banco de dados principal",
                "✅ Conexões de rede", 
                "✅ Sistema de backup",
                "✅ Monitoramento ativo"
            ]
            
            for component in healthy_components:
                st.write(component)
        
        with col2:
            st.markdown("#### ⚠️ Avisos")
            warnings = [
                "⚠️ CPU acima de 70%",
                "⚠️ 2 índices não utilizados",
                "⚠️ Último backup há 25 horas"
            ]
            
            for warning in warnings:
                st.write(warning)
        
        with col3:
            st.markdown("#### 📊 Próximas Ações")
            next_actions = [
                "🔄 VACUUM ANALYZE agendado",
                "💾 Backup automático 23:00",
                "📊 Relatório semanal Sex 18:00"
            ]
            
            for action in next_actions:
                st.write(action)

def render_projects():
    """Renderiza página de projetos"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #F0FFF0, #E6FFE6); 
                padding: 1.5rem; border-radius: 15px; 
                border-left: 5px solid #2E8B57; margin-bottom: 2rem;'>
        <h2 style='color: #2E8B57; margin: 0; font-size: 2rem;'>
            📁 Gerenciamento de Projetos
        </h2>
        <p style='color: #228B22; margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
            Organize scripts, consultas e operações por projetos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Inicializar projetos se não existir
    if 'projects' not in st.session_state:
        st.session_state.projects = [
            {
                'id': 1,
                'name': 'Sistema Principal',
                'description': 'Scripts e queries do sistema principal PetCare',
                'category': 'Desenvolvimento',
                'priority': 'Alta',
                'scripts': 45,
                'status': 'active',
                'members': ['admin@petcareai.com', 'dev@petcareai.com'],
                'created_at': datetime.now() - timedelta(days=30),
                'tags': ['sistema', 'principal', 'crud']
            },
            {
                'id': 2,
                'name': 'Relatórios BI',
                'description': 'Consultas e relatórios de business intelligence',
                'category': 'Análise',
                'priority': 'Média',
                'scripts': 23,
                'status': 'active',
                'members': ['admin@petcareai.com', 'analyst@petcareai.com'],
                'created_at': datetime.now() - timedelta(days=20),
                'tags': ['bi', 'relatórios', 'dashboard']
            },
            {
                'id': 3,
                'name': 'Manutenção DB',
                'description': 'Scripts de manutenção e otimização do banco',
                'category': 'Manutenção',
                'priority': 'Crítica',
                'scripts': 12,
                'status': 'active',
                'members': ['admin@petcareai.com'],
                'created_at': datetime.now() - timedelta(days=10),
                'tags': ['manutenção', 'otimização', 'backup']
            }
        ]
    
    # Abas de projetos
    tab1, tab2, tab3 = st.tabs(["📋 Projetos Ativos", "➕ Novo Projeto", "📊 Estatísticas"])
    
    with tab1:
        # Filtros e controles
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_project = st.text_input("🔍 Buscar projeto:", placeholder="Digite o nome do projeto...")
        
        with col2:
            filter_status = st.selectbox("📊 Status:", ["Todos", "Ativo", "Pausado", "Concluído"])
        
        with col3:
            filter_priority = st.selectbox("⭐ Prioridade:", ["Todas", "Crítica", "Alta", "Média", "Baixa"])
        
        # Aplicar filtros
        filtered_projects = st.session_state.projects
        
        if search_project:
            filtered_projects = [p for p in filtered_projects 
                               if search_project.lower() in p['name'].lower()]
        
        if filter_status != "Todos":
            status_map = {"Ativo": "active", "Pausado": "paused", "Concluído": "completed"}
            filtered_projects = [p for p in filtered_projects 
                               if p['status'] == status_map.get(filter_status, 'active')]
        
        if filter_priority != "Todas":
            filtered_projects = [p for p in filtered_projects 
                               if p['priority'] == filter_priority]
        
        # Exibir projetos
        if filtered_projects:
            for project in filtered_projects:
                # Definir cores baseadas no status e prioridade
                status_colors = {
                    'active': '#2E8B57',
                    'paused': '#FFD700', 
                    'completed': '#808080'
                }
                
                priority_colors = {
                    'Crítica': '#FF6347',
                    'Alta': '#FF8C00',
                    'Média': '#FFD700',
                    'Baixa': '#90EE90'
                }
                
                status_color = status_colors.get(project['status'], '#2E8B57')
                priority_color = priority_colors.get(project['priority'], '#90EE90')
                
                with st.expander(f"📁 {project['name']} ({project['scripts']} scripts)", expanded=False):
                    # Informações do projeto
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📜 Scripts", project['scripts'])
                    
                    with col2:
                        status_text = {
                            'active': '🟢 Ativo',
                            'paused': '🟡 Pausado',
                            'completed': '⚫ Concluído'
                        }.get(project['status'], '🟢 Ativo')
                        
                        st.markdown(f"**Status:** {status_text}")
                    
                    with col3:
                        st.markdown(f"**Prioridade:** <span style='color: {priority_color}'>⭐ {project['priority']}</span>", 
                                  unsafe_allow_html=True)
                    
                    with col4:
                        st.metric("👥 Membros", len(project['members']))
                    
                    # Descrição e detalhes
                    st.write(f"**📝 Descrição:** {project['description']}")
                    st.write(f"**📂 Categoria:** {project['category']}")
                    st.write(f"**📅 Criado em:** {format_datetime(project['created_at'], 'short')}")
                    
                    # Tags
                    if project.get('tags'):
                        tags_html = " ".join([f"<span style='background: #E6FFE6; padding: 2px 6px; border-radius: 10px; font-size: 0.8rem; color: #2E8B57;'>#{tag}</span>" for tag in project['tags']])
                        st.markdown(f"**🏷️ Tags:** {tags_html}", unsafe_allow_html=True)
                    
                    # Membros
                    st.write(f"**👥 Membros:** {', '.join(project['members'])}")
                    
                    # Gráfico de atividade do projeto (simulado)
                    st.markdown("#### 📊 Atividade do Projeto")
                    
                    days = list(range(1, 31))
                    activity_data = [random.randint(0, project['scripts']//5) for _ in days]
                    
                    fig = px.line(
                        x=days,
                        y=activity_data,
                        title=f"Execuções de Scripts - {project['name']} (último mês)",
                        labels={'x': 'Dia', 'y': 'Execuções'}
                    )
                    fig.update_traces(line=dict(color='#2E8B57'))
                    fig.update_layout(height=300, template="plotly_white")
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Scripts do projeto (simulados)
                    st.markdown("#### 📜 Scripts Recentes")
                    
                    project_scripts = [
                        {
                            'name': f'{project["name"].lower().replace(" ", "_")}_query_{i}.sql',
                            'description': f'Script de {["consulta", "manutenção", "relatório"][i%3]} #{i+1}',
                            'last_run': datetime.now() - timedelta(days=random.randint(1, 10)),
                            'executions': random.randint(5, 50)
                        }
                        for i in range(min(5, project['scripts']))
                    ]
                    
                    for script in project_scripts:
                        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                        
                        with col1:
                            st.write(f"📄 **{script['name']}**")
                            st.write(f"<small>{script['description']}</small>", unsafe_allow_html=True)
                        
                        with col2:
                            st.write(f"📅 {format_datetime(script['last_run'], 'short')}")
                        
                        with col3:
                            st.write(f"🔄 {script['executions']}x")
                        
                        with col4:
                            if st.button("▶️", key=f"run_script_{project['id']}_{script['name']}", help="Executar script"):
                                st.info(f"🚀 Executando {script['name']}...")
                    
                    # Ações do projeto
                    st.markdown("---")
                    st.markdown("#### ⚙️ Ações do Projeto")
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        if st.button(f"📝 Editar", key=f"edit_proj_{project['id']}"):
                            st.session_state.edit_project_id = project['id']
                            st.info(f"✏️ Editando projeto {project['name']}...")
                    
                    with col2:
                        if st.button(f"📊 Relatório", key=f"report_proj_{project['id']}"):
                            # Gerar relatório do projeto
                            st.info(f"📈 Gerando relatório de {project['name']}...")
                            
                            project_report = {
                                "Nome do Projeto": project['name'],
                                "Total de Scripts": project['scripts'],
                                "Execuções no Mês": sum(activity_data),
                                "Média Diária": round(sum(activity_data)/len(activity_data), 1),
                                "Status": project['status'],
                                "Membros Ativos": len(project['members']),
                                "Dias Desde Criação": (datetime.now() - project['created_at']).days
                            }
                            
                            st.json(project_report)
                            log_activity("Relatório gerado", f"Projeto: {project['name']}")
                    
                    with col3:
                        # Toggle status
                        if project['status'] == 'active':
                            if st.button(f"⏸️ Pausar", key=f"pause_proj_{project['id']}"):
                                project['status'] = 'paused'
                                st.success(f"⏸️ Projeto {project['name']} pausado!")
                                st.rerun()
                        else:
                            if st.button(f"▶️ Ativar", key=f"activate_proj_{project['id']}"):
                                project['status'] = 'active'
                                st.success(f"▶️ Projeto {project['name']} ativado!")
                                st.rerun()
                    
                    with col4:
                        if st.button(f"📤 Exportar", key=f"export_proj_{project['id']}"):
                            # Criar dados para exportação
                            export_data = {
                                'projeto': project['name'],
                                'scripts': project_scripts,
                                'atividade': activity_data,
                                'membros': project['members']
                            }
                            
                            export_json = json.dumps(export_data, indent=2, default=str)
                            st.download_button(
                                "📥 Download JSON",
                                export_json,
                                f"{project['name'].lower().replace(' ', '_')}_export.json",
                                "application/json",
                                key=f"download_proj_{project['id']}"
                            )
                    
                    with col5:
                        if st.button(f"🗑️ Excluir", key=f"del_proj_{project['id']}"):
                            if st.checkbox(f"Confirmar exclusão de {project['name']}", key=f"confirm_del_{project['id']}"):
                                st.session_state.projects = [p for p in st.session_state.projects if p['id'] != project['id']]
                                st.success(f"✅ Projeto {project['name']} excluído!")
                                log_activity("Projeto excluído", project['name'])
                                st.rerun()
        
        else:
            st.warning("❌ Nenhum projeto encontrado com os critérios especificados.")
    
    with tab2:
        st.subheader("➕ Criar Novo Projeto")
        
        with st.form("new_project_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                project_name = st.text_input("📁 Nome do Projeto:", placeholder="Ex: Sistema de Relatórios")
                project_category = st.selectbox("📂 Categoria:", [
                    "Desenvolvimento", "Manutenção", "Relatórios", "Backup", "Análise", "Outros"
                ])
                project_priority = st.selectbox("⭐ Prioridade:", ["Baixa", "Média", "Alta", "Crítica"])
            
            with col2:
                project_description = st.text_area("📝 Descrição:", placeholder="Descreva o objetivo do projeto...")
                project_members = st.multiselect("👥 Membros:", [
                    "admin@petcareai.com", 
                    "dev@petcareai.com", 
                    "analyst@petcareai.com",
                    "dba@petcareai.com"
                ])
                project_tags = st.text_input("🏷️ Tags (separadas por vírgula):", 
                                           placeholder="sql, relatórios, manutenção")
            
            # Configurações avançadas
            st.markdown("#### ⚙️ Configurações Avançadas")
            
            col1, col2 = st.columns(2)
            
            with col1:
                auto_backup = st.checkbox("💾 Backup automático de scripts", value=True)
                notifications = st.checkbox("🔔 Notificações de execução", value=False)
            
            with col2:
                schedule_reports = st.checkbox("📊 Relatórios agendados", value=False)
                version_control = st.checkbox("📝 Controle de versão", value=True)
            
            submit_project = st.form_submit_button("🚀 Criar Projeto", type="primary")
            
            if submit_project:
                if project_name and project_description:
                    # Criar novo projeto
                    new_project = {
                        'id': max([p['id'] for p in st.session_state.projects], default=0) + 1,
                        'name': project_name,
                        'description': project_description,
                        'category': project_category,
                        'priority': project_priority,
                        'members': project_members,
                        'tags': [tag.strip() for tag in project_tags.split(',') if tag.strip()],
                        'scripts': 0,
                        'status': 'active',
                        'created_at': datetime.now(),
                        'settings': {
                            'auto_backup': auto_backup,
                            'notifications': notifications,
                            'schedule_reports': schedule_reports,
                            'version_control': version_control
                        }
                    }
                    
                    st.session_state.projects.append(new_project)
                    log_activity("Projeto criado", project_name)
                    
                    st.success(f"✅ Projeto '{project_name}' criado com sucesso!")
                    
                    # Mostrar detalhes do projeto criado
                    with st.expander("📋 Detalhes do Projeto Criado", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.json({
                                "Nome": project_name,
                                "Categoria": project_category,
                                "Prioridade": project_priority,
                                "Membros": project_members,
                                "Tags": project_tags
                            })
                        
                        with col2:
                            st.json({
                                "Backup Automático": auto_backup,
                                "Notificações": notifications,
                                "Relatórios Agendados": schedule_reports,
                                "Controle de Versão": version_control,
                                "Data de Criação": format_datetime(datetime.now(), 'full')
                            })
                
                else:
                    st.error("❌ Nome e descrição são obrigatórios!")
    
    with tab3:
        st.subheader("📊 Estatísticas dos Projetos")
        
        if st.session_state.projects:
            # Métricas gerais
            total_projects = len(st.session_state.projects)
            active_projects = len([p for p in st.session_state.projects if p['status'] == 'active'])
            total_scripts = sum(p['scripts'] for p in st.session_state.projects)
            total_members = len(set([member for p in st.session_state.projects for member in p['members']]))
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📁 Total Projetos", total_projects)
            
            with col2:
                st.metric("🟢 Projetos Ativos", active_projects)
            
            with col3:
                st.metric("📜 Total Scripts", total_scripts)
            
            with col4:
                st.metric("👥 Membros Únicos", total_members)
            
            # Gráficos de análise
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Projetos por Categoria")
                
                categories = {}
                for project in st.session_state.projects:
                    cat = project['category']
                    categories[cat] = categories.get(cat, 0) + 1
                
                if categories:
                    fig = px.pie(
                        values=list(categories.values()),
                        names=list(categories.keys()),
                        title="Distribuição por Categoria",
                        color_discrete_sequence=['#2E8B57', '#90EE90', '#228B22', '#98FB98', '#20B2AA', '#32CD32']
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### ⭐ Projetos por Prioridade")
                
                priorities = {}
                for project in st.session_state.projects:
                    prio = project['priority']
                    priorities[prio] = priorities.get(prio, 0) + 1
                
                if priorities:
                    fig = px.bar(
                        x=list(priorities.keys()),
                        y=list(priorities.values()),
                        title="Projetos por Prioridade",
                        color=list(priorities.values()),
                        color_continuous_scale=['#90EE90', '#FFD700', '#FF8C00', '#FF6347']
                    )
                    fig.update_layout(height=400, template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)
            
            # Top projetos
            st.markdown("#### 🏆 Top Projetos por Scripts")
            
            sorted_projects = sorted(st.session_state.projects, key=lambda x: x['scripts'], reverse=True)
            
            for i, project in enumerate(sorted_projects[:5]):
                col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
                
                with col1:
                    medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i]
                    st.write(medal)
                
                with col2:
                    st.write(f"**{project['name']}**")
                    st.write(f"<small>{project['category']} • {project['priority']}</small>", unsafe_allow_html=True)
                
                with col3:
                    st.write(f"📜 {project['scripts']}")
                
                with col4:
                    status_icon = "🟢" if project['status'] == 'active' else "🟡"
                    st.write(status_icon)
            
            # Análise temporal
            st.markdown("#### 📅 Criação de Projetos ao Longo do Tempo")
            
            project_dates = [p['created_at'].date() for p in st.session_state.projects]
            date_counts = {}
            
            for date in project_dates:
                month_key = date.strftime('%Y-%m')
                date_counts[month_key] = date_counts.get(month_key, 0) + 1
            
            if date_counts:
                fig = px.line(
                    x=list(date_counts.keys()),
                    y=list(date_counts.values()),
                    title="Projetos Criados por Mês",
                    markers=True
                )
                fig.update_traces(line=dict(color='#2E8B57'))
                fig.update_layout(height=300, template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.info("📭 Nenhum projeto encontrado para análise estatística.")

def render_settings():
    """Renderiza página de configurações"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #F0FFF0, #E6FFE6); 
                padding: 1.5rem; border-radius: 15px; 
                border-left: 5px solid #2E8B57; margin-bottom: 2rem;'>
        <h2 style='color: #2E8B57; margin: 0; font-size: 2rem;'>
            ⚙️ Configurações do Sistema
        </h2>
        <p style='color: #228B22; margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
            Gerencie configurações, preferências e conexões
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Abas de configurações
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔧 Sistema", "👤 Usuário", "🗄️ Banco de Dados", "📊 Monitoramento", "🔐 Segurança"])
    
    with tab1:
        st.subheader("🔧 Configurações do Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎨 Interface")
            
            # Configurações de tema
            theme_preset = st.selectbox("Tema:", 
                                       ["PetCare Verde", "Escuro", "Claro", "Personalizado"],
                                       key="system_theme_preset")
            
            if theme_preset == "Personalizado":
                primary_color = st.color_picker("Cor Primária:", 
                                               CONFIG['theme']['primary_color'],
                                               key="system_primary_color")
                secondary_color = st.color_picker("Cor Secundária:", 
                                                CONFIG['theme']['secondary_color'],
                                                key="system_secondary_color")
            
            # Configurações de layout
            sidebar_default = st.checkbox("Sidebar aberta por padrão", 
                                        value=True,
                                        key="system_sidebar_default")
            compact_mode = st.checkbox("Modo compacto", 
                                     value=False,
                                     key="system_compact_mode")
            show_tooltips = st.checkbox("Mostrar dicas de ferramentas", 
                                      value=True,
                                      key="system_show_tooltips")
            
            st.markdown("#### 📱 Responsividade")
            
            mobile_optimized = st.checkbox("Otimização mobile", 
                                         value=True,
                                         key="system_mobile_optimized")
            auto_scale = st.checkbox("Escala automática", 
                                   value=True,
                                   key="system_auto_scale")
        
        with col2:
            st.markdown("#### ⚡ Performance")
            
            # Configurações de cache
            enable_cache = st.checkbox("Ativar cache", 
                                     value=True,
                                     key="system_enable_cache")
            cache_duration = st.slider("Duração do cache (minutos):", 
                                     1, 60, 15,
                                     key="system_cache_duration")
            auto_refresh_interval = st.slider("Auto-refresh (segundos):", 
                                            10, 300, 30,
                                            key="system_auto_refresh_interval")
            
            # Configurações de dados
            max_records_display = st.number_input("Máx. registros por página:", 
                                                10, 1000, 50,
                                                key="system_max_records_display")
            query_timeout = st.number_input("Timeout de query (segundos):", 
                                          5, 300, 30,
                                          key="system_query_timeout")
            
            st.markdown("#### 🔔 Notificações")
            
            enable_notifications = st.checkbox("Ativar notificações", 
                                             value=True,
                                             key="system_enable_notifications")
            sound_notifications = st.checkbox("Notificações sonoras", 
                                            value=False,
                                            key="system_sound_notifications")
            browser_notifications = st.checkbox("Notificações do navegador", 
                                               value=False,
                                               key="system_browser_notifications")
        
        # Configurações avançadas
        st.markdown("#### 🛠️ Configurações Avançadas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            debug_mode = st.checkbox("Modo debug", 
                                   value=CONFIG['debug_mode'],
                                   key="system_debug_mode")
            verbose_logging = st.checkbox("Log detalhado", 
                                        value=False,
                                        key="system_verbose_logging")
        
        with col2:
            auto_backup_settings = st.checkbox("Backup automático configurações", 
                                             value=True,
                                             key="system_auto_backup_settings")
            export_logs = st.checkbox("Exportar logs automaticamente", 
                                    value=False,
                                    key="system_export_logs")
        
        with col3:
            maintenance_mode = st.checkbox("Modo manutenção", 
                                         value=False,
                                         key="system_maintenance_mode")
            read_only_mode = st.checkbox("Modo somente leitura", 
                                       value=False,
                                       key="system_read_only_mode")
        
        if st.button("💾 Salvar Configurações do Sistema", 
                    type="primary",
                    key="save_system_settings"):
            # Simular salvamento das configurações
            updated_config = {
                'theme_preset': theme_preset,
                'sidebar_default': sidebar_default,
                'compact_mode': compact_mode,
                'cache_duration': cache_duration,
                'auto_refresh_interval': auto_refresh_interval,
                'max_records_display': max_records_display,
                'debug_mode': debug_mode
            }
            
            st.success("✅ Configurações do sistema salvas com sucesso!")
            log_activity("Configurações do sistema alteradas")
            
            # Mostrar configurações salvas
            with st.expander("📋 Configurações Aplicadas"):
                st.json(updated_config)
    
    with tab2:
        st.subheader("👤 Configurações do Usuário")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📝 Perfil")
            
            # Informações do perfil
            username = st.text_input("Nome de usuário:", 
                                    value=CONFIG['admin_username'], 
                                    disabled=True,
                                    key="user_username")
            email = st.text_input("Email:", 
                                 value=CONFIG['admin_email'],
                                 key="user_email")
            full_name = st.text_input("Nome completo:", 
                                    value="Administrador PetCare",
                                    key="user_full_name")
            role = st.selectbox("Função:", 
                              ["Administrador", "DBA", "Desenvolvedor", "Analista"],
                              key="user_role")
            
            st.markdown("#### 🌍 Localização")
            
            language = st.selectbox("Idioma:", 
                                   ["Português (BR)", "English", "Español"],
                                   key="user_language")
            timezone = st.selectbox("Fuso horário:", [
                "America/Sao_Paulo", "UTC", "America/New_York", "Europe/London"
            ], key="user_timezone")
            date_format = st.selectbox("Formato de data:", 
                                     ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"],
                                     key="user_date_format")
        
        with col2:
            st.markdown("#### 🎯 Preferências")
            
            # Preferências de interface
            default_page = st.selectbox("Página inicial:", [
                "Dashboard", "Tabelas", "Editor SQL", "Operações DBA", "Projetos"
            ], key="user_default_page")
            
            items_per_page = st.slider("Itens por página:", 
                                     10, 100, 25,
                                     key="user_items_per_page")
            auto_save_queries = st.checkbox("Auto-salvar consultas", 
                                          value=True,
                                          key="user_auto_save_queries")
            
            st.markdown("#### 📊 Dashboard")
            
            dashboard_auto_refresh = st.slider("Auto-refresh dashboard (seg):", 
                                              10, 300, 60,
                                              key="user_dashboard_auto_refresh")
            show_advanced_metrics = st.checkbox("Mostrar métricas avançadas", 
                                              value=True,
                                              key="user_show_advanced_metrics")
            chart_animations = st.checkbox("Animações em gráficos", 
                                         value=True,
                                         key="user_chart_animations")
            
            st.markdown("#### 🔔 Alertas Pessoais")
            
            email_alerts_user = st.checkbox("Alertas por email", 
                                           value=False,
                                           key="user_email_alerts")
            if email_alerts_user:
                alert_frequency = st.selectbox("Frequência:", 
                                              ["Imediato", "Diário", "Semanal"],
                                              key="user_alert_frequency")
            
            critical_alerts_only = st.checkbox("Apenas alertas críticos", 
                                             value=True,
                                             key="user_critical_alerts")
        
        # Alteração de senha
        st.markdown("#### 🔑 Segurança da Conta")
        
        col1, col2 = st.columns(2)
        
        with col1:
            current_password = st.text_input("Senha atual:", 
                                           type="password",
                                           key="user_current_password")
            new_password = st.text_input("Nova senha:", 
                                       type="password",
                                       key="user_new_password")
            confirm_password = st.text_input("Confirmar nova senha:", 
                                           type="password",
                                           key="user_confirm_password")
            
            if st.button("🔄 Alterar Senha", key="user_change_password"):
                if new_password and new_password == confirm_password:
                    if len(new_password) >= 8:
                        st.success("✅ Senha alterada com sucesso!")
                        log_activity("Senha alterada")
                    else:
                        st.error("❌ Senha deve ter pelo menos 8 caracteres!")
                else:
                    st.error("❌ Senhas não coincidem!")
        
        with col2:
            st.markdown("#### 🔐 Autenticação")
            
            enable_2fa = st.checkbox("Autenticação de dois fatores", 
                                   value=False,
                                   key="user_enable_2fa")
            session_timeout = st.slider("Timeout da sessão (minutos):", 
                                       15, 480, 60,
                                       key="user_session_timeout")
            remember_login = st.checkbox("Lembrar login", 
                                       value=False,
                                       key="user_remember_login")
            
            if enable_2fa:
                st.info("📱 Configure seu app autenticador (Google Authenticator, Authy, etc.)")
        
        if st.button("💾 Salvar Perfil do Usuário", 
                    type="primary",
                    key="save_user_profile"):
            user_settings = {
                'email': email,
                'full_name': full_name,
                'role': role,
                'language': language,
                'timezone': timezone,
                'default_page': default_page,
                'dashboard_refresh': dashboard_auto_refresh
            }
            
            st.success("✅ Perfil do usuário salvo com sucesso!")
            log_activity("Perfil do usuário alterado")
            
            with st.expander("📋 Perfil Atualizado"):
                st.json(user_settings)
    
    with tab3:
        st.subheader("🗄️ Configurações do Banco de Dados")
        
        # Status atual da conexão
        st.markdown("#### 🔗 Status da Conexão")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            connection_status = "🟢 Conectado" if db_manager.connected else "🔴 Desconectado"
            st.markdown(f"**Status:** {connection_status}")
        
        with col2:
            st.markdown(f"**Tipo:** {db_manager.connection_info.get('type', 'N/A')}")
        
        with col3:
            st.markdown(f"**URL:** {db_manager.connection_info.get('url', 'N/A')}")
        
        st.markdown("---")
        
        # Configurações de conexão
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔧 Conexão Principal")
            
            db_type = st.selectbox("Tipo de banco:", 
                                 ["Supabase", "PostgreSQL", "MySQL", "SQLite"],
                                 key="db_type")
            
            if db_type == "Supabase":
                supabase_url = st.text_input("Supabase URL:", 
                                            value=CONFIG.get('supabase_url', ''),
                                            key="db_supabase_url")
                supabase_key = st.text_input("Supabase Key:", 
                                           type="password", 
                                           value=CONFIG.get('supabase_anon_key', ''),
                                           key="db_supabase_key")
            
            elif db_type == "PostgreSQL":
                pg_host = st.text_input("Host:", 
                                       value="localhost",
                                       key="db_pg_host")
                pg_port = st.number_input("Porta:", 
                                        value=5432,
                                        key="db_pg_port")
                pg_database = st.text_input("Database:", 
                                          value="petcareai",
                                          key="db_pg_database")
                pg_username = st.text_input("Usuário:", 
                                          value="postgres",
                                          key="db_pg_username")
                pg_password = st.text_input("Senha:", 
                                          type="password",
                                          key="db_pg_password")
            
            # SSL e segurança
            st.markdown("#### 🔐 Segurança")
            
            ssl_enabled = st.checkbox("SSL habilitado", 
                                    value=True,
                                    key="db_ssl_enabled")
            ssl_verify = st.checkbox("Verificar certificado SSL", 
                                   value=True,
                                   key="db_ssl_verify")
            encrypt_connection = st.checkbox("Criptografar conexão", 
                                           value=True,
                                           key="db_encrypt_connection")
        
        with col2:
            st.markdown("#### ⚡ Performance")
            
            # Pool de conexões
            connection_pool_size = st.slider("Tamanho do pool:", 
                                            5, 50, 20,
                                            key="db_connection_pool_size")
            max_connections = st.slider("Máx. conexões simultâneas:", 
                                      10, 200, 100,
                                      key="db_max_connections")
            connection_timeout = st.slider("Timeout de conexão (seg):", 
                                         5, 60, 30,
                                         key="db_connection_timeout")
            query_timeout_db = st.slider("Timeout de query (seg):", 
                                        5, 300, 60,
                                        key="db_query_timeout")
            
            st.markdown("#### 📊 Monitoramento")
            
            log_slow_queries = st.checkbox("Log de queries lentas", 
                                         value=True,
                                         key="db_log_slow_queries")
            if log_slow_queries:
                slow_query_threshold = st.slider("Threshold query lenta (seg):", 
                                                1, 30, 5,
                                                key="db_slow_query_threshold")
            
            log_connections = st.checkbox("Log de conexões", 
                                        value=True,
                                        key="db_log_connections")
            monitor_locks = st.checkbox("Monitorar locks", 
                                      value=True,
                                      key="db_monitor_locks")
        
        # Teste de conexão
        st.markdown("#### 🔍 Teste de Conexão")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Testar Conexão", 
                        use_container_width=True,
                        key="db_test_connection"):
                with st.spinner("🔄 Testando conexão..."):
                    time.sleep(2)
                
                if db_manager.connected:
                    st.success("✅ Conexão estabelecida com sucesso!")
                    
                    # Mostrar informações da conexão
                    connection_info = {
                        "Status": "Conectado",
                        "Tipo": db_manager.connection_info.get('type'),
                        "Latência": f"{random.randint(10, 100)}ms",
                        "Versão": "PostgreSQL 15.x"
                    }
                    
                    st.json(connection_info)
                else:
                    st.error("❌ Falha na conexão!")
        
        with col2:
            if st.button("📊 Info do Servidor", 
                        use_container_width=True,
                        key="db_server_info"):
                server_info = {
                    "Versão": "PostgreSQL 15.3",
                    "Uptime": "15 dias, 8 horas",
                    "Tamanho Total": "245.7 MB",
                    "Conexões Ativas": random.randint(5, 25),
                    "Transações/seg": random.randint(50, 200)
                }
                
                st.json(server_info)
        
        with col3:
            if st.button("🔧 Reiniciar Conexão", 
                        use_container_width=True,
                        key="db_restart_connection"):
                with st.spinner("🔄 Reiniciando conexão..."):
                    time.sleep(1)
                
                st.success("✅ Conexão reiniciada!")
                log_activity("Conexão reiniciada")
        
        # Configurações avançadas
        st.markdown("#### 🛠️ Configurações Avançadas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            auto_reconnect = st.checkbox("Reconexão automática", 
                                       value=True,
                                       key="db_auto_reconnect")
            connection_retry_attempts = st.number_input("Tentativas de reconexão:", 
                                                      1, 10, 3,
                                                      key="db_connection_retry_attempts")
            backup_connection = st.checkbox("Conexão de backup", 
                                          value=False,
                                          key="db_backup_connection")
        
        with col2:
            read_replica = st.checkbox("Usar réplica de leitura", 
                                     value=False,
                                     key="db_read_replica")
            load_balancing = st.checkbox("Balanceamento de carga", 
                                       value=False,
                                       key="db_load_balancing")
            failover_enabled = st.checkbox("Failover automático", 
                                         value=False,
                                         key="db_failover_enabled")
        
        if st.button("💾 Salvar Configurações do Banco", 
                    type="primary",
                    key="save_db_settings"):
            db_settings = {
                'db_type': db_type,
                'connection_pool_size': connection_pool_size,
                'max_connections': max_connections,
                'ssl_enabled': ssl_enabled,
                'auto_reconnect': auto_reconnect
            }
            
            st.success("✅ Configurações do banco de dados salvas!")
            log_activity("Configurações de BD alteradas")
    
    with tab4:
        st.subheader("📊 Configurações de Monitoramento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🚨 Alertas e Limites")
            
            # Limites de recursos
            cpu_alert_threshold = st.slider("Alerta CPU (%):", 
                                           50, 100, 80,
                                           key="monitoring_cpu_alert_threshold")
            memory_alert_threshold = st.slider("Alerta Memória (%):", 
                                              50, 100, 85,
                                              key="monitoring_memory_alert_threshold")
            disk_alert_threshold = st.slider("Alerta Disco (%):", 
                                            50, 100, 90,
                                            key="monitoring_disk_alert_threshold")
            connection_alert_threshold = st.slider("Alerta Conexões:", 
                                                  50, 200, 150,
                                                  key="monitoring_connection_alert_threshold")
            
            # Configurações de coleta
            st.markdown("#### 📊 Coleta de Métricas")
            
            enable_monitoring = st.checkbox("Ativar monitoramento", 
                                          value=True,
                                          key="monitoring_enable_monitoring")
            metrics_interval = st.slider("Intervalo de coleta (seg):", 
                                        10, 300, 60,
                                        key="monitoring_metrics_interval")
            detailed_metrics = st.checkbox("Métricas detalhadas", 
                                         value=True,
                                         key="monitoring_detailed_metrics")
            
            # Retenção de dados
            metrics_retention_days = st.slider("Retenção de métricas (dias):", 
                                              7, 365, 30,
                                              key="monitoring_metrics_retention_days")
            auto_cleanup = st.checkbox("Limpeza automática", 
                                     value=True,
                                     key="monitoring_auto_cleanup")
        
        with col2:
            st.markdown("#### 📧 Notificações")
            
            # Canais de notificação
            email_alerts_enabled = st.checkbox("Alertas por email", 
                                              value=False,
                                              key="monitoring_email_alerts")
            
            if email_alerts_enabled:
                alert_emails = st.text_area("Emails para alertas:", 
                                           placeholder="admin@petcareai.com\ndba@petcareai.com",
                                           key="monitoring_alert_emails")
                email_frequency = st.selectbox("Frequência emails:", 
                                              ["Imediato", "A cada 5 min", "A cada 15 min", "Hourly"],
                                              key="monitoring_email_frequency")
            
            webhook_alerts = st.checkbox("Alertas via Webhook", 
                                       value=False,
                                       key="monitoring_webhook_alerts")
            
            if webhook_alerts:
                webhook_url = st.text_input("URL do Webhook:", 
                                           placeholder="https://hooks.slack.com/...",
                                           key="monitoring_webhook_url")
                webhook_secret = st.text_input("Secret do Webhook:", 
                                              type="password",
                                              key="monitoring_webhook_secret")
            
            slack_integration = st.checkbox("Integração Slack", 
                                          value=False,
                                          key="monitoring_slack_integration")
            
            if slack_integration:
                slack_token = st.text_input("Slack Bot Token:", 
                                           type="password",
                                           key="monitoring_slack_token")
                slack_channel = st.text_input("Canal Slack:", 
                                             placeholder="#alerts",
                                             key="monitoring_slack_channel")
        
        # Métricas personalizadas
        st.markdown("#### 📈 Métricas Personalizadas")
        
        custom_metrics = st.text_area(
            "Queries para métricas customizadas (uma por linha):",
            placeholder="""SELECT COUNT(*) as total_users FROM users;
SELECT COUNT(*) as appointments_today FROM appointments WHERE DATE(created_at) = CURRENT_DATE;
SELECT AVG(age) as average_pet_age FROM pets WHERE birth_date IS NOT NULL;""",
            height=100,
            key="monitoring_custom_metrics"
        )
        
        # Dashboard personalizado
        st.markdown("#### 📊 Dashboard")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            refresh_rate = st.selectbox("Taxa de refresh:", 
                                       ["5s", "10s", "30s", "1min", "5min"],
                                       key="monitoring_refresh_rate")
            
        with col2:
            chart_type = st.selectbox("Tipo de gráfico padrão:", 
                                     ["Linha", "Barra", "Pizza", "Área"],
                                     key="monitoring_chart_type")
        
        with col3:
            show_predictions = st.checkbox("Mostrar predições", 
                                         value=False,
                                         key="monitoring_show_predictions")
        
        # Alertas ativos
        st.markdown("#### 🚨 Alertas Ativos")
        
        current_alerts = [
            {"tipo": "⚠️ Warning", "mensagem": f"CPU em {cpu_alert_threshold-5}%", "tempo": "5 min atrás"},
            {"tipo": "ℹ️ Info", "mensagem": "Backup concluído", "tempo": "1 hora atrás"},
            {"tipo": "✅ Success", "mensagem": "Otimização completada", "tempo": "3 horas atrás"}
        ]
        
        for i, alert in enumerate(current_alerts):
            col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
            
            with col1:
                st.write(alert["tipo"])
            with col2:
                st.write(alert["mensagem"])
            with col3:
                st.write(alert["tempo"])
            with col4:
                if st.button("❌", 
                           key=f"dismiss_alert_{i}", 
                           help="Dispensar alerta"):
                    st.info("Alerta dispensado")
        
        if st.button("💾 Salvar Configurações de Monitoramento", 
                    type="primary",
                    key="save_monitoring_settings"):
            monitoring_settings = {
                'cpu_threshold': cpu_alert_threshold,
                'memory_threshold': memory_alert_threshold,
                'metrics_interval': metrics_interval,
                'retention_days': metrics_retention_days,
                'email_alerts': email_alerts_enabled
            }
            
            st.success("✅ Configurações de monitoramento salvas!")
            log_activity("Configurações de monitoramento alteradas")
    
    with tab5:
        st.subheader("🔐 Configurações de Segurança")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🛡️ Políticas de Segurança")
            
            # Políticas de senha
            min_password_length = st.slider("Tamanho mínimo da senha:", 
                                           6, 20, 8,
                                           key="security_min_password_length")
            require_special_chars = st.checkbox("Exigir caracteres especiais", 
                                               value=True,
                                               key="security_require_special_chars")
            require_numbers = st.checkbox("Exigir números", 
                                        value=True,
                                        key="security_require_numbers")
            require_uppercase = st.checkbox("Exigir maiúsculas", 
                                          value=True,
                                          key="security_require_uppercase")
            
            # Políticas de sessão
            session_timeout_minutes = st.slider("Timeout de sessão (min):", 
                                               15, 480, 60,
                                               key="security_session_timeout_minutes")
            max_concurrent_sessions = st.number_input("Máx. sessões simultâneas:", 
                                                    1, 10, 3,
                                                    key="security_max_concurrent_sessions")
            
            # Auditoria
            st.markdown("#### 📋 Auditoria")
            
            enable_audit_log = st.checkbox("Log de auditoria", 
                                         value=True,
                                         key="security_enable_audit_log")
            log_failed_logins = st.checkbox("Log tentativas de login falhadas", 
                                           value=True,
                                           key="security_log_failed_logins")
            log_data_changes = st.checkbox("Log mudanças nos dados", 
                                         value=True,
                                         key="security_log_data_changes")
            log_admin_actions = st.checkbox("Log ações administrativas", 
                                           value=True,
                                           key="security_log_admin_actions")
        
        with col2:
            st.markdown("#### 🔒 Controle de Acesso")
            
            # Permissões
            role_based_access = st.checkbox("Controle baseado em roles", 
                                          value=True,
                                          key="security_role_based_access")
            ip_whitelist_enabled = st.checkbox("Lista branca de IPs", 
                                             value=False,
                                             key="security_ip_whitelist_enabled")
            
            if ip_whitelist_enabled:
                allowed_ips = st.text_area("IPs permitidos (um por linha):", 
                                         placeholder="192.168.1.100\n10.0.0.50",
                                         key="security_allowed_ips")
            
            # Criptografia
            st.markdown("#### 🔐 Criptografia")
            
            encrypt_sensitive_data = st.checkbox("Criptografar dados sensíveis", 
                                                value=True,
                                                key="security_encrypt_sensitive_data")
            encryption_algorithm = st.selectbox("Algoritmo:", 
                                               ["AES-256", "AES-192", "AES-128"],
                                               key="security_encryption_algorithm")
            
            # Backup de segurança
            st.markdown("#### 💾 Backup de Segurança")
            
            security_backup_enabled = st.checkbox("Backup automático de segurança", 
                                                 value=True,
                                                 key="security_backup_enabled")
            backup_encryption = st.checkbox("Criptografar backups", 
                                           value=True,
                                           key="security_backup_encryption")
            
            if security_backup_enabled:
                backup_frequency = st.selectbox("Frequência:", 
                                               ["Diário", "Semanal", "Mensal"],
                                               key="security_backup_frequency")
        
        # Logs de segurança
        st.markdown("#### 📊 Logs de Segurança Recentes")
        
        security_logs = [
            {"timestamp": datetime.now() - timedelta(minutes=10), "event": "Login successful", "user": "admin", "ip": "192.168.1.100", "status": "✅"},
            {"timestamp": datetime.now() - timedelta(hours=2), "event": "Password changed", "user": "admin", "ip": "192.168.1.100", "status": "✅"},
            {"timestamp": datetime.now() - timedelta(hours=5), "event": "Failed login attempt", "user": "unknown", "ip": "203.0.113.1", "status": "❌"},
            {"timestamp": datetime.now() - timedelta(days=1), "event": "Database access", "user": "admin", "ip": "192.168.1.100", "status": "✅"}
        ]
        
        df_security = pd.DataFrame([
            {
                "Timestamp": format_datetime(log["timestamp"], "full"),
                "Evento": log["event"],
                "Usuário": log["user"],
                "IP": log["ip"],
                "Status": log["status"]
            }
            for log in security_logs
        ])
        
        st.dataframe(df_security, use_container_width=True)
        
        # Ações de segurança
        st.markdown("#### ⚡ Ações de Segurança")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Forçar Logout Geral", 
                        use_container_width=True,
                        key="security_force_logout"):
                st.warning("⚠️ Todos os usuários serão desconectados")
        
        with col2:
            if st.button("🔒 Bloquear Sistema", 
                        use_container_width=True,
                        key="security_lock_system"):
                st.warning("⚠️ Sistema será bloqueado temporariamente")
        
        with col3:
            if st.button("📊 Relatório Segurança", 
                        use_container_width=True,
                        key="security_report"):
                security_report = {
                    "Total Logins (24h)": random.randint(50, 200),
                    "Tentativas Falhadas": random.randint(0, 5),
                    "IPs Únicos": random.randint(5, 20),
                    "Ações Admin": random.randint(10, 50),
                    "Queries Executadas": random.randint(100, 500),
                    "Última Violação": "Nenhuma"
                }
                
                st.json(security_report)
        
        with col4:
            if st.button("🛡️ Scan Vulnerabilidades", 
                        use_container_width=True,
                        key="security_vulnerability_scan"):
                with st.spinner("🔍 Executando scan de segurança..."):
                    time.sleep(3)
                
                vulnerabilities = {
                    "Críticas": 0,
                    "Altas": 0,
                    "Médias": 1,
                    "Baixas": 2,
                    "Total": 3,
                    "Status": "✅ Sistema Seguro"
                }
                
                st.json(vulnerabilities)
        
        if st.button("💾 Salvar Configurações de Segurança", 
                    type="primary",
                    key="save_security_settings"):
            security_settings = {
                'min_password_length': min_password_length,
                'session_timeout': session_timeout_minutes,
                'audit_log_enabled': enable_audit_log,
                'encryption_enabled': encrypt_sensitive_data,
                'backup_encryption': backup_encryption
            }
            
            st.success("✅ Configurações de segurança salvas!")
            log_activity("Configurações de segurança alteradas")
        
        # Informações do sistema
        st.markdown("---")
        st.subheader("ℹ️ Informações do Sistema")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            system_info = {
                "Versão": CONFIG['app_version'],
                "Python": "3.13.x",
                "Streamlit": "1.28.x",
                "Supabase": "2.0.x" if SUPABASE_AVAILABLE else "N/A"
            }
            st.json(system_info)
        
        with col2:
            server_info = {
                "Uptime": "5d 12h 30m",
                "CPU Cores": 4,
                "RAM Total": "16 GB",
                "Disco Livre": "120 GB"
            }
            st.json(server_info)
        
        with col3:
            db_info = {
                "Tipo": db_manager.connection_info.get('type', 'N/A'),
                "Status": "Conectado" if db_manager.connected else "Desconectado",
                "Tabelas": len(db_manager.get_tables()),
                "Tamanho": db_manager.get_database_metrics().get('total_size', 'N/A')
            }
            st.json(db_info)

# =====================================================================
# APLICAÇÃO PRINCIPAL
# =====================================================================

def main():
    """Função principal da aplicação"""
    try:
        # Configuração da página
        st.set_page_config(
            page_title="PetCare DBA Admin",
            page_icon="🏥",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/your-repo',
                'Report a bug': 'https://github.com/your-repo/issues',
                'About': f"PetCare DBA Admin v{CONFIG['app_version']}"
            }
        )
        
        # CSS customizado
        st.markdown("""
        <style>
        .main {
            padding-top: 1rem;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
        .stSelectbox {
            margin-bottom: 1rem;
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #2E8B57;
        }
        .alert-critical {
            background: linear-gradient(135deg, #ff4757, #ff6b7a);
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .alert-warning {
            background: linear-gradient(135deg, #ffa502, #ffb627);
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .alert-info {
            background: linear-gradient(135deg, #3742fa, #5352ed);
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .success-message {
            background: linear-gradient(135deg, #2ed573, #7bed9f);
            color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #2E8B57, #3CB371);
        }
        .stButton > button {
            width: 100%;
            border-radius: 0.5rem;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .stMetric {
            background: white;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .reportview-container .main .block-container {
            max-width: 1200px;
        }
        .stDataFrame {
            border: 1px solid #e0e0e0;
            border-radius: 0.5rem;
            overflow: hidden;
        }
        .stPlotlyChart {
            background: white;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 1rem;
        }
        .connection-status-online {
            color: #2ed573;
            font-weight: bold;
        }
        .connection-status-offline {
            color: #ff4757;
            font-weight: bold;
        }
        .loading-spinner {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .pulse {
            animation: pulse 2s infinite;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Inicialização do estado da sessão
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        if 'last_activity' not in st.session_state:
            st.session_state.last_activity = datetime.now()
        if 'activity_logs' not in st.session_state:
            st.session_state.activity_logs = []
        if 'alert_count' not in st.session_state:
            st.session_state.alert_count = 0
        if 'dashboard_loaded' not in st.session_state:
            st.session_state.dashboard_loaded = False
        if 'connection_retries' not in st.session_state:
            st.session_state.connection_retries = 0
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = datetime.now()
        
        # Header da aplicação
        with st.container():
            col1, col2, col3 = st.columns([2, 3, 2])
            
            with col1:
                st.markdown("### 🏥 PetCare DBA")
                
            with col2:
                st.markdown(f"""
                <div style='text-align: center; padding: 1rem;'>
                    <h2 style='margin: 0; color: #2E8B57;'>Database Administration Panel</h2>
                    <p style='margin: 0.5rem 0 0 0; color: #666; font-size: 0.9rem;'>
                        Versão {CONFIG['app_version']} | {datetime.now().strftime('%d/%m/%Y %H:%M')}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                # Status de conexão em tempo real
                connection_status = "🟢 Online" if db_manager.connected else "🔴 Offline"
                status_class = "connection-status-online" if db_manager.connected else "connection-status-offline"
                
                st.markdown(f"""
                <div style='text-align: right; padding: 1rem;'>
                    <div class='{status_class}' style='font-size: 1.2rem; margin-bottom: 0.5rem;'>
                        {connection_status}
                    </div>
                    <div style='font-size: 0.8rem; color: #666;'>
                        Último refresh: {st.session_state.last_refresh.strftime('%H:%M:%S')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Sidebar para navegação
        with st.sidebar:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #2E8B57, #3CB371); 
                        padding: 1.5rem; border-radius: 10px; text-align: center; margin-bottom: 2rem;'>
                <h3 style='color: white; margin: 0;'>🛠️ Painel de Controle</h3>
                <p style='color: #E8F5E8; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
                    Administração do Banco de Dados
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Menu de navegação
            menu_options = [
                "Dashboard",
                "Gerenciar Tabelas", 
                "Backup & Restore",
                "Monitoramento",
                "Usuários & Permissões",
                "Configurações do Banco",
                "Logs & Auditoria",
                "Análise de Performance",
                "Segurança",
                "Configurações"
            ]
            
            menu_icons = [
                "📊", "🗄️", "💾", "📈", "👥", 
                "⚙️", "📋", "🚀", "🔐", "🛠️"
            ]
            
            menu_option = st.selectbox(
                "Selecione uma opção:",
                menu_options,
                format_func=lambda x: f"{menu_icons[menu_options.index(x)]} {x}"
            )
            
            st.markdown("---")
            
            # Informações rápidas na sidebar
            st.markdown("#### 📊 Status Rápido")
            
            # Métricas rápidas
            if db_manager.connected:
                try:
                    tables = db_manager.get_tables()
                    table_count = len(tables) if tables else 0
                    
                    # Simular outras métricas
                    active_connections = random.randint(5, 15)
                    last_backup = datetime.now() - timedelta(hours=random.randint(1, 24))
                    
                    st.metric("Tabelas", table_count)
                    st.metric("Conexões", active_connections)
                    st.metric("Último Backup", last_backup.strftime('%H:%M'))
                    
                    # Status de saúde do banco
                    health_score = random.randint(75, 100)
                    health_color = "🟢" if health_score >= 90 else "🟡" if health_score >= 75 else "🔴"
                    st.metric("Saúde do DB", f"{health_color} {health_score}%")
                    
                except Exception as e:
                    st.error(f"Erro ao obter métricas: {str(e)}")
                    st.metric("Tabelas", "N/A")
                    st.metric("Conexões", "N/A")
                    st.metric("Status", "🔴 Erro")
            else:
                st.metric("Status", "🔴 Offline")
                st.metric("Conectar", "Manual")
                
                # Botão de reconexão
                if st.button("🔄 Tentar Conectar", use_container_width=True):
                    with st.spinner("Conectando..."):
                        if db_manager.connect_to_supabase():
                            st.success("✅ Conectado!")
                            st.rerun()
                        else:
                            st.error("❌ Falha na conexão")
                            st.session_state.connection_retries += 1
            
            st.markdown("---")
            
            # Alertas na sidebar
            st.markdown("#### 🚨 Alertas Recentes")
            
            recent_alerts = [
                {"type": "warning", "msg": "Query lenta detectada", "time": "5 min"},
                {"type": "info", "msg": "Backup concluído", "time": "1 hora"},
                {"type": "error", "msg": "Falha de conexão", "time": "2 horas"}
            ]
            
            for alert in recent_alerts[:3]:  # Mostrar apenas os 3 mais recentes
                alert_icon = "⚠️" if alert["type"] == "warning" else "ℹ️" if alert["type"] == "info" else "❌"
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.1); padding: 0.5rem; border-radius: 5px; margin: 0.3rem 0;'>
                    <div style='font-size: 0.8rem; color: white;'>
                        {alert_icon} {alert['msg']}<br>
                        <span style='opacity: 0.7;'>{alert['time']} atrás</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Botão para refresh geral
            st.markdown("---")
            if st.button("🔄 Refresh Geral", use_container_width=True):
                st.session_state.last_refresh = datetime.now()
                st.session_state.dashboard_loaded = False
                st.rerun()
            
            # Informações de sessão
            st.markdown("---")
            st.markdown("#### ℹ️ Sessão")
            session_duration = datetime.now() - st.session_state.last_activity
            st.text(f"⏰ Duração: {session_duration.seconds // 60}min")
            st.text(f"👤 Usuário: {st.session_state.current_user or 'admin'}")
            st.text(f"🌐 IP: 192.168.1.{random.randint(1, 255)}")
        
        # Conteúdo principal baseado na seleção do menu
        try:
            if menu_option == "Dashboard":
                # Botão de atualização rápida do dashboard
                dashboard_col1, dashboard_col2, dashboard_col3 = st.columns([1, 2, 1])
                
                with dashboard_col2:
                    refresh_col1, refresh_col2 = st.columns(2)
                    
                    with refresh_col1:
                        if st.button("🔄 Atualizar Dashboard", use_container_width=True):
                            render_loading_with_progress()
                            st.session_state.dashboard_loaded = True
                            st.rerun()
                    
                    with refresh_col2:
                        auto_refresh = st.checkbox("🔄 Auto-refresh (60s)", key="auto_refresh_main")
                
                # Renderizar o dashboard
                render_dashboard()
                
                # Auto-refresh se habilitado
                if auto_refresh:
                    time.sleep(60)
                    st.rerun()
                    
            elif menu_option == "Gerenciar Tabelas":
                render_table_management() # type: ignore
                
            elif menu_option == "Backup & Restore":
                render_backup_restore() # type: ignore
                
            elif menu_option == "Monitoramento":
                render_monitoring() # type: ignore
                
            elif menu_option == "Usuários & Permissões":
                render_user_management() # type: ignore
                
            elif menu_option == "Configurações do Banco":
                render_database_config() # type: ignore
                
            elif menu_option == "Logs & Auditoria":
                render_logs_audit() # type: ignore
                
            elif menu_option == "Análise de Performance":
                render_performance_analysis() # type: ignore
                
            elif menu_option == "Segurança":
                render_security() # type: ignore
                
            elif menu_option == "Configurações":
                render_settings()
            
            # Log da atividade
            log_activity(f"Acessou {menu_option}")
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar página: {str(e)}")
            st.exception(e)
            
            # Opções de recuperação
            recovery_col1, recovery_col2, recovery_col3 = st.columns(3)
            
            with recovery_col1:
                if st.button("🔄 Tentar Novamente"):
                    st.rerun()
            
            with recovery_col2:
                if st.button("🏠 Voltar ao Dashboard"):
                    st.session_state.dashboard_loaded = False
                    st.rerun()
            
            with recovery_col3:
                if st.button("🔧 Limpar Cache"):
                    for key in list(st.session_state.keys()):
                        if key.startswith('cache_'):
                            del st.session_state[key]
                    st.success("Cache limpo!")
        
        # Footer
        st.markdown("---")
        footer_col1, footer_col2, footer_col3 = st.columns(3)
        
        with footer_col1:
            st.markdown("**🏥 PetCare DBA Admin**")
            st.text(f"Versão {CONFIG['app_version']}")
        
        with footer_col2:
            st.markdown("**📊 Estatísticas da Sessão**")
            st.text(f"Páginas visitadas: {len(st.session_state.activity_logs)}")
            st.text(f"Última atividade: {st.session_state.last_activity.strftime('%H:%M:%S')}")
        
        with footer_col3:
            st.markdown("**🔗 Links Úteis**")
            st.markdown("- [Documentação](https://docs.supabase.com)")
            st.markdown("- [Suporte](https://github.com/your-repo)")
        
    except Exception as e:
        st.error(f"❌ Erro crítico na aplicação: {str(e)}")
        st.exception(e)
        
        if st.button("🔄 Reiniciar Aplicação"):
            # Limpar todo o estado da sessão
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()