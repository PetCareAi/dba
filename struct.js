const fs = require('fs');
const path = require('path');

// Lista completa de arquivos e pastas que devem ser ignorados
const ignoredItems = new Set([
  // Dependências e build
  'node_modules',
  'bower_components',
  'vendor',
  'dist',
  'build',
  'out',
  '.next',
  '.nuxt',
  '.output',
  
  // Ambientes virtuais Python
  'venv',
  'env',
  '.venv',
  'virtualenv',
  '__pycache__',
  '*.pyc',
  '.pytest_cache',
  
  // Lock files
  'package-lock.json',
  'yarn.lock',
  'pnpm-lock.yaml',
  'composer.lock',
  'Pipfile.lock',
  'poetry.lock',
  'Gemfile.lock',
  'go.sum',
  'Cargo.lock',
  
  // Controle de versão (mas não .gitattributes, .gitmodules que são importantes)
  '.git',
  '.svn',
  '.hg',
  
  // IDEs e editores
  '.vscode',
  '.idea',
  '.vs',
  '*.swp',
  '*.swo',
  '*~',
  '.sublime-project',
  '.sublime-workspace',
  
  // Sistema operacional
  '.DS_Store',
  'Thumbs.db',
  'desktop.ini',
  '$RECYCLE.BIN',
  
  // Logs e temporários
  '*.log',
  'logs',
  '.log',
  '*.tmp',
  '*.temp',
  'tmp',
  'temp',
  '.cache',
  '.temp',
  '.tmp',
  'cache',
  
  // Coverage e testes
  'coverage',
  '.coverage',
  '.nyc_output',
  'junit.xml',
  '.jest',
  
  // Arquivos compilados
  '*.class',
  '*.o',
  '*.so',
  '*.dll',
  '*.exe',
  
  // Mobile
  'android/app/build',
  'ios/build',
  '.expo',
  '.expo-shared',
  
  // Terraform
  '.terraform',
  '*.tfstate',
  '*.tfstate.backup',
  
  // Outros
  'Backup*',
  '*.backup',
  '*.bak',
  '.sass-cache',
  '.parcel-cache'
]);

// Padrões de arquivos para ignorar (usando regex)
const ignoredPatterns = [
  /\.log$/i,               // Arquivos de log
  /\.tmp$/i,               // Arquivos temporários
  /\.temp$/i,              // Arquivos temporários
  /\.cache$/i,             // Arquivos de cache
  /~$/,                    // Backups do editor
  /\.swp$/i,               // Arquivos swap do vim
  /\.swo$/i,               // Arquivos swap do vim
  /\.pyc$/i,               // Python compiled
  /\.pyo$/i,               // Python optimized
  /\.class$/i,             // Java compiled
  /\.o$/i,                 // Object files
  /\.so$/i,                // Shared objects
  /\.dll$/i,               // Windows DLLs
  /\.exe$/i,               // Windows executables
  /\.bak$/i,               // Backup files
  /\.backup$/i,            // Backup files
  /^npm-debug\.log/i,      // npm debug logs
  /^yarn-debug\.log/i,     // yarn debug logs
  /^yarn-error\.log/i,     // yarn error logs
];

// Mapeamento de extensões para emojis
const extensionEmojis = {
  // Arquivos de código
  '.js': '⚡',
  '.jsx': '⚛️',
  '.ts': '📘',
  '.tsx': '⚛️',
  '.vue': '💚',
  '.py': '🐍',
  '.java': '☕',
  '.php': '🐘',
  '.rb': '💎',
  '.go': '🔵',
  '.rs': '🦀',
  '.cpp': '⚙️',
  '.c': '⚙️',
  '.cs': '🔷',
  '.swift': '🍎',
  '.kt': '🟣',
  
  // Arquivos web
  '.html': '📄',
  '.css': '🎨',
  '.scss': '🎨',
  '.sass': '🎨',
  '.less': '🎨',
  
  // Imagens
  '.png': '🖼️',
  '.jpg': '🖼️',
  '.jpeg': '🖼️',
  '.gif': '🖼️',
  '.svg': '🎨',
  '.ico': '🎯',
  '.webp': '🖼️',
  
  // Documentos
  '.md': '📝',
  '.txt': '📄',
  '.pdf': '📕',
  '.doc': '📄',
  '.docx': '📄',
  
  // Configuração
  '.json': '⚙️',
  '.xml': '📋',
  '.yml': '⚙️',
  '.yaml': '⚙️',
  '.toml': '⚙️',
  '.ini': '⚙️',
  '.config': '⚙️',
  
  // Scripts
  '.sh': '📜',
  '.bat': '📜',
  '.ps1': '📜',
  
  // Build e configuração
  '.cff': '📋',
  '.in': '⚙️',
  
  // Outros
  '.zip': '📦',
  '.tar': '📦',
  '.gz': '📦',
};

