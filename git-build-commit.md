# 🚀 Git Build & Commit Guide - PetCare DBA Admin

## 📋 Guia de Commits e Build do Projeto

Este documento descreve o processo de desenvolvimento, build e versionamento para o projeto PetCare DBA Admin.

## 🌿 Estrutura de Branches

### Branches Principais

- **`main`** - Branch principal de produção
  - Código estável e testado
  - Deploy automático quando configurado
  - Proteção contra push direto

- **`develop`** - Branch de desenvolvimento
  - Integração de features
  - Testes automatizados
  - Code review obrigatório

- **`release/x.x.x`** - Branches de release
  - Preparação para versões
  - Bug fixes finais
  - Documentação de release

### Branches de Feature

```bash
feature/nome-da-funcionalidade
hotfix/correcao-critica
bugfix/nome-do-bug
docs/atualizacao-documentacao
```

## 📝 Convenção de Commits

### Formato Padrão

```
<tipo>(<escopo>): <descrição>

<corpo da mensagem>

<rodapé>
```

### Tipos de Commit

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `feat` | Nova funcionalidade | `feat(dashboard): adiciona métricas em tempo real` |
| `fix` | Correção de bug | `fix(auth): corrige validação de senha` |
| `docs` | Documentação | `docs(readme): atualiza instruções de instalação` |
| `style` | Formatação/estilo | `style(css): melhora responsividade mobile` |
| `refactor` | Refatoração | `refactor(database): otimiza queries SQL` |
| `test` | Testes | `test(auth): adiciona testes de login` |
| `chore` | Manutenção | `chore(deps): atualiza dependências` |
| `perf` | Performance | `perf(sql): otimiza query de tabelas` |
| `ci` | CI/CD | `ci(github): adiciona workflow de deploy` |
| `build` | Build/deploy | `build(docker): atualiza Dockerfile` |

### Escopos Sugeridos

- `auth` - Autenticação e autorização
- `dashboard` - Dashboard principal
- `database` - Operações de banco de dados
- `ui` - Interface do usuário
- `api` - Integrações de API
- `config` - Configurações
- `docs` - Documentação
- `test` - Testes
- `deploy` - Deploy e CI/CD

### Exemplos de Commits

```bash
# Feature
feat(ai): adiciona assistente IA com Google Gemini

Implementa assistente IA para análise de banco de dados:
- Integração com Google Gemini 2.0 Flash
- Contexto em tempo real do banco
- Histórico de conversas no Supabase
- Interface de chat interativa

Closes #123

# Bug Fix
fix(auth): corrige validação de email em configurações

- Melhora regex de validação
- Adiciona mensagens de erro específicas
- Testa com diferentes formatos de email

Fixes #456

# Documentation
docs(api): adiciona documentação da API do Supabase

- Documenta endpoints principais
- Exemplos de uso
- Políticas RLS
- Scripts de criação de tabelas
```

## 🔧 Processo de Desenvolvimento

### 1. Configuração Inicial

```bash
# Clone do repositório
git clone https://github.com/PetCareAi/dba.git
cd dba

# Configuração do ambiente
./install.sh
./configure.sh

# Configuração do Git
git config user.name "Seu Nome"
git config user.email "seu.email@petcareai.com"
```

### 2. Criação de Feature Branch

```bash
# Atualizar branch principal
git checkout main
git pull origin main

# Criar nova branch
git checkout -b feature/nova-funcionalidade

# Ou usar o flow completo
git flow feature start nova-funcionalidade
```

### 3. Desenvolvimento

```bash
# Fazer alterações
# Executar testes locais
./run.sh --dev

# Adicionar arquivos
git add .

# Commit seguindo convenção
git commit -m "feat(dashboard): adiciona gráfico de performance

- Implementa gráfico em tempo real
- Usa Plotly para visualização
- Dados do Supabase em cache
- Atualização a cada 30 segundos

Closes #789"
```

### 4. Push e Pull Request

```bash
# Push da branch
git push origin feature/nova-funcionalidade

# Criar Pull Request no GitHub
# Seguir template de PR
# Aguardar code review
```

## 🏗️ Build e Deploy

### Build Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Verificar código
flake8 app.py
black --check app.py

# Executar testes
python -m pytest tests/

# Build para produção
./build.sh
```

### Build com Docker

```bash
# Build da imagem
docker build -t petcare-dba-admin:latest .

# Executar container
docker run -p 8501:8501 petcare-dba-admin:latest

# Build multi-stage
docker build --target production -t petcare-dba-admin:prod .
```

### Deploy Automático

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Production
        run: ./deploy.sh
```

