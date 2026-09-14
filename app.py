import streamlit as st
from supabase import create_client, Client
import random
import json
from datetime import datetime, timezone
import time

# ==============================================================================
# 1. CONFIGURAÇÃO DE ALTA PERFORMANCE E UI PREMIUM
# ==============================================================================
st.set_page_config(page_title="Plataforma de Avaliação Cognitiva", layout="wide", page_icon="🧠", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error("Configuração de segurança pendente. Insira SUPABASE_URL e SUPABASE_KEY nos Secrets.")
    st.stop()

# ==============================================================================
# 2. MOTOR COGNITIVO E ACESSO A DADOS
# ==============================================================================
class MotorCognitivo:
    def __init__(self, db_client):
        self.db = db_client

    def buscar_questoes(self, limite: int):
        try:
            res = self.db.table("banco_questoes_geral").select("*").execute()
            dados = res.data if hasattr(res, 'data') else res
            if not dados: return []
            random.shuffle(dados)
            return dados[:limite]
        except Exception:
            return []

    def registrar_auditoria(self, usuario: str, nota_bruta: float, nota_ponderada: float, acertos: int, erros: int, relatorio: list):
        dados = {
            "usuario": usuario,
            "nota": nota_bruta,
            "acertos": acertos,
            "erros": erros,
            "relatorio_descritivo": relatorio,
            "data_execucao": datetime.now(timezone.utc).isoformat()
        }
        try:
            self.db.table("resultados_simulados").insert(dados).execute()
        except Exception as e:
            st.error(f"Falha na sincronização de dados: {e}")

# ==============================================================================
# 3. ESTILIZAÇÃO AVANÇADA (CSS)
# ==============================================================================
st.markdown("""
<style>
    /* Tipografia e Fundo */
    .stApp { background-color: #f8fafc; }
    
    /* Cabeçalhos Premium */
    .hero-container { background: linear-gradient(135deg, #0f172a 0%, #3b82f6 100%); padding: 40px; border-radius: 16px; color: white; margin-bottom: 40px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); }
    .hero-title { font-size: 2.8rem; font-weight: 900; letter-spacing: -0.02em; margin-bottom: 10px; }
    .hero-subtitle { font-size: 1.1rem; color: #e2e8f0; font-weight: 300; }
    
    /* Cards de Questões */
    .question-card { background: white; padding: 35px; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); transition: transform 0.2s ease; }
    .question-card:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
    .question-number { font-size: 0.9rem; font-weight: 700; color: #3b82f6; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 15px; display: block; }
    .question-text { font-size: 1.2rem; color: #1e293b; font-weight: 600; line-height: 1.6; margin-bottom: 25px; }
    
    /* Relatórios Descritivos Textuais */
    .report-card { background: white; padding: 30px; border-radius: 12px; margin-bottom: 25px; border-left: 6px solid; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .report-success { border-color: #10b981; }
    .report-error { border-color: #ef4444; }
    .report-content { font-size: 1.1rem; line-height: 1.8; color: #334155; text-align: justify; margin-top: 15px; }
    
    /* Métricas */
    .metric-container { background: white; padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #e2e8f0; }
    .metric-value { font-size: 2.5rem; font-weight: 800; color: #0f172a; }
    .metric-label { font-size: 0.9rem; color: #64748b; font-weight: 600; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. GERENCIAMENTO DE ESTADO
# ==============================================================================
if 'motor' not in st.session_state: st.session_state.motor = MotorCognitivo(supabase)
if 'fase_app' not in st.session_state: st.session_state.fase_app = 'dashboard'
if 'start_time' not in st.session_state: st.session_state.start_time = None

# ==============================================================================
# 5. FASE 1: DASHBOARD E CONFIGURAÇÃO
# ==============================================================================
if st.session_state.fase_app == 'dashboard':
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Sistema de Avaliação Cognitiva</div>
        <div class="hero-subtitle">Plataforma algorítmica de alto rendimento. Análise pedagógica descritiva e ponderação de metacognição em tempo real.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("<div style='background: white; padding: 40px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #0f172a; text-align: center; margin-bottom: 30px;'>Parâmetros da Sessão de Estudo</h3>", unsafe_allow_html=True)
        
        qtd_questoes = st.slider("Extensão do simulado:", min_value=5, max_value=50, value=10, step=5)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 INICIAR SESSÃO DE ALTA PERFORMANCE", type="primary", use_container_width=True):
            with st.spinner("O motor cognitivo está extraindo e embaralhando o banco de dados..."):
                time.sleep(1) # Simulação de carregamento complexo para efeito premium
                questoes = st.session_state.motor.buscar_questoes(qtd_questoes)
                if questoes:
                    st.session_state.prova_atual = questoes
                    st.session_state.fase_app = 'execucao'
                    st.session_state.start_time = time.time()
                    st.rerun()
                else:
                    st.error("O banco de dados de questões está vazio. Acesse o painel SQL do Supabase para inserir o acervo.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# 6. FASE 2: EXECUÇÃO DA AVALIAÇÃO (COM METACOGNIÇÃO)
# ==============================================================================
elif st.session_state.fase_app == 'execucao':
    st.markdown("<h2 style='color: #0f172a; margin-bottom: 30px;'>Avaliação em Progresso</h2>", unsafe_allow_html=True)
    
    respostas = {}
    confiancas = {}
    
    with st.form("form_avaliacao"):
        for i, q in enumerate(st.session_state.prova_atual):
            st.markdown(f"<div class='question-card'>", unsafe_allow_html=True)
            st.markdown(f"<span class='question-number'>Questão Analítica {i+1}</span>", unsafe_allow_html=True)
            st.markdown(f"<div class='question-text'>{q.get('enunciado', 'Enunciado não localizado.')}</div>", unsafe_allow_html=True)
            
            alts = q.get("alternativas", [])
            if isinstance(alts, str):
                try: alts = json.loads(alts)
                except: alts = [alts]
                
            col_resp, col_conf = st.columns([2, 1])
            with col_resp:
                respostas[str(i)] = st.radio("Selecione sua diretriz:", alts, index=None, key=f"r_{i}", label_visibility="collapsed")
            with col_conf:
                st.markdown("<span style='font-size: 0.9rem; color: #64748b; font-weight: 600;'>Grau de Certeza Técnica:</span>", unsafe_allow_html=True)
                confiancas[str(i)] = st.select_slider("", options=["Dúvida/Chute", "Raciocínio Lógico", "Certeza Absoluta"], value="Raciocínio Lógico", key=f"c_{i}", label_visibility="collapsed")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        if st.form_submit_button("PROCESSAR DADOS E GERAR DIAGNÓSTICO", type="primary", use_container_width=True):
            tempo_gasto = round((time.time() - st.session_state.start_time) / 60, 2)
            acertos, erros = 0, 0
            pontuacao_ponderada = 0
            relatorio = []
            
            for i, q in enumerate(st.session_state.prova_atual):
                alts = q.get("alternativas", [])
                if isinstance(alts, str):
                    try: alts = json.loads(alts)
                    except: alts = [alts]
                    
                gab_idx = q.get("gabarito", 0)
                resp_user = respostas[str(i)]
                conf_user = confiancas[str(i)]
                
                is_correct = False
                if resp_user and resp_user in alts:
                    is_correct = (alts.index(resp_user) == gab_idx)
                
                if is_correct:
                    acertos += 1
                    if conf_user == "Certeza Absoluta": pontuacao_ponderada += 1.2
                    elif conf_user == "Raciocínio Lógico": pontuacao_ponderada += 1.0
                    else: pontuacao_ponderada += 0.8
                    
                    texto_parecer = f"A verificação dos registros cognitivos demonstra que a linha de raciocínio estabelecida para solucionar esta situação-problema atingiu a precisão esperada. A fundamentação selecionada, que aponta a resposta como sendo '{alts[gab_idx]}', converge inteiramente com as diretrizes técnicas e teóricas da base curricular adotada. O grau de certeza informado reflete uma ancoragem sólida do conhecimento, sugerindo que os conceitos estruturais pertinentes a esta disciplina já foram devidamente apropriados e processados pelo candidato."
                else:
                    erros += 1
                    if conf_user == "Certeza Absoluta": pontuacao_ponderada -= 0.5
                    elif conf_user == "Raciocínio Lógico": pontuacao_ponderada -= 0.2
                    
                    texto_parecer = f"O diagnóstico desta etapa revela uma dissintonia entre a construção analítica elaborada e os pressupostos validados oficialmente pelo gabarito. A interpretação registrada inclinou-se para a concepção de que a resposta adequada seria '{resp_user if resp_user else 'Opção deixada em branco'}', o que caracteriza um desvio de interpretação ou uma fragilidade conceitual frente ao objeto de estudo. Uma revisão aprofundada faz-se necessária para realinhar a percepção do candidato à resolução técnica correta, que estabelece categoricamente que a alternativa exata é '{alts[gab_idx]}'. Este apontamento foi registrado no histórico evolutivo para garantir a repescagem pedagógica deste conceito."
                
                relatorio.append({
                    "questao": i + 1,
                    "acertou": is_correct,
                    "certeza_informada": conf_user,
                    "texto_parecer": texto_parecer
                })
            
            nota_bruta = (acertos / len(st.session_state.prova_atual)) * 100
            st.session_state.resultado = {
                "nota": nota_bruta,
                "nota_ponderada": pontuacao_ponderada,
                "acertos": acertos,
                "erros": erros,
                "tempo": tempo_gasto,
                "relatorio": relatorio
            }
            
            st.session_state.motor.registrar_auditoria("Candidato_Premium", nota_bruta, pontuacao_ponderada, acertos, erros, relatorio)
            st.session_state.fase_app = 'relatorio'
            st.rerun()

# ==============================================================================
# 7. FASE 3: AUDITORIA E RELATÓRIO PEDAGÓGICO DESCRITIVO
# ==============================================================================
elif st.session_state.fase_app == 'relatorio':
    res = st.session_state.resultado
    
    st.markdown("<h2 style='color: #0f172a; margin-bottom: 20px;'>Auditoria de Desempenho e Diagnóstico</h2>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='metric-container'><div class='metric-value'>{res['nota']:.1f}%</div><div class='metric-label'>Precisão Bruta</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-container'><div class='metric-value'>{res['acertos']}</div><div class='metric-label'>Acertos Exatos</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='metric-container'><div class='metric-value'>{res['erros']}</div><div class='metric-label'>Intervenções Necessárias</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='metric-container'><div class='metric-value'>{res['tempo']}m</div><div class='metric-label'>Fadiga Cognitiva (Tempo)</div></div>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin-top: 40px; color: #1e293b;'>Pareceres Pedagógicos Descritivos</h3>", unsafe_allow_html=True)
    st.write("Abaixo consta a avaliação qualitativa em prosa contínua do seu rendimento por item, assegurando a compreensão integral das habilidades exigidas e das lacunas evidenciadas.")
    
    for det in res['relatorio']:
        css_class = "report-success" if det['acertou'] else "report-error"
        status_title = "Domínio Evidenciado" if det['acertou'] else "Revisão Crítica Recomendada"
        icon = "✅" if det['acertou'] else "❌"
        
        st.markdown(f"""
        <div class='report-card {css_class}'>
            <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; padding-bottom: 15px;'>
                <span style='font-size: 1.2rem; font-weight: 700; color: #0f172a;'>{icon} Análise da Questão {det['questao']} — {status_title}</span>
                <span style='font-size: 0.85rem; background-color: #f1f5f9; padding: 5px 12px; border-radius: 20px; color: #475569; font-weight: 600;'>Fator Declarado: {det['certeza_informada']}</span>
            </div>
            <div class='report-content'>{det['texto_parecer']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 RETORNAR AO CENTRO DE CONTROLE PARA NOVO CICLO", type="primary"):
        st.session_state.fase_app = 'dashboard'
        st.rerun()