// Mapeamento de nomes de pastas para emojis
const folderEmojis = {
  // Estrutura principal
  'src': '📁',
  'lib': '📚',
  'public': '🌐',
  'static': '🌐',
  'assets': '📦',
  
  // Componentes e UI
  'components': '🧩',
  'pages': '📄',
  'views': '👁️',
  'screens': '📱',
  'layouts': '📐',
  'templates': '📋',
  'widgets': '🧩',
  
  // Estilos
  'styles': '🎨',
  'css': '🎨',
  'scss': '🎨',
  'sass': '🎨',
  'themes': '🎨',
  
  // Dados e API
  'data': '💾',
  'api': '🌐',
  'services': '⚙️',
  'models': '🗄️',
  'database': '🗄️',
  'db': '🗄️',
  'migrations': '🗄️',
  
  // Lógica de negócio
  'controllers': '🎮',
  'routes': '🛣️',
  'middleware': '🔗',
  'helpers': '🛠️',
  'utils': '🔧',
  'tools': '🛠️',
  
  // Estado e contexto
  'store': '🏪',
  'context': '🔄',
  'hooks': '🪝',
  'reducers': '🔄',
  
  // Configuração
  'config': '⚙️',
  'settings': '⚙️',
  'env': '🔐',
  
  // Testes
  'test': '🧪',
  'tests': '🧪',
  '__tests__': '🧪',
  'spec': '🧪',
  'e2e': '🧪',
  
  // Documentação
  'docs': '📚',
  'documentation': '📚',
  'guides': '📖',
  
  // Build e deploy
  'build': '🏗️',
  'dist': '📦',
  'output': '📤',
  'scripts': '📜',
  
  // Segurança e autenticação
  'auth': '🔐',
  'security': '🛡️',
  'admin': '👑',
  
  // Internacionalização
  'locales': '🌐',
  'i18n': '🌐',
  'translations': '🌐',
  'lang': '🌐',
  
  // Recursos
  'images': '🖼️',
  'img': '🖼️',
  'icons': '🎯',
  'fonts': '🔤',
  'media': '📺',
  
  // Plugins e extensões
  'plugins': '🔌',
  'extensions': '🔌',
  'addons': '🔌',
  
  // Git hooks
  '.githooks': '🪝',
  'hooks': '🪝',
  
  // CI/CD
  '.github': '🔧',
  '.gitlab': '🔧',
  'ci': '🔧',
  'workflows': '🔧',
  
  // Containers
  'docker': '🐳',
  'k8s': '⚓',
  'kubernetes': '⚓',
};

