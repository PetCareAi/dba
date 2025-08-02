# Makefile para PetCare DBA Admin
# Automatiza tarefas comuns de desenvolvimento e deployment

# Variáveis de configuração
PYTHON := python3
PIP := pip3
STREAMLIT := streamlit
APP_FILE := app.py
PORT := 8501
HOST := localhost

# Configurações de ambiente
VENV_DIR := venv
REQUIREMENTS := requirements.txt
DEV_REQUIREMENTS := requirements-dev.txt

# Configurações de teste
TEST_DIR := tests
COVERAGE_DIR := htmlcov
MIN_COVERAGE := 80

# Configurações de build
BUILD_DIR := build
DIST_DIR := dist
DOCS_DIR := docs

# Cores para output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

.PHONY: help install install-dev clean test run build deploy docs lint format security check

# Comando padrão
.DEFAULT_GOAL := help

## Comandos principais

help: ## Mostra esta mensagem de ajuda
	@echo "$(BLUE)PetCare DBA Admin - Comandos Disponíveis$(NC)"
	@echo "======================================"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Instala dependências de produção
	@echo "$(YELLOW)Instalando dependências de produção...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQUIREMENTS)
	@echo "$(GREEN)Dependências instaladas com sucesso!$(NC)"

install-dev: ## Instala dependências de desenvolvimento
	@echo "$(YELLOW)Instalando dependências de desenvolvimento...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQUIREMENTS)
	@if [ -f $(DEV_REQUIREMENTS) ]; then $(PIP) install -r $(DEV_REQUIREMENTS); fi
	$(PIP) install pytest pytest-cov black flake8 bandit safety pre-commit
	@echo "$(GREEN)Dependências de desenvolvimento instaladas!$(NC)"

venv: ## Cria ambiente virtual
	@echo "$(YELLOW)Criando ambiente virtual...$(NC)"
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(GREEN)Ambiente virtual criado em $(VENV_DIR)$(NC)"
	@echo "$(BLUE)Para ativar: source $(VENV_DIR)/bin/activate$(NC)"

setup: venv install-dev ## Configuração completa do ambiente de desenvolvimento
	@echo "$(YELLOW)Configurando hooks do Git...$(NC)"
	@if [ -f .githooks/pre-commit ]; then \
		cp .githooks/pre-commit .git/hooks/; \
		chmod +x .git/hooks/pre-commit; \
	fi
	@if [ -f .githooks/pre-push ]; then \
		cp .githooks/pre-push .git/hooks/; \
		chmod +x .git/hooks/pre-push; \
	fi
	@echo "$(GREEN)Ambiente configurado com sucesso!$(NC)"

## Comandos de execução

run: ## Executa a aplicação localmente
	@echo "$(YELLOW)Iniciando PetCare DBA Admin...$(NC)"
	$(STREAMLIT) run $(APP_FILE) --server.port=$(PORT) --server.address=$(HOST)

run-prod: ## Executa em modo produção
	@echo "$(YELLOW)Iniciando em modo produção...$(NC)"
	$(STREAMLIT) run $(APP_FILE) --server.port=$(PORT) --server.headless=true

debug: ## Executa em modo debug
	@echo "$(YELLOW)Iniciando em modo debug...$(NC)"
	STREAMLIT_LOGGER_LEVEL=debug $(STREAMLIT) run $(APP_FILE) --server.port=$(PORT)

## Comandos de teste e qualidade

test: ## Executa todos os testes
	@echo "$(YELLOW)Executando testes...$(NC)"
	$(PYTHON) -m pytest $(TEST_DIR)/ -v

test-cov: ## Executa testes com cobertura
	@echo "$(YELLOW)Executando testes com cobertura...$(NC)"
	$(PYTHON) -m pytest $(TEST_DIR)/ --cov=. --cov-report=html --cov-report=term
	@echo "$(GREEN)Relatório de cobertura gerado em $(COVERAGE_DIR)/$(NC)"

test-watch: ## Executa testes em modo watch
	@echo "$(YELLOW)Executando testes em modo watch...$(NC)"
	$(PYTHON) -m pytest $(TEST_DIR)/ -f

lint: ## Verifica qualidade do código
	@echo "$(YELLOW)Verificando qualidade do código...$(NC)"
	flake8 $(APP_FILE) --max-line-length=120 --ignore=E203,W503
	@echo "$(GREEN)Verificação de lint concluída!$(NC)"

format: ## Formata o código
	@echo "$(YELLOW)Formatando código...$(NC)"
	black $(APP_FILE) --line-length=120
	@echo "$(GREEN)Código formatado!$(NC)"

format-check: ## Verifica se o código está formatado
	@echo "$(YELLOW)Verificando formatação...$(NC)"
	black --check $(APP_FILE) --line-length=120

security: ## Verifica vulnerabilidades de segurança
	@echo "$(YELLOW)Verificando segurança...$(NC)"
	bandit -r . -x $(TEST_DIR)/
	safety check
	@echo "$(GREEN)Verificação de segurança concluída!$(NC)"

check: lint format-check security test ## Executa todas as verificações

## Comandos de build e deploy

clean: ## Remove arquivos temporários e de build
	@echo "$(YELLOW)Limpando arquivos temporários...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf $(BUILD_DIR)/ $(DIST_DIR)/ *.egg-info/
	rm -rf $(COVERAGE_DIR)/ .pytest_cache/ .coverage
	rm -rf .mypy_cache/ .tox/
	@echo "$(GREEN)Limpeza concluída!$(NC)"

