#!/bin/bash

# PetCare DBA Admin - Script de Execução
# Sistema de Gerenciamento de Banco de Dados para PetCareAI

set -e  # Para no primeiro erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
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

# Banner de inicialização
echo -e "${GREEN}"
cat << "EOF"
🐾 =====================================================
   PetCare DBA Admin - Inicializando Sistema
   Sistema de Gerenciamento de Banco de Dados
=====================================================
EOF
echo -e "${NC}"

# Verificar se está no diretório correto
if [ ! -f "app.py" ]; then
    print_error "app.py não encontrado!"
    print_status "Execute este script no diretório do projeto."
    exit 1
fi

print_status "Iniciando PetCare DBA Admin..."

# Função para verificar porta
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Porta em uso
    else
        return 1  # Porta livre
    fi
}

# Função para obter porta disponível
get_available_port() {
    local start_port=8501
    local max_port=8510
    
    for ((port=$start_port; port<=$max_port; port++)); do
        if ! check_port $port; then
            echo $port
            return
        fi
    done
    
    echo $start_port  # Fallback
}

# Verificar dependências
print_status "Verificando dependências..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 não encontrado!"
    print_status "Instale Python 3.9+ e execute install.sh"
    exit 1
fi

# Verificar ambiente virtual
if [ ! -d "venv" ]; then
    print_error "Ambiente virtual não encontrado!"
    print_status "Execute install.sh para configurar o ambiente"
    exit 1
fi

# Ativar ambiente virtual
print_status "Ativando ambiente virtual..."
source venv/bin/activate

if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_success "Ambiente virtual ativo: $(basename $VIRTUAL_ENV)"
else
    print_error "Falha ao ativar ambiente virtual"
    exit 1
fi

# Verificar arquivo de configuração
if [ ! -f ".env" ]; then
    print_warning "Arquivo .env não encontrado!"
    print_status "Execute configure.sh para configurar o sistema"
    
    read -p "Deseja executar a configuração agora? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./configure.sh
    else
        print_error "Configuração necessária. Execute configure.sh"
        exit 1
    fi
fi

# Verificar configuração do Streamlit
if [ ! -f ".streamlit/secrets.toml" ]; then
    print_warning "Configuração do Streamlit não encontrada!"
    print_status "Execute configure.sh para configurar o sistema"
    exit 1
fi

# Verificar dependências Python
print_status "Verificando dependências Python..."
if ! python3 -c "import streamlit, supabase, pandas, plotly" 2>/dev/null; then
    print_warning "Dependências Python incompletas ou com problemas"
    print_status "Reinstalando dependências..."
    pip install -r requirements.txt
fi

# Verificar se Streamlit está instalado
if ! command -v streamlit &> /dev/null; then
    print_error "Streamlit não encontrado!"
    print_status "Instalando Streamlit..."
    pip install streamlit
fi

# Preparar ambiente
print_status "Preparando ambiente de execução..."

# Criar diretórios necessários se não existirem
mkdir -p logs
mkdir -p backups
mkdir -p exports
mkdir -p temp
mkdir -p uploads

# Configurar variáveis de ambiente
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_SERVER_ENABLE_CORS=false

# Verificar configurações críticas
print_status "Verificando configurações..."

# Verificar se Supabase está configurado
if grep -q "sua_chave_anonima_aqui" .env; then
    print_warning "Supabase não configurado - funcionará em modo demonstração"
else
    print_success "Supabase configurado"
fi

# Verificar se Google Gemini está configurado
if grep -q "sua_api_key_gemini_aqui" .env; then
    print_warning "Google Gemini não configurado - assistente IA indisponível"
else
    print_success "Google Gemini configurado"
fi

# Determinar porta
DEFAULT_PORT=8501
if [ -n "$1" ]; then
    PORT=$1
    print_status "Porta especificada: $PORT"
else
    if check_port $DEFAULT_PORT; then
        print_warning "Porta $DEFAULT_PORT em uso"
        PORT=$(get_available_port)
        print_status "Usando porta alternativa: $PORT"
    else
        PORT=$DEFAULT_PORT
    fi
fi

# Limpar cache se solicitado
if [[ "$2" == "--clear-cache" ]] || [[ "$1" == "--clear-cache" ]]; then
    print_status "Limpando cache do Streamlit..."
    rm -rf ~/.streamlit/
    print_success "Cache limpo"
fi

# Verificar modo de execução
RUN_MODE="normal"
if [[ "$*" == *"--dev"* ]]; then
    RUN_MODE="development"
    print_status "Modo de desenvolvimento ativado"
elif [[ "$*" == *"--debug"* ]]; then
    RUN_MODE="debug"
    print_status "Modo debug ativado"
elif [[ "$*" == *"--prod"* ]]; then
    RUN_MODE="production"
    print_status "Modo produção ativado"
fi

# Configurar variáveis baseadas no modo
case $RUN_MODE in
    "development")
        export STREAMLIT_SERVER_ENABLE_CORS=true
        export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
        export DEBUG_MODE=true
        ;;
    "debug")
        export STREAMLIT_SERVER_ENABLE_CORS=true
        export STREAMLIT_LOG_LEVEL=debug
        export DEBUG_MODE=true
        ;;
    "production")
        export STREAMLIT_SERVER_HEADLESS=true
        export STREAMLIT_SERVER_ENABLE_CORS=false
        export DEBUG_MODE=false
        ;;
