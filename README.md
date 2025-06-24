# 🐾 PetCare DBA Admin

Sistema completo de gerenciamento de banco de dados Supabase para a PetCareAI em arquivo único.

## 🚀 Características

- ✅ **Arquivo Único**: Todo o sistema em um só arquivo app.py
- ✅ **Dashboard Interativo**: Métricas em tempo real
- ✅ **Gerenciamento de Tabelas**: Exploração e análise
- ✅ **Editor SQL**: Execute queries com histórico
- ✅ **Gestão de Projetos**: Organize scripts
- ✅ **Configurações Completas**: Personalize tudo
- ✅ **Interface Moderna**: Design verde responsivo

## 📦 Instalação Rápida

### Executar o Setup:
```bash
node setup-sistema-streamlit.js
cd petcare-dba-admin
./start.sh
```

### Manual:
```bash
cd petcare-dba-admin
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 🔐 Acesso

- **URL**: http://localhost:8501
- **Usuário**: admin  
- **Senha**: petcare2025

## 📁 Estrutura Simples

```
petcare-dba-admin/
├── app.py              # Sistema completo
├── requirements.txt    # Dependências  
├── .env               # Configurações
├── start.sh          # Script de inicialização
└── .streamlit/
    └── config.toml   # Tema
```

## ⚙️ Configuração

1. **Configure Supabase** no .env:
```env
SUPABASE_URL=https://sua-url-supabase.supabase.co
SUPABASE_ANON_KEY=sua_chave_anonima
```

2. **Execute o SQL** fornecido no Supabase

3. **Inicie o sistema**:
```bash
./start.sh
```

## 🎯 Funcionalidades

### 📊 Dashboard
- Métricas CPU, Memória, Conexões
- Gráficos de performance
- Atividades recentes
- Alertas do sistema

### 🗃️ Tabelas  
- Lista todas as tabelas
- Exploração de dados
- Estatísticas detalhadas
- Operações de manutenção

### 📜 Editor SQL
- Syntax highlighting
- Execução de queries
- Histórico completo
- Validação e formatação

### 📁 Projetos
- Organização de scripts
- Estatísticas por projeto
- Controle de membros
- Relatórios de atividade

### ⚙️ Configurações
- Tema personalizado
- Configurações de usuário
- Conexão com banco
- Alertas e monitoramento

## 🛠️ Tecnologias

- **Python 3.13+**
- **Streamlit** - Interface web
- **Supabase** - Banco de dados
- **Plotly** - Gráficos interativos
- **Pandas** - Manipulação de dados

## 🎨 Design

- **Cores**: Verde escuro (#2E8B57) e claro (#90EE90)
- **Layout**: Responsivo e moderno
- **Componentes**: Cards, métricas, gráficos
- **Animações**: Hover effects suaves

## 🔧 Desenvolvimento

### Debug:
```bash
streamlit run app.py --logger.level=debug
```

### Personalizar:
- **Cores**: Edite `.streamlit/config.toml`
- **Configurações**: Modifique seção CONFIG em `app.py`
- **Funcionalidades**: Adicione na função correspondente

## 📱 Compatibilidade

- ✅ Python 3.8+
- ✅ macOS, Linux, Windows
- ✅ Chrome, Firefox, Safari, Edge
- ✅ Desktop e Mobile

## 🚀 Produção

Para deploy em produção:

```bash
# Configurar variáveis de ambiente
export SUPABASE_URL="sua_url_real"
export SUPABASE_ANON_KEY="sua_chave_real"

# Executar em modo produção
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 📞 Suporte

- **Email**: admin@petcareai.com
- **Documentação**: Veja comentários no código
- **Issues**: Use o sistema de issues

## 🔄 Atualizações

Para atualizar:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
streamlit run app.py
```

---

**🐾 PetCare DBA Admin - Desenvolvido com ❤️ para PetCareAI**
