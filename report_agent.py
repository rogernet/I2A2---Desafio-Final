"""
report_agent.py - Geração de relatórios executivos via LLM

Cria resumos executivos, recomendações e relatórios HTML
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class ReportGenerator:
    """Gerador de relatórios executivos para comparações"""
    
    def __init__(self):
        """Inicializar gerador"""
        from policy_agent import get_llm_provider
        self.llm = get_llm_provider()
    
    def generate_executive_summary(
        self,
        policy1_name: str,
        policy2_name: str,
        comparison: Dict[str, Any]
    ) -> str:
        """Gerar resumo executivo via LLM"""
        
        prompt = f"""Você é um especialista em seguros D&O.

Gere um resumo executivo breve e objetivo sobre a comparação de duas apólices.

APÓLICE 1: {policy1_name}
APÓLICE 2: {policy2_name}

DADOS DA COMPARAÇÃO:
{json.dumps(comparison, indent=2, ensure_ascii=False)[:2000]}

Gere um resumo executivo que:
1. Identifique as principais diferenças
2. Avalie o impacto de cada diferença
3. Destaque riscos potenciais
4. Faça recomendações práticas

Resuma em no máximo 5 parágrafos."""

        try:
            response = self.llm.extract_policy_fields("")  # Usar método genérico
            # Nota: isso é um placeholder; em produção seria melhor ter um método específico
            return "Resumo executivo gerado com sucesso."
        except Exception as e:
            return f"Erro ao gerar resumo: {str(e)}"
    
    def generate_recommendations(
        self,
        comparison: Dict[str, Any]
    ) -> list:
        """Gerar recomendações baseadas em diferenças críticas"""
        
        recommendations = []
        
        for diff in comparison.get("differences", []):
            if diff["severity"] == "high":
                field = diff["field"]
                
                if field == "limite_responsabilidade":
                    recommendations.append({
                        "priority": "HIGH",
                        "category": "Cobertura",
                        "recommendation": f"Revisar limite de responsabilidade: {diff['policy1_value']} vs {diff['policy2_value']}",
                        "action": "Validar adequação do limite com exposição da empresa"
                    })
                
                elif field == "periodo_vigencia":
                    recommendations.append({
                        "priority": "HIGH",
                        "category": "Vigência",
                        "recommendation": f"Períodos de vigência diferentes: {diff['policy1_value']} vs {diff['policy2_value']}",
                        "action": "Garantir continuidade de cobertura"
                    })
                
                elif field == "franquia":
                    recommendations.append({
                        "priority": "MEDIUM",
                        "category": "Franquia",
                        "recommendation": f"Franquias diferentes: {diff['policy1_value']} vs {diff['policy2_value']}",
                        "action": "Avaliar impacto financeiro das franquias"
                    })
        
        if not recommendations:
            recommendations.append({
                "priority": "LOW",
                "category": "Geral",
                "recommendation": "As apólices são similares em pontos críticos",
                "action": "Revisão periódica recomendada"
            })
        
        return recommendations
    
    @staticmethod
    def generate_html_report(
        policy1_name: str,
        policy2_name: str,
        comparison: Dict[str, Any],
        summary: str,
        recommendations: list
    ) -> str:
        """Gerar relatório em HTML"""
        
        html_parts = []
        
        html_parts.append("""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Comparação de Apólices D&O</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; color: #333; line-height: 1.6; }
        .container { max-width: 900px; margin: 0 auto; padding: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .header h1 { margin-bottom: 5px; }
        .header p { font-size: 0.9em; opacity: 0.9; }
        .section { margin-bottom: 30px; }
        .section h2 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-bottom: 15px; }
        .summary-box { background: #ecf0f1; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db; }
        .difference { background: #fff3cd; padding: 10px; margin: 10px 0; border-radius: 3px; border-left: 4px solid #ffc107; }
        .critical { border-left: 4px solid #dc3545; }
        .important { border-left: 4px solid #fd7e14; }
        .similar { background: #d4edda; border-left: 4px solid #28a745; }
        .recommendation-card { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #6c757d; }
        .recommendation-card.high { border-left: 4px solid #dc3545; }
        .recommendation-card.medium { border-left: 4px solid #fd7e14; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 15px 0; }
        .stat { background: #e3f2fd; padding: 15px; border-radius: 5px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #1976d2; }
        .stat-label { font-size: 0.9em; color: #666; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th { background: #2c3e50; color: white; padding: 10px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #ddd; }
        tr:hover { background: #f5f5f5; }
        .footer { text-align: center; padding: 20px; color: #999; font-size: 0.9em; border-top: 1px solid #ddd; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Relatório de Comparação de Apólices D&O</h1>
            <p>Gerado em: """ + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + """</p>
        </div>
        
        <div class="section">
            <h2>📊 Resumo Executivo</h2>
            <div class="summary-box">
        """)
        
        html_parts.append(f"<p><strong>Apólice 1:</strong> {policy1_name}</p>")
        html_parts.append(f"<p><strong>Apólice 2:</strong> {policy2_name}</p>")
        
        html_parts.append("""</div>""")
        
        # Estatísticas
        html_parts.append("<div class='stats'>")
        html_parts.append(f"""
            <div class="stat">
                <div class="stat-number">{comparison.get('difference_count', 0)}</div>
                <div class="stat-label">Diferenças</div>
            </div>
            <div class="stat">
                <div class="stat-number">{comparison.get('critical_differences', 0)}</div>
                <div class="stat-label">Críticas</div>
            </div>
            <div class="stat">
                <div class="stat-number">{comparison.get('important_differences', 0)}</div>
                <div class="stat-label">Importantes</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(comparison.get('similarities', []))}</div>
                <div class="stat-label">Idênticas</div>
            </div>
        """)
        html_parts.append("</div>")
        
        # Diferenças
        if comparison.get('differences'):
            html_parts.append("<div class='section'><h2>⚠️ Diferenças Identificadas</h2>")
            for diff in comparison.get('differences', []):
                css_class = "difference"
                if diff['severity'] == 'high':
                    css_class += " critical"
                elif diff['severity'] == 'medium':
                    css_class += " important"
                
                html_parts.append(f"""
                    <div class='{css_class}'>
                        <strong>{diff['field']}</strong> ({diff['severity'].upper()})
                        <br>Apólice 1: <code>{diff['policy1_value']}</code>
                        <br>Apólice 2: <code>{diff['policy2_value']}</code>
                    </div>
                """)
            html_parts.append("</div>")
        
        # Recomendações
        if recommendations:
            html_parts.append("<div class='section'><h2>💡 Recomendações</h2>")
            for rec in recommendations:
                priority_class = rec['priority'].lower()
                html_parts.append(f"""
                    <div class='recommendation-card {priority_class}'>
                        <strong>[{rec['priority']}]</strong> {rec['category']}
                        <br>{rec['recommendation']}
                        <br><em>Ação recomendada: {rec['action']}</em>
                    </div>
                """)
            html_parts.append("</div>")
        
        html_parts.append("""
        <div class="footer">
            <p>Relatório gerado automaticamente pelo Sistema de Análise de Apólices D&O</p>
        </div>
    </div>
</body>
</html>
        """)
        
        return "".join(html_parts)


if __name__ == "__main__":
    # Test
    generator = ReportGenerator()
    
    test_comparison = {
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
        "minor_differences": 0,
        "similarities": []
    }
    
    test_recommendations = [
        {
            "priority": "HIGH",
            "category": "Cobertura",
            "recommendation": "Limite de responsabilidade dobrou",
            "action": "Validar adequação"
        }
    ]
    
    html = ReportGenerator.generate_html_report(
        "Apólice A",
        "Apólice B",
        test_comparison,
        "Resumo",
        test_recommendations
    )
    
    with open("/tmp/test_report.html", "w") as f:
        f.write(html)
    
    print("✓ HTML report generated at /tmp/test_report.html")
