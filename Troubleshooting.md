# 🔧 Guia de Resolução de Problemas - PetCare DBA Admin

Este guia contém soluções para problemas comuns encontrados no PetCare DBA Admin.

## 📋 Índice

1. [Problemas de Instalação](#problemas-de-instalação)
2. [Problemas de Conexão com Banco](#problemas-de-conexão-com-banco)
3. [Problemas de Autenticação](#problemas-de-autenticação)
4. [Problemas de Interface](#problemas-de-interface)
5. [Problemas de Performance](#problemas-de-performance)
6. [Problemas com Supabase](#problemas-com-supabase)
7. [Problemas com Projetos/Scripts](#problemas-com-projetosscripts)
8. [Diagnóstico Geral](#diagnóstico-geral)

---

## 🚨 Problemas de Instalação

### ❌ Erro: "ModuleNotFoundError: No module named 'streamlit'"

**Sintomas:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Soluções:**
1. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verificar ambiente virtual:**
   ```bash
   # Criar ambiente virtual
   python -m venv venv
   
   # Ativar (Windows)
   venv\Scripts\activate
   
   # Ativar (Linux/Mac)
   source venv/bin/activate
   
   # Instalar dependências
   pip install -r requirements.txt
   ```

3. **Verificar versão do Python:**
   ```bash
   python --version  # Deve ser 3.9+
   ```

### ❌ Erro: "No module named 'supabase'"

**Sintomas:**
```
ImportError: No module named 'supabase'
```

**Soluções:**
1. **Instalar Supabase:**
   ```bash
   pip install supabase>=2.0.0
   ```

2. **Atualizar pip:**
   ```bash
   python -m pip install --upgrade pip
   pip install supabase
   ```

### ❌ Erro de Dependências do psycopg2

**Sintomas:**
```
Error: Microsoft Visual C++ 14.0 is required
```

**Soluções:**
1. **Usar versão binária:**
   ```bash
   pip install psycopg2-binary
   ```

2. **No Ubuntu/Debian:**
   ```bash
   sudo apt-get install python3-dev libpq-dev
   pip install psycopg2
   ```

---

## 🗄️ Problemas de Conexão com Banco

### ❌ Erro: "Conexão com Supabase falhou"

**Sintomas:**
- Modo demo ativado automaticamente
- Mensagem "❌ Erro ao conectar com Supabase"

**Soluções:**

1. **Verificar credenciais no .streamlit/secrets.toml:**
   ```toml
   [supabase]
   url = "https://seu-projeto.supabase.co"
   anon_key = "sua_chave_anonima"
   service_key = "sua_chave_service"
   ```

2. **Testar conexão manualmente:**
   ```python
   from supabase import create_client
   
   url = "sua_url"
   key = "sua_chave"
   supabase = create_client(url, key)
   
   # Teste simples
   response = supabase.table('projetos_analytics').select('id').limit(1).execute()
   print(response)
   ```

3. **Verificar URL do Supabase:**
   - Deve começar com `https://`
   - Deve terminar com `.supabase.co`
   - Não deve conter espaços ou caracteres especiais

### ❌ Erro: "Row Level Security"

**Sintomas:**
```
permission denied for table projetos_analytics
```

**Soluções:**

1. **Executar script de correção RLS:**
   ```sql
   -- Opção 1: Desabilitar RLS temporariamente
   ALTER TABLE projetos_analytics DISABLE ROW LEVEL SECURITY;
   ALTER TABLE scripts_projetos DISABLE ROW LEVEL SECURITY;
   ALTER TABLE execucoes_scripts DISABLE ROW LEVEL SECURITY;
   
   -- Opção 2: Criar políticas para service_role
   CREATE POLICY "service_role_all_access" ON projetos_analytics
   FOR ALL TO service_role
   USING (true)
   WITH CHECK (true);
   ```

2. **Verificar chave service_role:**
   - Use a chave `service_role` e não `anon`
   - Verifique se a chave não expirou

### ❌ Tabelas não encontradas

**Sintomas:**
- "📭 Nenhuma tabela encontrada"
- Lista de tabelas vazia

**Soluções:**

1. **Executar scripts de criação:**
   ```bash
   # Execute os SQLs do diretório database/
   psql -f database/supabase-projects-table.sql
   psql -f database/supabase-conversas-ia.sql
   ```

2. **Criar tabelas manualmente no Supabase:**
   - Vá para SQL Editor no painel Supabase
   - Execute os scripts em `database/`

3. **Verificar permissões de schema:**
   ```sql
   -- Verificar tabelas existentes
   SELECT table_name FROM information_schema.tables 
   WHERE table_schema = 'public';
   ```

---

## 🔐 Problemas de Autenticação

### ❌ Login não funciona

**Sintomas:**
- "❌ Usuário ou senha incorretos!"
- Página de login não avança

**Soluções:**

1. **Credenciais padrão:**
   - **Usuário:** `admin`
   - **Senha:** `petcare2025`

2. **Verificar configuração:**
   ```toml
   # .streamlit/secrets.toml
   [admin]
   username = "admin"
   password = "petcare2025"
   email = "admin@petcareai.com"
   ```

3. **Limpar cache do navegador:**
   - Ctrl+F5 para recarregar
   - Limpar cookies do localhost

### ❌ Sessão expira rapidamente

**Sintomas:**
- Redirecionamento constante para login
- Perda de estado da aplicação

**Soluções:**

1. **Verificar configurações de sessão:**
   ```python
   # No código, ajustar timeout
   session_timeout = 3600  # 1 hora
   ```

2. **Verificar cookies do navegador:**
   - Permitir cookies para localhost
   - Verificar configurações de privacidade

---

## 🎨 Problemas de Interface

### ❌ Interface quebrada ou mal formatada

**Sintomas:**
- CSS não carrega corretamente
- Elementos desalinhados
- Cores incorretas

**Soluções:**

1. **Limpar cache do Streamlit:**
   ```bash
   streamlit cache clear
   ```

2. **Recarregar página:**
   - Ctrl+F5 (recarregamento forçado)
   - Fechar e reabrir o navegador

3. **Verificar compatibilidade do navegador:**
   - Use Chrome, Firefox ou Edge atualizados
   - Desabilite extensões que podem interferir

### ❌ Gráficos não aparecem

**Sintomas:**
- Espaços em branco onde deveriam haver gráficos
- Erro com Plotly

**Soluções:**

1. **Verificar instalação do Plotly:**
   ```bash
   pip install plotly>=5.17.0
   ```

2. **Verificar JavaScript no navegador:**
   - Habilitar JavaScript
   - Desabilitar bloqueadores de script

---

## ⚡ Problemas de Performance

### ❌ Aplicação lenta

**Sintomas:**
- Carregamento demorado das páginas
- Timeout em operações

**Soluções:**

1. **Otimizar configurações:**
   ```toml
   # .streamlit/config.toml
   [server]
   maxUploadSize = 200
   maxMessageSize = 200
   
   [client]
   caching = true
   ```

2. **Reduzir dados exibidos:**
   ```python
   # Limitar registros
   df.head(100)  # Em vez de mostrar todos
   ```

3. **Usar cache:**
   ```python
   @st.cache_data
   def load_data():
       # Sua função aqui
       pass
   ```

### ❌ Alto uso de memória

**Sintomas:**
- Sistema lento
- Erro de memória

**Soluções:**

1. **Limpar cache periodicamente:**
   ```python
   st.cache_data.clear()
   ```

2. **Otimizar DataFrames:**
   ```python
   # Usar tipos de dados eficientes
   df = df.astype({'id': 'int32'})
   ```

---

## 🔗 Problemas com Supabase

### ❌ Erro 401 - Unauthorized

**Sintomas:**
```
{"code":401,"message":"Invalid JWT"}
```

**Soluções:**

1. **Verificar chaves:**
   - Use `service_role` key para operações admin
   - Verifique se a chave não expirou

2. **Regenerar chaves:**
   - Vá para Settings > API no painel Supabase
   - Gere novas chaves se necessário

### ❌ Erro 403 - Forbidden

**Sintomas:**
```
{"code":403,"message":"Forbidden"}
```

**Soluções:**

1. **Verificar RLS policies:**
   ```sql
   -- Ver políticas existentes
   SELECT * FROM pg_policies WHERE tablename = 'projetos_analytics';
   ```

2. **Criar política permissiva:**
   ```sql
   CREATE POLICY "allow_all_for_service_role" ON projetos_analytics
   FOR ALL TO service_role
   USING (true)
   WITH CHECK (true);
   ```

### ❌ Timeout de conexão

**Sintomas:**
- Operações demoram muito
- Erro de timeout

**Soluções:**

1. **Verificar região:**
   - Use região mais próxima do usuário
   - Considere migrar projeto se necessário

2. **Otimizar queries:**
   ```sql
   -- Adicionar índices
   CREATE INDEX idx_nome_coluna ON tabela(coluna);
   ```

---

## 📁 Problemas com Projetos/Scripts

### ❌ Não consegue criar projetos

**Sintomas:**
- Erro ao salvar projeto
- "❌ Erro ao criar projeto no Supabase"

**Soluções:**

1. **Verificar tabelas:**
   ```sql
   -- Verificar se tabela existe
   SELECT EXISTS (
       SELECT FROM information_schema.tables 
       WHERE table_name = 'projetos_analytics'
   );
   ```

2. **Executar script de criação:**
   - Execute `database/supabase-projects-table.sql`

3. **Verificar permissões:**
   ```sql
   -- Dar permissões explícitas
   GRANT ALL ON projetos_analytics TO service_role;
   ```

### ❌ Scripts não executam

**Sintomas:**
- "❌ Erro na execução"
- Timeout em scripts

**Soluções:**

1. **Verificar sintaxe SQL:**
   ```sql
   -- Testar script separadamente
   SELECT 1; -- Script simples para teste
   ```

2. **Verificar permissões de tabelas:**
   ```sql
   -- Verificar se pode acessar tabelas
   SELECT * FROM information_schema.table_privileges 
   WHERE grantee = 'your_role';
   ```

---

## 🔍 Diagnóstico Geral

### 🧪 Script de Diagnóstico Completo

Execute este script Python para diagnosticar problemas:

```python
import streamlit as st
import sys
import pkg_resources
from datetime import datetime
import os

def diagnostic_check():
    """Executa verificação completa do sistema"""
    
    print("🔍 PetCare DBA Admin - Diagnóstico Completo")
    print("=" * 50)
    
    # Verificar Python
    print(f"🐍 Python: {sys.version}")
    
    # Verificar dependências
    required_packages = [
        'streamlit', 'supabase', 'pandas', 'plotly', 
        'psycopg2', 'sqlparse', 'numpy', 'requests'
    ]
    
    print("\n📦 Dependências:")
    for package in required_packages:
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"  ✅ {package}: {version}")
        except:
            print(f"  ❌ {package}: NÃO INSTALADO")
    
    # Verificar arquivos
    print("\n📁 Arquivos:")
    required_files = [
        'app.py', 'requirements.txt', '.streamlit/secrets.toml'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}: Existe")
        else:
            print(f"  ❌ {file}: NÃO ENCONTRADO")
    
    # Verificar configurações
    print("\n⚙️ Configurações:")
    try:
        import streamlit as st
        if os.path.exists('.streamlit/secrets.toml'):
            print("  ✅ Secrets configurado")
        else:
            print("  ❌ Secrets não encontrado")
    except:
        print("  ❌ Erro ao verificar configurações")
    
    print(f"\n📅 Diagnóstico executado em: {datetime.now()}")

if __name__ == "__main__":
    diagnostic_check()
```

### 🛠️ Comandos Úteis

```bash
# Verificar instalação
python -c "import streamlit; print('Streamlit OK')"

# Verificar porta
netstat -an | grep 8501

# Verificar logs
streamlit run app.py --logger.level=debug

# Limpar cache
rm -rf ~/.streamlit/cache

# Reinstalar dependências
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### 📞 Quando Pedir Ajuda

Se os problemas persistirem, colete estas informações:

1. **Versão do Python:** `python --version`
2. **Sistema operacional:** Windows/Mac/Linux
3. **Versão do Streamlit:** `streamlit version`
4. **Mensagem de erro completa**
5. **Logs da aplicação**
6. **Configurações do Supabase** (sem chaves sensíveis)

**Contato:**
- 📧 Email: admin@petcareai.com
- 🐙 GitHub: https://github.com/petcareai/dba-admin/issues
- 📚 Documentação: https://docs.petcareai.com

---

## 📋 Checklist de Resolução

- [ ] Verificar versão do Python (3.9+)
- [ ] Instalar dependências (`pip install -r requirements.txt`)
- [ ] Configurar secrets.toml
- [ ] Testar conexão Supabase
- [ ] Executar scripts de banco
- [ ] Verificar RLS policies
- [ ] Testar login da aplicação
- [ ] Verificar logs de erro

---

*Este guia é atualizado constantemente. Para problemas não listados, consulte a documentação completa ou entre em contato com o suporte.*
