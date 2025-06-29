# Contributing to PetCare DBA Admin

Obrigado por seu interesse em contribuir com o PetCare DBA Admin! Este documento fornece diretrizes e informações sobre como contribuir para o projeto.

## 🎯 Como Contribuir

### 1. Tipos de Contribuições Aceitas

- 🐛 **Correção de Bugs**: Relatórios e correções de problemas
- ✨ **Novas Funcionalidades**: Implementação de recursos solicitados
- 📚 **Documentação**: Melhorias na documentação e exemplos
- 🎨 **Interface**: Melhorias na experiência do usuário
- ⚡ **Performance**: Otimizações de código e banco de dados
- 🧪 **Testes**: Adição de testes automatizados
- 🌐 **Tradução**: Tradução para outros idiomas

### 2. Processo de Contribuição

#### Antes de Começar
1. Verifique se já existe uma issue relacionada ao seu problema/funcionalidade
2. Para mudanças significativas, abra uma issue primeiro para discussão
3. Fork o repositório
4. Clone seu fork localmente

#### Configurando o Ambiente
```bash
# Clone seu fork
git clone https://github.com/SEU_USUARIO/petcare-dba-admin.git
cd petcare-dba-admin

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações
```

#### Fazendo Mudanças
1. Crie uma branch para sua feature/correção:
   ```bash
   git checkout -b feature/nome-da-feature
   # ou
   git checkout -b fix/nome-do-bug
   ```

2. Faça suas mudanças seguindo os padrões do projeto
3. Teste suas mudanças localmente
4. Commit suas mudanças:
   ```bash
   git add .
   git commit -m "feat: adiciona nova funcionalidade X"
   ```

#### Enviando Pull Request
1. Push para seu fork:
   ```bash
   git push origin feature/nome-da-feature
   ```

2. Abra um Pull Request no GitHub com:
   - Título claro e descritivo
   - Descrição detalhada das mudanças
   - Screenshots (se aplicável)
   - Referência à issue relacionada

## 📝 Padrões de Código

### Python/Streamlit
- Siga PEP 8 para formatação
- Use type hints quando possível
- Documente funções complexas
- Mantenha funções pequenas e focadas
- Use nomes descritivos para variáveis

### SQL
- Use UPPERCASE para palavras-chave SQL
- Indente subconsultas adequadamente
- Comente queries complexas
- Use aliases descritivos

### Documentação
- Use Markdown para documentação
- Inclua exemplos práticos
- Mantenha screenshots atualizados
- Documente APIs e configurações

## 🐛 Relatando Bugs

### Antes de Relatar
- Verifique se o bug já foi reportado
- Teste na versão mais recente
- Reproduza o problema consistentemente

### Informações Necessárias
Inclua no relatório:
- **Versão**: Versão do PetCare DBA Admin
- **Ambiente**: SO, versão Python, navegador
- **Passos**: Como reproduzir o problema
- **Resultado Esperado**: O que deveria acontecer
- **Resultado Atual**: O que acontece
- **Screenshots/Logs**: Evidências do problema

### Template de Bug Report
```markdown
## Descrição do Bug
Descrição clara e concisa do problema.

## Passos para Reproduzir
1. Vá para '...'
2. Clique em '....'
3. Veja erro

## Comportamento Esperado
O que você esperava que acontecesse.

## Screenshots
Se aplicável, adicione screenshots.

## Ambiente
- OS: [ex: Ubuntu 20.04]
- Python: [ex: 3.11]
- Navegador: [ex: Chrome 91]
- Versão: [ex: v2.0.0]

## Informações Adicionais
Qualquer outro contexto sobre o problema.
```

## ✨ Solicitando Funcionalidades

### Template de Feature Request
```markdown
## É sua solicitação relacionada a um problema?
Descrição clara do problema. Ex: Eu fico frustrado quando [...]

## Descreva a solução que você gostaria
Descrição clara do que você quer que aconteça.

## Descreva alternativas consideradas
Descrição de soluções alternativas consideradas.

## Contexto adicional
Screenshots, mockups, ou contexto adicional.
```

## 🧪 Testes

### Executando Testes
```bash
# Testes básicos de funcionalidade
python -m pytest tests/

# Testes de interface (quando disponível)
streamlit run app.py
```

### Criando Testes
- Adicione testes para novas funcionalidades
- Teste casos de borda
- Inclua testes de integração para componentes críticos
- Teste com diferentes configurações de banco

## 📋 Checklist do Pull Request

Antes de enviar seu PR, verifique:

- [ ] Código segue os padrões do projeto
- [ ] Mudanças foram testadas localmente
- [ ] Documentação foi atualizada (se necessário)
- [ ] Commit messages são claros
- [ ] Não há arquivos desnecessários incluídos
- [ ] Screenshots adicionados (para mudanças de UI)
- [ ] Issue relacionada está referenciada

## 🔄 Processo de Review

1. **Automated Checks**: GitHub Actions executam verificações automáticas
2. **Code Review**: Mantenedores revisam o código
3. **Testing**: Testes em diferentes ambientes
4. **Documentation**: Verificação de documentação
5. **Merge**: Após aprovação, PR é integrado

## 🚀 Primeiros Passos

### Good First Issues
Procure por issues marcadas com:
- `good first issue`: Bom para iniciantes
- `help wanted`: Ajuda é bem-vinda
- `documentation`: Melhorias na documentação

### Áreas que Precisam de Ajuda
- 📱 Interface mobile/responsiva
- 🌐 Tradução para outros idiomas
- 🧪 Testes automatizados
- 📊 Novos tipos de relatórios
- ⚡ Otimizações de performance
- 🔒 Melhorias de segurança

## 📞 Precisa de Ajuda?

- 📧 **Email**: dev@petcareai.com
- 💬 **Discord**: [PetCare Community](https://discord.gg/petcare)
- 📖 **Documentação**: [docs.petcareai.com](https://docs.petcareai.com)
- 🐛 **Issues**: [GitHub Issues](https://github.com/petcareai/dba-admin/issues)

## 📜 Código de Conduta

Este projeto adere ao [Código de Conduta](CODE_OF_CONDUCT.md). Ao participar, você está concordando em seguir essas diretrizes.

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a [Licença MIT](LICENSE).

---

**Obrigado por ajudar a tornar o PetCare DBA Admin melhor! 🐾**