// Mapeamento específico de nomes de arquivos
const fileNameEmojis = {
  // Package managers
  'package.json': '📦',
  'composer.json': '📦',
  'requirements.txt': '📦',
  'Pipfile': '📦',
  'Gemfile': '💎',
  'go.mod': '🔵',
  'Cargo.toml': '🦀',
  'pom.xml': '☕',
  'build.gradle': '🐘',
  
  // Configuração TypeScript/JavaScript
  'tsconfig.json': '📘',
  'jsconfig.json': '📘',
  'babel.config.js': '🔄',
  'webpack.config.js': '📦',
  'vite.config.js': '⚡',
  'rollup.config.js': '📦',
  'next.config.js': '⚡',
  'nuxt.config.js': '💚',
  'vue.config.js': '💚',
  'svelte.config.js': '🧡',
  'tailwind.config.js': '🎨',
  'postcss.config.js': '🎨',
  
  // Qualidade de código
  '.eslintrc': '📏',
  '.eslintrc.js': '📏',
  '.eslintrc.json': '📏',
  '.prettierrc': '✨',
  '.prettierrc.js': '✨',
  '.prettierrc.json': '✨',
  'commitlint.config.js': '📝',
  '.editorconfig': '📝',
  
  // Git e controle de versão
  '.gitignore': '🚫',
  '.gitattributes': '⚙️',
  '.gitmodules': '🔗',
  '.git-blame-ignore-revs': '🚫',
  
  // CI/CD
  '.travis.yml': '🔧',
  'dependabot.yml': '🤖',
  '.pre-commit-config.yaml': '🪝',
  'CODEOWNERS': '👥',
  
  // Testes
  'jest.config.js': '🧪',
  'vitest.config.js': '🧪',
  'cypress.json': '🧪',
  'playwright.config.js': '🧪',
  
  // Docker
  'Dockerfile': '🐳',
  'docker-compose.yml': '🐳',
  'docker-compose.yaml': '🐳',
  '.dockerignore': '🚫',
  
  // Documentação do projeto
  'README.md': '📖',
  'README.rst': '📖',
  'README.txt': '📖',
  'architecture.md': '🏗️',
  'archtecture.md': '🏗️',
  'todo.md': '📝',
  'TODO.md': '📝',
  'release.md': '🚀',
  'RELEASE.md': '🚀',
  'requisitos-funcionais.md': '📋',
  'requisitos.md': '📋',
  'CHANGELOG.md': '📜',
  'CHANGES.md': '📜',
  'HISTORY.md': '📜',
  'Roadmap.md': '🗺️',
  'ROADMAP.md': '🗺️',
  
  // Contribuição e comunidade
  'CONTRIBUTING.md': '🤝',
  'CONTRIBUTORS.md': '👥',
  'contributors.yml': '👥',
  'CODE_OF_CONDUCT.md': '📜',
  'MAINTAINING.md': '🛠️',
  'MAINTAINING': '🛠️',
  
  // Segurança e legal
  'SECURITY.md': '🛡️',
  'LICENSE': '📜',
  'LICENSE.md': '📜',
  'LICENSE.txt': '📜',
  'COPYRIGHT': '©️',
  'NOTICE.md': '📢',
  'NOTICE': '📢',
  
  // Build e instalação
  'BUILDING.md': '🏗️',
  'BUILDING': '🏗️',
  'Makefile': '🔨',
  'makefile': '🔨',
  'MANIFEST.in': '📋',
  'install.sh': '💾',
  'configure.sh': '⚙️',
  'run.sh': '🚀',
  'start.sh': '🚀',
  'stop.sh': '⏹️',
  'build.sh': '🏗️',
  'deploy.sh': '🚀',
  
  // Citação e metadados
  'citation.cff': '📚',
  'CITATION.cff': '📚',
  
  // Troubleshooting
  'Troubleshooting': '🔧',
  'TROUBLESHOOTING.md': '🔧',
  'troubleshooting.md': '🔧',
  
  // Versioning
  '.version': '🏷️',
  'VERSION': '🏷️',
  'version.txt': '🏷️',
  
  // Arquivos principais
  'index.html': '🏠',
  'index.js': '🚀',
  'index.ts': '🚀',
  'main.js': '🚀',
  'main.ts': '🚀',
  'app.js': '⚛️',
  'App.js': '⚛️',
  'App.tsx': '⚛️',
  'server.js': '🖥️',
  'server.ts': '🖥️',
  
  // Configuração PWA/Web
  'manifest.json': '📱',
  'sw.js': '⚙️',
  'service-worker.js': '⚙️',
  'favicon.ico': '🎯',
  'robots.txt': '🤖',
  'sitemap.xml': '🗺️',
  '.htaccess': '⚙️',
  'web.config': '⚙️',
  
  // Ambiente
  '.env': '🔐',
  '.env.example': '🔐',
  '.env.local': '🔐',
  '.env.development': '🔐',
  '.env.production': '🔐',
  '.env.test': '🔐',
  
  // Git hooks específicos
  'pre-commit': '🪝',
  'pre-push': '🪝',
  'commit-msg': '🪝',
  'post-commit': '🪝',
  'post-merge': '🪝',
  'pre-receive': '🪝',
  'post-receive': '🪝',
  'update': '🪝',
};

