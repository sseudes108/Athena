# Módulo de configuração de layout e estilos
import streamlit as st  # Framework para criação de aplicações web

def set_config_title():
    """
    Configura os elementos visuais principais da página:
    - Título principal
    - Subtítulo (caption)
    - Configurações gerais da página
    - Estilos CSS personalizados
    """
    
    # Título principal da aplicação (exibido no topo)
    st.title("🏛️ Athena")
    
    # Subtítulo com informações de autoria e ano
    st.caption("Calculadora de Capacity - CIPE - 2025")
    
    # Configurações globais da página Streamlit
    st.set_page_config(
        page_icon='🏛️',        # Ícone exibido na aba do navegador
        page_title="Athena",    # Título da aba do navegador
        layout='wide'           # Layout expandido (utiliza toda a largura)
    )
    
    # Aplica o CSS customizado definido abaixo
    st.markdown(css, unsafe_allow_html=True)

# Bloco de CSS customizado para estilização de componentes específicos
css = '''
<style>
    /* Container do uploader de arquivos */
    [data-testid='stFileUploader'] {
        width: max-content;  /* Largura ajustada ao conteúdo */
    }
    
    /* Seção principal do uploader */
    [data-testid='stFileUploader'] section {
        padding: 0;     /* Remove padding interno */
        float: left;    /* Alinha à esquerda */
    }
    
    /* Esconde a área de arrastar/soltar (drag-and-drop) */
    [data-testid='stFileUploader'] section > input + div {
        display: none;
    }
    
    /* Área do botão de upload */
    [data-testid='stFileUploader'] section + div {
        float: right;   /* Alinha à direita */
        padding-top: 0; /* Remove espaçamento superior */
    }
</style>
'''