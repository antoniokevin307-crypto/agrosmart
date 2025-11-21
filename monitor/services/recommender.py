def irrigation_recommendation(temperature: float, humidity: float, rain_mm: float) -> str:
    """
    Reglas heurísticas simples para recomendar riego/protección.
    - Si llueve > 5 mm: NO regar.
    - Si temperatura > 33°C y humedad < 40% y lluvia == 0: regar 15–20 mm temprano.
    - Si temperatura entre 28–33°C y humedad < 50%: riego ligero 5–10 mm.
    - En otro caso: monitoreo sin riego.
    """
    # Normalización de None
    t = temperature or 0
    h = humidity or 0
    r = rain_mm or 0

    if r >= 5:
        return "Lluvia significativa detectada. No se recomienda regar hoy."
    if t > 33 and h < 40 and r == 0:
        return "Alta temperatura y baja humedad sin lluvia. Regar 15–20 mm a primera hora."
    if 28 <= t <= 33 and h < 50 and r == 0:
        return "Condiciones cálidas con humedad moderada. Aplicar riego ligero de 5–10 mm."
    return "Sin condiciones críticas. Mantener monitoreo y posponer riego."
