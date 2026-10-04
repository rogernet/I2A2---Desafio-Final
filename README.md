# AI2Shield 🛡️

**Plataforma Inteligente para Análise e Comparação de Apólices D&O**

Uma solução MVP que automatiza a análise, extração estruturada e comparação de apólices de seguro usando Inteligência Artificial Generativa.

---

## 🎯 Objetivo

Reduzir o tempo de análise de apólices D&O (Directors and Officers) de horas para minutos, automatizando:

- ✨ **Extração de Conteúdo** — OCR inteligente e processamento de PDFs
- 🤖 **Estruturação de Dados** — Extração de campos via LLM
- ⚖️ **Comparação Determinística** — Análise campo a campo
- 📊 **Relatórios Executivos** — Resumos e recomendações via LLM
- 💾 **Persistência** — Armazenamento em SQLite

---

## 🏗️ Arquitetura

### Componentes

```
┌─────────────────────────────────────────────────┐
│         Interface Streamlit (app.py)            │
│  ┌───────────────────────────────────────────┐  │
│  │ • Extração de Apólices                    │  │
│  │ • Comparação de Apólices                  │  │
│  │ • Visualização de Histórico               │  │
│  └───────────────────────────────────────────┘  │
└────┬────────────────────────────────┬───────┬───┘
     │                                │       │
     ▼                                ▼       ▼
┌──────────────┐    ┌──────────────┐  │   ┌─────────────────┐
│ extraction.py│    │policy_agent │  │   │storage.py       │
│              │    │.py (LLM)    │  │   │(SQLite)         │
│ • pdfplumber │    │             │  │   │                 │
│ • OCR        │    │ • OpenAI    │  │   │ • PolicyStorage │
│ • Hash       │    │ • Anthropic │  │   │ • Comparisons   │
└──────────────┘    │ • Gemini    │  │   │ • Reports       │
                    │ • Ollama    │  │   └─────────────────┘
                    └──────────────┘  │
                                      │
                    ┌─────────────────┘
                    ▼
         ┌──────────────────────┐
         │compare_agent.py      │
         │(Determinístico)      │
         │                      │
         │ • Comparação campo   │
         │   a campo            │
         │ • Severidade         │
         │ • Resumo             │
         └──────────────────────┘
                    │
                    ▼
         ┌──────────────────────┐
         │report_agent.py       │
         │(LLM Report)          │
         │                      │
         │ • Executive Summary  │
         │ • Recomendações      │
         │ • HTML Report        │
         └──────────────────────┘
```

### Fluxo de Dados

1. **Upload** → PDFou Imagem
2. **Extração** → Texto via pdfplumber + OCR fallback
3. **Estruturação** → Campos JSON via LLM
4. **Armazenamento** → SQLite
5. **Comparação** → Análise determinística
6. **Relatório** → HTML via LLM
7. **Download** → Arquivo final

---

## 🚀 Quickstart

### Pré-requisitos

- Python 3.8+
- pip ou conda

### Instalação

```bash
# 1. Clonar repositório
git clone https://github.com/rogernet/apolicediff.git
cd apolicediff

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas chaves de API
```

### Configurar LLM

#### Opção 1: Ollama (Local, Gratuito)

```bash
# Instalar Ollama: https://ollama.ai
# Rodar modelo
ollama run qwen2.5-coder:3b

# Configurar .env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:3b
```

#### Opção 2: OpenAI

```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxx
OPENAI_MODEL=gpt-4-turbo
```

#### Opção 3: Anthropic Claude

```
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxx
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

#### Opção 4: Google Gemini

```
LLM_PROVIDER=gemini
GEMINI_API_KEY=xxxxx
GEMINI_MODEL=gemini-pro
```

### Executar

```bash
streamlit run app.py
```

Acesse: `http://localhost:8501`

---

## 📖 Guia de Uso

### 1. Extrair Apólice

1. Vá para **📄 Extrair Apólice**
2. Upload PDF ou Imagem
3. Sistema fará:
   - Extração de texto (pdfplumber/OCR)
   - Extração de campos (LLM)
   - Armazenamento em BD
4. Clique **💾 Salvar Apólice**

### 2. Comparar Apólices

1. Vá para **⚖️ Comparar Apólices**
2. Selecione 2 apólices da lista
3. Clique **🔄 Comparar Apólices**
4. Sistema fará:
   - Comparação determinística
   - Geração de recomendações (LLM)
   - Relatório HTML
5. Baixe o relatório com **📥 Baixar Relatório**

### 3. Consultar Histórico

Vá para **📊 Histórico** para ver:
- Apólices extraídas
- Comparações realizadas
- Relatórios gerados

