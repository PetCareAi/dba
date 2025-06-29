#!/bin/bash

# PetCare DBA Admin - Script de Configuração
# Sistema de Gerenciamento de Banco de Dados para PetCareAI

set -e  # Para no primeiro erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_input() {
    echo -e "${CYAN}[INPUT]${NC} $1"
}

# Banner de configuração
echo -e "${GREEN}"
cat << "EOF"
🐾 =====================================================
   PetCare DBA Admin - Configuração do Sistema
   Configure suas credenciais e preferências
=====================================================
EOF
echo -e "${NC}"

# Verificar se está no diretório correto
if [ ! -f "app.py" ]; then
    print_error "app.py não encontrado!"
    print_status "Execute este script no diretório do projeto."
    exit 1
fi

print_status "Iniciando configuração interativa..."

# Função para solicitar entrada do usuário
ask_input() {
    local prompt="$1"
    local default="$2"
    local secret="$3"
    
    if [ "$secret" = "true" ]; then
        print_input "$prompt"
        read -s user_input
        echo
    else
        if [ -n "$default" ]; then
            print_input "$prompt [$default]: "
            read user_input
            user_input=${user_input:-$default}
        else
            print_input "$prompt: "
            read user_input
        fi
    fi
    echo "$user_input"
}

# Função para validar URL
validate_url() {
    local url="$1"
    if [[ $url =~ ^https://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}.*$ ]]; then
        return 0
    else
        return 1
    fi
}

# Função para validar email
validate_email() {
    local email="$1"
    if [[ $email =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

echo ""
print_status "🔧 CONFIGURAÇÃO BÁSICA"
echo ""

# Configurações da aplicação
APP_TITLE=$(ask_input "Nome da aplicação" "PetCare DBA Admin")
APP_VERSION=$(ask_input "Versão da aplicação" "2.1.0")
DEBUG_MODE=$(ask_input "Modo debug (true/false)" "false")

echo ""
print_status "👤 CONFIGURAÇÃO DO ADMINISTRADOR"
echo ""

# Configurações do administrador
while true; do
    ADMIN_USERNAME=$(ask_input "Nome de usuário do administrador" "admin")
    if [ ${#ADMIN_USERNAME} -ge 3 ]; then
        break
    else
        print_error "Nome de usuário deve ter pelo menos 3 caracteres"
    fi
done

while true; do
    ADMIN_PASSWORD=$(ask_input "Senha do administrador" "" "true")
    if [ ${#ADMIN_PASSWORD} -ge 8 ]; then
        print_warning "Confirme a senha:"
        ADMIN_PASSWORD_CONFIRM=$(ask_input "Confirmar senha" "" "true")
        if [ "$ADMIN_PASSWORD" = "$ADMIN_PASSWORD_CONFIRM" ]; then
            break
        else
            print_error "Senhas não coincidem. Tente novamente."
        fi
    else
        print_error "Senha deve ter pelo menos 8 caracteres"
    fi
done

while true; do
    ADMIN_EMAIL=$(ask_input "Email do administrador" "admin@petcareai.com")
    if validate_email "$ADMIN_EMAIL"; then
        break
    else
        print_error "Email inválido. Tente novamente."
    fi
done

echo ""
print_status "🎨 CONFIGURAÇÃO DE TEMA"
echo ""

PRIMARY_COLOR=$(ask_input "Cor primária (hex)" "#2E8B57")
SECONDARY_COLOR=$(ask_input "Cor secundária (hex)" "#90EE90")
BACKGROUND_COLOR=$(ask_input "Cor de fundo (hex)" "#F0FFF0")
TEXT_COLOR=$(ask_input "Cor do texto (hex)" "#006400")

echo ""
print_status "🗄️ CONFIGURAÇÃO DO SUPABASE"
echo ""

print_warning "Para usar todas as funcionalidades, configure o Supabase:"
print_status "1. Crie uma conta em https://supabase.com"
print_status "2. Crie um novo projeto"
print_status "3. Vá em Settings > API para encontrar as chaves"
echo ""

CONFIGURE_SUPABASE=$(ask_input "Configurar Supabase agora? (y/n)" "y")

if [[ $CONFIGURE_SUPABASE =~ ^[Yy]$ ]]; then
    while true; do
        SUPABASE_URL=$(ask_input "URL do projeto Supabase" "https://seu-projeto.supabase.co")
        if validate_url "$SUPABASE_URL" && [[ $SUPABASE_URL == *"supabase.co"* ]]; then
            break
        else
            print_error "URL do Supabase inválida. Deve ser https://seu-projeto.supabase.co"
        fi
    done

    SUPABASE_ANON_KEY=$(ask_input "Chave anônima (anon key)" "")
    SUPABASE_SERVICE_KEY=$(ask_input "Chave de serviço (service role key)" "")
else
    SUPABASE_URL="https://seu-projeto.supabase.co"
    SUPABASE_ANON_KEY="sua_chave_anonima_aqui"
    SUPABASE_SERVICE_KEY="sua_chave_service_aqui"
    print_warning "Configuração do Supabase pulada. Configure manualmente depois."
fi

echo ""
print_status "🤖 CONFIGURAÇÃO DO GOOGLE GEMINI (IA ASSISTENTE)"
echo ""

print_warning "Para usar o assistente IA, configure o Google Gemini:"
print_status "1. Acesse https://ai.google.dev"
print_status "2. Obtenha uma API key gratuita"
print_status "3. Insira a chave abaixo"
echo ""

CONFIGURE_GEMINI=$(ask_input "Configurar Google Gemini agora? (y/n)" "n")

if [[ $CONFIGURE_GEMINI =~ ^[Yy]$ ]]; then
    GEMINI_API_KEY=$(ask_input "API Key do Google Gemini" "")
    GEMINI_MODEL=$(ask_input "Modelo do Gemini" "gemini-2.0-flash-exp")
    GEMINI_BASE_URL=$(ask_input "URL base da API" "https://generativelanguage.googleapis.com")
else
    GEMINI_API_KEY="sua_api_key_gemini_aqui"
    GEMINI_MODEL="gemini-2.0-flash-exp"
    GEMINI_BASE_URL="https://generativelanguage.googleapis.com"
    print_warning "Configuração do Gemini pulada. Configure manualmente depois."
fi

echo ""
print_status "💾 SALVANDO CONFIGURAÇÕES..."

# Criar arquivo .env
cat > .env << EOF
# PetCare DBA Admin - Configuração
# Gerado automaticamente em $(date)

# Configurações da Aplicação
APP_TITLE=$APP_TITLE
APP_VERSION=$APP_VERSION
DEBUG_MODE=$DEBUG_MODE

# Configurações de Administrador
ADMIN_USERNAME=$ADMIN_USERNAME
ADMIN_PASSWORD=$ADMIN_PASSWORD
ADMIN_EMAIL=$ADMIN_EMAIL

# Configurações de Tema
PRIMARY_COLOR=$PRIMARY_COLOR
SECONDARY_COLOR=$SECONDARY_COLOR
BACKGROUND_COLOR=$BACKGROUND_COLOR
TEXT_COLOR=$TEXT_COLOR

# Supabase Configuration
SUPABASE_URL=$SUPABASE_URL
SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
SUPABASE_SERVICE_KEY=$SUPABASE_SERVICE_KEY

# Google Gemini Configuration
GEMINI_API_KEY=$GEMINI_API_KEY
GEMINI_MODEL=$GEMINI_MODEL
GEMINI_BASE_URL=$GEMINI_BASE_URL
EOF

# Criar/atualizar arquivo secrets.toml do Streamlit
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
# PetCare DBA Admin - Configurações do Streamlit
# Gerado automaticamente em $(date)

[app]
title = "$APP_TITLE"
version = "$APP_VERSION"
debug_mode = $DEBUG_MODE

[admin]
username = "$ADMIN_USERNAME"
password = "$ADMIN_PASSWORD"
email = "$ADMIN_EMAIL"

[theme]
primary_color = "$PRIMARY_COLOR"
secondary_color = "$SECONDARY_COLOR"
background_color = "$BACKGROUND_COLOR"
text_color = "$TEXT_COLOR"

[supabase]
url = "$SUPABASE_URL"
anon_key = "$SUPABASE_ANON_KEY"
service_key = "$SUPABASE_SERVICE_KEY"

[gemini]
api_key = "$GEMINI_API_KEY"
model = "$GEMINI_MODEL"
base_url = "$GEMINI_BASE_URL"
EOF

print_success "Configurações salvas em .env e .streamlit/secrets.toml"

# Configurar Streamlit config.toml se não existir
if [ ! -f ".streamlit/config.toml" ]; then
    print_status "Criando configuração do Streamlit..."
    cat > .streamlit/config.toml << 'EOF'
[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = false
maxUploadSize = 200

[browser]
gatherUsageStats = false
showErrorDetails = true

[theme]
primaryColor = "#2E8B57"
backgroundColor = "#F0FFF0"
secondaryBackgroundColor = "#E6FFE6"
textColor = "#006400"

[global]
developmentMode = false
logLevel = "info"
EOF
fi

# Testar configuração
echo ""
print_status "🧪 TESTANDO CONFIGURAÇÃO..."

# Verificar se o ambiente virtual está ativo
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_success "Ambiente virtual ativo: $VIRTUAL_ENV"
else
    print_warning "Ambiente virtual não ativo. Ativando..."
    if [ -d "venv" ]; then
        source venv/bin/activate
        print_success "Ambiente virtual ativado"
    else
        print_error "Ambiente virtual não encontrado. Execute install.sh primeiro."
        exit 1
    fi
fi

# Testar importações Python
print_status "Testando dependências Python..."
if python3 -c "
import streamlit
import supabase
import pandas
import plotly
print('✅ Todas as dependências estão funcionando')
" 2>/dev/null; then
    print_success "Dependências Python OK"
else
    print_error "Erro nas dependências Python"
    print_status "Execute: pip install -r requirements.txt"
    exit 1
fi

# Testar configuração do Supabase (se configurado)
if [[ $SUPABASE_URL != "https://seu-projeto.supabase.co" ]] && [[ $SUPABASE_ANON_KEY != "sua_chave_anonima_aqui" ]]; then
    print_status "Testando conexão com Supabase..."
    python3 -c "
from supabase import create_client
try:
    supabase = create_client('$SUPABASE_URL', '$SUPABASE_ANON_KEY')
    print('✅ Conexão com Supabase bem-sucedida')
except Exception as e:
    print(f'❌ Erro na conexão: {e}')
    print('⚠️ Verifique suas credenciais do Supabase')
" 2>/dev/null || print_warning "Verifique as configurações do Supabase"
fi

# Criar backup da configuração
BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
cp .env "$BACKUP_DIR/env_backup_$TIMESTAMP"
cp .streamlit/secrets.toml "$BACKUP_DIR/secrets_backup_$TIMESTAMP"
print_success "Backup das configurações criado em $BACKUP_DIR/"

echo ""
print_success "🎉 CONFIGURAÇÃO CONCLUÍDA!"
echo ""
echo -e "${YELLOW}📋 RESUMO DA CONFIGURAÇÃO:${NC}"
echo ""
echo "✅ Aplicação: $APP_TITLE v$APP_VERSION"
echo "✅ Administrador: $ADMIN_USERNAME ($ADMIN_EMAIL)"
echo "✅ Supabase: $([ "$SUPABASE_URL" != "https://seu-projeto.supabase.co" ] && echo "Configurado" || echo "Pendente")"
echo "✅ Google Gemini: $([ "$GEMINI_API_KEY" != "sua_api_key_gemini_aqui" ] && echo "Configurado" || echo "Pendente")"
echo ""
echo -e "${YELLOW}🚀 PRÓXIMOS PASSOS:${NC}"
echo ""

if [[ $SUPABASE_URL == "https://seu-projeto.supabase.co" ]]; then
    echo "1. 🗄️ Configure o Supabase:"
    echo "   - Edite .env e .streamlit/secrets.toml"
    echo "   - Execute os scripts SQL em database/"
    echo ""
fi

if [[ $GEMINI_API_KEY == "sua_api_key_gemini_aqui" ]]; then
    echo "2. 🤖 Configure o Google Gemini (opcional):"
    echo "   - Obtenha API key em https://ai.google.dev"
    echo "   - Edite .env e .streamlit/secrets.toml"
    echo ""
fi

echo "3. 🗃️ Configure o banco de dados:"
echo "   - Execute os scripts SQL em database/"
echo "   - Teste a conexão na aplicação"
echo ""
echo "4. 🚀 Inicie a aplicação:"
echo "   ./run.sh"
echo ""
echo "5. 🌐 Acesse no navegador:"
echo "   http://localhost:8501"
echo ""
print_warning "IMPORTANTE: Mantenha suas credenciais seguras!"
print_warning "Não commite os arquivos .env e secrets.toml no Git!"
echo ""
print_success "Configuração finalizada! Execute ./run.sh para iniciar."