function shouldIgnore(itemName) {
  // Verifica se está na lista de itens ignorados
  if (ignoredItems.has(itemName)) {
    return true;
  }
  
  // Verifica se corresponde a algum padrão ignorado
  return ignoredPatterns.some(pattern => pattern.test(itemName));
}

function getEmoji(itemPath, isDirectory) {
  const itemName = path.basename(itemPath);
  
  if (isDirectory) {
    return folderEmojis[itemName.toLowerCase()] || '📁';
  }
  
  // Verifica primeiro por nome específico do arquivo
  if (fileNameEmojis[itemName]) {
    return fileNameEmojis[itemName];
  }
  
  // Depois verifica por extensão
  const ext = path.extname(itemName).toLowerCase();
  return extensionEmojis[ext] || '📄';
}

function generateComment(itemPath, isDirectory) {
  const itemName = path.basename(itemPath);
  
  // Comentários específicos baseados no nome
  const comments = {
    // ===== ARQUIVOS DE CONFIGURAÇÃO DE PROJETO =====
    'package.json': 'Dependências e scripts do projeto NPM',
    'composer.json': 'Dependências e autoload do PHP',
    'requirements.txt': 'Dependências do Python',
    'Pipfile': 'Dependências do Python com Pipenv',
    'Gemfile': 'Dependências do Ruby',
    'go.mod': 'Módulo e dependências do Go',
    'Cargo.toml': 'Manifesto e dependências do Rust',
    'pom.xml': 'Configuração do projeto Maven (Java)',
    'build.gradle': 'Script de build do Gradle',
    
    // ===== CONFIGURAÇÃO TYPESCRIPT/JAVASCRIPT =====
    'tsconfig.json': 'Configuração do compilador TypeScript',
    'jsconfig.json': 'Configuração do JavaScript para IDEs',
    'babel.config.js': 'Configuração do transpilador Babel',
    'webpack.config.js': 'Configuração do bundler Webpack',
    'vite.config.js': 'Configuração do build tool Vite',
    'rollup.config.js': 'Configuração do bundler Rollup',
    'next.config.js': 'Configuração do framework Next.js',
    'nuxt.config.js': 'Configuração do framework Nuxt.js',
    'vue.config.js': 'Configuração de build do Vue.js',
    'svelte.config.js': 'Configuração do Svelte',
    'tailwind.config.js': 'Configuração do Tailwind CSS',
    'postcss.config.js': 'Configuração do processador PostCSS',
    
    // ===== QUALIDADE DE CÓDIGO =====
    '.eslintrc': 'Regras do linter ESLint',
    '.eslintrc.js': 'Configuração do ESLint em JavaScript',
    '.eslintrc.json': 'Configuração do ESLint em JSON',
    '.prettierrc': 'Configuração do formatador Prettier',
    '.prettierrc.js': 'Configuração do Prettier em JavaScript',
    '.prettierrc.json': 'Configuração do Prettier em JSON',
    'commitlint.config.js': 'Regras para validação de commits',
    '.editorconfig': 'Configuração de formatação entre editores',
    
    // ===== GIT E CONTROLE DE VERSÃO =====
    '.gitignore': 'Arquivos e pastas ignorados pelo Git',
    '.gitattributes': 'Atributos específicos de arquivos no Git',
    '.gitmodules': 'Configuração de submódulos Git',
    '.git-blame-ignore-revs': 'Commits ignorados no git blame',
    
    // ===== CI/CD E AUTOMAÇÃO =====
    '.travis.yml': 'Configuração do Travis CI',
    'dependabot.yml': 'Configuração do Dependabot para atualizações',
    '.pre-commit-config.yaml': 'Configuração de hooks pre-commit',
    'CODEOWNERS': 'Definição de responsáveis por áreas do código',
    
    // ===== TESTES =====
    'jest.config.js': 'Configuração do framework de testes Jest',
    'vitest.config.js': 'Configuração do framework de testes Vitest',
    'cypress.json': 'Configuração de testes E2E com Cypress',
    'playwright.config.js': 'Configuração de testes com Playwright',
    
    // ===== DOCKER =====
    'Dockerfile': 'Instruções para build da imagem Docker',
    'docker-compose.yml': 'Orquestração de múltiplos containers',
    'docker-compose.yaml': 'Orquestração de múltiplos containers',
    '.dockerignore': 'Arquivos ignorados no build Docker',
    
    // ===== DOCUMENTAÇÃO DO PROJETO =====
    'README.md': 'Documentação principal e guia de introdução',
    'README.rst': 'Documentação principal em reStructuredText',
    'README.txt': 'Documentação principal em texto simples',
    'architecture.md': 'Documentação da arquitetura do sistema',
    'archtecture.md': 'Documentação da arquitetura do sistema',
    'todo.md': 'Lista de tarefas pendentes e melhorias',
    'TODO.md': 'Lista de tarefas pendentes e melhorias',
    'release.md': 'Notas e planejamento de releases',
    'RELEASE.md': 'Notas e planejamento de releases',
    'requisitos-funcionais.md': 'Especificação dos requisitos funcionais',
    'requisitos.md': 'Documentação de requisitos do sistema',
    'CHANGELOG.md': 'Histórico detalhado de mudanças e versões',
    'CHANGES.md': 'Registro de alterações entre versões',
    'HISTORY.md': 'Histórico do projeto e evolução',
    'Roadmap.md': 'Planejamento e cronograma de funcionalidades',
    'ROADMAP.md': 'Planejamento e cronograma de funcionalidades',
    
    // ===== CONTRIBUIÇÃO E COMUNIDADE =====
    'CONTRIBUTING.md': 'Guia para contribuidores do projeto',
    'CONTRIBUTORS.md': 'Lista de pessoas que contribuíram',
    'contributors.yml': 'Dados estruturados dos contribuidores',
    'CODE_OF_CONDUCT.md': 'Código de conduta da comunidade',
    'MAINTAINING.md': 'Guia para mantenedores do projeto',
    'MAINTAINING': 'Guia para mantenedores do projeto',
    
    // ===== SEGURANÇA E LEGAL =====
    'SECURITY.md': 'Política de segurança e vulnerabilidades',
    'LICENSE': 'Licença de uso e distribuição do software',
    'LICENSE.md': 'Licença de uso e distribuição do software',
    'LICENSE.txt': 'Licença de uso e distribuição do software',
    'COPYRIGHT': 'Informações de direitos autorais',
    'NOTICE.md': 'Avisos legais e atribuições necessárias',
    'NOTICE': 'Avisos legais e atribuições necessárias',
    
    // ===== BUILD E INSTALAÇÃO =====
    'BUILDING.md': 'Instruções detalhadas para build do projeto',
    'BUILDING': 'Instruções detalhadas para build do projeto',
    'Makefile': 'Automação de build e tarefas do projeto',
    'makefile': 'Automação de build e tarefas do projeto',
    'MANIFEST.in': 'Especificação de arquivos para distribuição',
    'install.sh': 'Script de instalação automática',
    'configure.sh': 'Script de configuração do ambiente',
    'run.sh': 'Script para execução da aplicação',
    'start.sh': 'Script de inicialização do serviço',
    'stop.sh': 'Script para parar a aplicação',
    'build.sh': 'Script de build automatizado',
    'deploy.sh': 'Script de deploy para produção',
    
    // ===== CITAÇÃO E METADADOS =====
    'citation.cff': 'Formato de citação para trabalhos acadêmicos',
    'CITATION.cff': 'Formato de citação para trabalhos acadêmicos',
    
    // ===== TROUBLESHOOTING =====
    'Troubleshooting': 'Guia de resolução de problemas comuns',
    'TROUBLESHOOTING.md': 'Guia de resolução de problemas comuns',
    'troubleshooting.md': 'Guia de resolução de problemas comuns',
    
    // ===== VERSIONING =====
    '.version': 'Número da versão atual do projeto',
    'VERSION': 'Número da versão atual do projeto',
    'version.txt': 'Número da versão atual do projeto',
    
    // ===== ARQUIVOS PRINCIPAIS =====
    'index.html': 'Página principal da aplicação web',
    'index.js': 'Ponto de entrada principal da aplicação',
    'index.ts': 'Ponto de entrada principal em TypeScript',
    'main.js': 'Arquivo principal de execução',
    'main.ts': 'Arquivo principal de execução em TypeScript',
    'app.js': 'Configuração principal da aplicação',
    'App.js': 'Componente raiz da aplicação React',
    'App.tsx': 'Componente raiz da aplicação React em TypeScript',
    'server.js': 'Servidor HTTP principal',
    'server.ts': 'Servidor HTTP principal em TypeScript',
    
    // ===== PWA E WEB =====
    'manifest.json': 'Manifesto para Progressive Web App',
    'sw.js': 'Service Worker para funcionalidades offline',
    'service-worker.js': 'Service Worker para cache e offline',
    'favicon.ico': 'Ícone exibido na aba do navegador',
    'robots.txt': 'Instruções para crawlers de busca',
    'sitemap.xml': 'Mapa do site para SEO',
    '.htaccess': 'Configuração do servidor Apache',
    'web.config': 'Configuração do servidor IIS',
    
    // ===== VARIÁVEIS DE AMBIENTE =====
    '.env': 'Variáveis de ambiente (não versionado)',
    '.env.example': 'Exemplo de variáveis de ambiente',
    '.env.local': 'Variáveis de ambiente locais',
    '.env.development': 'Variáveis para ambiente de desenvolvimento',
    '.env.production': 'Variáveis para ambiente de produção',
    '.env.test': 'Variáveis para ambiente de testes',
    
    // ===== GIT HOOKS =====
    'pre-commit': 'Hook executado antes de cada commit',
    'pre-push': 'Hook executado antes de cada push',
    'commit-msg': 'Hook para validação de mensagens de commit',
    'post-commit': 'Hook executado após cada commit',
    'post-merge': 'Hook executado após merge de branches',
    'pre-receive': 'Hook do servidor antes de receber push',
    'post-receive': 'Hook do servidor após receber push',
    'update': 'Hook executado durante atualizações',
    
    // ===== PASTAS PRINCIPAIS =====
    'src': 'Código fonte principal da aplicação',
    'lib': 'Bibliotecas e módulos reutilizáveis',
    'public': 'Arquivos estáticos servidos publicamente',
    'static': 'Recursos estáticos (imagens, fonts, etc)',
    'assets': 'Recursos da aplicação (imagens, ícones, etc)',
    
    // ===== COMPONENTES E UI =====
    'components': 'Componentes de interface reutilizáveis',
    'pages': 'Páginas e rotas da aplicação',
    'views': 'Views e templates da aplicação',
    'screens': 'Telas da aplicação (mobile/desktop)',
    'layouts': 'Layouts base para páginas',
    'templates': 'Templates reutilizáveis',
    'widgets': 'Widgets e micro-componentes',
    
    // ===== ESTILOS =====
    'styles': 'Arquivos de estilo CSS/SCSS',
    'css': 'Folhas de estilo CSS',
    'scss': 'Arquivos Sass/SCSS',
    'sass': 'Arquivos Sass',
    'themes': 'Temas e variações visuais',
    
    // ===== DADOS E API =====
    'data': 'Dados estáticos e mocks',
    'api': 'Endpoints e configuração da API',
    'services': 'Serviços e integrações externas',
    'models': 'Modelos de dados e entidades',
    'database': 'Configuração e scripts de banco',
    'db': 'Arquivos relacionados ao banco de dados',
    'migrations': 'Scripts de migração do banco',
    
    // ===== LÓGICA DE NEGÓCIO =====
    'controllers': 'Controladores da aplicação',
    'routes': 'Definições de rotas e endpoints',
    'middleware': 'Middlewares de processamento',
    'helpers': 'Funções auxiliares e utilitários',
    'utils': 'Utilitários e funções genéricas',
    'tools': 'Ferramentas de desenvolvimento',
    
    // ===== ESTADO E CONTEXTO =====
    'store': 'Gerenciamento de estado global',
    'context': 'Contextos React/Vue',
    'hooks': 'Custom hooks e composables',
    'reducers': 'Reducers para gerenciamento de estado',
    
    // ===== CONFIGURAÇÃO =====
    'config': 'Arquivos de configuração',
    'settings': 'Configurações da aplicação',
    'env': 'Configurações de ambiente',
    
    // ===== TESTES =====
    'test': 'Testes automatizados',
    'tests': 'Suíte de testes',
    '__tests__': 'Testes Jest/React Testing Library',
    'spec': 'Especificações e testes',
    'e2e': 'Testes end-to-end',
    
    // ===== DOCUMENTAÇÃO =====
    'docs': 'Documentação técnica detalhada',
    'documentation': 'Documentação completa do projeto',
    'guides': 'Guias e tutoriais',
    
    // ===== BUILD E DEPLOY =====
    'build': 'Arquivos de build gerados',
    'dist': 'Distribuição otimizada para produção',
    'output': 'Saída de builds e compilações',
    'scripts': 'Scripts de automação e deploy',
    
    // ===== SEGURANÇA =====
    'auth': 'Autenticação e autorização',
    'security': 'Configurações de segurança',
    'admin': 'Funcionalidades administrativas',
    
    // ===== INTERNACIONALIZAÇÃO =====
    'locales': 'Arquivos de localização e idiomas',
    'i18n': 'Internacionalização da aplicação',
    'translations': 'Traduções para múltiplos idiomas',
    'lang': 'Arquivos de idioma',
    
    // ===== RECURSOS =====
    'images': 'Imagens e recursos visuais',
    'img': 'Imagens da aplicação',
    'icons': 'Ícones e elementos gráficos',
    'fonts': 'Fontes tipográficas customizadas',
    'media': 'Arquivos de mídia (vídeo, áudio)',
    
    // ===== PLUGINS =====
    'plugins': 'Plugins e extensões',
    'extensions': 'Extensões de funcionalidade',
    'addons': 'Complementos e add-ons',
    
    // ===== GIT HOOKS =====
    '.githooks': 'Scripts de automação Git customizados',
    'hooks': 'Hooks de automação do Git',
    
    // ===== CI/CD =====
    '.github': 'Configuração GitHub Actions e templates',
    '.gitlab': 'Configuração GitLab CI/CD',
    'ci': 'Scripts de integração contínua',
    'workflows': 'Workflows de automação',
    
    // ===== CONTAINERS =====
    'docker': 'Configuração e scripts Docker',
    'k8s': 'Manifests Kubernetes',
    'kubernetes': 'Configuração de deploy Kubernetes',
  };
  
  if (comments[itemName]) {
    return comments[itemName];
  }
  
  // Comentários baseados em extensão para arquivos não específicos
  const ext = path.extname(itemName).toLowerCase();
  const extensionComments = {
    '.tsx': 'Componente React com TypeScript',
    '.jsx': 'Componente React com JavaScript',
    '.vue': 'Componente Vue.js single-file',
    '.svelte': 'Componente Svelte',
    '.css': 'Folha de estilo CSS',
    '.scss': 'Folha de estilo Sass',
    '.sass': 'Folha de estilo Sass (sintaxe indentada)',
    '.less': 'Folha de estilo Less',
    '.js': 'Script JavaScript',
    '.ts': 'Script TypeScript',
    '.mjs': 'Módulo JavaScript ES6',
    '.json': 'Dados estruturados JSON',
    '.yaml': 'Configuração YAML',
    '.yml': 'Configuração YAML',
    '.toml': 'Configuração TOML',
    '.xml': 'Documento XML estruturado',
    '.md': 'Documentação em Markdown',
    '.rst': 'Documentação reStructuredText',
    '.txt': 'Arquivo de texto simples',
    '.png': 'Imagem PNG otimizada',
    '.jpg': 'Imagem JPEG comprimida',
    '.jpeg': 'Imagem JPEG comprimida',
    '.gif': 'Imagem GIF animada',
    '.svg': 'Gráfico vetorial escalável',
    '.ico': 'Ícone de aplicação',
    '.webp': 'Imagem WebP otimizada',
    '.pdf': 'Documento PDF',
    '.sh': 'Script shell Unix/Linux',
    '.bat': 'Script batch Windows',
    '.ps1': 'Script PowerShell',
    '.py': 'Script Python',
    '.rb': 'Script Ruby',
    '.go': 'Código fonte Go',
    '.rs': 'Código fonte Rust',
    '.java': 'Código fonte Java',
    '.cpp': 'Código fonte C++',
    '.c': 'Código fonte C',
    '.cs': 'Código fonte C#',
    '.php': 'Script PHP',
    '.sql': 'Script SQL de banco de dados',
  };
  
  return extensionComments[ext] || '';
}

