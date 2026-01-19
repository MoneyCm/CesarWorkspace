import streamlit as st
import os

def load_css():
    """Inyecta el CSS personalizado en la aplicación."""
    # Build absolute path to styles.css assuming it's in the same directory as this file (app/)
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    
    if os.path.exists(css_path):
        with open(css_path, "r", encoding='utf-8') as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        # Fallback if file not found (shouldn't happen in dev)
        st.warning(f"No se encontró el archivo de estilos en: {css_path}")

def render_header(title: str = None, subtitle: str = None):
    """Renderiza el encabezado estándar de DIAN Sim."""
    
    st.markdown("""
        <div class="dian-header-container">
            <div class="dian-logo-text">
                🇨🇴 DIAN Sim
            </div>
            <div style="color: var(--dian-text-muted); font-size: 0.9rem;">
                Concurso de Méritos 2025
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if title:
        st.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)
    
    if subtitle:
        st.markdown(f"<p style='color: var(--dian-text-muted); margin-top: -10px;'>{subtitle}</p>", unsafe_allow_html=True)
    
    st.divider()

def card_container(key=None):
    """Retorna un contenedor estilo tarjeta."""
    return st.container(border=True) # Streamlit's native container with border maps well to our styling if customized, 
                                     # or we can use markdown divs. Let's stick to native for interaction, 
                                     # but inject a wrapper class if possible. 
                                     # Streamlit doesn't easily allow adding classes to containers. 
                                     # Hybrid approach: Use native for layout, customize global border/bg via CSS.

def metric_card(label: str, value: str, sublabel: str = ""):
    """Renderiza una tarjeta de métrica personalizada."""
    st.markdown(f"""
    <div class="dian-card">
        <div class="dian-card-header">{label}</div>
        <div class="dian-stat">{value}</div>
        <div class="dian-stat-label">{sublabel}</div>
    </div>
    """, unsafe_allow_html=True)
