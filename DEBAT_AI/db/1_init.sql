CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE debates (
    id SERIAL PRIMARY KEY,
    topic TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    debate_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (debate_id) REFERENCES debates (id),
    arg_type VARCHAR(50) DEFAULT 'claim',      -- Exemple: 'claim', 'premise'
    relation_type VARCHAR(50) DEFAULT 'none',  -- Exemple: 'attack', 'support'
    target_id INTEGER REFERENCES messages(id),  -- L'ID du message qu'on attaque
    feedback TEXT, -- Stocke le conseil/critique de l'IA
    session_id VARCHAR(255)
);
