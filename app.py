import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# CONFIGURAÇÃO DA PÁGINA (Tema e Layout)
# ==========================================
st.set_page_config(
    page_title="Gerenciamento de Projetos - Neoenergia",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS para o efeito Dark & Neon Verde
st.markdown("""
<style>
    /* Fundo principal escuro garantido */
    .stApp { background-color: #0E1117; }
    
    /* Texto Neon para Títulos */
    .neon-title {
        color: #39FF14;
        text-shadow: 0 0 5px #39FF14, 0 0 10px #00A335;
        font-family: 'Arial Black', sans-serif;
        text-align: center;
        padding-bottom: 20px;
    }
    
    /* Borda neon nos cartões de métricas */
    div[data-testid="metric-container"] {
        background-color: #1A1C23;
        border: 1px solid #39FF14;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 0 15px rgba(57, 255, 20, 0.15);
    }
    div[data-testid="stMetricValue"] > div {
        color: #39FF14 !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">⚡ DASHBOARD DE GERENCIAMENTO | PROJETOS NEOENERGIA</h1>', unsafe_allow_html=True)

# ==========================================
# CARREGAMENTO E TRATAMENTO DE DADOS
# ==========================================
@st.cache_data
def carregar_dados():
    df = pd.read_excel('relatorio_projetos_neoenergia.xlsx')
    
    # Converter datas
    df['Data de Entrada'] = pd.to_datetime(df['Data de Entrada'], format='%d/%m/%Y %H:%M', errors='coerce')
    df['Data da Nota 92'] = pd.to_datetime(df['Data da Nota 92'], format='%d/%m/%Y %H:%M', errors='coerce')
    
    # Extrair Mês
    df['Mes_Num'] = df['Data de Entrada'].dt.month
    meses_map = {6: 'Junho', 7: 'Julho', 8: 'Agosto', 9: 'Setembro'}
    df['Mês'] = df['Mes_Num'].map(meses_map)
    
    # Converter pontos para número
    df['Quantidade de Pontos'] = pd.to_numeric(df['Quantidade de Pontos'], errors='coerce').fillna(0)
    
    # Calcular tempo de análise (em dias)
    df['Tempo Analise (Dias)'] = (df['Data da Nota 92'] - df['Data de Entrada']).dt.total_seconds() / (24 * 3600)
    
    return df

df = carregar_dados()

# ==========================================
# CÁLCULOS DAS MÉTRICAS
# ==========================================
# Faturamento
preco_ponto = 11.52
faturamento_total = df['Quantidade de Pontos'].sum() * preco_ponto

# Média de tempo de análise (ignorando os que ainda não têm nota)
media_tempo = df['Tempo Analise (Dias)'].mean()

# Totais por período
pontos_setembro = df[df['Mes_Num'] == 9]['Quantidade de Pontos'].sum()
pontos_ago_set = df[df['Mes_Num'].isin([8, 9])]['Quantidade de Pontos'].sum()
pontos_jul_ago_set = df[df['Mes_Num'].isin([7, 8, 9])]['Quantidade de Pontos'].sum()

# Maior Projeto
maior_projeto = df.loc[df['Quantidade de Pontos'].idxmax()]
tempo_maior_projeto = maior_projeto['Tempo Analise (Dias)']
texto_tempo_maior = f"{tempo_maior_projeto:.1f} dias" if pd.notna(tempo_maior_projeto) else "Ainda em análise"

# ==========================================
# LINHA 1: MÉTRICAS GERAIS (KPIs)
# ==========================================
st.subheader("📊 Visão Geral do Faturamento e Performance")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Faturamento Gerado (Neoenergia)", f"R$ {faturamento_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
with c2:
    st.metric("Tempo Médio de Análise", f"{media_tempo:.1f} dias" if pd.notna(media_tempo) else "N/A")
with c3:
    st.metric(
        "Maior Projeto (Pontos)", 
        f"{int(maior_projeto['Quantidade de Pontos'])} pts", 
        delta=f"Provedor: {maior_projeto['Empresa']}", 
        delta_color="off"
    )
with c4:
    st.metric(
        "Análise do Maior Projeto", 
        texto_tempo_maior, 
        delta=f"Rota: {maior_projeto['Rota']}", 
        delta_color="off"
    )

st.markdown("---")

# ==========================================
# LINHA 2: ENTREGAS POR PERÍODO
# ==========================================
st.subheader("🎯 Quantidade de Pontos Entregues")
col1, col2, col3 = st.columns(3)
col1.metric("Último Mês (Setembro)", f"{int(pontos_setembro)} pts")
col2.metric("Últimos 2 Meses (Ago - Set)", f"{int(pontos_ago_set)} pts")
col3.metric("Últimos 3 Meses (Jul - Set)", f"{int(pontos_jul_ago_set)} pts")

st.markdown("---")

# ==========================================
# LINHA 3: GRÁFICOS (VISUAL DARK & NEON)
# ==========================================
st.subheader("📈 Evolução de Projetos")

# Preparar dados para os gráficos
df_agrupado = df.groupby(['Mes_Num', 'Mês']).size().reset_index(name='Quantidade')
df_agrupado = df_agrupado.sort_values('Mes_Num')

# Calcular a diferença (crescimento) em relação ao mês anterior
df_agrupado['Crescimento'] = df_agrupado['Quantidade'].diff().fillna(0)

g1, g2 = st.columns(2)

with g1:
    # Gráfico de Barras: Quantidade por Mês
    fig1 = px.bar(
        df_agrupado, 
        x='Mês', 
        y='Quantidade', 
        title='Projetos Abertos por Mês',
        template='plotly_dark',
        text='Quantidade'
    )
    fig1.update_traces(marker_color='#39FF14', textposition='outside', textfont=dict(color='white', size=14))
    fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig1, use_container_width=True)

with g2:
    # Gráfico de Linha: Tendência e Crescimento
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_agrupado['Mês'], 
        y=df_agrupado['Quantidade'],
        mode='lines+markers+text',
        name='Projetos',
        line=dict(color='#39FF14', width=4),
        marker=dict(size=12, color='#0E1117', line=dict(width=3, color='#39FF14')),
        text=df_agrupado['Crescimento'].apply(lambda x: f"+{int(x)}" if x > 0 else f"{int(x)}"),
        textposition='top center',
        textfont=dict(color='#00FFFF', size=14)
    ))
    fig2.update_layout(
        title='Curva de Crescimento (Diferença para o Mês Anterior)',
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# LINHA 4: TABELA DE DADOS DETALHADA
# ==========================================
st.markdown("---")
st.subheader("📋 Histórico e Detalhamento dos Projetos")

# Criar uma cópia para formatar a exibição sem alterar os dados originais dos gráficos
df_exibicao = df.copy()

# Formatar a coluna de dias para ficar mais legível na tabela
df_exibicao['Tempo Analise (Dias)'] = df_exibicao['Tempo Analise (Dias)'].apply(
    lambda x: f"{x:.1f} dias" if pd.notna(x) else "Aguardando"
)

# Selecionar e organizar as colunas
colunas_exibicao = [
    'Data de Entrada', 
    'Rota', 
    'Empresa', 
    'CNPJ', 
    'Quantidade de Pontos', 
    'Nota 92', 
    'Data da Nota 92', 
    'Tempo Analise (Dias)'
]

# Exibir o dataframe na tela
st.dataframe(
    df_exibicao[colunas_exibicao],
    use_container_width=True,
    hide_index=True
)