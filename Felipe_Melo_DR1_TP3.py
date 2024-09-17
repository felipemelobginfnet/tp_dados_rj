#!/usr/bin/env python
# coding: utf-8

# In[33]:


import pandas as pd
import streamlit as st
import time
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np

st.write("""Este painel tem como objetivo dar insights em relação a sazonalidade de visitas ao parque, 
auxiliando o visitante a escolher o melhor dia para não enfrentar grandes esperas""")

@st.cache_data
def load_data(file):
    return pd.read_csv(file)

# Carregar o arquivo de Excel diretamente
df = pd.read_excel("visitantes_por_dia.xlsx", sheet_name="2023")
df = df.dropna(subset=["Data.Rio", "Unnamed: 3"])
df.columns = ["Mes",
    "Visitantes Dias uteis", 
    "Visitantes Fins de semana, feriados e pontos facultativos", 
    "Total Visitantes Mensais", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", 
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", 
    "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"
]

# Inicializar os estados da sessão
if "mes_selecionado" not in st.session_state:
    st.session_state["mes_selecionado"] = []

if "tipo_dia" not in st.session_state:
    st.session_state["tipo_dia"] = "Visitantes Dias uteis"

if "colunas_selecionadas" not in st.session_state:
    st.session_state["colunas_selecionadas"] = ["Mes", "Total Visitantes Mensais"]

if "bg_color" not in st.session_state:
    st.session_state["bg_color"] = "#000000"  

if "font_color" not in st.session_state:
    st.session_state["font_color"] = "#FFFFFF"  

# Título do painel
st.title("Upload de Arquivo CSV - Dados de Turismo")

st.write("Por favor, faça o upload de um arquivo CSV contendo dados de turismo do portal Data.Rio.")

# Upload de arquivo CSV
arquivo_upload = st.file_uploader("Escolha o arquivo CSV", type="csv")

# Sidebar para personalização de cores
st.sidebar.header("Personalização de cores")
bg_color = st.sidebar.color_picker("Escolha a cor de fundo", st.session_state["bg_color"])
font_color = st.sidebar.color_picker("Escolha a cor da fonte", st.session_state["font_color"])

# Atualização dos estados da sessão para as cores
st.session_state["bg_color"] = bg_color
st.session_state["font_color"] = font_color

# Aplicação de CSS para as cores personalizadas
codigo_css = f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {font_color};
    }}
    h1, h2, h3, h4, h5, h6, p, div, label, span, .stMarkdown {{
        color: {font_color} !important;
    }}
    .css-1v0mbdj a {{
        color: {font_color} !important;  /* Links */
    }}
    </style>
