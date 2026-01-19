import React, {useEffect, useState} from 'react'

export default function App(){
  const [indicadores, setIndicadores] = useState([])

  useEffect(()=>{
    fetch('/api/indicadores')
      .then(r=>r.json())
      .then(setIndicadores)
  },[])

  return (
    <div style={{padding:20}}>
      <h1>SISC MVP - Jamundí</h1>
      <h2>Indicadores</h2>
      <ul>
        {indicadores.map((i,idx)=>(<li key={idx}>{i.tipo_evento}: {i.count}</li>))}
      </ul>
      <p>Frontend mínimo. Ver API en <a href="/api/docs">/api/docs</a></p>
    </div>
  )
}