esac

# Backup automático de configurações
BACKUP_DIR="backups"
if [ -d "$BACKUP_DIR" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    if [ -f ".env" ]; then
        cp .env "$BACKUP_DIR/env_backup_$TIMESTAMP" 2>/dev/null || true
    fi
    print_status "Backup de configurações realizado"
fi

# Verificar logs anteriores
LOG_FILE="logs/app_$(date +%Y%m%d).log"
if [ -f "$LOG_FILE" ]; then
    LOG_SIZE=$(wc -c < "$LOG_FILE")
    if [ $LOG_SIZE -gt 10485760 ]; then  # 10MB
        print_warning "Log muito grande ($(($LOG_SIZE / 1048576))MB)"
        mv "$LOG_FILE" "${LOG_FILE}.old"
        print_status "Log anterior arquivado"
    fi
fi

# Mostrar informações do sistema
echo ""
print_status "=== INFORMAÇÕES DO SISTEMA ==="
echo "🐍 Python: $(python3 --version)"
echo "🌊 Streamlit: $(streamlit version | head -n1)"
echo "🐾 App: $(grep APP_TITLE .env | cut -d'=' -f2) $(grep APP_VERSION .env | cut -d'=' -f2)"
echo "🌐 Porta: $PORT"
echo "📁 Diretório: $(pwd)"
echo "🖥️ Sistema: $(uname -s)"
echo "👤 Usuário: $(whoami)"
echo "⏰ Início: $(date '+%d/%m/%Y %H:%M:%S')"
echo ""

# Exibir URLs de acesso
echo -e "${CYAN}🌐 ACESSO À APLICAÇÃO:${NC}"
echo ""
echo "Local:     http://localhost:$PORT"
echo "Rede:      http://$(hostname -I | awk '{print $1}'):$PORT"
if command -v ip &> /dev/null; then
    EXTERNAL_IP=$(ip route get 8.8.8.8 | awk -F"src " 'NR==1{split($2,a," ");print a[1]}')
    echo "Externo:   http://$EXTERNAL_IP:$PORT"
fi
echo ""

# Exibir credenciais padrão
echo -e "${YELLOW}🔐 CREDENCIAIS DE ACESSO:${NC}"
echo ""
ADMIN_USER=$(grep ADMIN_USERNAME .env | cut -d'=' -f2)
ADMIN_PASS=$(grep ADMIN_PASSWORD .env | cut -d'=' -f2)
echo "Usuário:   $ADMIN_USER"
echo "Senha:     $ADMIN_PASS"
echo ""

print_warning "IMPORTANTE: Altere as credenciais padrão em produção!"
echo ""

# Verificar se há atualizações (se git disponível)
if command -v git &> /dev/null && [ -d ".git" ]; then
    print_status "Verificando atualizações..."
    git fetch origin main 2>/dev/null || true
    BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null || echo "0")
    if [ "$BEHIND" -gt "0" ]; then
        print_warning "Existem $BEHIND commit(s) novos disponíveis"
        print_status "Execute 'git pull origin main' para atualizar"
    fi
fi

# Função para cleanup ao sair
cleanup() {
    echo ""
    print_status "Encerrando aplicação..."
    
    # Matar processos Streamlit
    pkill -f "streamlit run" 2>/dev/null || true
    
    # Log de encerramento
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Aplicação encerrada" >> "$LOG_FILE"
    
    print_success "Aplicação encerrada com sucesso"
    exit 0
}

# Configurar trap para cleanup
trap cleanup SIGINT SIGTERM

# Função para monitorar aplicação
monitor_app() {
    sleep 5
    while true; do
        if ! pgrep -f "streamlit run" > /dev/null; then
            print_error "Aplicação parou inesperadamente"
            exit 1
        fi
        sleep 30
    done
}

# Criar arquivo de PID
echo $ > .app.pid

# Log de inicialização
echo "$(date '+%Y-%m-%d %H:%M:%S') - Aplicação iniciada na porta $PORT" >> "$LOG_FILE"

# Exibir comandos úteis
echo -e "${PURPLE}📋 COMANDOS ÚTEIS:${NC}"
echo ""
echo "• Parar aplicação:    Ctrl+C"
echo "• Limpar cache:       ./run.sh --clear-cache"
echo "• Modo debug:         ./run.sh --debug"
echo "• Modo desenvolvimento: ./run.sh --dev"
echo "• Porta customizada:  ./run.sh 8502"
echo ""

print_success "Iniciando aplicação..."
echo ""
echo -e "${GREEN}=== STREAMLIT INICIANDO ===${NC}"
echo ""

# Iniciar aplicação
if [[ "$RUN_MODE" == "debug" ]]; then
    # Modo debug com saída detalhada
    streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --logger.level=debug
elif [[ "$RUN_MODE" == "development" ]]; then
    # Modo desenvolvimento
    streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.runOnSave=true
else
    # Modo normal/produção com monitoramento
    monitor_app &
    MONITOR_PID=$!
    
    streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
    
    # Cleanup do monitor
    kill $MONITOR_PID 2>/dev/null || true
fi

# Se chegou até aqui, a aplicação foi encerrada normalmente
cleanup
