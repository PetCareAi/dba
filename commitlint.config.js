// Configuração do commitlint para padronização de mensagens de commit
// Baseado na convenção Conventional Commits

module.exports = {
  // Extende a configuração convencional
  extends: ['@commitlint/config-conventional'],
  
  // Regras personalizadas para o projeto PetCare DBA Admin
  rules: {
    // Tipos permitidos de commit
    'type-enum': [
      2,
      'always',
      [
        'feat',      // Nova funcionalidade
        'fix',       // Correção de bug
        'docs',      // Documentação
        'style',     // Formatação, ponto e vírgula, etc
        'refactor',  // Refatoração de código
        'perf',      // Melhoria de performance
        'test',      // Testes
        'chore',     // Manutenção
        'ci',        // CI/CD
        'build',     // Sistema de build
        'revert',    // Reverter commit
        'security',  // Correções de segurança
        'deps',      // Atualizações de dependências
        'config',    // Configurações
        'db',        // Mudanças no banco de dados
        'ui',        // Mudanças na interface
        'api',       // Mudanças na API
        'ai'         // Mudanças relacionadas à IA
      ]
    ],
    
    // Escopo é opcional mas quando usado deve seguir padrões
    'scope-enum': [
      2,
      'always',
      [
        'auth',         // Autenticação
        'dashboard',    // Dashboard
        'sql-editor',   // Editor SQL
        'projects',     // Gerenciamento de projetos
        'tables',       // Visualização de tabelas
        'dba-ops',      // Operações DBA
        'ai-assistant', // Assistente IA
        'settings',     // Configurações
        'database',     // Conexões e operações de BD
        'supabase',     // Integrações Supabase
        'gemini',       // Integração Google Gemini
        'security',     // Segurança e RLS
        'performance',  // Otimizações de performance
        'monitoring',   // Monitoramento
        'backup',       // Backup e restore
        'scripts',      // Scripts SQL
        'ui',           // Interface do usuário
        'api',          // Integrações de API
        'docs',         // Documentação
        'tests',        // Testes
        'deps',         // Dependências
        'config',       // Configurações
        'deploy',       // Deploy e infraestrutura
        'core'          // Funcionalidades core
      ]
    ],
    
    // Formato do header (tipo(escopo): descrição)
    'header-max-length': [2, 'always', 100],
    'header-min-length': [2, 'always', 10],
    
    // Tipo é obrigatório
    'type-empty': [2, 'never'],
    'type-case': [2, 'always', 'lower-case'],
    
    // Escopo é opcional
    'scope-empty': [0, 'never'],
    'scope-case': [2, 'always', 'lower-case'],
    
    // Descrição
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    'subject-case': [2, 'always', 'lower-case'],
    
    // Corpo do commit
    'body-leading-blank': [2, 'always'],
    'body-max-line-length': [2, 'always', 200],
    
    // Footer
    'footer-leading-blank': [2, 'always'],
    
    // Quebras (BREAKING CHANGES)
    'breaking-change-format': [
      2,
      'always',
      /^BREAKING CHANGE: [\s\S]*$/
    ]
  },
  
  // Configurações específicas
  parserPreset: {
    parserOpts: {
      // Padrão para interpretar o header
      headerPattern: /^(\w*)(?:\(([\w$.\-*/ ]*)\))?: (.*)$/,
      headerCorrespondence: ['type', 'scope', 'subject'],
      
      // Padrões para notas especiais
      noteKeywords: ['BREAKING CHANGE', 'BREAKING-CHANGE'],
      
      // Padrão para referências
      referenceActions: [
        'close',
        'closes',
        'closed',
        'fix',
        'fixes',
        'fixed',
        'resolve',
        'resolves',
        'resolved'
      ],
      
      // Padrão para issues
      issuePrefixes: ['#']
    }
  },
  
  // Configurações de ignores
  ignores: [
    // Ignorar commits de merge
    (commit) => commit.includes('Merge'),
    
    // Ignorar commits automáticos do dependabot
    (commit) => commit.includes('dependabot'),
    
    // Ignorar commits de release automáticos
    (commit) => commit.includes('chore(release)'),
    
    // Ignorar commits do GitHub
    (commit) => commit.includes('github-actions')
  ],
  
  // Configuração de help
  helpUrl: 'https://github.com/conventional-changelog/commitlint/#what-is-commitlint',
  
  // Prompt personalizado (se usando commitizen)
  prompt: {
    questions: {
      type: {
        description: 'Selecione o tipo de mudança que você está commitando:',
        enum: {
          feat: {
            description: 'Uma nova funcionalidade',
            title: 'Features'
          },
          fix: {
            description: 'Uma correção de bug',
            title: 'Bug Fixes'
          },
          docs: {
            description: 'Mudanças apenas na documentação',
            title: 'Documentation'
          },
          style: {
            description: 'Mudanças que não afetam o significado do código (espaço em branco, formatação, ponto e vírgula, etc)',
            title: 'Styles'
          },
          refactor: {
            description: 'Uma mudança de código que não corrige um bug nem adiciona uma funcionalidade',
            title: 'Code Refactoring'
          },
          perf: {
            description: 'Uma mudança de código que melhora a performance',
            title: 'Performance Improvements'
          },
          test: {
            description: 'Adicionando testes faltando ou corrigindo testes existentes',
            title: 'Tests'
          },
          chore: {
            description: 'Mudanças no processo de build ou ferramentas auxiliares e bibliotecas',
            title: 'Chores'
          },
          ci: {
            description: 'Mudanças nos arquivos e scripts de configuração de CI',
            title: 'Continuous Integrations'
          },
          build: {
            description: 'Mudanças que afetam o sistema de build ou dependências externas',
            title: 'Builds'
          },
          revert: {
            description: 'Reverte um commit anterior',
            title: 'Reverts'
          },
          security: {
            description: 'Correções de segurança',
            title: 'Security'
          },
          deps: {
            description: 'Atualizações de dependências',
            title: 'Dependencies'
          },
          db: {
            description: 'Mudanças relacionadas ao banco de dados',
            title: 'Database'
          },
          ai: {
            description: 'Mudanças relacionadas ao assistente IA',
            title: 'AI Assistant'
          }
        }
      },
      scope: {
        description: 'Qual é o escopo desta mudança (ex: auth, dashboard, sql-editor)?'
      },
      subject: {
        description: 'Escreva uma descrição curta e imperativa da mudança:'
      },
      body: {
        description: 'Forneça uma descrição mais longa da mudança:'
      },
      isBreaking: {
        description: 'Existem mudanças que quebram compatibilidade?'
      },
      breakingBody: {
        description: 'Um commit BREAKING CHANGE requer um corpo. Por favor, insira uma descrição mais longa do próprio commit:'
      },
      breaking: {
        description: 'Descreva as mudanças que quebram compatibilidade:'
      },
      isIssueAffected: {
        description: 'Esta mudança afeta alguma issue aberta?'
      },
      issuesBody: {
        description: 'Se issues são fechadas, o commit requer um corpo. Por favor, insira uma descrição mais longa do próprio commit:'
      },
      issues: {
        description: 'Adicione referências de issues (ex: "fix #123", "re #123".):'
      }
    }
  }
};
