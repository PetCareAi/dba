# 🚀 Scripts de Release - PetCare DBA Admin

Este diretório contém scripts para automatizar o processo de release e deployment da aplicação PetCare DBA Admin.

## 📁 Estrutura dos Scripts

### 🔧 Scripts de Build
- `build.sh` - Script principal de build
- `build-docker.sh` - Build da imagem Docker
- `build-package.sh` - Criação de pacotes de distribuição

### 🚀 Scripts de Deploy
- `deploy-staging.sh` - Deploy para ambiente de staging
- `deploy-production.sh` - Deploy para produção
- `deploy-rollback.sh` - Rollback de deploy

### ✅ Scripts de Validação
- `validate-environment.sh` - Validação do ambiente
- `health-check.sh` - Verificação de saúde da aplicação
- `smoke-tests.sh` - Testes básicos pós-deploy

### 📊 Scripts de Monitoramento
- `monitor-deployment.sh` - Monitoramento durante deploy
- `collect-metrics.sh` - Coleta de métricas de deploy
- `generate-report.sh` - Geração de relatórios

## 🔐 Configuração de Segurança

### Variáveis de Ambiente Necessárias
```bash
# Configurações de banco de dados
export SUPABASE_URL="sua_url_supabase"
export SUPABASE_SERVICE_KEY="sua_chave_servico"

# Configurações de deploy
export DEPLOY_ENV="staging|production"
export DEPLOY_VERSION="v1.0.0"

# Notificações
export SLACK_WEBHOOK_URL="url_do_webhook"
export EMAIL_NOTIFICATIONS="admin@petcareai.com"
```

### Arquivos de Configuração
- `config/staging.env` - Configurações de staging
- `config/production.env` - Configurações de produção
- `config/secrets.env.example` - Template de secrets

## 🚀 Processo de Release

### 1. Preparação
```bash
# Executar validações
./validate-environment.sh

# Criar tag de release
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### 2. Build
```bash
# Build completo
./build.sh v1.0.0

# Ou build específico
./build-docker.sh v1.0.0
```

### 3. Deploy Staging
```bash
# Deploy para staging
./deploy-staging.sh v1.0.0

# Executar testes
./smoke-tests.sh staging
```

### 4. Deploy Produção
```bash
# Deploy para produção (requer confirmação)
./deploy-production.sh v1.0.0
```

## 📋 Checklist de Release

### Pré-Release
- [ ] Todos os testes passaram
- [ ] Documentação atualizada
- [ ] Changelog atualizado
- [ ] Versão bumped
- [ ] Tag criada no Git

### Durante Release
- [ ] Build executado com sucesso
- [ ] Deploy staging concluído
- [ ] Testes de fumaça passaram
- [ ] Aprovação para produção obtida

### Pós-Release
- [ ] Deploy produção concluído
- [ ] Health checks passaram
- [ ] Métricas coletadas
- [ ] Notificações enviadas
- [ ] Documentação de release criada

## 🔧 Scripts Utilitários

### Backup e Restore
- `backup-database.sh` - Backup do banco antes do deploy
- `restore-database.sh` - Restore em caso de problemas

### Configuração
- `setup-environment.sh` - Configuração inicial do ambiente
- `update-dependencies.sh` - Atualização de dependências

### Monitoramento
- `check-logs.sh` - Verificação de logs
- `performance-check.sh` - Verificação de performance

## 📊 Métricas e Logging

### Métricas Coletadas
- Tempo total de deploy
- Taxa de sucesso/falha
- Downtime durante deploy
- Performance pós-deploy

### Logs
- Todos os scripts geram logs em `logs/`
- Formato: `YYYY-MM-DD_HH-MM-SS_script-name.log`
- Retenção: 30 dias

## 🚨 Troubleshooting

### Problemas Comuns

#### Deploy Falha
```bash
# Verificar logs
tail -f logs/latest-deploy.log

# Verificar status dos serviços
./health-check.sh

# Rollback se necessário
./deploy-rollback.sh
```

#### Problemas de Conectividade
```bash
# Testar conexão com banco
./validate-environment.sh --check-db

# Verificar configurações de rede
./health-check.sh --network
```

### Contatos de Emergência
- DevOps Lead: devops@petcareai.com
- DBA Lead: dba@petcareai.com
- Admin: admin@petcareai.com

## 🔄 Versionamento

### Estratégia de Versionamento
- Semantic Versioning (SemVer)
- Formato: MAJOR.MINOR.PATCH
- Exemplo: v1.2.3

### Branches
- `main` - Produção
- `develop` - Desenvolvimento
- `release/v1.2.3` - Preparação de release
- `hotfix/v1.2.4` - Correções críticas

## 📝 Exemplos de Uso

### Release Completo
```bash
# 1. Preparar release
./prepare-release.sh v1.2.0

# 2. Build e teste
./build.sh v1.2.0
./validate-build.sh v1.2.0

# 3. Deploy staging
./deploy-staging.sh v1.2.0
./run-integration-tests.sh

# 4. Deploy produção
./deploy-production.sh v1.2.0
```

### Hotfix Urgente
```bash
# 1. Build hotfix
./build.sh v1.1.1 --hotfix

# 2. Deploy direto produção
./deploy-production.sh v1.1.1 --skip-staging

# 3. Monitorar
./monitor-deployment.sh v1.1.1
```
