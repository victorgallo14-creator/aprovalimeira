import streamlit as st
from supabase import create_client, Client
import random
import json
from datetime import datetime, timezone

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E CONEXÃO COM SUPABASE
# ==============================================================================
st.set_page_config(page_title="Plataforma de Avaliação", layout="wide", page_icon="📝")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error("Configure as credenciais do Supabase (SUPABASE_URL e SUPABASE_KEY) nos Secrets do Streamlit Cloud.")
    st.stop()

# ==============================================================================
# 2. CLASSES DE GERENCIAMENTO
# ==============================================================================
class SistemaSimulados:
    def __init__(self, db_client):
        self.db = db_client

    def buscar_questoes_aleatorias(self, limite: int):
        try:
            res = self.db.table("banco_questoes_geral").select("*").execute()
            dados = res.data if hasattr(res, 'data') else res
            if not dados:
                return []
            random.shuffle(dados)
            return dados[:limite]
        except Exception as e:
            st.error(f"Erro de conexão ao extrair questões: {e}")
            return []

    def registrar_resultado(self, usuario: str, nota: float, acertos: int, erros: int, relatorio_descritivo: list):
        dados_historico = {
            "usuario": usuario,
            "nota": nota,
            "acertos": acertos,
            "erros": erros,
            "relatorio_descritivo": relatorio_descritivo,
            "data_execucao": datetime.now(timezone.utc).isoformat()
        }
        try:
            self.db.table("resultados_simulados").insert(dados_historico).execute()
        except Exception as e:
            st.error(f"Falha de sincronização ao registrar o diagnóstico da prova: {e}")

# ==============================================================================
# 3. INICIALIZAÇÃO DE ESTADOS E ESTILOS
# ==============================================================================
if 'gerenciador_simulados' not in st.session_state:
    st.session_state.gerenciador_simulados = SistemaSimulados(supabase)

if 'estado_prova' not in st.session_state:
    st.session_state.estado_prova = 'configuracao'

