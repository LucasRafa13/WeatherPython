-- init_db.sql

-- Cria a tabela para armazenar os dados contextuais dos eventos.
-- IF NOT EXISTS garante que a tabela só será criada se não existir,
-- evitando erros em reinicializações se o volume de dados persistir.
CREATE TABLE IF NOT EXISTS event_context_data (
    -- event_id: Identificador único do evento (ex: "EDUARDO_COSTA_CUIABA_20250820").
    -- Definido como PRIMARY KEY para garantir unicidade e indexação automática.
    event_id VARCHAR(255) PRIMARY KEY,
    
    -- context_data: Armazena os dados contextuais (como informações meteorológicas)
    -- no formato JSONB. JSONB é otimizado para armazenamento e consulta de dados JSON.
    context_data JSONB NOT NULL,
    
    -- data_retrieval_timestamp: Registra quando os dados foram coletados/armazenados.
    -- DEFAULT CURRENT_TIMESTAMP preenche automaticamente com a hora atual na inserção.
    -- TIMESTAMP WITH TIME ZONE é recomendado para lidar com fusos horários.
    data_retrieval_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Opcional: Adiciona um índice na coluna data_retrieval_timestamp para otimizar
-- consultas que ordenam ou filtram dados por data/hora de coleta, especialmente
-- se você precisar da informação mais recente.
CREATE INDEX IF NOT EXISTS idx_data_retrieval_timestamp ON event_context_data (data_retrieval_timestamp DESC);

-- Opcional: Adiciona um índice GIN (Generalized Inverted Index) na coluna JSONB.
-- Este tipo de índice é útil se você planeja realizar consultas complexas dentro
-- do campo JSONB, como buscar por chaves específicas ou valores dentro dos dados JSON.
-- Descomente a linha abaixo se você planeja esse tipo de consulta.
-- CREATE INDEX IF NOT EXISTS idx_context_data_gin ON event_context_data USING GIN (context_data);

-- Exemplo de inserção de dados (opcional, para teste rápido se precisar popular manualmente)
-- INSERT INTO event_context_data (event_id, context_data) VALUES
-- ('EXEMPLO_EVENTO_CIDADE_20241231', '{
--   "weather": {
--     "temperature": 25,
--     "condition": "Sunny",
--     "wind_speed": 10
--   },
--   "location": {
--     "city": "Example City",
--     "latitude": -12.34,
--     "longitude": -56.78
--   }
-- }');