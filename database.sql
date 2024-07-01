--
-- Arquivo gerado com SQLiteStudio v3.4.4 em seg jul 1 15:38:06 2024
--
-- Codificação de texto usada: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Tabela: carrinho
CREATE TABLE IF NOT EXISTS carrinho (id integer PRIMARY KEY AUTOINCREMENT, id_usuario integer NOT NULL, preco real NOT NULL, qtd INTEGER, data datetime, data_update datetime, finalizado boolean NOT NULL);

-- Tabela: itens_carrinho
CREATE TABLE IF NOT EXISTS itens_carrinho (id integer PRIMARY KEY AUTOINCREMENT, id_carrinho integer NOT NULL, id_produto text NOT NULL, qtd integer NOT NULL, valor_unitario real NOT NULL, valor_total real NOT NULL);

-- Tabela: produtos
CREATE TABLE IF NOT EXISTS produtos (id integer PRIMARY KEY, nome text NOT NULL UNIQUE, qtd integer NOT NULL, valor real NOT NULL);

-- Tabela: usuario
CREATE TABLE IF NOT EXISTS usuario (id integer PRIMARY KEY AUTOINCREMENT, nome text NOT NULL, email text NOT NULL UNIQUE, senha text NOT NULL, admin boolean NOT NULL);

-- Trigger: delete_produtos_carrinho
CREATE TRIGGER IF NOT EXISTS delete_produtos_carrinho AFTER DELETE ON itens_carrinho BEGIN UPDATE carrinho
    SET preco = preco - OLD.valor_total,
    qtd = qtd - 1
    WHERE id = OLD.id_carrinho;
UPDATE produtos
    SET qtd = qtd + OLD.qtd
    WHERE id = OLD.id_produto;
DELETE FROM carrinho WHERE qtd = 0; END;

-- Trigger: insert_produtos_carrinho
CREATE TRIGGER IF NOT EXISTS insert_produtos_carrinho AFTER INSERT ON itens_carrinho BEGIN UPDATE carrinho
    SET preco = preco + NEW.valor_total,
    qtd = qtd + 1,
    data_update = datetime('now')
    WHERE id = NEW.id_carrinho;
UPDATE produtos
    SET qtd = qtd - NEW.qtd
    WHERE id = NEW.id_produto; END;

-- Visualizar: transacoes
CREATE VIEW IF NOT EXISTS transacoes AS SELECT 
    c.id AS id_transacao,
    u.id AS id_usuario,
    u.nome AS nome_usuario,
    c.preco AS valor_total_carrinho,
    c.qtd AS quantidade_total_carrinho,
    strftime('%d', c.data) || '/' || 
    strftime('%m', c.data) || '/' || 
    strftime('%Y', c.data) || ' ' ||
    strftime('%H', c.data) || ':' ||
    strftime('%M', c.data) || ':' ||
    strftime('%S', c.data) AS data_transacao
    GROUP_CONCAT(ic.id_produto, ',') AS id_produtos,
    GROUP_CONCAT(p.nome, ',') AS produtos,
    GROUP_CONCAT(ic.qtd, ',') AS qtd_produtos,
    GROUP_CONCAT(ic.valor_unitario, ',') AS valor_unitario_produtos,
    GROUP_CONCAT(ic.valor_total, ',') AS valor_total_produtos
FROM 
    carrinho c
JOIN 
    usuario u ON c.id_usuario = u.id
JOIN 
    itens_carrinho ic ON c.id = ic.id_carrinho
JOIN 
    produtos p ON ic.id_produto = p.id
WHERE 
    c.finalizado = 1
GROUP BY 
    c.id;

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
