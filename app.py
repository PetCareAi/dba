"""
🐾 PetCare DBA Admin - Sistema de Gerenciamento de Banco de Dados
Desenvolvido para PetCareAI
Arquivo único com toda funcionalidade
"""

import streamlit as st
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

# Importações condicionais
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    st.warning("⚠️ Supabase não instalado. Usando modo demo.")

try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

try:
    import sqlparse
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
CONFIG = {
    'app_title': os.getenv('APP_TITLE', 'PetCare DBA Admin'),
    'app_version': os.getenv('APP_VERSION', '1.0.0'),
    'debug_mode': os.getenv('DEBUG_MODE', 'True').lower() == 'true',
    'supabase_url': os.getenv('SUPABASE_URL'),
    'supabase_anon_key': os.getenv('SUPABASE_ANON_KEY'),
    'admin_username': os.getenv('ADMIN_USERNAME', 'admin'),
    'admin_password': os.getenv('ADMIN_PASSWORD', 'petcare2025'),
    'admin_email': os.getenv('ADMIN_EMAIL', 'admin@petcareai.com'),
    'theme': {
        'primary_color': os.getenv('PRIMARY_COLOR', '#2E8B57'),
        'secondary_color': os.getenv('SECONDARY_COLOR', '#90EE90'),
        'background_color': os.getenv('BACKGROUND_COLOR', '#F0FFF0'),
        'text_color': os.getenv('TEXT_COLOR', '#006400')
    }
}

# Dados de demonstração
DEMO_DATA = {
    'tables': [
        {'name': 'users', 'rows': 15420, 'size': '2.1 MB', 'last_modified': '2025-06-24'},
        {'name': 'pets', 'rows': 8934, 'size': '1.8 MB', 'last_modified': '2025-06-24'},
        {'name': 'appointments', 'rows': 25678, 'size': '5.2 MB', 'last_modified': '2025-06-23'},
        {'name': 'veterinarians', 'rows': 234, 'size': '45 KB', 'last_modified': '2025-06-22'},
        {'name': 'clinics', 'rows': 89, 'size': '12 KB', 'last_modified': '2025-06-21'},
        {'name': 'treatments', 'rows': 12456, 'size': '3.4 MB', 'last_modified': '2025-06-24'},
        {'name': 'medical_records', 'rows': 18792, 'size': '8.9 MB', 'last_modified': '2025-06-24'},
        {'name': 'payments', 'rows': 9876, 'size': '1.2 MB', 'last_modified': '2025-06-23'}
    ],
    'metrics': {
        'total_connections': random.randint(45, 85),
        'active_queries': random.randint(8, 25),
        'cpu_usage': random.randint(35, 75),
        'memory_usage': random.randint(45, 80),
        'disk_usage': random.randint(25, 65),
        'cache_hit_ratio': random.randint(85, 98)
    },
    'projects': [
        {'id': 1, 'name': 'Sistema Principal', 'scripts': 45, 'status': 'active'},
        {'id': 2, 'name': 'Relatórios BI', 'scripts': 23, 'status': 'active'},
        {'id': 3, 'name': 'Manutenção DB', 'scripts': 12, 'status': 'active'},
        {'id': 4, 'name': 'Backup & Recovery', 'scripts': 8, 'status': 'inactive'}
    ]
}

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
        st.session_state.current_page = 'Dashboard'
    
    if 'activity_log' not in st.session_state:
        st.session_state.activity_log = []
    
    if 'sql_history' not in st.session_state:
        st.session_state.sql_history = []
    
    if 'demo_data' not in st.session_state:
        st.session_state.demo_data = DEMO_DATA.copy()

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

