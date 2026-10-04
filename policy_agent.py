"""
policy_agent.py - Agente LLM para extração estruturada de apólices

Agnóstico a modelo (OpenAI, Anthropic, Gemini, Ollama)
"""

import json
import os
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()

# === LLM PROVIDERS ===
class LLMProvider(ABC):
    """Interface para diferentes provedores de LLM"""
    
    @abstractmethod
    def extract_policy_fields(self, policy_text: str) -> Dict[str, Any]:
        """Extrair campos estruturados de apólice"""
        pass
    
    def _build_extraction_prompt(self, policy_text: str) -> str:
        """Construir prompt para extração"""
        return f"""Você é um especialista em análise de apólices de seguro D&O.

Analise o seguinte texto de apólice e extraia os campos solicitados em JSON puro.

CAMPOS OBRIGATÓRIOS:
- numero_apolice: número da apólice
- segurada: nome da empresa segurada
- periodo_vigencia: período de cobertura (data início - data fim)
- limite_responsabilidade: valor do limite de responsabilidade
- franquia: franquia aplicável
- coberturas: lista de coberturas inclusas
- exclusoes: lista de exclusões
- clausulas_principais: principais cláusulas especiais (como dict)
- data_emissao: data de emissão da apólice
- segurador: nome da seguradora

TEXTO DA APÓLICE:
---
{policy_text[:2000]}
---

Retorne APENAS um JSON válido, sem markdown, sem explicações, sem preamble.
Se um campo não encontrar, use null."""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parsear resposta JSON do LLM com fallback"""
        # Limpar markdown code blocks se existirem
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        
        response = response.strip()
        
        # Tentar parse direto
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Se falhar, tentar extrair JSON da resposta
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Se tudo falhar, retornar com "raw" para análise manual
        print("❌ Failed to parse LLM response as JSON")
        print(f"Response: {response[:200]}...")
        
        # Criar resposta padrão com valores estruturados extraídos
        return {
            "numero_apolice": None,
            "segurada": None,
            "periodo_vigencia": None,
            "limite_responsabilidade": None,
            "franquia": None,
            "coberturas": None,
            "exclusoes": None,
            "clausulas_principais": None,
            "data_emissao": None,
            "segurador": None,
            "error": "JSON parsing failed - response não é JSON válido",
            "raw": response[:500]  # Apenas primeiros 500 chars para não pesar
        }


class OllamaProvider(LLMProvider):
    """Ollama (modelo local)"""
    
    def __init__(self):
        try:
            # Tentar usar langchain_ollama (nova forma)
            try:
                from langchain_ollama import OllamaLLM
                base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")
                self.llm = OllamaLLM(base_url=base_url, model=model)
            except ImportError:
                # Fallback para langchain_community (deprecado)
                from langchain_community.llms import Ollama
                base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")
                self.llm = Ollama(base_url=base_url, model=model)
        except ImportError:
            raise ImportError("langchain-ollama ou langchain-community não instalado")
    
    def extract_policy_fields(self, policy_text: str) -> Dict[str, Any]:
        """Extrair com Ollama"""
        prompt = self._build_extraction_prompt(policy_text)
        response = self.llm.invoke(prompt)
        return self._parse_response(response)


class OpenAIProvider(LLMProvider):
    """OpenAI (GPT)"""
    
    def __init__(self):
        try:
            from langchain_openai import ChatOpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
            self.llm = ChatOpenAI(api_key=api_key, model=model, temperature=0)
        except ImportError:
            raise ImportError("langchain-openai não instalado")
    
    def extract_policy_fields(self, policy_text: str) -> Dict[str, Any]:
        """Extrair com OpenAI"""
        prompt = self._build_extraction_prompt(policy_text)
        response = self.llm.invoke(prompt)
        return self._parse_response(response.content)


class AnthropicProvider(LLMProvider):
    """Anthropic (Claude)"""
    
    def __init__(self):
        try:
            from langchain_anthropic import ChatAnthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            model = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
            self.llm = ChatAnthropic(api_key=api_key, model=model)
        except ImportError:
            raise ImportError("langchain-anthropic não instalado")
    
    def extract_policy_fields(self, policy_text: str) -> Dict[str, Any]:
        """Extrair com Claude"""
        prompt = self._build_extraction_prompt(policy_text)
        response = self.llm.invoke(prompt)
        return self._parse_response(response.content)


class GeminiProvider(LLMProvider):
    """Google Gemini"""
    
    def __init__(self):
        try:
            import google.generativeai as genai
            api_key = os.getenv("GEMINI_API_KEY")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                os.getenv("GEMINI_MODEL", "gemini-pro")
            )
        except ImportError:
            raise ImportError("google-generativeai não instalado")
    
    def extract_policy_fields(self, policy_text: str) -> Dict[str, Any]:
        """Extrair com Gemini"""
        prompt = self._build_extraction_prompt(policy_text)
        response = self.model.generate_content(prompt)
        return self._parse_response(response.text)


def get_llm_provider() -> LLMProvider:
    """Factory para seleção de provedor LLM"""
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    
    if provider == "ollama":
        return OllamaProvider()
    elif provider == "openai":
        return OpenAIProvider()
    elif provider == "anthropic":
        return AnthropicProvider()
    elif provider == "gemini":
        return GeminiProvider()
    else:
        print(f"⚠️ LLM provider '{provider}' não reconhecido, usando Ollama")
        return OllamaProvider()


# === POLICY AGENT ===
class PolicyExtractionAgent:
    """Agente para extração estruturada de apólices D&O"""
    
    EXTRACTION_SCHEMA = {
        "numero_apolice": "str",
        "segurada": "str",
        "periodo_vigencia": "str",
        "limite_responsabilidade": "str",
        "franquia": "str",
        "coberturas": "list",
        "exclusoes": "list",
        "clausulas_principais": "dict",
        "data_emissao": "str",
        "segurador": "str"
    }
    
    def __init__(self):
        self.llm = get_llm_provider()
    
    def extract_fields(self, policy_text: str) -> Dict[str, Any]:
        """Extrair campos estruturados da apólice"""
        return self.llm.extract_policy_fields(policy_text)


if __name__ == "__main__":
    # Test
    agent = PolicyExtractionAgent()
    
    test_text = """
    APÓLICE DE SEGURO DE RESPONSABILIDADE CIVIL D&O
    Número: DO-2024-001234
    Segurada: Acme Corporation S.A.
    Período: 01/01/2024 a 31/12/2024
    Limite de Responsabilidade: R$ 5.000.000,00
    Franquia: R$ 50.000,00
    
    Coberturas:
    - Responsabilidade Civil do Diretor
    - Responsabilidade Civil do Administrador
    - Responsabilidade Profissional
    
    Exclusões:
    - Atos de má fé
    - Fraude intencional
    - Ilegalidade manifesta
    """
    
    result = agent.extract_fields(test_text)
    print(json.dumps(result, indent=2, ensure_ascii=False))
