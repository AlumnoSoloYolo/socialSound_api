def encontrar_byte_invalido(ruta_archivo):
    with open(ruta_archivo, 'rb') as archivo:
        contenido = archivo.read()
        
    # Revisar byte por byte
    for i, byte in enumerate(contenido):
        try:
            bytes([byte]).decode('utf-8')
        except UnicodeDecodeError:
            contexto = contenido[max(0, i-20):min(len(contenido), i+20)]
            print(f"Byte inválido encontrado en posición {i}")
            print(f"Valor del byte: 0x{byte:02x}")
            print("Contexto alrededor del byte:")
            print(contexto)
            return i
            
    return None

# Uso
posicion = encontrar_byte_invalido('socialSound/fixtures/datos.json')