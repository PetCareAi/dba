# 📊 Notebooks de Análise - PetCare DBA Admin

Este diretório contém notebooks Jupyter para análise de dados, prototipagem e documentação de análises específicas do sistema PetCare DBA Admin.

## 📁 Estrutura dos Notebooks

### 📈 Análises de Performance
- `performance_analysis.ipynb` - Análise de performance do banco de dados
- `query_optimization.ipynb` - Otimização de consultas SQL
- `index_analysis.ipynb` - Análise e recomendações de índices

### 📊 Relatórios Executivos
- `dashboard_metrics.ipynb` - Métricas para dashboard executivo
- `usage_statistics.ipynb` - Estatísticas de uso do sistema
- `growth_analysis.ipynb` - Análise de crescimento de dados

### 🔍 Análises Exploratórias
- `data_exploration.ipynb` - Exploração inicial dos dados
- `user_behavior.ipynb` - Análise de comportamento dos usuários
- `system_health.ipynb` - Monitoramento de saúde do sistema

### 🤖 Machine Learning
- `predictive_maintenance.ipynb` - Manutenção preditiva do banco
- `anomaly_detection.ipynb` - Detecção de anomalias
- `capacity_planning.ipynb` - Planejamento de capacidade

### 📚 Tutoriais e Documentação
- `getting_started.ipynb` - Introdução ao uso dos notebooks
- `api_examples.ipynb` - Exemplos de uso da API
- `best_practices.ipynb` - Melhores práticas

## 🚀 Como Usar

### Pré-requisitos
```bash
# Instalar Jupyter e dependências
pip install jupyter pandas numpy matplotlib seaborn plotly

# Instalar dependências específicas do projeto
pip install -r ../requirements.txt
```

### Iniciando o Jupyter
```bash
# No diretório raiz do projeto
jupyter lab notebooks/

# Ou para Jupyter Notebook clássico
jupyter notebook notebooks/
```

### Configuração do Ambiente
1. Copie o arquivo `.env.example` para `.env`
2. Configure as variáveis de ambiente necessárias
3. Execute o notebook `getting_started.ipynb` para verificar a configuração

## 📋 Convenções

### Estrutura dos Notebooks
1. **Header Cell**: Título, descrição e metadados
2. **Setup**: Imports e configurações
3. **Configuração**: Parâmetros e conexões
4. **Análise**: Código principal
5. **Resultados**: Visualizações e conclusões
6. **Conclusões**: Resumo e próximos passos

### Nomenclatura
- Use snake_case para nomes de arquivos
- Prefixos: `analysis_`, `report_`, `tutorial_`, `ml_`
- Inclua data no nome se for análise temporal: `analysis_performance_2025_01.ipynb`

### Documentação
- Cada célula deve ter comentários explicativos
- Use Markdown para explicações detalhadas
- Inclua referências e fontes quando aplicável

## 🔧 Utilitários

### Scripts de Apoio
- `utils/database_connection.py` - Conexão com banco de dados
- `utils/data_processing.py` - Funções de processamento
- `utils/visualization.py` - Funções de visualização
- `utils/metrics.py` - Cálculo de métricas

### Templates
- `templates/analysis_template.ipynb` - Template para análises
- `templates/report_template.ipynb` - Template para relatórios
- `templates/ml_template.ipynb` - Template para ML

## 📊 Dados de Exemplo

O diretório `sample_data/` contém conjuntos de dados de exemplo para testes:
- `sample_users.csv` - Dados de usuários
- `sample_queries.csv` - Histórico de consultas
- `sample_metrics.csv` - Métricas de sistema

## ⚙️ Configuração do Kernel

### Kernel Python Personalizado
Para criar um kernel com as dependências do projeto:

```bash
# Criar ambiente virtual
python -m venv venv_notebooks
source venv_notebooks/bin/activate  # Linux/Mac
# ou
venv_notebooks\Scripts\activate     # Windows

# Instalar dependências
pip install ipykernel
pip install -r ../requirements.txt

# Registrar kernel
python -m ipykernel install --user --name=petcare_analysis --display-name="PetCare Analysis"
```

## 🔒 Segurança e Boas Práticas

### Dados Sensíveis
- **NUNCA** commite notebooks com dados reais
- Use dados anonimizados ou sintéticos
- Configure `.gitignore` para excluir arquivos de dados

### Limpeza antes do Commit
```bash
# Usar nbstripout para remover outputs
pip install nbstripout
nbstripout --install

# Ou limpar manualmente
jupyter nbconvert --clear-output --inplace *.ipynb
```

## 📈 Métricas e KPIs

### Métricas de Performance
- Tempo de execução de consultas
- Uso de CPU e memória
- Throughput do banco de dados
- Latência de resposta

### Métricas de Negócio
- Número de usuários ativos
- Consultas por usuário
- Tempo de sessão médio
- Taxa de erro

## 🔄 Automação

### Execução Programada
```bash
# Script para executar notebooks automaticamente
python scripts/run_scheduled_analysis.py

# Usando papermill para parametrização
papermill analysis_template.ipynb output/analysis_$(date +%Y%m%d).ipynb -p data_date "2025-01-15"
```

### CI/CD Integration
- Notebooks de teste são executados no pipeline
- Relatórios são gerados automaticamente
- Resultados são enviados por email/Slack

## 📞 Suporte

Para dúvidas sobre os notebooks:
- Consulte a documentação interna
- Abra uma issue no repositório
- Entre em contato com a equipe de dados

## 📝 Changelog

### 2025-01-15
- Adicionado template para análises de ML
- Melhoradas funções de visualização
- Incluído suporte para dados do Supabase

### 2025-01-01
- Estrutura inicial dos notebooks
- Templates básicos criados
- Documentação inicial
