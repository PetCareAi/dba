#!/bin/bash

# PetCare DBA Admin - Script de Instalação
# Sistema de Gerenciamento de Banco de Dados para PetCareAI

set -e  # Para no primeiro erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Banner de boas-vindas
echo -e "${GREEN}"
cat << "EOF"
🐾 =====================================================
   PetCare DBA Admin - Sistema de Instalação
   Sistema de Gerenciamento de Banco de Dados
   Versão 2.1.0
=====================================================
EOF
echo -e "${NC}"

print_status "Iniciando processo de instalação..."

# Verificar sistema operacional
OS="Unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
    OS="Windows"
fi

print_status "Sistema operacional detectado: $OS"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 não encontrado!"
    print_status "Por favor, instale Python 3.9 ou superior:"
    
    case $OS in
        "Linux")
            echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip python3-venv"
            echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
            ;;
        "macOS")
            echo "  Homebrew: brew install python3"
            echo "  ou baixe de: https://www.python.org/downloads/"
            ;;
        "Windows")
            echo "  Baixe de: https://www.python.org/downloads/"
            ;;
    esac
    exit 1
fi

# Verificar versão do Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
MIN_VERSION="3.9"

print_status "Versão do Python: $PYTHON_VERSION"

if [[ "$(printf '%s\n' "$MIN_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$MIN_VERSION" ]]; then
    print_success "Versão do Python compatível"
else
    print_error "Python $MIN_VERSION ou superior é necessário. Versão atual: $PYTHON_VERSION"
    exit 1
fi

# Verificar se git está instalado
if ! command -v git &> /dev/null; then
    print_warning "Git não encontrado. Instalação manual será necessária."
else
    print_success "Git encontrado"
fi

# Criar diretório de instalação
INSTALL_DIR="$HOME/petcare-dba-admin"
if [ -d "$INSTALL_DIR" ]; then
    print_warning "Diretório $INSTALL_DIR já existe"
    read -p "Deseja sobrescrever? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
        print_status "Diretório removido"
    else
        print_error "Instalação cancelada"
        exit 1
    fi
fi

print_status "Criando diretório de instalação: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Baixar código (se git disponível)
if command -v git &> /dev/null; then
    print_status "Clonando repositório..."
    git clone https://github.com/PetCareAi/dba.git .
else
    print_warning "Git não disponível. Por favor, baixe manualmente:"
    echo "  https://github.com/PetCareAi/dba/archive/main.zip"
    echo "  E extraia para: $INSTALL_DIR"
    read -p "Pressione Enter quando terminar..."
fi

# Verificar se arquivos essenciais existem
REQUIRED_FILES=("app.py" "requirements.txt" ".env.example")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Arquivo obrigatório não encontrado: $file"
        exit 1
    fi
done

print_success "Arquivos do projeto verificados"

# Criar ambiente virtual
print_status "Criando ambiente virtual Python..."
python3 -m venv venv

# Ativar ambiente virtual
print_status "Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
print_status "Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
print_status "Instalando dependências Python..."
pip install -r requirements.txt

# Criar arquivo de configuração
if [ ! -f ".env" ]; then
    print_status "Criando arquivo de configuração..."
    cp .env.example .env
    print_warning "IMPORTANTE: Configure o arquivo .env com suas credenciais!"
    print_status "Edite o arquivo: $INSTALL_DIR/.env"
fi

# Criar diretórios necessários
print_status "Criando estrutura de diretórios..."
mkdir -p logs
mkdir -p backups
mkdir -p exports
mkdir -p temp

# Configurar permissões
if [[ "$OS" != "Windows" ]]; then
    print_status "Configurando permissões..."
    chmod +x start.sh
    chmod +x configure.sh
    chmod +x run.sh
fi

# Criar arquivo de secrets do Streamlit
print_status "Criando configuração do Streamlit..."
mkdir -p .streamlit
cat > .streamlit/secrets.toml << 'EOF'
# Configurações do PetCare DBA Admin
# IMPORTANTE: Configure com suas credenciais reais

[app]
title = "PetCare DBA Admin"
version = "2.1.0"
debug_mode = true

[admin]
username = "admin"
password = "petcare2025"
email = "admin@petcareai.com"

[theme]
primary_color = "#2E8B57"
secondary_color = "#90EE90"
background_color = "#F0FFF0"
text_color = "#006400"

[supabase]
url = "https://seu-projeto.supabase.co"
anon_key = "sua_chave_anonima_aqui"
service_key = "sua_chave_service_aqui"

[gemini]
api_key = "sua_api_key_gemini_aqui"
model = "gemini-2.0-flash-exp"
base_url = "https://generativelanguage.googleapis.com"
EOF

# Testar instalação
print_status "Testando instalação..."
if python3 -c "import streamlit, supabase, pandas, plotly" 2>/dev/null; then
    print_success "Dependências instaladas corretamente"
else
    print_error "Erro na instalação das dependências"
    exit 1
fi

# Instruções finais
print_success "Instalação concluída com sucesso!"
echo ""
echo -e "${YELLOW}📋 PRÓXIMOS PASSOS:${NC}"
echo ""
echo "1. 📝 Configure suas credenciais:"
echo "   - Edite: $INSTALL_DIR/.env"
echo "   - Edite: $INSTALL_DIR/.streamlit/secrets.toml"
echo ""
echo "2. 🗄️ Configure o Supabase:"
echo "   - Crie um projeto em https://supabase.com"
echo "   - Execute os scripts SQL em database/"
echo "   - Adicione as credenciais nos arquivos de config"
echo ""
echo "3. 🤖 Configure o Google Gemini (opcional):"
echo "   - Obtenha API key em https://ai.google.dev"
echo "   - Adicione a chave nos arquivos de config"
echo ""
echo "4. 🚀 Execute a aplicação:"
echo "   cd $INSTALL_DIR"
echo "   ./run.sh"
echo ""
echo "5. 🌐 Acesse no navegador:"
echo "   http://localhost:8501"
echo ""
echo "👤 Login padrão:"
echo "   Usuário: admin"
echo "   Senha: petcare2025"
echo ""
print_warning "IMPORTANTE: Altere as credenciais padrão antes de usar em produção!"
echo ""
print_success "Instalação finalizada! Consulte README.md para mais informações."