build: clean ## Cria pacote para distribuição
	@echo "$(YELLOW)Criando pacote...$(NC)"
	$(PYTHON) setup.py sdist bdist_wheel
	@echo "$(GREEN)Pacote criado em $(DIST_DIR)/$(NC)"

package: ## Cria pacote Docker
	@echo "$(YELLOW)Criando imagem Docker...$(NC)"
	docker build -t petcare-dba-admin:latest .
	@echo "$(GREEN)Imagem Docker criada!$(NC)"

deploy-staging: ## Deploy para ambiente de staging
	@echo "$(YELLOW)Fazendo deploy para staging...$(NC)"
	@if [ -f release-scripts/deploy-staging.sh ]; then \
		bash release-scripts/deploy-staging.sh; \
	else \
		echo "$(RED)Script de deploy não encontrado!$(NC)"; \
	fi

deploy-prod: ## Deploy para produção
	@echo "$(RED)ATENÇÃO: Deploy para produção!$(NC)"
	@read -p "Tem certeza? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(YELLOW)Fazendo deploy para produção...$(NC)"; \
		if [ -f release-scripts/deploy-production.sh ]; then \
			bash release-scripts/deploy-production.sh; \
		else \
			echo "$(RED)Script de deploy não encontrado!$(NC)"; \
		fi; \
	else \
		echo "$(BLUE)Deploy cancelado.$(NC)"; \
	fi

## Comandos de documentação

docs: ## Gera documentação
	@echo "$(YELLOW)Gerando documentação...$(NC)"
	@if [ -d $(DOCS_DIR) ]; then \
		cd $(DOCS_DIR) && make html; \
	else \
		echo "$(BLUE)Documentação será gerada em formato simples$(NC)"; \
		mkdir -p $(DOCS_DIR); \
		echo "# Documentação do PetCare DBA Admin" > $(DOCS_DIR)/README.md; \
	fi
	@echo "$(GREEN)Documentação gerada!$(NC)"

docs-serve: docs ## Serve documentação localmente
	@echo "$(YELLOW)Servindo documentação...$(NC)"
	@if command -v python3 -m http.server >/dev/null 2>&1; then \
		cd $(DOCS_DIR) && $(PYTHON) -m http.server 8000; \
	else \
		echo "$(RED)Servidor HTTP não disponível$(NC)"; \
	fi

## Comandos de banco de dados

db-setup: ## Configura banco de dados
	@echo "$(YELLOW)Configurando banco de dados...$(NC)"
	@if [ -f database/setup.sql ]; then \
		echo "$(BLUE)Execute o script database/setup.sql no seu banco$(NC)"; \
	else \
		echo "$(RED)Script de setup não encontrado!$(NC)"; \
	fi

db-migrate: ## Executa migrações do banco
	@echo "$(YELLOW)Executando migrações...$(NC)"
	@if [ -d database/migrations ]; then \
		echo "$(BLUE)Execute os scripts em database/migrations/$(NC)"; \
	else \
		echo "$(BLUE)Nenhuma migração encontrada$(NC)"; \
	fi

## Comandos de desenvolvimento

dev-watch: ## Monitora mudanças e reinicia
	@echo "$(YELLOW)Monitorando mudanças...$(NC)"
	@if command -v watchdog >/dev/null 2>&1; then \
		watchmedo auto-restart --patterns="*.py" --recursive -- $(STREAMLIT) run $(APP_FILE); \
	else \
		echo "$(RED)watchdog não instalado. Install: pip install watchdog$(NC)"; \
		$(MAKE) run; \
	fi

profile: ## Executa profiling da aplicação
	@echo "$(YELLOW)Executando profiling...$(NC)"
	$(PYTHON) -m cProfile -o app.profile -s tottime $(APP_FILE)
	@echo "$(GREEN)Profile salvo em app.profile$(NC)"

requirements: ## Atualiza arquivo de requirements
	@echo "$(YELLOW)Atualizando requirements...$(NC)"
	$(PIP) freeze > $(REQUIREMENTS)
	@echo "$(GREEN)Requirements atualizados!$(NC)"

## Informações do sistema

info: ## Mostra informações do ambiente
	@echo "$(BLUE)Informações do Ambiente$(NC)"
	@echo "======================"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Pip: $$($(PIP) --version)"
	@echo "Streamlit: $$($(STREAMLIT) --version 2>/dev/null || echo 'Não instalado')"
	@echo "Diretório atual: $$(pwd)"
	@echo "Usuário: $$(whoami)"
	@echo "Data: $$(date)"

status: ## Mostra status do projeto
	@echo "$(BLUE)Status do Projeto$(NC)"
	@echo "=================="
	@echo "Arquivos Python: $$(find . -name '*.py' | wc -l)"
	@echo "Linhas de código: $$(find . -name '*.py' -exec wc -l {} + | tail -1 | awk '{print $$1}')"
	@echo "Último commit: $$(git log -1 --pretty=format:'%h - %s (%cr)' 2>/dev/null || echo 'Git não inicializado')"
	@echo "Branch atual: $$(git branch --show-current 2>/dev/null || echo 'Git não inicializado')"
