-- Tabela para armazenar projetos
CREATE TABLE IF NOT EXISTS projetos_analytics (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    categoria VARCHAR(100),
    prioridade VARCHAR(50) DEFAULT 'Média',
    status VARCHAR(50) DEFAULT 'ativo',
    tags TEXT[], -- Array de tags
    membros TEXT[], -- Array de emails dos membros
    configuracoes JSONB, -- Configurações específicas do projeto
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255),
    CONSTRAINT projetos_analytics_status_check CHECK (status IN ('ativo', 'pausado', 'concluido', 'arquivado')),
    CONSTRAINT projetos_analytics_prioridade_check CHECK (prioridade IN ('Baixa', 'Média', 'Alta', 'Crítica'))
);

-- Tabela para armazenar scripts SQL dos projetos
CREATE TABLE IF NOT EXISTS scripts_projetos (
    id SERIAL PRIMARY KEY,
    projeto_id INTEGER REFERENCES projetos_analytics(id) ON DELETE CASCADE,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    sql_content TEXT NOT NULL,
    tipo_script VARCHAR(50) DEFAULT 'consulta', -- consulta, relatorio, manutencao, backup
    parametros JSONB, -- Parâmetros do script
    tags TEXT[], -- Tags específicas do script
    status VARCHAR(50) DEFAULT 'ativo',
    versao INTEGER DEFAULT 1,
    ultima_execucao TIMESTAMP WITH TIME ZONE,
    total_execucoes INTEGER DEFAULT 0,
    tempo_medio_execucao INTERVAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255),
    CONSTRAINT scripts_projetos_status_check CHECK (status IN ('ativo', 'pausado', 'obsoleto')),
    CONSTRAINT scripts_projetos_tipo_check CHECK (tipo_script IN ('consulta', 'relatorio', 'manutencao', 'backup', 'migracao', 'otimizacao'))
);

-- Tabela para histórico de execuções dos scripts
CREATE TABLE IF NOT EXISTS execucoes_scripts (
    id SERIAL PRIMARY KEY,
    script_id INTEGER REFERENCES scripts_projetos(id) ON DELETE CASCADE,
    projeto_id INTEGER REFERENCES projetos_analytics(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL, -- sucesso, erro, cancelado
    resultado JSONB, -- Resultado da execução (dados, erro, métricas)
    tempo_execucao INTERVAL,
    registros_afetados INTEGER,
    parametros_usados JSONB,
    erro_mensagem TEXT,
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    executed_by VARCHAR(255),
    CONSTRAINT execucoes_scripts_status_check CHECK (status IN ('sucesso', 'erro', 'cancelado', 'executando'))
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_projetos_analytics_status ON projetos_analytics(status);
CREATE INDEX IF NOT EXISTS idx_projetos_analytics_categoria ON projetos_analytics(categoria);
CREATE INDEX IF NOT EXISTS idx_scripts_projetos_projeto_id ON scripts_projetos(projeto_id);
CREATE INDEX IF NOT EXISTS idx_scripts_projetos_status ON scripts_projetos(status);
CREATE INDEX IF NOT EXISTS idx_execucoes_scripts_script_id ON execucoes_scripts(script_id);
CREATE INDEX IF NOT EXISTS idx_execucoes_scripts_executed_at ON execucoes_scripts(executed_at);

-- RLS (Row Level Security) policies
ALTER TABLE projetos_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE scripts_projetos ENABLE ROW LEVEL SECURITY;
ALTER TABLE execucoes_scripts ENABLE ROW LEVEL SECURITY;

-- Políticas básicas (ajustar conforme necessário)
CREATE POLICY "Usuários podem gerenciar próprios projetos" ON projetos_analytics
    FOR ALL TO authenticated
    USING (created_by = auth.email() OR auth.email() = ANY(membros));

CREATE POLICY "Usuários podem gerenciar scripts de seus projetos" ON scripts_projetos
    FOR ALL TO authenticated
    USING (EXISTS (
        SELECT 1 FROM projetos_analytics p 
        WHERE p.id = projeto_id 
        AND (p.created_by = auth.email() OR auth.email() = ANY(p.membros))
    ));

CREATE POLICY "Usuários podem ver execuções de seus projetos" ON execucoes_scripts
    FOR SELECT TO authenticated
    USING (EXISTS (
        SELECT 1 FROM projetos_analytics p 
        WHERE p.id = projeto_id 
        AND (p.created_by = auth.email() OR auth.email() = ANY(p.membros))
    ));