"""
st.markdown(codigo_css, unsafe_allow_html=True)

# Carregar o arquivo CSV
if arquivo_upload is not None:
    with st.spinner("Processando o arquivo..."):
        time.sleep(2)  # Simula o tempo de processamento
        
        # Barra de progresso
        progress_bar = st.progress(0)
        
        for percent_complete in range(1, 6):
            time.sleep(1)  
            progress_bar.progress(percent_complete * 20)

        df = load_data(arquivo_upload)

        st.write("Aqui estão os primeiros registros do seu arquivo:")
        st.dataframe(df.head())

        st.write("Informações sobre o arquivo:")
        st.write(df.describe())
    
    st.success("Arquivo processado com sucesso!")
else:
    st.write("Nenhum arquivo foi carregado ainda.")

# Filtros na barra lateral
st.sidebar.header("Filtros")

mes_selecionado = st.sidebar.multiselect(
    "Selecione o mês", 
    df["Mes"].unique(), 
    default=st.session_state["mes_selecionado"]
)
st.session_state["mes_selecionado"] = mes_selecionado

tipo_dia = st.sidebar.radio(
    "Tipo de Dia",
    ("Visitantes Dias uteis", "Visitantes Fins de semana, feriados e pontos facultativos"),
    index=("Visitantes Dias uteis", "Visitantes Fins de semana, feriados e pontos facultativos").index(st.session_state["tipo_dia"])
)
st.session_state["tipo_dia"] = tipo_dia

colunas_selecionadas = st.sidebar.multiselect(
    "Selecione as colunas que deseja visualizar",
    df.columns,
    default=st.session_state["colunas_selecionadas"]
)
st.session_state["colunas_selecionadas"] = colunas_selecionadas

# Filtrar os dados com base no mês selecionado
if mes_selecionado:
    df_filtrado = df[df["Mes"].isin(mes_selecionado)][colunas_selecionadas]
else:
    df_filtrado = df[colunas_selecionadas]

# Exibir a tabela filtrada
st.subheader("Tabela Interativa")

st.dataframe(df_filtrado)

# Botão para download dos dados filtrados
csv = df_filtrado.to_csv(index=False)
st.download_button(
    label="Baixar dados filtrados em CSV",
    data=csv,
    file_name="dados_filtrados.csv",
    mime="text/csv"
)

# Exibir métricas básicas
st.subheader("Métricas Básicas")

if "Total Visitantes Mensais" in df_filtrado.columns:
    media_mensal = df_filtrado["Total Visitantes Mensais"].mean()
    st.metric(label="Média Mensal", value=f"{int(media_mensal)}")

if "Total Visitantes Mensais" in df_filtrado.columns:
    soma_mensal = df_filtrado["Total Visitantes Mensais"].sum()
    st.metric(label="Visitantes no Ano", value=f"{soma_mensal}")

# Visualizações
st.subheader("Visualizações")

# Gráfico de barras
if "Total Visitantes Mensais" in df_filtrado.columns and "Mes" in df_filtrado.columns:
    bar_chart = px.bar(df_filtrado, x="Mes", y="Total Visitantes Mensais", title="Visitantes por Mês")
    st.plotly_chart(bar_chart)

# Gráfico de pizza
total_visitantes_dias_uteis = df["Visitantes Dias uteis"].sum()
total_fins_semana_feriados = df["Visitantes Fins de semana, feriados e pontos facultativos"].sum()

grafico = pd.DataFrame({
    "Categoria": ["Dias Uteis", "Fins de Semana/Feriados"],
    "Valor": [total_visitantes_dias_uteis, total_fins_semana_feriados]
})

pie_chart = px.pie(
    grafico, 
    names="Categoria", 
    values="Valor", 
    title="Comparação de Visitantes",
    color_discrete_sequence=["#000080", "#800000"] 
)

pie_chart.update_layout(
    title_font=dict(color="white"),
    font=dict(color="white"),
    legend_font=dict(color="white"),
    paper_bgcolor=st.session_state["bg_color"],
    plot_bgcolor=st.session_state["bg_color"]
)

st.plotly_chart(pie_chart)

# Gráfico de média de visitantes diários por mês
ordem_meses = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho", 
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
]

colunas_dias = [str(i) for i in range(1, 32)]  

colunas_dias_existentes = [col for col in colunas_dias if col in df.columns]
df["Média Visitantes Diários"] = df[colunas_dias_existentes].mean(axis=1)

df["Mes"] = pd.Categorical(df["Mes"], categories=ordem_meses, ordered=True)

media_diaria_por_mes = df.groupby("Mes")["Média Visitantes Diários"].mean().reset_index()

st.subheader("Gráfico de Barras: Média de Visitantes Diários por Mês")
bar_chart_media_diaria = px.bar(
     media_diaria_por_mes, 
     x="Mes", 
     y="Média Visitantes Diários", 
     title="Média de Visitantes Diários por Mês",
     labels={"Média Visitantes Diários": "Média de Visitantes Diários"}
)

bar_chart_media_diaria.update_layout(
     title_font=dict(color="white"),
     font=dict(color="white"),
     paper_bgcolor=st.session_state["bg_color"],
     plot_bgcolor=st.session_state["bg_color"]
)

st.plotly_chart(bar_chart_media_diaria)




# In[ ]:


get_ipython().system('streamlit run modelo.py')


# In[ ]:




