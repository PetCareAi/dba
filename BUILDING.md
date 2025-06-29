# 🔨 Guia de Construção - PetCare DBA Admin

Este documento fornece instruções detalhadas para construir, configurar e executar o PetCare DBA Admin a partir do código fonte.

## 📋 Pré-requisitos

### Software Necessário

- **Python 3.9+** (Recomendado: Python 3.11 ou 3.13)
- **pip** (gerenciador de pacotes Python)
- **Git** (para clonar o repositório)
- **Conta Supabase** (para funcionalidade completa)

### Verificação dos Pré-requisitos

```bash
# Verificar versão do Python
python --version
# ou
python3 --version

# Verificar pip
pip --version

# Verificar Git
git --version
```

## 🚀 Instalação Rápida

### 1. Clonar o Repositório

```bash
git clone https://github.com/PetCareAi/dba.git
cd dba
```

### 2. Criar Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows:
venv\Scripts\activate

# No macOS/Linux:
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
# Instalar todas as dependências
pip install -r requirements.txt

# Ou instalar manualmente as principais:
pip install streamlit supabase python-dotenv pandas plotly
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações
nano .env
# ou
notepad .env
```

### 5. Executar a Aplicação

```bash
# Iniciar servidor Streamlit
streamlit run app.py

# Ou usar o script de inicialização
chmod +x start.sh
./start.sh
```

## ⚙️ Configuração Avançada

### Configuração do Supabase

1. **Criar Projeto no Supabase**
   - Acesse [supabase.com](https://supabase.com)
   - Crie um novo projeto
   - Anote a URL e as chaves de API

2. **Executar Scripts SQL**
   ```sql
   -- Execute os scripts na seguinte ordem:
   -- 1. database/supabase-projects-table.sql
   -- 2. database/supabase-conversas-ia.sql
   ```

3. **Configurar RLS (Row Level Security)**
   ```sql
   -- Verificar se RLS está habilitado
   SELECT schemaname, tablename, rowsecurity 
   FROM pg_tables 
   WHERE tablename IN ('projetos_analytics', 'scripts_projetos', 'execucoes_scripts');
   ```

### Estrutura de Configuração

```yaml
# .streamlit/config.toml
[server]
port = 8501
headless = true

[theme]
primaryColor = "#2E8B57"
backgroundColor = "#F0FFF0"
secondaryBackgroundColor = "#E6FFE6"
textColor = "#006400"

[global]
developmentMode = false
```

## 🧪 Desenvolvimento

### Estrutura do Projeto

```
petcare-dba-admin/
├── app.py                  # Aplicação principal
├── requirements.txt        # Dependências Python
├── .env.example           # Exemplo de configuração
├── .streamlit/
│   └── config.toml        # Configurações Streamlit
├── database/
│   ├── supabase-projects-table.sql
│   └── supabase-conversas-ia.sql
├── public/
│   └── assets/            # Recursos estáticos
└── docs/                  # Documentação
```

### Modo Desenvolvimento

```bash
# Executar com debug habilitado
export DEBUG_MODE=True
streamlit run app.py --server.runOnSave true

# Ou configurar no .env
echo "DEBUG_MODE=True" >> .env
```

### Instalação de Dependências de Desenvolvimento

```bash
# Instalar ferramentas de desenvolvimento
pip install black flake8 pytest mypy

# Formatação de código
black app.py

# Verificação de estilo
flake8 app.py

# Verificação de tipos
mypy app.py
```

## 🐳 Construção com Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  petcare-dba:
    build: .
    ports:
      - "8501:8501"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
    volumes:
      - ./user_settings.json:/app/user_settings.json
```

### Construir e Executar

```bash
# Construir imagem
docker build -t petcare-dba-admin .

# Executar container
docker run -p 8501:8501 --env-file .env petcare-dba-admin

# Ou com Docker Compose
docker-compose up --build
```

## 🧪 Testes

### Executar Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-streamlit

# Executar todos os testes
pytest

# Executar testes específicos
pytest tests/test_database.py

# Executar com cobertura
pytest --cov=app
```

### Testes Manuais

```bash
# Testar conexão Supabase
python -c "
import os
from supabase import create_client
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY'))
print('✅ Conexão Supabase OK')
"

# Testar importações
python -c "
import streamlit as st
import pandas as pd
import plotly.express as px
print('✅ Todas as importações OK')
"
```

## 📦 Construção para Produção

### Otimizações de Performance

```bash
# Instalar dependências otimizadas
pip install --upgrade streamlit pandas plotly

# Configurar cache
export STREAMLIT_SERVER_ENABLE_STATIC_SERVING=false
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Variáveis de Ambiente de Produção

```bash
# .env.production
DEBUG_MODE=False
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLE_CORS=false
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
```

### Script de Deploy

```bash
#!/bin/bash
# deploy.sh

echo "🚀 Iniciando deploy..."

# Ativar ambiente virtual
source venv/bin/activate

# Atualizar dependências
pip install -r requirements.txt --upgrade

# Configurações de produção
cp .env.production .env

# Iniciar aplicação
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 🔧 Solução de Problemas de Build

### Problema: Dependências não Instaladas

```bash
# Limpar cache pip
pip cache purge

# Reinstalar dependências
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Problema: Conflitos de Versão

```bash
# Criar novo ambiente virtual
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Problema: Erro no Supabase

```bash
# Verificar conectividade
ping your-project.supabase.co

# Testar chaves
python -c "
import os
print(f'URL: {os.getenv(\"SUPABASE_URL\")}')
print(f'Key: {os.getenv(\"SUPABASE_ANON_KEY\")[:20]}...')
"
```

## 📋 Checklist de Build

- [ ] Python 3.9+ instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas
- [ ] Arquivo .env configurado
- [ ] Projeto Supabase criado
- [ ] Scripts SQL executados
- [ ] Aplicação iniciada com sucesso
- [ ] Conexão com Supabase testada
- [ ] Login funcionando
- [ ] Todas as páginas carregando

## 🆘 Suporte

Se encontrar problemas durante a construção:

1. **Consulte o arquivo [Troubleshooting.md](./Troubleshooting.md)**
2. **Verifique os logs**: `streamlit run app.py --logger.level debug`
3. **Abra uma issue**: [GitHub Issues](https://github.com/PetCareAi/dba/issues)
4. **Entre em contato**: admin@petcareai.com

## 📚 Recursos Adicionais

- [Documentação Streamlit](https://docs.streamlit.io)
- [Documentação Supabase](https://supabase.com/docs)
- [Guia Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [Guia Docker](https://docs.docker.com/get-started/)

---

**Última atualização:** Janeiro 2025  
**Versão do documento:** 1.0
