from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import text
from jinja2 import Template
from .db import SessionLocal
from weasyprint import HTML
import io

router = APIRouter()

@router.post('/reportes/boletin-mensual')
def boletin_mensual(mes: str):
    db = SessionLocal()
    sql = text("SELECT tipo_evento, count(*) FROM eventos WHERE date_trunc('month', fecha_hecho)=to_date(:mes,'YYYY-MM') GROUP BY tipo_evento")
    res = db.execute(sql, {"mes": mes}).fetchall()
    rows = [{'tipo': r[0], 'count': r[1]} for r in res]
    tpl = Template("""
    <html>
      <body>
        <h1>Boletín mensual - {{ mes }}</h1>
        <h2>Indicadores</h2>
        <ul>
        {% for r in rows %}
          <li>{{ r.tipo }}: {{ r.count }}</li>
        {% endfor %}
        </ul>
      </body>
    </html>
    """)
    html = tpl.render(mes=mes, rows=rows)
    try:
        pdf = HTML(string=html).write_pdf()
        return Response(content=pdf, media_type='application/pdf')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