## 📊 Versionamento Semântico

### Formato: `MAJOR.MINOR.PATCH`

- **MAJOR** - Mudanças incompatíveis na API
- **MINOR** - Novas funcionalidades compatíveis
- **PATCH** - Correções de bugs compatíveis

### Processo de Release

```bash
# Preparar release
git checkout develop
git pull origin develop

# Criar branch de release
git checkout -b release/2.1.0

# Atualizar versão
echo "APP_VERSION=2.1.0" > .version

# Commit de versão
git commit -m "chore(release): bump version to 2.1.0"

# Merge para main
git checkout main
git merge release/2.1.0

# Tag da versão
git tag -a v2.1.0 -m "Release v2.1.0

- Nova funcionalidade X
- Melhoria Y
- Correção Z"

# Push tags
git push origin main --tags

# Merge back para develop
git checkout develop
git merge main
```

## 🔍 Code Review

### Checklist para Pull Requests

#### Funcionalidade
- [ ] Funcionalidade implementada conforme especificação
- [ ] Testes unitários adicionados/atualizados
- [ ] Documentação atualizada
- [ ] Sem breaking changes não documentadas

#### Código
- [ ] Código segue padrões do projeto
- [ ] Variáveis e funções bem nomeadas
- [ ] Comentários em partes complexas
- [ ] Sem código comentado/debug

#### Performance
- [ ] Queries SQL otimizadas
- [ ] Cache implementado onde necessário
- [ ] Sem vazamentos de memória
- [ ] Tratamento de erros adequado

#### Segurança
- [ ] Validação de entrada de dados
- [ ] Sanitização de SQL
- [ ] Credenciais não expostas
- [ ] Políticas RLS implementadas

### Template de Pull Request

```markdown
## 📝 Descrição

Breve descrição das mudanças implementadas.

## 🎯 Tipo de Mudança

- [ ] Bug fix
- [ ] Nova funcionalidade
- [ ] Breaking change
- [ ] Documentação

## ✅ Checklist

- [ ] Código testado localmente
- [ ] Testes passando
- [ ] Documentação atualizada
- [ ] Self-review realizado

## 📊 Testes

Descreva os testes realizados.

## 📱 Screenshots

Se aplicável, adicione screenshots.

## 📋 Notas Adicionais

Informações adicionais para os reviewers.
```

## 🛠️ Ferramentas de Desenvolvimento

### Pre-commit Hooks

```bash
# Instalar pre-commit
pip install pre-commit

# Configurar hooks
pre-commit install

# Executar manualmente
pre-commit run --all-files
```

### Configuração `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
        args: [--max-line-length=88]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.2.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

## 🔄 Workflow Completo

### Desenvolvimento de Feature

```bash
# 1. Configuração
git checkout main
git pull origin main
git checkout -b feature/assistente-ia

# 2. Desenvolvimento
# Fazer mudanças...
git add .
git commit -m "feat(ai): implementa assistente com Gemini"

# 3. Testes
./run.sh --dev
python -m pytest

# 4. Push e PR
git push origin feature/assistente-ia
# Criar PR no GitHub

# 5. Após aprovação
git checkout main
git pull origin main
git branch -d feature/assistente-ia
```

### Hotfix Crítico

```bash
# 1. Criar hotfix
git checkout main
git checkout -b hotfix/correcao-critica

# 2. Correção
# Fazer correção...
git commit -m "fix(auth): corrige vulnerabilidade de segurança"

# 3. Deploy rápido
git checkout main
git merge hotfix/correcao-critica
git tag -a v2.0.1 -m "Hotfix v2.0.1"
git push origin main --tags

# 4. Merge para develop
git checkout develop
git merge main
```

## 📚 Recursos Adicionais

### Links Úteis

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

### Comandos Git Úteis

```bash
# Desfazer último commit (mantém mudanças)
git reset --soft HEAD~1

# Rebase interativo
git rebase -i HEAD~3

# Cherry-pick
git cherry-pick <commit-hash>

# Stash temporário
git stash
git stash pop

# Ver diferenças
git diff HEAD~1
git diff --cached

# Log bonito
git log --oneline --graph --all
```

## 🎯 Metas de Qualidade

- **Coverage de Testes**: > 80%
- **Performance**: < 2s tempo de carregamento
- **Compatibilidade**: Python 3.9+
- **Segurança**: Zero vulnerabilidades críticas
- **Documentação**: 100% APIs documentadas

---

**Desenvolvido para PetCareAI** 🐾  
*Sistema de Gerenciamento de Banco de Dados*
