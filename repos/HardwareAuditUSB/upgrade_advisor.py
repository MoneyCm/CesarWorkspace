def analyze_upgrades(sys_info):
    suggestions = []
    
    # 1. RAM Check
    try:
        # Convert e.g. "15.8GB" back or use raw bytes if passed. 
        # We stored raw bytes in 'ram_total_bytes'
        total_ram_gb = sys_info.get('ram_total_bytes', 0) / (1024**3)
        
        if total_ram_gb < 8:
            suggestions.append({
                "component": "Memoria RAM",
                "status": "Crítico",
                "advice": "Tienes menos de 8GB de RAM. Se recomienda encarecidamente actualizar a 16GB para estándares modernos."
            })
        elif total_ram_gb < 16:
            suggestions.append({
                "component": "Memoria RAM",
                "status": "Mejorable",
                "advice": "Tienes entre 8GB y 16GB. Para multitarea pesada o juegos modernos, considera subir a 16GB o 32GB."
            })
        else:
             suggestions.append({
                "component": "Memoria RAM",
                "status": "Óptimo",
                "advice": f"Tienes {total_ram_gb:.1f}GB de RAM, lo cual es suficiente para la mayoría de tareas."
            })
    except Exception as e:
        suggestions.append({"component": "RAM", "status": "Error", "advice": f"No se pudo analizar: {e}"})

    # 2. Disk Check
    disk_type = sys_info.get('main_disk_type', 'Desconocido')
    if disk_type == 'HDD':
        suggestions.append({
            "component": "Almacenamiento Principal",
            "status": "Crítico",
            "advice": "Tu sistema parece estar arrancando desde un HDD mecánico. Cambiar a un SSD NVMe o SATA acelerará tu PC drásticamente (hasta 5x-10x)."
        })
    elif disk_type == 'SSD':
        suggestions.append({
            "component": "Almacenamiento Principal",
            "status": "Óptimo",
            "advice": "Ya cuentas con tecnología SSD."
        })
    else:
        suggestions.append({
            "component": "Almacenamiento",
            "status": "Desconocido",
            "advice": "No pudimos determinar si usas SSD o HDD con certeza. Si tu PC tarda más de 30-40s en iniciar, probablemente sea un HDD."
        })

    # 3. CPU Age Heuristic
    # Very basic keywords
    cpu_model = sys_info.get('cpu_model', '').lower()
    
    # Checks for Intel
    old_intel_keywords = [
        "core 2", "pentium", "celeron", 
        "i3-2", "i5-2", "i7-2", # 2nd gen
        "i3-3", "i5-3", "i7-3", # 3rd gen
        "i3-4", "i5-4", "i7-4",
        "i3-5", "i5-5", "i7-5",
        "i3-6", "i5-6", "i7-6", 
        "i3-7", "i5-7", "i7-7"  # 7th gen (approx 2017) -> 6+ years old
    ]
    
    # Checks for AMD
    old_amd_keywords = [
        "fx-", "a4-", "a6-", "a8-", "a10-", "phenom", "athlon",
        "ryzen 3 1200", "ryzen 5 1400", "ryzen 5 1600", "ryzen 7 1700", # Ryzen 1st gen (2017)
        "ryzen 3 2200", # Ryzen 2nd gen APU but roughly that era
    ]

    is_old = False
    for k in old_intel_keywords + old_amd_keywords:
        if k in cpu_model:
            is_old = True
            break
            
    if is_old:
        suggestions.append({
            "component": "Procesador (CPU)",
            "status": "Antiguo",
            "advice": "Tu procesador tiene probablemente más de 6 años. Considera una renovación de plataforma (Placa + CPU + RAM) para mejor rendimiento en apps actuales."
        })
    else:
        suggestions.append({
            "component": "Procesador (CPU)",
            "status": "Estable",
            "advice": "Tu procesador parece ser relativamente reciente o no está en nuestra lista de 'obsoletos'."
        })

    return suggestions