st.markdown("""
<style>
    .sim-header { background: linear-gradient(135deg, #1e293b 0%, #334155 100%); padding: 30px; border-radius: 12px; color: white; margin-bottom: 30px; box-shadow: 0 10px 25px rgba(15, 23, 42, 0.2); }
    .sim-title { font-size: 2.2rem; font-weight: 800; line-height: 1.1; margin-bottom: 5px; }
    .questao-box { background: white; padding: 30px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);}
    .feedback-box { padding: 25px; margin-bottom: 20px; border-radius: 8px; line-height: 1.7; color: #334155; text-align: justify; font-size: 1.05rem; }
    .feedback-acerto { background-color: #f0fdf4; border-left: 5px solid #22c55e; }
    .feedback-erro { background-color: #fef2f2; border-left: 5px solid #ef4444; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sim-header">
    <div class="sim-title">Plataforma de Avaliação Dinâmica</div>
    <div style="color: #cbd5e1; font-size: 1rem;">Geração algorítmica de simulados e emissão de pareceres qualitativos independentes.</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. FLUXO 1: CONFIGURAÇÃO DO SIMULADO
# ==============================================================================
if st.session_state.estado_prova == 'configuracao':
    st.markdown("### Parâmetros da Avaliação")
    qtd = st.number_input("Defina a extensão do simulado (número de questões):", min_value=5, max_value=100, value=20, step=5)
    
    if st.button("Gerar e Iniciar Prova", type="primary", use_container_width=True):
        questoes_selecionadas = st.session_state.gerenciador_simulados.buscar_questoes_aleatorias(qtd)
        
        if questoes_selecionadas:
            st.session_state.prova_atual = questoes_selecionadas
            st.session_state.estado_prova = 'execucao'
            st.rerun()
        else:
            st.warning("O banco de dados encontra-se desabastecido. Cadastre questões na tabela 'banco_questoes_geral' do Supabase para iniciar.")

# ==============================================================================
# 5. FLUXO 2: EXECUÇÃO DA PROVA
# ==============================================================================
elif st.session_state.estado_prova == 'execucao':
    form_respostas = {}
    
    with st.form(key="form_prova_independente"):
        for i, q in enumerate(st.session_state.prova_atual):
            st.markdown(f"<div class='questao-box'>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 1.1rem; font-weight: 600; color: #0f172a;'>Questão {i+1}: {q.get('enunciado', 'Enunciado indisponível')}</p>", unsafe_allow_html=True)
            
            alts = q.get("alternativas", [])
            if isinstance(alts, str):
                try: alts = json.loads(alts)
                except: alts = [alts]
            
            form_respostas[str(i)] = st.radio(
                f"Selecione sua resposta para a questão {i+1}", 
                alts, 
                index=None, 
                key=f"alt_rad_{i}",
                label_visibility="collapsed"
            )
            st.markdown("</div>", unsafe_allow_html=True)
            
        submitted = st.form_submit_button("Submeter Avaliação e Obter Diagnóstico", type="primary", use_container_width=True)
        
        if submitted:
            acertos = 0
            erros = 0
            relatorio_qualitativo = []
            
            for i, q in enumerate(st.session_state.prova_atual):
                alts = q.get("alternativas", [])
                if isinstance(alts, str):
                    try: alts = json.loads(alts)
                    except: alts = [alts]
                    
                gabarito_idx = q.get("gabarito", 0)
                resposta_usuario = form_respostas[str(i)]
                
                is_correct = False
                if resposta_usuario and resposta_usuario in alts:
                    idx_resp = alts.index(resposta_usuario)
                    is_correct = (idx_resp == gabarito_idx)
                    
                if is_correct: acertos += 1
                else: erros += 1
                
                texto_parecer = f"A análise diagnóstica do seu desempenho nesta questão confirma a plena exatidão do seu raciocínio lógico e interpretativo. A alternativa assinalada reflete rigorosamente a fundamentação exigida pela base de dados, consolidando o entendimento de que a resposta adequada é a afirmação de que '{alts[gabarito_idx]}'. Esta concordância evidencia uma sólida apropriação conceitual acerca da temática abordada." if is_correct else f"O percurso de resolução adotado nesta questão culminou em um desvio em relação ao gabarito técnico institucional. O sistema registrou a marcação da alternativa '{resposta_usuario if resposta_usuario else 'Opção não assinalada'}', o que contrasta com a diretriz oficial esperada para a situação-problema apresentada. A avaliação criteriosa aponta que a interpretação correta repousa sobre a premissa de que '{alts[gabarito_idx]}'. Esta divergência foi formalmente documentada no histórico analítico para nortear futuros direcionamentos formativos e revisões de conteúdo."
                
                relatorio_qualitativo.append({
                    "questao": i + 1,
                    "acertou": is_correct,
                    "texto_parecer": texto_parecer
                })
            
            total_q = len(st.session_state.prova_atual)
            nota_final = (acertos / total_q) * 100 if total_q > 0 else 0
            
            # Como é independente, usamos um identificador padrão genérico até você implementar login
            usuario_identificacao = "Aluno_Plataforma"
            st.session_state.gerenciador_simulados.registrar_resultado(
                usuario_identificacao, nota_final, acertos, erros, relatorio_qualitativo
            )
            
            st.session_state.resultado_atual = {
                "nota": nota_final, "acertos": acertos, "erros": erros, "relatorio": relatorio_qualitativo
            }
            st.session_state.estado_prova = 'diagnostico'
            st.rerun()

# ==============================================================================
# 6. FLUXO 3: DIAGNÓSTICO E PARECERES DESCRITIVOS
# ==============================================================================
elif st.session_state.estado_prova == 'diagnostico':
    res = st.session_state.resultado_atual
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Índice de Aproveitamento", f"{res['nota']:.1f}%")
    c2.metric("Total de Acertos", res['acertos'])
    c3.metric("Total de Erros", res['erros'])
    
    st.markdown("<h3 style='margin-top: 30px; color: #0f172a;'>Pareceres Analíticos do Desempenho</h3>", unsafe_allow_html=True)
    
    for det in res['relatorio']:
        classe_css = "feedback-acerto" if det['acertou'] else "feedback-erro"
        icone_titulo = "Aprovação Qualitativa" if det['acertou'] else "Oportunidade de Correção"
        
        st.markdown(f"""
        <div class='feedback-box {classe_css}'>
            <strong style='font-size: 1.15rem;'>Questão {det['questao']} - {icone_titulo}</strong><br><br>
            {det['texto_parecer']}
        </div>
        """, unsafe_allow_html=True)
        
    if st.button("Configurar Novo Ciclo de Avaliação", type="primary"):
        st.session_state.estado_prova = 'configuracao'
        st.session_state.prova_atual = []
        st.session_state.resultado_atual = {}
        st.rerun()
