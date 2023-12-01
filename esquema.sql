CREATE TABLE IF NOT EXISTS vagas (
    id_vaga INTEGER PRIMARY KEY,
    tipo_vaga TEXT NOT NULL,
    cargo_vaga TEXT NOT NULL,
    requisitos_vaga TEXT NOT NULL,
    salario_vaga REAL NOT NULL,
    local_vaga TEXT NOT NULL,
    email_vaga TEXT NOT NULL,
    desc_vaga TEXT NOT NULL,
    img_vaga TEXT NOT NULL
);