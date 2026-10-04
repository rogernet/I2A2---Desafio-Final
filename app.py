"""
app.py - Interface Streamlit para AI2Shield

MVP funcional de plataforma de análise e comparação de apólices D&O
"""

import streamlit as st
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

# === TIMEZONE BRT ===
BRT = timezone(timedelta(hours=-3))

def datetime_brt():
    """Retorna datetime atual em timezone BRT (Brasília)"""
    return datetime.now(BRT).replace(tzinfo=None)

from extraction import PolicyExtractor
from policy_agent import PolicyExtractionAgent
from compare_agent import PolicyComparer
from report_agent import ReportGenerator
from storage import PolicyStorage, ComparisonStorage, ReportStorage, init_db, SessionLocal, PolicyExtraction, PolicyComparison

# === CONFIG ===
st.set_page_config(
    page_title="AI2Shield — Plataforma de Análise D&O",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar banco de dados
init_db()

# === SESSION STATE ===
if "last_file_hash" not in st.session_state:
    st.session_state.last_file_hash = None
if "extraction_complete" not in st.session_state:
    st.session_state.extraction_complete = False

# === STYLES ===
st.markdown("""
<style>
    body {
        background-color: #0f1419;
        color: #e0e6ed;
    }
    
    .main-header { 
        font-size: 2.5em; 
        font-weight: bold; 
        color: #00d9ff;
    }
    
    .section-header { 
        font-size: 1.8em; 
        font-weight: bold; 
        color: #00d9ff; 
        border-bottom: 2px solid #00d9ff; 
        padding-bottom: 10px; 
    }
    
    .stat-box { 
        padding: 15px; 
        border-radius: 5px; 
        background: #1a1f2e;
    }
    
    .difference-high { 
        background: #2d1f26; 
        padding: 10px; 
        border-radius: 3px; 
        margin: 5px 0;
        color: #e0e6ed;
    }
    
    .difference-medium { 
        background: #2d2620; 
        padding: 10px; 
        border-radius: 3px; 
        margin: 5px 0;
        color: #e0e6ed;
    }
    
    .success { 
        background: #1f2d26; 
        padding: 10px; 
        border-radius: 3px;
        color: #e0e6ed;
    }
    
    .stMetric {
        background-color: #1a1f2e;
        padding: 10px;
        border-radius: 8px;
    }
    
    .stButton > button {
        background-color: #1e3a5f;
        color: #e0e6ed;
        border: 1px solid #00d9ff;
    }
    
    .stButton > button:hover {
        background-color: #00d9ff;
        color: #0f1419;
    }
</style>
""", unsafe_allow_html=True)

# === SIDEBAR ===
with st.sidebar:
    st.markdown("# ⚙️ Configuração")
    
    mode = st.radio(
        "Modo de Operação",
        ["📄 Extrair Apólice", "⚖️ Comparar Apólices", "📊 Histórico", "⚙️ Administração"],
        help="Selecione o modo de operação"
    )
    
    st.markdown("---")
    st.markdown("### Sobre")
    st.markdown("""
    **AI2Shield** v1.0
    
    Plataforma inteligente para análise e comparação de apólices D&O.
    
    Desenvolvido por AI2Shield
    
    Powered by:
    - ✨ Inteligência Artificial (LLM)
    - 🔍 OCR Inteligente
    - 📊 Análise Comparativa
    """)


# === MAIN CONTENT ===
st.markdown('<div class="main-header">🛡️ AI2Shield</div>', unsafe_allow_html=True)
st.markdown("*Análise Inteligente de Apólices D&O*")
st.markdown("---")

# === MODE 1: EXTRAIR APÓLICE ===
if mode == "📄 Extrair Apólice":
    st.markdown('<div class="section-header">Extração de Apólices</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Upload de Documento")
        uploaded_file = st.file_uploader(
            "Selecione um PDF ou Imagem",
            type=["pdf", "png", "jpg", "jpeg", "gif", "bmp"],
            help="Suportado: PDF, PNG, JPG, etc."
        )
    
    with col2:
        st.markdown("### Opções")
        use_ocr = st.checkbox("Forçar OCR", value=False)
    
    if uploaded_file:
        # Computar hash para detectar mudança de arquivo
        temp_path = f"/tmp/{uploaded_file.name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        file_hash = hashlib.sha256(uploaded_file.getbuffer()).hexdigest()
        
        # Se arquivo mudou, limpar logs anteriores
        if file_hash != st.session_state.last_file_hash:
            st.session_state.last_file_hash = file_hash
            st.session_state.extraction_complete = False
            # Limpar tela
            st.rerun()
        
        # Container que será limpo a cada novo processamento
        output_area = st.empty()
        
        with output_area.container():
            with st.spinner("🔄 Processando..."):
                # ETAPA 1: Extração
                st.markdown("### 1️⃣ Extração de Texto")
                extractor = PolicyExtractor()
                extraction = extractor.extract(temp_path)
                file_hash = extractor.compute_hash(temp_path)
                
                if extraction["success"]:
                    st.success("✓ Texto extraído com sucesso")
                    st.markdown(f"**Páginas:** {extraction.get('pages', '?')}")
                    with st.expander("📄 Ver texto extraído"):
                        st.text_area("Conteúdo", extraction["text"][:1000] + "...", height=200, disabled=True)
                else:
                    st.error(f"❌ Erro na extração: {extraction.get('error', 'Unknown error')}")
                    st.stop()
                
                # ETAPA 2: Extração Estruturada
                st.markdown("### 2️⃣ Extração de Campos")
                agent = PolicyExtractionAgent()
                
                with st.spinner("🤖 Analisando com IA..."):
                    try:
                        fields = agent.extract_fields(extraction["text"])
                        st.success("✓ Campos extraídos com sucesso")
                        
                        # Mostrar campos
                        for key, value in fields.items():
                            if not key.startswith("error"):
                                st.markdown(f"**{key}:** `{str(value)[:100]}`")
                        
                        # ETAPA 3: Salvar
                        st.markdown("### 3️⃣ Armazenamento")
                        if st.button("💾 Salvar Apólice", key="save_btn"):
                            policy = PolicyStorage.save_extraction(
                                filename=uploaded_file.name,
                                file_hash=file_hash,
                                extracted_data=fields,
                                raw_text=extraction["text"],
                                metadata={
                                    "pages": extraction.get("pages"),
                                    "upload_date": datetime_brt().isoformat()
                                }
                            )
                            st.success(f"✓ Apólice salva com ID: {policy.id}")
                            st.balloons()
                    
                    except Exception as e:
                        st.error(f"❌ Erro na extração: {str(e)}")


# === MODE 2: COMPARAR APÓLICES ===
elif mode == "⚖️ Comparar Apólices":
    st.markdown('<div class="section-header">Comparação de Apólices</div>', unsafe_allow_html=True)
    
    # Listar apólices salvas
    policies = PolicyStorage.list_extractions()
    
    if not policies:
        st.warning("⚠️ Nenhuma apólice extraída ainda. Vá para 'Extrair Apólice' primeiro.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Apólice 1")
            policy1_id = st.selectbox(
                "Selecione a primeira apólice",
                options=[p.id for p in policies],
                format_func=lambda x: next((p.filename for p in policies if p.id == x), "Unknown")
            )
        
        with col2:
            st.markdown("### Apólice 2")
            policy2_id = st.selectbox(
                "Selecione a segunda apólice",
                options=[p.id for p in policies],
                format_func=lambda x: next((p.filename for p in policies if p.id == x), "Unknown"),
                key="policy2_select"
            )
        
        if policy1_id and policy2_id:
            if st.button("🔄 Comparar Apólices"):
                with st.spinner("Comparando..."):
                    p1 = PolicyStorage.get_extraction(policy1_id)
                    p2 = PolicyStorage.get_extraction(policy2_id)
                    
                    # Validar qualidade de extração ANTES de comparar
                    def count_none_fields(data):
                        """Contar quantos campos são None"""
                        if not data:
                            return 10
                        return sum(1 for v in data.values() if v is None)
                    
                    none_count_p1 = count_none_fields(p1.extracted_data)
                    none_count_p2 = count_none_fields(p2.extracted_data)
                    
                    if none_count_p1 > 5:
                        st.error(f"⚠️ Apólice 1 tem problemas: {none_count_p1}/10 campos não extraídos")
                        st.warning("Tente re-uploadar o PDF com melhor qualidade")
                        st.stop()
                    
                    if none_count_p2 > 5:
                        st.error(f"⚠️ Apólice 2 tem problemas: {none_count_p2}/10 campos não extraídos")
                        st.info(f"Dados brutos encontrados: {str(p2.extracted_data.get('raw', ''))[:100]}...")
                        st.warning("Tente re-uploadar o PDF com melhor qualidade")
                        st.stop()
                    
                    # Comparação
                    comparer = PolicyComparer()
                    comparison = comparer.compare(
                        p1.extracted_data,
                        p2.extracted_data
                    )
                    summary = comparer.generate_comparison_summary(comparison)
                    
                    # Salvar comparação
                    comp_record = ComparisonStorage.save_comparison(
                        policy1_id=policy1_id,
                        policy2_id=policy2_id,
                        comparison_result=comparison,
                        differences=comparison.get("differences", [])
                    )
                    
                    # Gerar recomendações
                    report_gen = ReportGenerator()
                    recommendations = report_gen.generate_recommendations(comparison)
                    
                    # Gerar relatório HTML
                    html_report = report_gen.generate_html_report(
                        p1.filename,
                        p2.filename,
                        comparison,
                        summary,
                        recommendations
                    )
                    
                    # Salvar relatório
                    ReportStorage.save_report(
                        comparison_id=comp_record.id,
                        summary=summary,
                        recommendations=recommendations,
                        report_html=html_report
                    )
                    
                    # EXIBIR RESULTADOS
                    st.success("✓ Comparação concluída!")
                    
                    # Stats
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown('<div class="stat-box"><div style="font-size:2em; font-weight:bold;">' + 
                                   str(comparison["difference_count"]) + '</div><div>Diferenças</div></div>',
                                   unsafe_allow_html=True)
                    with col2:
                        st.markdown('<div class="stat-box"><div style="font-size:2em; font-weight:bold;">' + 
                                   str(comparison["critical_differences"]) + '</div><div>Críticas</div></div>',
                                   unsafe_allow_html=True)
                    with col3:
                        st.markdown('<div class="stat-box"><div style="font-size:2em; font-weight:bold;">' + 
                                   str(comparison["important_differences"]) + '</div><div>Importantes</div></div>',
                                   unsafe_allow_html=True)
                    with col4:
                        st.markdown('<div class="stat-box"><div style="font-size:2em; font-weight:bold;">' + 
                                   str(len(comparison.get("similarities", []))) + '</div><div>Idênticas</div></div>',
                                   unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Resumo
                    st.markdown("### 📊 Resumo")
                    st.text(summary)
                    
                    st.markdown("---")
                    
                    # Recomendações
                    st.markdown("### 💡 Recomendações")
                    for rec in recommendations:
                        if rec["priority"] == "HIGH":
                            st.markdown(f'<div class="difference-high"><strong>[{rec["priority"]}]</strong> {rec["category"]}: {rec["recommendation"]}</div>', unsafe_allow_html=True)
                        elif rec["priority"] == "MEDIUM":
                            st.markdown(f'<div class="difference-medium"><strong>[{rec["priority"]}]</strong> {rec["category"]}: {rec["recommendation"]}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="success"><strong>[{rec["priority"]}]</strong> {rec["category"]}: {rec["recommendation"]}</div>', unsafe_allow_html=True)
                    
                    # Download HTML
                    st.markdown("---")
                    st.download_button(
                        label="📥 Baixar Relatório (HTML)",
                        data=html_report,
                        file_name=f"apolice_comparison_{datetime_brt().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html"
                    )


# === MODE 3: HISTÓRICO ===
elif mode == "📊 Histórico":
    st.markdown('<div class="section-header">Histórico de Operações</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Apólices", "Comparações", "Relatórios"])
    
    with tab1:
        st.markdown("### Apólices Extraídas")
        policies = PolicyStorage.list_extractions()
        if policies:
            for p in policies:
                st.markdown(f"**{p.filename}** (ID: {p.id})")
                st.markdown(f"Data: {p.created_at} | Hash: `{p.file_hash[:16]}...`")
                st.json(p.extracted_data)
                st.markdown("---")
        else:
            st.info("Nenhuma apólice extraída ainda")
    
    with tab2:
        st.markdown("### Comparações Realizadas")
        comparisons = ComparisonStorage.list_comparisons()
        if comparisons:
            for c in comparisons:
                st.markdown(f"**Comparação ID {c.id}**")
                st.markdown(f"Apólices: {c.policy1_id} vs {c.policy2_id} | Data: {c.created_at}")
                st.markdown(f"Diferenças: {len(c.differences)}")
                st.markdown("---")
        else:
            st.info("Nenhuma comparação realizada ainda")
    
    with tab3:
        st.markdown("### Relatórios Gerados")
        st.info("Relatórios são gerados junto com as comparações")


# === MODE 4: ADMINISTRAÇÃO ===
elif mode == "⚙️ Administração":
    st.markdown('<div class="section-header">Painel de Administração</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Estatísticas do Banco")
        
        extractions = PolicyStorage.list_extractions()
        comparisons = ComparisonStorage.list_comparisons()
        
        st.metric("Apólices Extraídas", len(extractions) if extractions else 0)
        st.metric("Comparações Realizadas", len(comparisons) if comparisons else 0)
    
    with col2:
        st.markdown("#### 🗑️ Limpeza de Dados")
        st.warning("**⚠️ CUIDADO:** Estas operações são irreversíveis!")
        
        col_delete, col_restore = st.columns(2)
        
        with col_delete:
            if st.button("🗑️ Deletar TODAS as Apólices", key="delete_all_extractions"):
                try:
                    db = SessionLocal()
                    db.query(PolicyExtraction).delete()
                    db.commit()
                    db.close()
                    st.success("✅ Todas as apólices foram deletadas!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Erro ao deletar: {str(e)}")
        
        with col_restore:
            if st.button("🗑️ Deletar TODAS as Comparações", key="delete_all_comparisons"):
                try:
                    db = SessionLocal()
                    db.query(PolicyComparison).delete()
                    db.commit()
                    db.close()
                    st.success("✅ Todas as comparações foram deletadas!")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ Erro ao deletar: {str(e)}")
    
    st.markdown("---")
    
    # Listar apólices para deletar individualmente
    st.markdown("#### 📋 Apólices para Deletar")
    
    extractions = PolicyStorage.list_extractions()
    if extractions:
        for extraction in extractions:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{extraction.filename}** (ID: {extraction.id})")
                st.caption(f"Hash: {extraction.file_hash[:16]}... | {extraction.created_at}")
            
            with col2:
                if st.button("👁️ Ver", key=f"view_{extraction.id}"):
                    st.json(extraction.extracted_data)
            
            with col3:
                if st.button("🗑️", key=f"delete_{extraction.id}"):
                    try:
                        db = SessionLocal()
                        db.query(PolicyExtraction).filter(PolicyExtraction.id == extraction.id).delete()
                        db.commit()
                        db.close()
                        st.success(f"✅ {extraction.filename} deletado!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
    else:
        st.info("Nenhuma apólice para deletar")


# === FOOTER ===
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.9em;">
    <p>AI2Shield v1.0 | Análise Inteligente de Apólices D&O</p>
    <p>Desenvolvido por AI2Shield</p>
</div>
""", unsafe_allow_html=True)
