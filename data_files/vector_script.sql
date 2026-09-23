-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the table
CREATE TABLE public.hr_policy_docs (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding VECTOR(300)
);

-- 3. Create the HNSW index (using cosine distance as an example)
CREATE INDEX policy_idx 
ON public.hr_policy_docs 
USING hnsw (embedding vector_cosine_ops);