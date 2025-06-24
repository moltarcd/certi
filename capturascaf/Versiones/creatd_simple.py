def calcular_dv_luhn_izquierda(pan_sin_dv: str) -> int:
    digitos = [int(d) for d in pan_sin_dv]
    suma = 0

    for i, d in enumerate(digitos):
        if i % 2 == 0:  # Posiciones impares desde la izquierda (0-indexed)
            doble = d * 2
            if doble > 9:
                doble -= 9
            suma += doble
        else:
            suma += d

    dv = (10 - (suma % 10)) % 10
    return dv

# Ejemplo de uso
pan = "451758000002072"
print(f"El DV para {pan} es: {calcular_dv_luhn_izquierda(pan)}")
