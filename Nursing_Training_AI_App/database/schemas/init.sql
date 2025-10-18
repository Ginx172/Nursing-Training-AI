-- 🗄️ Database Schema pentru Nursing Training AI
-- PostgreSQL Schema de inițializare

-- Extensii necesare
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Enum-uri
CREATE TYPE user_role AS ENUM ('admin', 'trainer', 'student', 'demo');
CREATE TYPE nhs_band AS ENUM ('band_2', 'band_3', 'band_4', 'band_5', 'band_6', 'band_7', 'band_8a', 'band_8b', 'band_8c', 'band_8d', 'band_9');
CREATE TYPE subscription_tier AS ENUM ('demo', 'basic', 'professional', 'enterprise');
CREATE TYPE question_type AS ENUM ('multiple_choice', 'true_false', 'calculation', 'scenario', 'case_study');
CREATE TYPE difficulty_level AS ENUM ('beginner', 'intermediate', 'advanced', 'expert');

-- Tabela utilizatori
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    
    -- Informații profesionale
    nhs_band nhs_band,
    specialization VARCHAR(100),
    years_experience INTEGER DEFAULT 0,
    
    -- Abonament și acces
    subscription_tier subscription_tier DEFAULT 'demo',
    subscription_expires_at TIMESTAMP,
    demo_questions_used INTEGER DEFAULT 0,
    demo_questions_limit INTEGER DEFAULT 3,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    role user_role DEFAULT 'student',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    -- Preferințe
    preferred_language VARCHAR(10) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC'
);

-- Indexuri pentru utilizatori
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_nhs_band ON users(nhs_band);
CREATE INDEX idx_users_subscription_tier ON users(subscription_tier);

-- Tabela progres utilizatori
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Progres pe band
    current_band nhs_band NOT NULL,
    band_progress_percentage INTEGER DEFAULT 0,
    
    -- Statistici
    total_questions_answered INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    total_study_time_minutes INTEGER DEFAULT 0,
    
    -- Competențe
    clinical_skills_score INTEGER DEFAULT 0,
    management_skills_score INTEGER DEFAULT 0,
    communication_skills_score INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexuri pentru progres
CREATE INDEX idx_user_progress_user_id ON user_progress(user_id);
CREATE INDEX idx_user_progress_current_band ON user_progress(current_band);

-- Tabela sesiuni utilizatori
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    
    -- Informații sesiune
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_type VARCHAR(50),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexuri pentru sesiuni
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_active ON user_sessions(is_active);

-- Tabela întrebări
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    
    -- Conținut
    title VARCHAR(500) NOT NULL,
    question_text TEXT NOT NULL,
    question_type question_type NOT NULL,
    difficulty_level difficulty_level NOT NULL,
    
    -- Opțiuni pentru multiple choice
    options JSONB,
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    
    -- Metadate
    nhs_band VARCHAR(20) NOT NULL,
    specialization VARCHAR(100),
    tags JSONB,
    
    -- Calculări
    calculation_formula TEXT,
    calculation_units VARCHAR(100),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_demo BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexuri pentru întrebări
CREATE INDEX idx_questions_nhs_band ON questions(nhs_band);
CREATE INDEX idx_questions_question_type ON questions(question_type);
CREATE INDEX idx_questions_difficulty_level ON questions(difficulty_level);
CREATE INDEX idx_questions_is_active ON questions(is_active);
CREATE INDEX idx_questions_is_demo ON questions(is_demo);
CREATE INDEX idx_questions_tags ON questions USING GIN(tags);

-- Tabela răspunsuri utilizatori
CREATE TABLE user_answers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    
    -- Răspuns
    user_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    confidence_level INTEGER,
    
    -- Timp de răspuns
    time_taken_seconds INTEGER,
    
    -- Feedback
    ai_feedback TEXT,
    improvement_suggestions TEXT,
    
    -- Timestamp
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexuri pentru răspunsuri
CREATE INDEX idx_user_answers_user_id ON user_answers(user_id);
CREATE INDEX idx_user_answers_question_id ON user_answers(question_id);
CREATE INDEX idx_user_answers_answered_at ON user_answers(answered_at);

-- Tabela sesiuni de training
CREATE TABLE training_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Configurare sesiune
    session_name VARCHAR(200),
    nhs_band VARCHAR(20) NOT NULL,
    specialization VARCHAR(100),
    question_count INTEGER DEFAULT 10,
    
    -- Rezultate
    total_questions INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    score_percentage FLOAT DEFAULT 0.0,
    
    -- Timp
    duration_minutes INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Status
    is_completed BOOLEAN DEFAULT FALSE,
    is_demo BOOLEAN DEFAULT FALSE
);

-- Indexuri pentru sesiuni de training
CREATE INDEX idx_training_sessions_user_id ON training_sessions(user_id);
CREATE INDEX idx_training_sessions_nhs_band ON training_sessions(nhs_band);
CREATE INDEX idx_training_sessions_started_at ON training_sessions(started_at);

-- Tabela căi de învățare
CREATE TABLE learning_paths (
    id SERIAL PRIMARY KEY,
    
    -- Informații de bază
    name VARCHAR(200) NOT NULL,
    description TEXT,
    nhs_band VARCHAR(20) NOT NULL,
    specialization VARCHAR(100),
    
    -- Structură
    modules JSONB,
    prerequisites JSONB,
    
    -- Metadate
    estimated_hours INTEGER DEFAULT 0,
    difficulty_level difficulty_level NOT NULL,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_demo BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexuri pentru căi de învățare
CREATE INDEX idx_learning_paths_nhs_band ON learning_paths(nhs_band);
CREATE INDEX idx_learning_paths_difficulty_level ON learning_paths(difficulty_level);
CREATE INDEX idx_learning_paths_is_active ON learning_paths(is_active);

-- Tabela progres pe căi de învățare
CREATE TABLE user_learning_paths (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    learning_path_id INTEGER NOT NULL REFERENCES learning_paths(id) ON DELETE CASCADE,
    
    -- Progres
    current_module INTEGER DEFAULT 0,
    completed_modules JSONB,
    progress_percentage FLOAT DEFAULT 0.0,
    
    -- Timp
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Status
    is_completed BOOLEAN DEFAULT FALSE,
    is_paused BOOLEAN DEFAULT FALSE
);

-- Indexuri pentru progres pe căi de învățare
CREATE INDEX idx_user_learning_paths_user_id ON user_learning_paths(user_id);
CREATE INDEX idx_user_learning_paths_learning_path_id ON user_learning_paths(learning_path_id);

-- Funcție pentru actualizarea updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger-uri pentru actualizarea updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_progress_updated_at BEFORE UPDATE ON user_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_questions_updated_at BEFORE UPDATE ON questions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_learning_paths_updated_at BEFORE UPDATE ON learning_paths
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
