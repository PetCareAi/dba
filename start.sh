#!/bin/bash

# PetCare DBA Admin - Script de Inicialização

echo "🐾 Iniciando PetCare DBA Admin..."

# Verificar se está no diretório correto
if [ ! -f "app.py" ]; then
    echo "❌ Erro: app.py não encontrado!"
    echo "Execute este script no diretório do projeto."
    exit 1
fi

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "⚡ Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Verificar se o Streamlit está instalado
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit não encontrado!"
    echo "Instalando dependências..."
    pip install -r requirements.txt
fi

# Configurar variáveis de ambiente
export PYTHONPATH=${PYTHONPATH}:$(pwd)

# Iniciar aplicação
echo "🚀 Iniciando aplicação..."
echo "🌐 Acesse: http://localhost:8501"
echo "👤 Usuário: admin"
echo "🔑 Senha: petcare2025"
echo ""

streamlit run app.py