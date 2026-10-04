"""
compare_agent.py - Comparação determinística entre apólices D&O

Análise campo a campo sem dependência de LLM (determinístico, rápido)
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import json


@dataclass
class FieldDifference:
    """Representação de diferença entre campos"""
    field_name: str
    value_policy1: Any
    value_policy2: Any
    field_type: str
    severity: str  # low, medium, high


class PolicyComparer:
    """Comparador determinístico de apólices"""
    
    # Campos críticos (alta severidade se diferentes)
    CRITICAL_FIELDS = {
        "numero_apolice",
        "limite_responsabilidade",
        "periodo_vigencia",
        "segurada",
        "segurador"
    }
    
    # Campos importantes (média severidade)
    IMPORTANT_FIELDS = {
        "franquia",
        "data_emissao"
    }
    
    def compare(self, policy1: Dict[str, Any], policy2: Dict[str, Any]) -> Dict[str, Any]:
        """Comparar duas apólices extraídas"""
        
        differences = []
        similarities = []
        
        # Coletar todos os campos
        all_fields = set(policy1.keys()) | set(policy2.keys())
        
        for field in sorted(all_fields):
            val1 = policy1.get(field)
            val2 = policy2.get(field)
            
            if val1 is None and val2 is None:
                continue
            
            field_type = self._get_field_type(val1 or val2)
            
            # Comparar valores
            if val1 != val2:
                severity = self._determine_severity(field)
                diff = FieldDifference(
                    field_name=field,
                    value_policy1=val1,
                    value_policy2=val2,
                    field_type=field_type,
                    severity=severity
                )
                differences.append(diff)
            else:
                similarities.append({
                    "field": field,
                    "value": val1,
                    "type": field_type
                })
        
        return {
            "differences": self._serialize_differences(differences),
            "similarities": similarities,
            "difference_count": len(differences),
            "critical_differences": len([d for d in differences if d.severity == "high"]),
            "important_differences": len([d for d in differences if d.severity == "medium"]),
            "minor_differences": len([d for d in differences if d.severity == "low"])
        }
    
    @staticmethod
    def _get_field_type(value: Any) -> str:
        """Inferir tipo de campo"""
        if isinstance(value, list):
            return "list"
        elif isinstance(value, dict):
            return "dict"
        elif isinstance(value, (int, float)):
            return "number"
        elif isinstance(value, bool):
            return "boolean"
        else:
            return "string"
    
    def _determine_severity(self, field_name: str) -> str:
        """Determinar severidade da diferença"""
        if field_name in self.CRITICAL_FIELDS:
            return "high"
        elif field_name in self.IMPORTANT_FIELDS:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def _serialize_differences(differences: List[FieldDifference]) -> List[Dict]:
        """Serializar diferenças para JSON"""
        return [
            {
                "field": d.field_name,
                "type": d.field_type,
                "severity": d.severity,
                "policy1_value": d.value_policy1,
                "policy2_value": d.value_policy2
            }
            for d in differences
        ]
    
    @staticmethod
    def generate_comparison_summary(comparison: Dict[str, Any]) -> str:
        """Gerar resumo textual da comparação"""
        summary = []
        
        critical = comparison.get("critical_differences", 0)
        important = comparison.get("important_differences", 0)
        minor = comparison.get("minor_differences", 0)
        total = comparison.get("difference_count", 0)
        
        summary.append(f"RESUMO DA COMPARAÇÃO")
        summary.append(f"{'='*50}")
        summary.append(f"Total de diferenças: {total}")
        summary.append(f"  • Críticas (HIGH): {critical}")
        summary.append(f"  • Importantes (MEDIUM): {important}")
        summary.append(f"  • Menores (LOW): {minor}")
        summary.append("")
        
        if critical > 0:
            summary.append("⚠️  DIFERENÇAS CRÍTICAS (ATENÇÃO):")
            for diff in comparison.get("differences", []):
                if diff["severity"] == "high":
                    summary.append(f"  • {diff['field']}:")
                    summary.append(f"      Apólice 1: {diff['policy1_value']}")
                    summary.append(f"      Apólice 2: {diff['policy2_value']}")
            summary.append("")
        
        if important > 0:
            summary.append("⚡ DIFERENÇAS IMPORTANTES:")
            for diff in comparison.get("differences", []):
                if diff["severity"] == "medium":
                    summary.append(f"  • {diff['field']}:")
                    summary.append(f"      Apólice 1: {diff['policy1_value']}")
                    summary.append(f"      Apólice 2: {diff['policy2_value']}")
            summary.append("")
        
        similarities = comparison.get("similarities", [])
        if similarities:
            summary.append(f"✓ CAMPOS IDÊNTICOS ({len(similarities)}):")
            for sim in similarities[:5]:  # Mostrar apenas os 5 primeiros
                summary.append(f"  • {sim['field']}")
            if len(similarities) > 5:
                summary.append(f"  ... e mais {len(similarities)-5}")
        
        return "\n".join(summary)


def compare_policies(
    policy1: Dict[str, Any],
    policy2: Dict[str, Any]
) -> Tuple[Dict[str, Any], str]:
    """Função convenience para comparar apólices"""
    comparer = PolicyComparer()
    comparison = comparer.compare(policy1, policy2)
    summary = comparer.generate_comparison_summary(comparison)
    return comparison, summary


if __name__ == "__main__":
    # Test
    policy1 = {
        "numero_apolice": "DO-2024-001",
        "segurada": "Acme Corp",
        "limite_responsabilidade": "5M",
        "periodo_vigencia": "01/01/2024 - 31/12/2024",
        "franquia": "50k",
        "coberturas": ["DC", "DA", "RP"]
    }
    
    policy2 = {
        "numero_apolice": "DO-2024-002",
        "segurada": "Acme Corp",
        "limite_responsabilidade": "10M",
        "periodo_vigencia": "01/01/2024 - 31/12/2024",
        "franquia": "100k",
        "coberturas": ["DC", "DA", "RP", "RC"]
    }
    
    comparison, summary = compare_policies(policy1, policy2)
    print(summary)
    print("\n" + "="*50)
    print(json.dumps(comparison, indent=2, ensure_ascii=False, default=str))
