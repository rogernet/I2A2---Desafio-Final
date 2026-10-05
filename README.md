# InsurMinds - Plataforma Inteligente para Análise de Apólices D&O

## Descrição do Projeto

InsurMinds é uma plataforma inteligente para análise e comparação automática de apólices de seguro D&O (Directors and Officers). Utiliza IA Generativa para extrair, estruturar e comparar dados de apólices.

### Objetivo
Automatizar o processo manual de análise de apólices, facilitando a tomada de decisão de especialistas em seguros através de uma arquitetura baseada em agentes especializados.

---

## Instruções de Instalação

### Pré-requisitos
- Python 3.9+
- pip
- Git

### Instalação Automática (setup.sh)

```bash
# Linux / Mac
chmod +x setup.sh
./setup.sh

# Windows (PowerShell como admin)
.\setup.sh
```

O script configura ambiente virtual, instala dependências e cria `.env` automaticamente.

### Windows (Manual)

```powershell
git clone https://github.com/rogernet/I2A2---Desafio-Final.git
cd I2A2---Desafio-Final
python -m venv venv
venv\Scripts\activate
pip install --only-binary :all: -r requirements.txt
copy .env.example .env
# Editar .env com suas chaves de API
```

### Linux / Mac (Manual)

```bash
git clone https://github.com/rogernet/I2A2---Desafio-Final.git
cd I2A2---Desafio-Final
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env com suas chaves de API
```

---

## Instruções de Execução

```bash
# Assegurar que venv está ativado
streamlit run app.py
```

Acessa em: **http://localhost:8501**

### Fluxo de Uso
1. Upload de apólice(s) em PDF
2. Extração automática via LLM
3. Comparar duas apólices
4. Visualizar relatório com diferenças por severidade
5. Download em HTML

---

## Tecnologias Utilizadas

| Componente | Tecnologia | Versão |
|---|---|---|
| Linguagem | Python | 3.9+ |
| Interface | Streamlit | 1.40.0 |
| IA/LLM | LangChain | 0.3.0 |
| PDF/OCR | pdfplumber | 0.10.3 |
| Imagens | Pillow | 10.4.0 |
| Banco | SQLite + SQLAlchemy | 2.1.0 |
| LLMs | Anthropic, OpenAI, Ollama, Gemini | N/A |

---

## Integrantes

| Nome | Email | Papel |
|---|---|---|
| Daniel Sampaio Passos | danielsba@gmail.com | Dev |
| Flávia da Silva | flaviapcnp@gmail.com | Dev |
| Juan Pablo de Jesus Sampaio | juanpablo.fifa9@gmail.com | Dev |
| Marcio Pohlmann | marcpohl@gmail.com | Dev |
| Rogério Rodrigues de Oliveira | rogerio.rogernet@gmail.com | Dev |

---

## Licença

Este projeto está licenciado sob a **Licença MIT**. Veja [LICENSE.txt](LICENSE.txt).

---

## Documentação Adicional

### Arquivos Principais
- **app.py** - Interface Streamlit com Dark Mode
- **storage.py** - Banco SQLite + SQLAlchemy ORM
- **policy_agent.py** - Extração via LLM com retry automático
- **compare_agent.py** - Comparação inteligente (3 níveis severidade)
- **extraction.py** - Processamento PDF/imagens (pdfplumber + Pillow)
- **report_agent.py** - Geração de relatórios HTML com Dark Mode AAA
- **setup.sh** - Script de instalação automática (alternativa ao manual)

### Artefatos
- **Projeto_Final_Artefatos/InsurMinds_Projeto_Final_Relatorio_Tecnico.pdf** - Relatório técnico (arquitetura, agentes, limitações)
- **Projeto_Final_Artefatos/InsurMinds_Projeto_Final.pptx** - Pitch Deck (15 slides)
- **Projeto_Final_Artefatos/InsurMinds_Projeto_Final.mp4** - Vídeo demo (≤5 min)
- **Projeto_Final_Artefatos/InsurMinds_Projeto_Final_Relatorio_Tecnico.docx** - Relatório editável

---

## Segurança

Nunca faça commit de `.env` com chaves reais. Use `.env.example` como template.

---

## Troubleshooting

### Erro: "No module named X"
```powershell
pip install --only-binary :all: -r requirements.txt
```

### App não carrega
```powershell
rm -r .streamlit/
streamlit run app.py
```

---

## Estrutura de Pastas

```
I2A2---Desafio-Final/
│
├── README.md                              ← OBRIGATÓRIO
├── LICENSE.txt                            ← MIT License
├── .gitignore
├── .env.example
├── setup.sh                               ← Script de instalação automática
│
├── app.py                                 ← Streamlit principal
├── storage.py                             ← SQLite + SQLAlchemy ORM
├── policy_agent.py                        ← Extração via LLM
├── compare_agent.py                       ← Comparação de apólices
├── extraction.py                          ← Processamento PDF/imagens
├── report_agent.py                        ← Geração de relatórios HTML
├── requirements.txt                       ← Dependências
│
└── Projeto_Final_Artefatos/
    ├── InsurMinds_Projeto_Final.pptx
    ├── InsurMinds_Projeto_Final.mp4
    ├── InsurMinds_Projeto_Final_Relatorio_Tecnico.pdf
    └── InsurMinds_Projeto_Final_Relatorio_Tecnico.docx
```

---

## Contato

challenges@i2a2.academy

---

**Status**: Pronto para Avaliação Final | **Data**: 06/10/2026