function buildTree(dirPath, prefix = '', isLast = true) {
  let result = '';
  
  try {
    const items = fs.readdirSync(dirPath)
      .filter(item => !shouldIgnore(item))
      .map(item => {
        const fullPath = path.join(dirPath, item);
        const stats = fs.statSync(fullPath);
        return {
          name: item,
          path: fullPath,
          isDirectory: stats.isDirectory()
        };
      })
      .sort((a, b) => {
        // Ordem de prioridade customizada
        const getPriority = (item) => {
          // Pastas importantes primeiro
          if (item.isDirectory) {
            const importantFolders = ['.github', '.githooks', 'src', 'lib', 'public', 'docs'];
            if (importantFolders.includes(item.name)) return 0;
            return 1;
          }
          
          // Arquivos de documentação importante
          const importantDocs = ['README.md', 'LICENSE', 'CHANGELOG.md'];
          if (importantDocs.includes(item.name)) return 2;
          
          // Arquivos de configuração principal
          const mainConfigs = ['package.json', 'tsconfig.json', 'Dockerfile'];
          if (mainConfigs.includes(item.name)) return 3;
          
          // Outros arquivos
          return 4;
        };
        
        const priorityA = getPriority(a);
        const priorityB = getPriority(b);
        
        if (priorityA !== priorityB) return priorityA - priorityB;
        
        // Se mesma prioridade, diretórios primeiro, depois alfabético
        if (a.isDirectory && !b.isDirectory) return -1;
        if (!a.isDirectory && b.isDirectory) return 1;
        return a.name.localeCompare(b.name);
      });

    items.forEach((item, index) => {
      const isLastItem = index === items.length - 1;
      const connector = isLastItem ? '└── ' : '├── ';
      const emoji = getEmoji(item.path, item.isDirectory);
      const comment = generateComment(item.path, item.isDirectory);
      const commentText = comment ? ` # ${comment}` : '';
      
      result += `${prefix}${connector}${emoji} ${item.name}`;
      
      if (item.isDirectory) {
        result += '/';
      }
      
      if (commentText) {
        // Adiciona espaços para alinhar o comentário
        const nameLength = item.name.length + (item.isDirectory ? 1 : 0);
        const spaces = Math.max(1, 35 - nameLength);
        result += ' '.repeat(spaces) + commentText;
      }
      
      result += '\n';
      
      if (item.isDirectory) {
        const newPrefix = prefix + (isLastItem ? '    ' : '│   ');
        result += buildTree(item.path, newPrefix, isLastItem);
      }
    });
  } catch (error) {
    console.error(`Erro ao ler diretório ${dirPath}:`, error.message);
  }
  
  return result;
}

