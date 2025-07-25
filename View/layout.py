import streamlit as st

def set_config_title():
    st.title("🏛️ Athena")
    st.caption("Calculadora de Capacity - Eudes - 2025")
    
    st.set_page_config(
        page_icon='🏛️',
        page_title="Athena",
        layout='wide'
    )
    
    st.markdown(css, unsafe_allow_html=True)


css = '''
<style>
    [data-testid='stFileUploader'] {
        width: max-content;
    }
    [data-testid='stFileUploader'] section {
        padding: 0;
        float: left;
    }
    [data-testid='stFileUploader'] section > input + div {
        display: none;
    }
    [data-testid='stFileUploader'] section + div {
        float: right;
        padding-top: 0;
    }

</style>
'''


def main():
    pass

if __name__ == '__main__':
    main()