import streamlit as st
import os, sys

# Add root to python path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from db.session import SessionLocal
from db.models import Skill, Attempt, Achievement, UserStats
from ui_utils import load_css, render_header
import datetime

st.set_page_config(page_title="Dashboard | DIAN Sim", page_icon="📊", layout="wide")
load_css()
render_header(title="Panel de Control", subtitle="Analítica de progreso y gamificación")

db = SessionLocal()

# 1. User Stats (Sidebar/Top)
stats = db.query(UserStats).first()
if not stats:
    stats = UserStats(current_streak=0, max_streak=0, total_points=0)

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.metric("🔥 Racha Actual", f"{stats.current_streak} días")
with col_s2:
    st.metric("🏆 Puntos Totales", f"{stats.total_points} pts")
with col_s3:
    st.metric("🔝 Racha Máxima", f"{stats.max_streak} días")

st.divider()

# 2. Mapa de Calor / Progreso por Eje
st.markdown('<div class="dian-card">', unsafe_allow_html=True)
st.subheader("🎯 Nivel de Dominio por Eje")
skills = db.query(Skill).all()
if skills:
    df_skills = pd.DataFrame([{
        'Eje': s.track,
        'Competencia': s.competency,
        'Dominio': s.mastery_score
    } for s in skills])
    
    fig = px.sunburst(df_skills, path=['Eje', 'Competencia'], values='Dominio',
                  color='Dominio', color_continuous_scale='RdYlGn',
                  range_color=[0, 100])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aún no hay datos de progreso. ¡Realiza tu primer simulacro!")
st.markdown('</div>', unsafe_allow_html=True)

# 3. Rendimiento en el Tiempo
st.markdown('<div class="dian-card">', unsafe_allow_html=True)
st.subheader("📈 Rendimiento de los últimos intentos")
attempts = db.query(Attempt).order_by(Attempt.created_at.desc()).limit(50).all()
if attempts:
    df_att = pd.DataFrame([{
        'Fecha': a.created_at,
        'Resultado': 1 if a.is_correct else 0
    } for a in attempts])
    
    # Agrupar por fecha
    df_att['Fecha'] = df_att['Fecha'].dt.date
    df_daily = df_att.groupby('Fecha').agg({'Resultado': 'mean'}).reset_index()
    df_daily['Porcentaje'] = df_daily['Resultado'] * 100
    
    fig_line = px.line(df_daily, x='Fecha', y='Porcentaje', title="Precisión Diaria (%)",
                       markers=True, line_shape='spline')
    fig_line.update_yaxes(range=[0, 105])
    fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_line, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# 4. Radar de Habilidades & Refuerzo
col_d1, col_d2 = st.columns(2)

with col_d1:
    st.subheader("🛡️ Radar de Competencias")
    if skills:
        avg_competencies = df_skills.groupby('Competencia')['Dominio'].mean().reset_index()
        fig_radar = go.Figure()
        # Actual Mastery
        fig_radar.add_trace(go.Scatterpolar(
            r=avg_competencies['Dominio'],
            theta=avg_competencies['Competencia'],
            fill='toself',
            name='Dominio Actual',
            line_color='#2c3e50',
            fillcolor='rgba(44, 62, 80, 0.3)'
        ))
        # Target Mastery (Ideal 90%)
        fig_radar.add_trace(go.Scatterpolar(
            r=[90] * len(avg_competencies),
            theta=avg_competencies['Competencia'],
            name='Meta (90%)',
            line_color='rgba(230, 0, 0, 0.5)',
            line_dash='dot'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            margin=dict(l=40, r=40, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("Sin datos para el radar.")

with col_d2:
    st.subheader("⚠️ Habilidades a Reforzar")
    if skills:
        top_weak = db.query(Skill).order_by(Skill.mastery_score.asc()).limit(5).all()
        for s in top_weak:
            color = "red" if s.mastery_score < 40 else "orange"
            st.markdown(f"""
            <div style="background: white; border-left: 5px solid {color}; padding: 10px; border-radius: 8px; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">
                <b style="color: #333;">{s.topic}</b><br>
                <span style="font-size: 0.8rem; color: #666;">{s.competency} | Dominio: {s.mastery_score:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay sugerencias todavía.")

# 5. Vitrina de Trofeos
st.markdown('<div class="dian-card">', unsafe_allow_html=True)
st.subheader("🏆 Tu Vitrina de Trofeos")

achievements = db.query(Achievement).all()
if achievements:
    cols = st.columns(4)
    for i, ach in enumerate(achievements):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="text-align: center; background: rgba(255,255,255,0.4); border-radius: 15px; padding: 15px; border: 1px solid rgba(255,255,255,0.8); height: 100%;">
                <div style="font-size: 2.5rem; margin-bottom: 5px;">{ach.icon}</div>
                <div style="font-size: 0.9rem; font-weight: 800; color: var(--dian-red); line-height: 1.1;">{ach.name}</div>
                <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 5px;">{ach.description}</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Continúa practicando para desbloquear medallas y logros especiales.")
st.markdown('</div>', unsafe_allow_html=True)

# 6. Herramientas Administrativas
st.divider()
st.subheader("🛠️ Herramientas de Datos")
col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    if st.button("📤 Exportar Banco a Excel", use_container_width=True):
        from db.models import Question
        all_qs = db.query(Question).all()
        if all_qs:
            df_export = pd.DataFrame([{
                'track': q.track,
                'competency': q.competency,
                'topic': q.topic,
                'difficulty': q.difficulty,
                'stem': q.stem,
                'correct_key': q.correct_key,
                'rationale': q.rationale
            } for q in all_qs])
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Banco_Preguntas')
            
            st.download_button(
                label="📥 Descargar Excel",
                data=output.getvalue(),
                file_name=f"Banco_Preguntas_DIAN_{datetime.datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("El banco está vacío.")

with col_exp2:
    if st.button("🗑️ Reiniciar Estadísticas", use_container_width=True):
        st.error("¿Estás seguro de reiniciar tus puntos y rachas?")
        if st.button("Sí, deseo reiniciar todo"):
             db.query(UserStats).delete()
             db.commit()
             st.success("Estadísticas reiniciadas.")
             st.rerun()

db.close()