function generateMarkdownTree(rootPath = '.') {
  const rootName = path.basename(path.resolve(rootPath));
  const emoji = getEmoji(rootPath, true);
  const comment = generateComment(rootPath, true);
  const commentText = comment ? ` # ${comment}` : '';
  
  let markdown = `${emoji} ${rootName}/`;
  
  if (commentText) {
    const spaces = Math.max(1, 35 - rootName.length - 1);
    markdown += ' '.repeat(spaces) + commentText;
  }
  
  markdown += '\n';
  markdown += buildTree(rootPath);
  
  return markdown;
}

// Função principal
function main() {
  const targetPath = process.argv[2] || '.';
  
  console.log('🚀 Gerando estrutura profissional de arquivos...\n');
  console.log('```');
  console.log(generateMarkdownTree(targetPath));
  console.log('```');
  
  // Salvar em arquivo com timestamp
  const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
  const outputFile = `file-structure-${timestamp}.md`;
  
  const content = `# 📂 Estrutura de Arquivos do Projeto

> Gerado automaticamente em ${new Date().toLocaleString('pt-BR')}

\`\`\`
${generateMarkdownTree(targetPath)}
\`\`\`

---
*Estrutura gerada com script profissional de análise de projetos*
`;
  
  fs.writeFileSync(outputFile, content, 'utf8');
  console.log(`\n✅ Estrutura salva em: ${outputFile}`);
  console.log(`📊 Total de itens mapeados: ${Object.keys(fileNameEmojis).length + Object.keys(folderEmojis).length}`);
}

// Executar se este arquivo for chamado diretamente
if (require.main === module) {
  main();
}

module.exports = { generateMarkdownTree, buildTree, shouldIgnore, getEmoji, generateComment };