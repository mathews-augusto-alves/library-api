CREATE TABLE IF NOT EXISTS pessoas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(50) NOT NULL,
    data_nascimento DATE NOT NULL,
    email VARCHAR(255) UNIQUE
);

-- Índices adicionais conforme o modelo
CREATE INDEX IF NOT EXISTS idx_pessoas_id ON pessoas(id);
CREATE INDEX IF NOT EXISTS idx_pessoas_email ON pessoas(email);

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_usuarios_id ON usuarios(id);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);

-- Tabela de livros
CREATE TABLE IF NOT EXISTS livros (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    autor VARCHAR(255) NOT NULL,
    disponivel BOOLEAN NOT NULL DEFAULT TRUE
);

-- Tabela de empréstimos
CREATE TABLE IF NOT EXISTS emprestimos (
    id SERIAL PRIMARY KEY,
    livro_id INTEGER NOT NULL REFERENCES livros(id),
    pessoa_id INTEGER NOT NULL REFERENCES pessoas(id),
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    data_emprestimo TIMESTAMP NOT NULL DEFAULT NOW(),
    data_devolucao TIMESTAMP NULL
);

CREATE INDEX IF NOT EXISTS idx_livros_id ON livros(id);
CREATE INDEX IF NOT EXISTS idx_emprestimos_livro_id ON emprestimos(livro_id);
CREATE INDEX IF NOT EXISTS idx_emprestimos_pessoa_id ON emprestimos(pessoa_id);
CREATE INDEX IF NOT EXISTS idx_emprestimos_usuario_id ON emprestimos(usuario_id); 