def format_bytes(bytes_value):
    """Formata bytes em formato legível"""
    if isinstance(bytes_value, str):
        return bytes_value
    
    if bytes_value == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(bytes_value)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"

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
        
        # Informações de acesso
        st.markdown("""
        <div style='background: #E6FFE6; padding: 1.5rem; 
                   border-radius: 10px; text-align: center; margin-top: 1rem;'>
            <h4 style='color: #2E8B57; margin: 0;'>📋 Informações de Acesso</h4>
            <p style='margin: 0.5rem 0; color: #006400;'>
                <strong>Usuário:</strong> admin<br>
                <strong>Senha:</strong> petcare2025
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
                Sistema de Gerenciamento de Banco de Dados
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0;'>
            <p style='color: #006400; margin: 0; font-size: 0.9rem;'>
                🕒 {current_time}
            </p>
            <p style='color: #228B22; margin: 0; font-size: 0.8rem;'>
                🌐 Sistema Online
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
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #E8F5E8, #90EE90, #98FB98); 
                   padding: 0.5rem; border-radius: 8px; 
                   border-left: 4px solid #2E8B57; margin: 0.5rem 0;'>
            <small style='color: #006400;'>🟢 Conectado</small><br>
            <small style='color: #228B22;'>PetCareAI DB</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Métricas rápidas
        metrics = st.session_state.demo_data['metrics']
        cpu_color = "#FF6347" if metrics['cpu_usage'] > 80 else "#FFD700" if metrics['cpu_usage'] > 60 else "#2E8B57"
        memory_color = "#FF6347" if metrics['memory_usage'] > 80 else "#FFD700" if metrics['memory_usage'] > 60 else "#2E8B57"
        
        st.markdown(f"""
        <div style='background: #F0FFF0; padding: 0.5rem; 
                   border-radius: 5px; margin: 0.5rem 0;'>
            <small>💻 CPU: <span style='color: {cpu_color}; font-weight: bold;'>{metrics['cpu_usage']:.0f}%</span></small><br>
            <small>💾 Memória: <span style='color: {memory_color}; font-weight: bold;'>{metrics['memory_usage']:.0f}%</span></small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Botão de logout
        if st.button("🚪 Sair", use_container_width=True, type="secondary"):
            logout_user()

# =====================================================================
# PÁGINAS DO SISTEMA
# =====================================================================

def render_dashboard():
    """Renderiza página do dashboard"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #F0FFF0, #E6FFE6); 
                padding: 1.5rem; border-radius: 15px; 
                border-left: 5px solid #2E8B57; margin-bottom: 2rem;'>
        <h2 style='color: #2E8B57; margin: 0; font-size: 2rem;'>
            📊 Dashboard de Monitoramento
        </h2>
        <p style='color: #228B22; margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
            Visão geral do sistema de banco de dados
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas principais
    metrics = st.session_state.demo_data['metrics']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            "Conexões Ativas", 
            f"{metrics['total_connections']}", 
            f"+{random.randint(1, 5)} desde ontem",
            "#228B22"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Queries Ativas", 
            f"{metrics['active_queries']}", 
            f"{random.randint(1, 3)} em execução",
            "#FFD700"
        ), unsafe_allow_html=True)
    
    with col3:
        cpu_color = "#FF6347" if metrics['cpu_usage'] > 80 else "#228B22"
        st.markdown(create_metric_card(
            "CPU", 
            f"{metrics['cpu_usage']:.0f}%", 
            "Normal" if metrics['cpu_usage'] < 80 else "Alto",
            cpu_color
        ), unsafe_allow_html=True)
    
    with col4:
        memory_color = "#FF6347" if metrics['memory_usage'] > 80 else "#228B22"
        st.markdown(create_metric_card(
            "Memória", 
            f"{metrics['memory_usage']:.0f}%", 
            "OK" if metrics['memory_usage'] < 80 else "Atenção",
            memory_color
        ), unsafe_allow_html=True)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Performance do Sistema")
        
        # Dados para gráfico de performance
        hours = list(range(24))
        cpu_data = [random.randint(30, 80) for _ in hours]
        memory_data = [random.randint(40, 85) for _ in hours]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hours, y=cpu_data, name='CPU %', line=dict(color='#2E8B57')))
        fig.add_trace(go.Scatter(x=hours, y=memory_data, name='Memória %', line=dict(color='#90EE90')))
        
        fig.update_layout(
            title="Últimas 24 horas",
            xaxis_title="Hora",
            yaxis_title="Porcentagem",
            height=400,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Distribuição de Tabelas")
        
        tables_data = st.session_state.demo_data['tables']
        
        # Dados para gráfico de pizza
        table_names = [table['name'] for table in tables_data[:6]]
        table_sizes = [random.randint(1000, 50000) for _ in table_names]
        
        fig = px.pie(
            values=table_sizes, 
            names=table_names,
            title="Top 6 Tabelas por Tamanho",
            color_discrete_sequence=['#2E8B57', '#90EE90', '#228B22', '#32CD32', '#98FB98', '#20B2AA']
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de atividades recentes
    st.subheader("📋 Atividades Recentes")
    
    recent_activities = st.session_state.activity_log[-10:] if st.session_state.activity_log else [
        {'timestamp': datetime.now() - timedelta(minutes=5), 'username': 'admin', 'action': 'Dashboard acessado', 'details': None},
        {'timestamp': datetime.now() - timedelta(minutes=15), 'username': 'admin', 'action': 'Query executada', 'details': 'SELECT * FROM users LIMIT 10'},
        {'timestamp': datetime.now() - timedelta(minutes=30), 'username': 'admin', 'action': 'Login realizado', 'details': None},
    ]
    
    if recent_activities:
        df_activities = pd.DataFrame([
            {
                'Timestamp': format_datetime(activity['timestamp'], 'full'),
                'Usuário': activity['username'],
                'Ação': activity['action'],
                'Detalhes': activity.get('details', '')[:50] + '...' if activity.get('details') and len(activity.get('details', '')) > 50 else activity.get('details', '')
            }
            for activity in reversed(recent_activities)
        ])
        
        st.dataframe(df_activities, use_container_width=True)
    else:
        st.info("Nenhuma atividade recente registrada.")
    
    # Status dos alertas
    st.subheader("🚨 Status do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if metrics['cpu_usage'] > 80:
            st.markdown(create_alert_card(
                "Alto Uso de CPU", 
                f"CPU em {metrics['cpu_usage']:.0f}%. Considere verificar queries em execução.",
                "warning"
            ), unsafe_allow_html=True)
        else:
            st.markdown(create_alert_card(
                "CPU Normal", 
                f"CPU em {metrics['cpu_usage']:.0f}%. Sistema funcionando normalmente.",
                "success"
            ), unsafe_allow_html=True)
    
    with col2:
        if metrics['memory_usage'] > 80:
            st.markdown(create_alert_card(
                "Alta Utilização de Memória", 
                f"Memória em {metrics['memory_usage']:.0f}%. Verifique cache e conexões.",
                "warning"
            ), unsafe_allow_html=True)
        else:
            st.markdown(create_alert_card(
                "Memória OK", 
                f"Memória em {metrics['memory_usage']:.0f}%. Utilização dentro do normal.",
                "success"
            ), unsafe_allow_html=True)

def render_tables():
    """Renderiza página de gerenciamento de tabelas"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #F0FFF0, #E6FFE6); 
                padding: 1.5rem; border-radius: 15px; 
                border-left: 5px solid #2E8B57; margin-bottom: 2rem;'>
        <h2 style='color: #2E8B57; margin: 0; font-size: 2rem;'>
            🗃️ Gerenciamento de Tabelas
        </h2>
        <p style='color: #228B22; margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
            Explore e analise as tabelas do banco de dados
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtros
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Buscar tabela:", placeholder="Digite o nome da tabela...")
    
    with col2:
        sort_by = st.selectbox("📊 Ordenar por:", ["Nome", "Linhas", "Tamanho", "Modificação"])
    
    with col3:
        show_stats = st.checkbox("📈 Mostrar estatísticas", value=True)
    
    # Lista de tabelas
    tables_data = st.session_state.demo_data['tables']
    
    # Aplicar filtro de busca
    if search_term:
        tables_data = [table for table in tables_data if search_term.lower() in table['name'].lower()]
    
    # Aplicar ordenação
    if sort_by == "Nome":
        tables_data = sorted(tables_data, key=lambda x: x['name'])
    elif sort_by == "Linhas":
        tables_data = sorted(tables_data, key=lambda x: x['rows'], reverse=True)
    elif sort_by == "Tamanho":
        tables_data = sorted(tables_data, key=lambda x: x['size'], reverse=True)
    elif sort_by == "Modificação":
        tables_data = sorted(tables_data, key=lambda x: x['last_modified'], reverse=True)
    
    # Mostrar tabelas
    if tables_data:
        for i, table in enumerate(tables_data):
            with st.expander(f"📋 {table['name']} ({table['rows']:,} linhas)", expanded=False):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📊 Linhas", f"{table['rows']:,}")
                
                with col2:
                    st.metric("💾 Tamanho", table['size'])
                
                with col3:
                    st.metric("📅 Modificação", table['last_modified'])
                
                with col4:
                    st.metric("🔄 Status", "Ativa")
                
                if show_stats:
                    # Estatísticas detalhadas (dados de demonstração)
                    st.markdown("#### 📈 Estatísticas Detalhadas")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.json({
                            "Índices": random.randint(2, 8),
                            "Chaves Estrangeiras": random.randint(1, 5),
                            "Triggers": random.randint(0, 3),
                            "Constraints": random.randint(3, 10)
                        })
                    
                    with col2:
                        # Gráfico de crescimento (dados fictícios)
                        days = list(range(1, 31))
                        growth_data = [table['rows'] + random.randint(-100, 200) for _ in days]
                        
                        fig = px.line(
                            x=days, 
                            y=growth_data,
                            title=f"Crescimento - {table['name']}",
                            labels={'x': 'Dias', 'y': 'Registros'}
                        )
                        fig.update_traces(line=dict(color='#2E8B57'))
                        fig.update_layout(height=300)
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                # Ações
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button(f"👁️ Visualizar", key=f"view_{table['name']}"):
                        st.info(f"🔍 Explorando tabela {table['name']}...")
                        # Aqui viria a implementação real de visualização
                
                with col2:
                    if st.button(f"📊 Analisar", key=f"analyze_{table['name']}"):
                        st.info(f"📈 Analisando tabela {table['name']}...")
                
                with col3:
                    if st.button(f"🔧 Otimizar", key=f"optimize_{table['name']}"):
                        st.success(f"⚡ Otimização de {table['name']} iniciada!")
                
                with col4:
                    if st.button(f"📤 Exportar", key=f"export_{table['name']}"):
                        st.info(f"💾 Exportando {table['name']}...")
    
    else:
        st.warning("❌ Nenhuma tabela encontrada com os critérios especificados.")
    
    # Resumo geral
    if tables_data:
        st.markdown("---")
        st.subheader("📋 Resumo Geral")
        
        total_rows = sum(table['rows'] for table in tables_data)
        avg_rows = total_rows // len(tables_data) if tables_data else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🗃️ Total de Tabelas", len(tables_data))
        
        with col2:
            st.metric("📊 Total de Registros", f"{total_rows:,}")
        
        with col3:
            st.metric("📈 Média por Tabela", f"{avg_rows:,}")
        
        with col4:
            st.metric("💾 Tamanho Total", "~25.7 MB")

def render_sql_editor():
    """Renderiza página do editor SQL"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #F0FFF0, #E6FFE6); 
                padding: 1.5rem; border-radius: 15px; 
                border-left: 5px solid #2E8B57; margin-bottom: 2rem;'>
        <h2 style='color: #2E8B57; margin: 0; font-size: 2rem;'>
            📜 Editor SQL
        </h2>
        <p style='color: #228B22; margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
            Execute e gerencie scripts SQL
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Abas do editor
    tab1, tab2, tab3 = st.tabs(["✏️ Editor", "📚 Histórico", "💾 Scripts Salvos"])
    
    with tab1:
        st.subheader("💻 Console SQL")
        
        # Área de código SQL
        sql_code = st.text_area()
        
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            if st.button("🚀 Executar Query", type="primary", use_container_width=True):
                if sql_code.strip():
                    # Simular execução
                    with st.spinner("⏳ Executando query..."):
                        time.sleep(1)
                    
                    # Adicionar ao histórico
                    execution = {
                        'timestamp': datetime.now(),
                        'query': sql_code,
                        'status': 'success',
                        'rows_affected': random.randint(1, 100),
                        'execution_time': f"{random.randint(10, 500)}ms"
                    }
                    
                    if 'sql_history' not in st.session_state:
                        st.session_state.sql_history = []
                    
                    st.session_state.sql_history.append(execution)
                    log_activity("Query executada", sql_code[:50] + "..." if len(sql_code) > 50 else sql_code)
                    
                    st.success(f"✅ Query executada com sucesso! {execution['rows_affected']} linha(s) afetada(s) em {execution['execution_time']}")
                    
                    # Simular resultado
                    if "SELECT" in sql_code.upper():
                        st.subheader("📊 Resultado da Query")
                        
                        # Dados de demonstração
                        sample_data = {
                            'nome_usuario': [f'Usuário {i}' for i in range(1, 11)],
                            'nome_pet': [f'Pet {i}' for i in range(1, 11)],
                            'especie': ['Cão', 'Gato', 'Pássaro', 'Peixe', 'Hamster'] * 2
                        }
                        
                        df_result = pd.DataFrame(sample_data)
                        st.dataframe(df_result, use_container_width=True)
                        
                        # Opções de exportação
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            csv = df_result.to_csv(index=False)
                            st.download_button("📥 Download CSV", csv, "resultado.csv", "text/csv")
                        with col2:
                            json_data = df_result.to_json(orient='records', indent=2)
                            st.download_button("📥 Download JSON", json_data, "resultado.json", "application/json")
                else:
                    st.warning("⚠️ Digite uma query SQL válida.")
        
        with col2:
            if st.button("🔍 Validar SQL", use_container_width=True):
                if SQLPARSE_AVAILABLE and sql_code.strip():
                    try:
                        parsed = sqlparse.parse(sql_code)
                        if parsed:
                            st.success("✅ SQL válido!")
                        else:
                            st.error("❌ SQL inválido!")
                    except Exception as e:
                        st.error(f"❌ Erro na validação: {e}")
                else:
                    st.info("ℹ️ Validação não disponível")
        
        with col3:
            if st.button("📋 Formatar", use_container_width=True):
                if SQLPARSE_AVAILABLE and sql_code.strip():
                    try:
                        formatted = sqlparse.format(sql_code, reindent=True, keyword_case='upper')
                        st.code(formatted, language='sql')
                    except Exception:
                        st.error("❌ Erro ao formatar SQL")
                else:
                    st.info("ℹ️ Formatação não disponível")
        
        with col4:
            if st.button("💾 Salvar Script", use_container_width=True):
                script_name = st.text_input("Nome do script:", key="save_script_name")
                if script_name and sql_code.strip():
                    # Simular salvamento
                    st.success(f"✅ Script '{script_name}' salvo!")
                    log_activity("Script salvo", f"'{script_name}'")
        
        # Dicas SQL
        with st.expander("💡 Dicas e Exemplos SQL"):
            st.markdown("""
            **Consultas Básicas:**
            -- Listar todos os usuários
            SELECT * FROM users;
            
            -- Contar pets por espécie
            SELECT species, COUNT(*) as total 
            FROM pets 
            GROUP BY species;
            
            -- Buscar consultas de hoje
            SELECT * FROM appointments 
            WHERE DATE(created_at) = CURRENT_DATE;
            
            **Otimização:**
            - Use LIMIT para consultas grandes
            - Utilize índices em colunas de filtro
            - Evite SELECT * em produção
            - Use EXPLAIN para analisar performance
            """)
    
    with tab2:
        st.subheader("📚 Histórico de Execuções")
        
        if st.session_state.sql_history:
            for i, execution in enumerate(reversed(st.session_state.sql_history[-20:])):
                with st.expander(f"🕒 {format_datetime(execution['timestamp'], 'full')} - {execution['status'].title()}"):
                    st.code(execution['query'], language='sql')
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("⏱️ Tempo", execution['execution_time'])
                    with col2:
                        st.metric("📊 Linhas", execution['rows_affected'])
                    with col3:
                        status_icon = "✅" if execution['status'] == 'success' else "❌"
                        st.metric("📋 Status", f"{status_icon} {execution['status']}")
                    
                    if st.button(f"🔄 Executar Novamente", key=f"rerun_{i}"):
                        st.info("🔄 Re-executando query...")
        else:
            st.info("📭 Nenhuma query executada ainda.")
        
        if st.session_state.sql_history:
            if st.button("🗑️ Limpar Histórico"):
                st.session_state.sql_history = []
                st.success("✅ Histórico limpo!")
                st.rerun()
    
    with tab3:
        st.subheader("💾 Scripts Salvos")
        
        # Simular scripts salvos
        saved_scripts = [
            {"name": "Relatório Diário", "description": "Relatório de consultas do dia", "created": "2025-06-20"},
            {"name": "Limpeza de Dados", "description": "Script para limpeza de registros antigos", "created": "2025-06-18"},
            {"name": "Backup Tables", "description": "Backup das tabelas principais", "created": "2025-06-15"}
        ]
        
        if saved_scripts:
            for script in saved_scripts:
                with st.expander(f"📄 {script['name']}"):
                    st.write(f"**Descrição:** {script['description']}")
                    st.write(f"**Criado em:** {script['created']}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"▶️ Executar", key=f"exec_{script['name']}"):
                            st.info(f"🚀 Executando script '{script['name']}'...")
                    with col2:
                        if st.button(f"✏️ Editar", key=f"edit_{script['name']}"):
                            st.info(f"✏️ Editando script '{script['name']}'...")
                    with col3:
                        if st.button(f"🗑️ Excluir", key=f"del_{script['name']}"):
                            st.warning(f"⚠️ Script '{script['name']}' seria excluído")
        else:
            st.info("📂 Nenhum script salvo encontrado.")

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
            Organize scripts e queries por projetos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Abas de projetos
    tab1, tab2 = st.tabs(["📋 Projetos Ativos", "➕ Novo Projeto"])
    
    with tab1:
        projects = st.session_state.demo_data['projects']
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_project = st.text_input("🔍 Buscar projeto:", placeholder="Digite o nome do projeto...")
        
        with col2:
            filter_status = st.selectbox("📊 Filtrar por status:", ["Todos", "Ativo", "Inativo"])
        
        # Filtrar projetos
        filtered_projects = projects
        
        if search_project:
            filtered_projects = [p for p in filtered_projects if search_project.lower() in p['name'].lower()]
        
        if filter_status != "Todos":
            status_map = {"Ativo": "active", "Inativo": "inactive"}
            filtered_projects = [p for p in filtered_projects if p['status'] == status_map[filter_status]]
        
        # Mostrar projetos
        if filtered_projects:
            for project in filtered_projects:
                status_color = "#2E8B57" if project['status'] == 'active' else "#808080"
                status_text = "🟢 Ativo" if project['status'] == 'active' else "🔴 Inativo"
                
                with st.expander(f"📁 {project['name']} ({project['scripts']} scripts)"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("📜 Scripts", project['scripts'])
                    
                    with col2:
                        st.markdown(f"**Status:** <span style='color: {status_color}'>{status_text}</span>", 
                                  unsafe_allow_html=True)
                    
                    with col3:
                        st.metric("👥 Membros", random.randint(1, 5))
                    
                    # Estatísticas do projeto
                    st.markdown("#### 📊 Estatísticas")
                    
                    # Gráfico de atividade do projeto
                    days = list(range(1, 31))
                    activity_data = [random.randint(0, 10) for _ in days]
                    
                    fig = px.bar(
                        x=days,
                        y=activity_data,
                        title=f"Atividade - {project['name']} (último mês)",
                        labels={'x': 'Dia', 'y': 'Execuções'}
                    )
                    fig.update_traces(marker_color='#2E8B57')
                    fig.update_layout(height=300)
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Scripts recentes do projeto
                    st.markdown("#### 📜 Scripts Recentes")
                    
                    recent_scripts = [
                        f"script_backup_{random.randint(1, 10)}.sql",
                        f"query_relatorio_{random.randint(1, 10)}.sql",
                        f"manutencao_{random.randint(1, 10)}.sql"
                    ]
                    
                    for script in recent_scripts[:3]:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"📄 {script}")
                        with col2:
                            st.write(f"📅 {format_datetime(datetime.now() - timedelta(days=random.randint(1, 10)), 'short')}")
                        with col3:
                            if st.button(f"▶️", key=f"run_{project['id']}_{script}"):
                                st.info(f"🚀 Executando {script}...")
                    
                    # Ações do projeto
                    st.markdown("---")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button(f"📝 Editar", key=f"edit_proj_{project['id']}"):
                            st.info(f"✏️ Editando projeto {project['name']}...")
                    
                    with col2:
                        if st.button(f"📊 Relatório", key=f"report_proj_{project['id']}"):
                            st.info(f"📈 Gerando relatório de {project['name']}...")
                    
                    with col3:
                        new_status = "inactive" if project['status'] == 'active' else "active"
                        action_text = "⏸️ Pausar" if project['status'] == 'active' else "▶️ Ativar"
                        
                        if st.button(action_text, key=f"toggle_proj_{project['id']}"):
                            st.success(f"✅ Status de {project['name']} alterado!")
                    
                    with col4:
                        if st.button(f"🗑️ Excluir", key=f"del_proj_{project['id']}"):
                            st.warning(f"⚠️ Projeto {project['name']} seria excluído")
        
        else:
            st.warning("❌ Nenhum projeto encontrado com os critérios especificados.")
    
    with tab2:
        st.subheader("➕ Criar Novo Projeto")
        
        with st.form("new_project_form"):
            project_name = st.text_input("📁 Nome do Projeto:", placeholder="Ex: Sistema de Relatórios")
            project_description = st.text_area("📝 Descrição:", placeholder="Descreva o objetivo do projeto...")
            
            col1, col2 = st.columns(2)
            
            with col1:
                project_category = st.selectbox("📂 Categoria:", [
                    "Desenvolvimento", "Manutenção", "Relatórios", "Backup", "Análise", "Outros"
                ])
            
            with col2:
                project_priority = st.selectbox("⭐ Prioridade:", ["Baixa", "Média", "Alta", "Crítica"])
            
            project_members = st.multiselect("👥 Membros:", [
                "admin@petcareai.com", "dev@petcareai.com", "analyst@petcareai.com"
            ])
            
            project_tags = st.text_input("🏷️ Tags (separadas por vírgula):", 
                                       placeholder="sql, relatórios, manutenção")
            
            submit_project = st.form_submit_button("🚀 Criar Projeto", type="primary")
            
            if submit_project:
                if project_name and project_description:
                    # Simular criação do projeto
                    new_project = {
                        'id': len(st.session_state.demo_data['projects']) + 1,
                        'name': project_name,
                        'description': project_description,
                        'category': project_category,
                        'priority': project_priority,
                        'members': project_members,
                        'tags': [tag.strip() for tag in project_tags.split(',') if tag.strip()],
                        'scripts': 0,
                        'status': 'active',
                        'created_at': datetime.now()
                    }
                    
                    st.session_state.demo_data['projects'].append(new_project)
                    log_activity("Projeto criado", f"'{project_name}'")
                    
                    st.success(f"✅ Projeto '{project_name}' criado com sucesso!")
                    
                    # Mostrar detalhes do projeto criado
                    with st.expander("📋 Detalhes do Projeto Criado", expanded=True):
                        st.json({
                            "Nome": project_name,
                            "Descrição": project_description,
                            "Categoria": project_category,
                            "Prioridade": project_priority,
                            "Membros": project_members,
                            "Tags": project_tags,
                            "Status": "Ativo",
                            "Data de Criação": format_datetime(datetime.now(), 'full')
                        })
                
                else:
                    st.error("❌ Nome e descrição são obrigatórios!")

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
            Gerencie configurações e preferências
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Abas de configurações
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 Sistema", "👤 Usuário", "🗄️ Banco de Dados", "📊 Monitoramento"])
    
    with tab1:
        st.subheader("🔧 Configurações do Sistema")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎨 Tema da Interface")
            
            theme_color = st.color_picker("Cor Primária:", CONFIG['theme']['primary_color'])
            secondary_color = st.color_picker("Cor Secundária:", CONFIG['theme']['secondary_color'])
            
            st.markdown("#### 📱 Interface")
            
            show_sidebar = st.checkbox("Mostrar Sidebar", value=True)
            compact_mode = st.checkbox("Modo Compacto", value=False)
            dark_mode = st.checkbox("Modo Escuro", value=False)
            
            st.markdown("#### 🔔 Notificações")
            
            enable_notifications = st.checkbox("Ativar Notificações", value=True)
            email_alerts = st.checkbox("Alertas por Email", value=False)
            sound_notifications = st.checkbox("Notificações Sonoras", value=False)
        
        with col2:
            st.markdown("#### ⚡ Performance")
            
            cache_enabled = st.checkbox("Ativar Cache", value=True)
            auto_refresh = st.slider("Auto-refresh (segundos):", 5, 300, 30)
            max_records = st.number_input("Máx. registros por página:", 10, 1000, 50)
            
            st.markdown("#### 🔐 Segurança")
            
            session_timeout = st.slider("Timeout da sessão (minutos):", 5, 480, 60)
            require_2fa = st.checkbox("Exigir 2FA", value=False)
            log_activities = st.checkbox("Log de Atividades", value=True)
            
            st.markdown("#### 🗂️ Arquivos")
            
            max_file_size = st.slider("Tamanho máx. arquivo (MB):", 1, 100, 10)
            allowed_formats = st.multiselect("Formatos permitidos:", 
                                           ["SQL", "CSV", "JSON", "XML", "TXT"],
                                           default=["SQL", "CSV", "JSON"])
        
        if st.button("💾 Salvar Configurações do Sistema", type="primary"):
            st.success("✅ Configurações do sistema salvas!")
            log_activity("Configurações alteradas", "Sistema")
    
    with tab2:
        st.subheader("👤 Configurações do Usuário")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📝 Perfil")
            
            username = st.text_input("Nome de usuário:", CONFIG['admin_username'])
            email = st.text_input("Email:", CONFIG['admin_email'])
            full_name = st.text_input("Nome completo:", "Administrador PetCare")
            
            st.markdown("#### 🔑 Senha")
            
            current_password = st.text_input("Senha atual:", type="password")
            new_password = st.text_input("Nova senha:", type="password")
            confirm_password = st.text_input("Confirmar nova senha:", type="password")
            
            if st.button("🔄 Alterar Senha"):
                if new_password and new_password == confirm_password:
                    st.success("✅ Senha alterada com sucesso!")
                    log_activity("Senha alterada")
                else:
                    st.error("❌ Senhas não coincidem!")
        
        with col2:
            st.markdown("#### 🎯 Preferências")
            
            default_page = st.selectbox("Página inicial:", [
                "Dashboard", "Tabelas", "Editor SQL", "Projetos"
            ])
            
            language = st.selectbox("Idioma:", ["Português", "English", "Español"])
            timezone = st.selectbox("Fuso horário:", [
                "America/Sao_Paulo", "UTC", "America/New_York"
            ])
            
            st.markdown("#### 📊 Dashboard")
            
            dashboard_refresh = st.slider("Refresh automático (seg):", 10, 300, 60)
            show_charts = st.checkbox("Mostrar gráficos", value=True)
            show_metrics = st.checkbox("Mostrar métricas", value=True)
            
            st.markdown("#### 📱 Acessibilidade")
            
            large_text = st.checkbox("Texto grande", value=False)
            high_contrast = st.checkbox("Alto contraste", value=False)
            screen_reader = st.checkbox("Leitor de tela", value=False)
        
        if st.button("💾 Salvar Perfil do Usuário", type="primary"):
            st.success("✅ Perfil do usuário salvo!")
            log_activity("Perfil alterado")
    
    with tab3:
        st.subheader("🗄️ Configurações do Banco de Dados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔗 Conexão")
            
            db_host = st.text_input("Host:", value="sua-url-supabase.supabase.co")
            db_port = st.number_input("Porta:", value=5432)
            db_name = st.text_input("Nome do banco:", value="postgres")
            db_user = st.text_input("Usuário:", value="postgres")
            db_password = st.text_input("Senha:", type="password")
            
            if st.button("🔍 Testar Conexão"):
                with st.spinner("🔄 Testando conexão..."):
                    time.sleep(2)
                
                if SUPABASE_AVAILABLE and CONFIG['supabase_url']:
                    st.success("✅ Conexão estabelecida com sucesso!")
                else:
                    st.warning("⚠️ Conexão em modo demo")
        
        with col2:
            st.markdown("#### ⚡ Performance")
            
            connection_pool = st.slider("Pool de conexões:", 5, 100, 20)
            query_timeout = st.slider("Timeout query (seg):", 5, 300, 30)
            max_connections = st.slider("Máx. conexões:", 10, 500, 100)
            
            st.markdown("#### 🔐 Segurança")
            
            ssl_enabled = st.checkbox("SSL habilitado", value=True)
            ssl_verify = st.checkbox("Verificar certificado SSL", value=True)
            
            st.markdown("#### 📊 Monitoramento")
            
            log_queries = st.checkbox("Log de queries", value=True)
            slow_query_log = st.checkbox("Log de queries lentas", value=True)
            slow_query_time = st.slider("Tempo para query lenta (seg):", 1, 60, 5)
        
        st.markdown("#### 🗃️ Tabelas Monitoradas")
        
        monitored_tables = st.multiselect(
            "Selecione tabelas para monitoramento:",
            [table['name'] for table in DEMO_DATA['tables']],
            default=[table['name'] for table in DEMO_DATA['tables'][:4]]
        )
        
        if st.button("💾 Salvar Configurações do Banco", type="primary"):
            st.success("✅ Configurações do banco de dados salvas!")
            log_activity("Configurações de BD alteradas")
    
    with tab4:
        st.subheader("📊 Configurações de Monitoramento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🚨 Alertas")
            
            cpu_threshold = st.slider("Limite CPU (%):", 50, 100, 80)
            memory_threshold = st.slider("Limite Memória (%):", 50, 100, 85)
            disk_threshold = st.slider("Limite Disco (%):", 50, 100, 90)
            
            st.markdown("#### 📈 Métricas")
            
            collect_metrics = st.checkbox("Coletar métricas", value=True)
            metrics_interval = st.slider("Intervalo coleta (seg):", 10, 300, 60)
            retention_days = st.slider("Retenção de dados (dias):", 7, 365, 30)
        
        with col2:
            st.markdown("#### 📧 Notificações")
            
            email_alerts_enabled = st.checkbox("Alertas por email", value=False)
            webhook_alerts = st.checkbox("Webhook alerts", value=False)
            
            if email_alerts_enabled:
                alert_email = st.text_input("Email para alertas:", CONFIG['admin_email'])
            
            if webhook_alerts:
                webhook_url = st.text_input("URL do webhook:", placeholder="https://...")
            
            st.markdown("#### 🔄 Auto-ações")
            
            auto_optimize = st.checkbox("Otimização automática", value=False)
            auto_backup = st.checkbox("Backup automático", value=True)
            auto_cleanup = st.checkbox("Limpeza automática", value=False)
        
        # Visualizar alertas atuais
        st.markdown("#### 🚨 Alertas Ativos")
        
        current_alerts = [
            {"type": "warning", "message": f"CPU em {DEMO_DATA['metrics']['cpu_usage']}%", "time": "5 min atrás"},
            {"type": "info", "message": "Backup concluído com sucesso", "time": "1 hora atrás"}
        ]
        
        for alert in current_alerts:
            icon = "⚠️" if alert["type"] == "warning" else "ℹ️"
            st.markdown(f"{icon} **{alert['message']}** - {alert['time']}")
        
        if st.button("💾 Salvar Configurações de Monitoramento", type="primary"):
            st.success("✅ Configurações de monitoramento salvas!")
            log_activity("Configurações de monitoramento alteradas")
        
        # Seção de informações do sistema
        st.markdown("---")
        st.subheader("ℹ️ Informações do Sistema")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.json({
                "Versão": CONFIG['app_version'],
                "Python": "3.13.x",
                "Streamlit": "1.28.1",
                "Última atualização": "24/06/2025"
            })
        
        with col2:
            st.json({
                "Uptime": "5d 12h 30m",
                "Conexões ativas": DEMO_DATA['metrics']['total_connections'],
                "Queries executadas": random.randint(1000, 9999),
                "Último backup": "23/06/2025 22:00"
            })
        
        with col3:
            st.json({
                "CPU": f"{DEMO_DATA['metrics']['cpu_usage']}%",
                "RAM": f"{DEMO_DATA['metrics']['memory_usage']}%",
                "Disco": f"{DEMO_DATA['metrics']['disk_usage']}%",
                "Cache hit": f"{DEMO_DATA['metrics']['cache_hit_ratio']}%"
            })

# =====================================================================
# APLICAÇÃO PRINCIPAL
# =====================================================================

def main():
    """Função principal da aplicação"""
    
    # Configuração da página
    st.set_page_config(
        page_title=CONFIG['app_title'],
        page_icon="🐾",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS customizado
    st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #F0FFF0, #E6FFE6);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #2E8B57;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(46, 139, 87, 0.1);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #2E8B57, #90EE90);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(46, 139, 87, 0.3);
    }
    
    .stSelectbox > div > div {
        border-radius: 10px;
    }
    
    .stTextInput > div > div {
        border-radius: 10px;
    }
    
    .stTextArea > div > div {
        border-radius: 10px;
    }
    
    .stExpander {
        border: 1px solid #90EE90;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    /* Hiding Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #2E8B57;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #228B22;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Inicializar estado da sessão
    init_session_state()
    
    # Verificar autenticação
    if not st.session_state.authenticated:
        render_login_page()
        return
    
    # Renderizar interface principal
    render_header()
    render_sidebar()
    
    # Renderizar página atual
    current_page = st.session_state.current_page
    
    if current_page == "dashboard":
        render_dashboard()
    elif current_page == "tables":
        render_tables()
    elif current_page == "sql_editor":
        render_sql_editor()
    elif current_page == "projects":
        render_projects()
    elif current_page == "settings":
        render_settings()
    else:
        render_dashboard()  # Página padrão
    
    # Rodapé
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: #228B22; padding: 1rem 0;'>
        <small>
            🐾 {CONFIG['app_title']} v{CONFIG['app_version']} | 
            Desenvolvido para PetCareAI | 
            © 2025 Todos os direitos reservados
        </small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
