#!/bin/bash

# setup.sh - Script de inicialização do apólice.diff

set -e

echo "🚀 Iniciando setup do apólice.diff..."
echo "======================================="

# 1. Python version check
echo "✓ Verificando Python..."
python3 --version || python --version

# 2. Criar venv
echo "✓ Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv || python -m venv venv
fi

# 3. Ativar venv
echo "✓ Ativando ambiente virtual..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

# 4. Upgrade pip
echo "✓ Atualizando pip..."
pip install --upgrade pip

# 5. Instalar dependências
echo "✓ Instalando dependências..."
pip install -r requirements.txt

# 6. Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo "✓ Criando arquivo .env..."
    cp .env.example .env
    echo "  ⚠️  Edite .env com suas configurações de LLM/OCR"
fi

# 7. Criar diretórios necessários
echo "✓ Criando diretórios..."
mkdir -p instance
mkdir -p data
mkdir -p Projeto_Final_Artefatos

# 8. Inicializar banco de dados
echo "✓ Inicializando banco de dados..."
python3 -c "from storage import init_db; init_db()" 2>/dev/null || \
python -c "from storage import init_db; init_db()"

# 9. Verificar Tesseract
echo ""
echo "✓ Verificando OCR (Tesseract)..."
if command -v tesseract &> /dev/null; then
    echo "  ✅ Tesseract encontrado"
    tesseract --version | head -1
else
    echo "  ⚠️  Tesseract não encontrado. Instale com:"
    echo "     Linux: sudo apt-get install tesseract-ocr"
    echo "     macOS: brew install tesseract"
    echo "     Windows: https://github.com/UB-Mannheim/tesseract/wiki"
fi

echo ""
echo "✅ Setup concluído!"
echo "======================================="
echo ""
echo "📝 Próximos passos:"
echo "  1. Edite o arquivo .env com suas chaves de API"
echo "  2. Para usar Ollama: ollama run qwen2.5-coder:3b"
echo "  3. Execute: streamlit run app.py"
echo ""
echo "🌐 Acesso: http://localhost:8501"
