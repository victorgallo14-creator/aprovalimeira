import streamlit as st
from supabase import create_client, Client
import random
import json
import time
from datetime import datetime, timezone

# ==============================================================================
# CONFIGURAÇÃO CORE E PERFORMANCE
# ==============================================================================
st.set_page_config(page_title="Aprova Limeira | Avaliação Cognitiva", layout="wide", page_icon="🏛️")

@st.cache_resource
def init_connection() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase = init_connection()
except Exception:
    st.error("Credenciais do Supabase ausentes nos Secrets.")
    st.stop()

# Cache de alta performance com tempo de expiração (TTL) para evitar chamadas redundantes
@st.cache_data(ttl=3600)
def carregar_banco_questoes(cargo_alvo: str):
    res = supabase.table("banco_questoes_geral").select("*").eq("cargo", cargo_alvo).execute()
    return res.data if hasattr(res, 'data') else res

# ==============================================================================
# CSS PREMIUM E DESIGN SYSTEM
# ==============================================================================
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    .login-container { max-width: 450px; margin: 10vh auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }
    .brand-title { font-size: 2.5rem; font-weight: 900; color: #0f172a; text-align: center; letter-spacing: -1px; }
    .brand-subtitle { font-size: 1rem; color: #64748b; text-align: center; margin-bottom: 30px; }
    
    .nav-header { background: #0f172a; padding: 20px 40px; color: white; border-radius: 12px; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center; }
    
    .question-card { background: white; padding: 35px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 25px; transition: 0.2s; }
    .question-card:hover { border-color: #cbd5e1; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }
    .question-text { font-size: 1.15rem; color: #1e293b; font-weight: 600; line-height: 1.6; margin-bottom: 20px; }
    
    .report-card { background: white; padding: 25px; border-radius: 8px; margin-bottom: 20px; border-left: 5px solid; }
    .report-success { border-color: #10b981; }
    .report-error { border-color: #ef4444; }
    .report-text { font-size: 1.05rem; line-height: 1.7; color: #334155; text-align: justify; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# CONTROLE DE SESSÃO
# ==============================================================================
if 'usuario' not in st.session_state: st.session_state.usuario = None
if 'rota' not in st.session_state: st.session_state.rota = 'login'

# ==============================================================================
# ÁREA DE IDENTIFICAÇÃO E REGISTRO
# ==============================================================================
if st.session_state.usuario is None:
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<div class='brand-title'>Aprova Limeira</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-subtitle'>Plataforma de Alta Performance</div>", unsafe_allow_html=True)
    
    aba_login, aba_registro = st.tabs(["Acesso", "Novo Cadastro"])
    
    with aba_login:
        email_login = st.text_input("E-mail de acesso")
        if st.button("Entrar", use_container_width=True, type="primary"):
            res = supabase.table("candidatos").select("*").eq("email", email_login.strip()).execute()
            dados = res.data if hasattr(res, 'data') else res
            if dados:
                st.session_state.usuario = dados[0]
                st.session_state.rota = 'dashboard'
                st.rerun()
            else:
                st.error("Candidato não localizado. Verifique o e-mail ou realize o cadastro.")
                
    with aba_registro:
        nome_reg = st.text_input("Nome completo")
        email_reg = st.text_input("E-mail corporativo ou pessoal")
        cargo_reg = st.selectbox("Cargo pleiteado", ["Diretor de Escola", "Agente de Desenvolvimento Educacional (ADE)"])
        
        if st.button("Criar Perfil", use_container_width=True):
            if nome_reg and email_reg:
                try:
                    novo_user = {"nome": nome_reg, "email": email_reg.strip(), "cargo_alvo": cargo_reg}
                    res = supabase.table("candidatos").insert(novo_user).execute()
                    st.success("Perfil criado! Faça login na aba lateral.")
                except Exception:
                    st.error("E-mail já cadastrado no sistema.")
            else:
                st.warning("Preencha todos os campos obrigatórios.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==============================================================================
# MENU DE NAVEGAÇÃO SUPERIOR
# ==============================================================================
usuario = st.session_state.usuario
st.markdown(f"""
<div class='nav-header'>
    <div>
        <h2 style='margin:0; font-size: 1.5rem;'>Aprova Limeira</h2>
        <span style='color: #94a3b8;'>Módulo: {usuario['cargo_alvo']}</span>
    </div>
    <div style='text-align: right;'>
        <span style='font-weight: 600;'>{usuario['nome']}</span><br>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# DASHBOARD E CONFIGURAÇÃO DA PROVA
# ==============================================================================
if st.session_state.rota == 'dashboard':
    st.markdown("### Centro de Comando Operacional")
    
    with st.container():
        st.markdown("<div style='background: white; padding: 30px; border-radius: 12px; border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        st.write("Configure sua próxima bateria de exercícios. O algoritmo selecionará questões estratégicas do banco de dados focadas exclusivamente no seu edital.")
        
        qtd_questoes = st.slider("Carga da avaliação (questões):", min_value=5, max_value=40, value=15, step=5)
        
        if st.button("🚀 Iniciar Ciclo de Avaliação", type="primary"):
            banco_filtrado = carregar_banco_questoes(usuario['cargo_alvo'])
            if not banco_filtrado:
                st.error(f"O banco de questões para {usuario['cargo_alvo']} está em fase de estruturação. Insira dados no Supabase para prosseguir.")
            else:
                random.shuffle(banco_filtrado)
                st.session_state.prova_atual = banco_filtrado[:qtd_questoes]
                st.session_state.rota = 'execucao'
                st.session_state.inicio_prova = time.time()
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# EXECUÇÃO DA AVALIAÇÃO
# ==============================================================================
elif st.session_state.rota == 'execucao':
    st.markdown("### Avaliação Cognitiva em Andamento")
    respostas_usuario = {}
    
    with st.form("form_simulado"):
        for i, q in enumerate(st.session_state.prova_atual):
            st.markdown(f"<div class='question-card'>", unsafe_allow_html=True)
            st.markdown(f"<div style='color: #3b82f6; font-weight: 700; margin-bottom: 10px;'>QUESTÃO {i+1}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='question-text'>{q['enunciado']}</div>", unsafe_allow_html=True)
            
            alts = q["alternativas"] if isinstance(q["alternativas"], list) else json.loads(q["alternativas"])
            respostas_usuario[str(i)] = st.radio("Alternativas:", alts, index=None, key=f"q_{i}", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)
            
        if st.form_submit_button("Finalizar e Processar Diagnóstico", type="primary", use_container_width=True):
            acertos, erros = 0, 0
            relatorio = []
            
            for i, q in enumerate(st.session_state.prova_atual):
                alts = q["alternativas"] if isinstance(q["alternativas"], list) else json.loads(q["alternativas"])
                gab_idx = q["gabarito"]
                resposta_selecionada = respostas_usuario[str(i)]
                
                acertou = False
                if resposta_selecionada and resposta_selecionada in alts:
                    acertou = (alts.index(resposta_selecionada) == gab_idx)
                
                if acertou: acertos += 1
                else: erros += 1
                
                # Pareceres em prosa descritiva contínua, sem uso de marcadores ou itens
                texto_parecer = f"A verificação dos registros cognitivos demonstra que a linha de raciocínio estabelecida para solucionar esta situação-problema atingiu a precisão esperada no contexto de {usuario['cargo_alvo']}. A fundamentação selecionada, que aponta a resposta como sendo '{alts[gab_idx]}', converge inteiramente com as diretrizes técnicas e teóricas da base curricular adotada, sugerindo que os conceitos estruturais pertinentes a esta disciplina já foram devidamente apropriados." if acertou else f"O diagnóstico desta etapa revela uma dissintonia entre a construção analítica elaborada e os pressupostos validados oficialmente pelo gabarito do cargo. A interpretação registrada inclinou-se para a concepção de que a resposta adequada seria '{resposta_selecionada if resposta_selecionada else 'Opção não assinalada'}', o que caracteriza um desvio frente ao objeto de estudo. Uma revisão aprofundada faz-se necessária para realinhar a percepção do candidato à resolução técnica correta, que estabelece categoricamente que a alternativa exata é '{alts[gab_idx]}'."
                
                relatorio.append({
                    "questao": i + 1,
                    "acertou": acertou,
                    "texto": texto_parecer
                })
            
            nota_final = (acertos / len(st.session_state.prova_atual)) * 100
            
            dados_resultado = {
                "candidato_id": usuario["id"],
                "nota": nota_final,
                "acertos": acertos,
                "erros": erros,
                "relatorio_descritivo": relatorio
            }
            supabase.table("resultados_simulados").insert(dados_resultado).execute()
            
            st.session_state.resultado = dados_resultado
            st.session_state.rota = 'relatorio'
            st.rerun()

# ==============================================================================
# AUDITORIA E DIAGNÓSTICO
# ==============================================================================
elif st.session_state.rota == 'relatorio':
    res = st.session_state.resultado
    
    st.markdown("### Diagnóstico de Competências")
    c1, c2, c3 = st.columns(3)
    c1.metric("Aproveitamento Global", f"{res['nota']:.1f}%")
    c2.metric("Decisões Corretas", res['acertos'])
    c3.metric("Revisões Necessárias", res['erros'])
    
    st.markdown("<hr style='margin: 30px 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)
    
    for det in res['relatorio_descritivo']:
        classe_css = "report-success" if det['acertou'] else "report-error"
        icone = "✅" if det['acertou'] else "❌"
        
        st.markdown(f"""
        <div class='report-card {classe_css}'>
            <div style='font-weight: 700; color: #0f172a; font-size: 1.1rem;'>{icone} Resolução da Questão {det['questao']}</div>
            <div class='report-text'>{det['texto']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    if st.button("Retornar ao Centro de Comando", type="primary"):
        st.session_state.rota = 'dashboard'
        st.rerun()