---

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```env
# LLM (escolha um)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:3b

# OCR (escolha um)
OCR_PROVIDER=tesseract

# Banco de Dados
DATABASE_URL=sqlite:///instance/apolices.db
SQLITE_DB_PATH=instance/apolices.db

# Aplicação
ENVIRONMENT=development
DEBUG=True
PORT=8501
HOST=0.0.0.0
```

### Instalar OCR

**Tesseract (recomendado)**:
```bash
# Linux
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download: https://github.com/UB-Mannheim/tesseract/wiki
```

---

## 📊 Estrutura de Dados

### PolicyExtraction (Apólice Extraída)

```json
{
  "id": 1,
  "filename": "apolice.pdf",
  "file_hash": "sha256...",
  "extracted_data": {
    "numero_apolice": "DO-2024-001",
    "segurada": "Acme Corp",
    "limite_responsabilidade": "R$ 5M",
    "periodo_vigencia": "01/01/2024 - 31/12/2024",
    "franquia": "R$ 50k",
    "coberturas": ["DC", "DA", "RP"],
    "exclusoes": ["fraude", "má fé"]
  },
  "created_at": "2024-01-15T10:30:00"
}
```

### PolicyComparison (Resultado da Comparação)

```json
{
  "id": 1,
  "policy1_id": 1,
  "policy2_id": 2,
  "differences": [
    {
      "field": "limite_responsabilidade",
      "severity": "high",
      "policy1_value": "R$ 5M",
      "policy2_value": "R$ 10M"
    }
  ],
  "critical_differences": 1,
  "important_differences": 0,
  "minor_differences": 3
}
```

---

## 🧪 Testes

```bash
# Testar extração
python extraction.py

# Testar policy agent
python policy_agent.py

# Testar comparação
python compare_agent.py

# Testar relatório
python report_agent.py
```

---

## 📁 Estrutura de Pastas

```
apolicediff/
├── app.py                 # Interface Streamlit principal
├── extraction.py          # Extração de PDFs/Imagens
├── policy_agent.py        # Agente LLM para extração
├── compare_agent.py       # Comparador determinístico
├── report_agent.py        # Gerador de relatórios
├── storage.py             # Persistência SQLite
├── requirements.txt       # Dependências
├── .env.example           # Template de variáveis
├── .gitignore             # Exclusões Git
├── README.md              # Este arquivo
├── instance/              # Banco de dados (criado automaticamente)
│   └── apolices.db
├── data/                  # Exemplos de apólices
│   ├── apolice_exemplo_1.pdf
│   └── apolice_exemplo_2.pdf
└── Projeto_Final_Artefatos/
    ├── AI2Shield_Apresentacao.pptx
    ├── AI2Shield_Apresentacao.mp4
    └── comparacao_tecnica.pdf
```

---

## 🤖 Tecnologias Utilizadas

| Componente | Tecnologia | Nota |
|-----------|-----------|------|
| **Web Framework** | Streamlit | Interface interativa |
| **LLM** | Ollama/OpenAI/Anthropic/Gemini | Agnóstico |
| **LLM Framework** | LangChain | Abstração de modelos |
| **PDF/Imagem** | pdfplumber + Pytesseract | Extração de texto |
| **Banco de Dados** | SQLAlchemy + SQLite | Persistência local |
| **Versionamento** | Git + GitHub | Controle de código |

---

## 📝 Requisitos Atendidos

✅ Permitir leitura de PDFs/Imagens  
✅ Extrair automaticamente informações  
✅ Estruturar dados em formato organizado  
✅ Comparar pelo menos 2 apólices  
✅ Apresentar diferenças ao usuário  
✅ Usar modelo de IA Generativa  
✅ Disponibilizar interface de demonstração  

---

## 🚀 Próximos Passos (Roadmap)

- [ ] Integração com APIs de documentos em nuvem (Google Drive, OneDrive)
- [ ] Autenticação de usuários
- [ ] Multi-idioma (português, inglês, espanhol)
- [ ] Análise de tendências históricas
- [ ] Integração com sistemas reais de seguradoras
- [ ] Melhorias na interface (Dark Mode, Mobile)
- [ ] Cache de resultados
- [ ] Exportação para Word, Excel

---

## 📄 Licença

MIT License - veja LICENSE.txt para detalhes

---

## 👤 Autor

Desenvolvido pelo grupo **AI2Shield** | Plataforma Inteligente de Análise de Apólices D&O

- 🌐 GitHub: [@rogernet](https://github.com/rogernet)
- 📧 Email: rogerio.rogernet@gmail.com

---

**Versão:** 1.0  
**Última atualização:** Outubro 2026  
**Status:** MVP Funcional ✅
