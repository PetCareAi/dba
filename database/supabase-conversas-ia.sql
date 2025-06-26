-- Tabela para armazenar conversas com a IA
CREATE TABLE IF NOT EXISTS duvidas_analitics_ia (
    id SERIAL PRIMARY KEY,
    usuario VARCHAR(255) NOT NULL,
    pergunta TEXT NOT NULL,
    resposta TEXT NOT NULL,
    contexto_banco JSONB, -- Contexto do banco no momento da pergunta
    tokens_utilizados JSONB, -- Informações de tokens da resposta
    tempo_resposta FLOAT, -- Tempo em segundos
    avaliacao INTEGER CHECK (avaliacao >= 1 AND avaliacao <= 5), -- Avaliação da resposta (1-5)
    feedback TEXT, -- Feedback opcional do usuário
    categoria VARCHAR(100), -- Categoria da pergunta (performance, estrutura, etc)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    session_id VARCHAR(255), -- ID da sessão para agrupar conversas
    ip_address INET, -- IP do usuário (opcional)
    status VARCHAR(50) DEFAULT 'ativa' CHECK (status IN ('ativa', 'arquivada', 'reportada'))
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_duvidas_analitics_ia_usuario ON duvidas_analitics_ia(usuario);
CREATE INDEX IF NOT EXISTS idx_duvidas_analitics_ia_created_at ON duvidas_analitics_ia(created_at);
CREATE INDEX IF NOT EXISTS idx_duvidas_analitics_ia_session_id ON duvidas_analitics_ia(session_id);
CREATE INDEX IF NOT EXISTS idx_duvidas_analitics_ia_categoria ON duvidas_analitics_ia(categoria);

-- RLS (Row Level Security)
ALTER TABLE duvidas_analitics_ia ENABLE ROW LEVEL SECURITY;

-- Política para permitir que usuários vejam suas próprias conversas
CREATE POLICY "Usuários podem gerenciar próprias conversas IA" ON duvidas_analitics_ia
    FOR ALL TO authenticated
    USING (usuario = auth.email());

-- Política para service role (admin total)
CREATE POLICY "Service role acesso total conversas IA" ON duvidas_analitics_ia
    FOR ALL TO service_role
    USING (true)
    WITH CHECK (true);