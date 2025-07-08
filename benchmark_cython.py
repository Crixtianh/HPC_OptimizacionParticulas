import numpy as np
import time
import engine_cython
import sys

# Valores por defecto
DEFAULT_NUM_PARTICULAS = 100
DEFAULT_ANCHO_MUNDO = 800.0
DEFAULT_ALTO_MUNDO = 600.0
DEFAULT_RADIO_PARTICULA = 5.0
DEFAULT_DT = 0.1
DEFAULT_NUM_PASOS = 1000
DEFAULT_VELOCIDAD_INICIAL_MAX = 20.0
DEFAULT_COEF_RESTITUCION_PARED = 0.8
DEFAULT_COEF_RESTITUCION_PARTICULA = 0.9
DEFAULT_SEMILLA = 42

# Variables globales que se configurarán desde argumentos
NUM_PARTICULAS = DEFAULT_NUM_PARTICULAS
ANCHO_MUNDO = DEFAULT_ANCHO_MUNDO
ALTO_MUNDO = DEFAULT_ALTO_MUNDO
RADIO_PARTICULA = DEFAULT_RADIO_PARTICULA
DT = DEFAULT_DT
NUM_PASOS = DEFAULT_NUM_PASOS
VELOCIDAD_INICIAL_MAX = DEFAULT_VELOCIDAD_INICIAL_MAX
COEF_RESTITUCION_PARED = DEFAULT_COEF_RESTITUCION_PARED
COEF_RESTITUCION_PARTICULA = DEFAULT_COEF_RESTITUCION_PARTICULA
SEMILLA = DEFAULT_SEMILLA

def parse_arguments():
    """Parsea los argumentos de línea de comandos"""
    global NUM_PARTICULAS, NUM_PASOS, SEMILLA
    
    if len(sys.argv) == 1:
        print("Usando valores por defecto.")
        print(f"Uso: python {sys.argv[0]} <NUM_PARTICULAS> <NUM_PASOS> <SEMILLA>")
        print(f"Ejemplo: python {sys.argv[0]} 100 1000 46")
        print(f"Valores actuales: NUM_PARTICULAS={NUM_PARTICULAS}, NUM_PASOS={NUM_PASOS}, SEMILLA={SEMILLA}")
        return
    
    if len(sys.argv) != 4:
        print("Error: Se requieren exactamente 3 argumentos.")
        print(f"Uso: python {sys.argv[0]} <NUM_PARTICULAS> <NUM_PASOS> <SEMILLA>")
        print(f"Ejemplo: python {sys.argv[0]} 100 1000 46")
        sys.exit(1)
    
    try:
        NUM_PARTICULAS = int(sys.argv[1])
        NUM_PASOS = int(sys.argv[2])
        SEMILLA = int(sys.argv[3])
        
        if NUM_PARTICULAS <= 0 or NUM_PASOS <= 0:
            raise ValueError("NUM_PARTICULAS y NUM_PASOS deben ser positivos")
            
        print(f"Parámetros configurados: NUM_PARTICULAS={NUM_PARTICULAS}, NUM_PASOS={NUM_PASOS}, SEMILLA={SEMILLA}")
        
    except ValueError as e:
        print(f"Error en los argumentos: {e}")
        print(f"Uso: python {sys.argv[0]} <NUM_PARTICULAS> <NUM_PASOS> <SEMILLA>")
        print("Todos los argumentos deben ser números enteros positivos.")
        sys.exit(1)

def run_simulation_cython():
    print("Iniciando benchmark con Cython")

    colisiones_particula_particula = 0
    colisiones_con_pared = 0
    
    np.random.seed(SEMILLA)
    posiciones = np.random.rand(NUM_PARTICULAS, 2) * [ANCHO_MUNDO - 2*RADIO_PARTICULA, ALTO_MUNDO - 2*RADIO_PARTICULA] + RADIO_PARTICULA
    velocidades = (np.random.rand(NUM_PARTICULAS, 2) - 0.5) * (2 * VELOCIDAD_INICIAL_MAX)

    start_time = time.time()

    for paso in range(NUM_PASOS):
        if (paso + 1) % (NUM_PASOS // 10) == 0:
            print(f"  Progreso: {paso + 1} / {NUM_PASOS} pasos completados...")

        posiciones += velocidades * DT

        for i in range(NUM_PARTICULAS):
            pared_colisiono = False
            if posiciones[i, 0] - RADIO_PARTICULA < 0:
                posiciones[i, 0] = RADIO_PARTICULA
                velocidades[i, 0] *= -COEF_RESTITUCION_PARED
                pared_colisiono = True
            elif posiciones[i, 0] + RADIO_PARTICULA > ANCHO_MUNDO:
                posiciones[i, 0] = ANCHO_MUNDO - RADIO_PARTICULA
                velocidades[i, 0] *= -COEF_RESTITUCION_PARED
                pared_colisiono = True
            if posiciones[i, 1] - RADIO_PARTICULA < 0:
                posiciones[i, 1] = RADIO_PARTICULA
                velocidades[i, 1] *= -COEF_RESTITUCION_PARED
                pared_colisiono = True
            elif posiciones[i, 1] + RADIO_PARTICULA > ALTO_MUNDO:
                posiciones[i, 1] = ALTO_MUNDO - RADIO_PARTICULA
                velocidades[i, 1] *= -COEF_RESTITUCION_PARED
                pared_colisiono = True
            if pared_colisiono:
                colisiones_con_pared += 1
        
        colisiones_particula_particula += engine_cython.run_collision_cython(
            posiciones,
            velocidades,
            NUM_PARTICULAS,
            RADIO_PARTICULA,
            COEF_RESTITUCION_PARTICULA
        )

    end_time = time.time()
    total_time = end_time - start_time

    print("-" * 30)
    print(f"SIMULACIÓN OPTIMIZADA (CON CYTHON)")
    print(f"Simulación completada en {total_time:.4f} segundos, con semilla{SEMILLA}.")
    print(f"Total pasos: {NUM_PASOS}, partículas: {NUM_PARTICULAS} ")
    print(f"Total colisiones Partícula-Partícula: {colisiones_particula_particula}")
    print(f"Total colisiones con Pared: {colisiones_con_pared}")
    print("-" * 30)

if __name__ == "__main__":
    parse_arguments()
    run_simulation_cython()