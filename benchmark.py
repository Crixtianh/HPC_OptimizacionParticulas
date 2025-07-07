import numpy as np
import time
import sys

# Parámetros por defecto
NUM_PARTICULAS = 100
ANCHO_MUNDO = 800.0
ALTO_MUNDO = 600.0
RADIO_PARTICULA = 5.0
DT = 0.1
NUM_PASOS = 1000
VELOCIDAD_INICIAL_MAX = 20.0
COEF_RESTITUCION_PARED = 0.8
COEF_RESTITUCION_PARTICULA = 0.9
SEMILLA = 42

def run_simulation(num_particulas=NUM_PARTICULAS, num_pasos=NUM_PASOS, semilla=SEMILLA):
    print(f"Iniciando benchmark con {num_particulas} partículas, {num_pasos} pasos, semilla {semilla}")

    colisiones_particula_particula = 0
    colisiones_con_pared = 0

    np.random.seed(semilla)
    posiciones = np.random.rand(num_particulas, 2) * [ANCHO_MUNDO - 2*RADIO_PARTICULA, ALTO_MUNDO - 2*RADIO_PARTICULA] + RADIO_PARTICULA
    velocidades = (np.random.rand(num_particulas, 2) - 0.5) * (2 * VELOCIDAD_INICIAL_MAX)

    start_time = time.time()

    for paso in range(num_pasos):
        if (paso + 1) % (num_pasos // 10) == 0 and (num_pasos // 10) > 0:
            print(f"  Progreso: {paso + 1} / {num_pasos} pasos completados...")

        posiciones += velocidades * DT

        for i in range(num_particulas):
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

        for i in range(num_particulas):
            for j in range(i + 1, num_particulas):
                dist_vec_check = posiciones[i] - posiciones[j]
                dist_sq_check = np.sum(dist_vec_check**2)
                
                if dist_sq_check < (2 * RADIO_PARTICULA)**2:
                    pos1, vel1 = posiciones[i], velocidades[i]
                    pos2, vel2 = posiciones[j], velocidades[j]
                    dist_vec = dist_vec_check
                    dist_mag_sq = dist_sq_check
                    if not(dist_mag_sq == 0 or np.dot(dist_vec, vel1 - vel2) > 0):
                        colisiones_particula_particula += 1
                        dist_mag = np.sqrt(dist_mag_sq)
                        normal_vec = dist_vec / dist_mag
                        v1_normal = np.dot(vel1, normal_vec)
                        v2_normal = np.dot(vel2, normal_vec)
                        velocidades[i] += (v2_normal - v1_normal) * normal_vec * COEF_RESTITUCION_PARTICULA
                        velocidades[j] += (v1_normal - v2_normal) * normal_vec * COEF_RESTITUCION_PARTICULA
                        overlap = 2 * RADIO_PARTICULA - dist_mag
                        if overlap > 0:
                            correction = overlap / 2 * normal_vec
                            posiciones[i] -= correction
                            posiciones[j] += correction

    end_time = time.time()
    total_time = end_time - start_time

    print("-" * 30)
    print(f"SIMULACIÓN BASE")
    print(f"Simulación completada en {total_time:.4f} segundos, con semilla {semilla}.")
    print(f"Total pasos: {num_pasos}, Partículas: {num_particulas}")
    print(f"Total colisiones Partícula-Partícula: {colisiones_particula_particula}")
    print(f"Total colisiones con Pared: {colisiones_con_pared}")
    print("-" * 30)

def mostrar_ayuda():
    print("Uso: python benchmark.py [NUM_PARTICULAS] [NUM_PASOS] [SEMILLA]")
    print("Ejemplo: python benchmark.py 200 2000 42")
    print("Parámetros por defecto: NUM_PARTICULAS=100, NUM_PASOS=1000, SEMILLA=42")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help', 'help']:
        mostrar_ayuda()
    elif len(sys.argv) == 1:
        # Usar valores por defecto
        run_simulation()
    elif len(sys.argv) == 4:
        try:
            num_particulas = int(sys.argv[1])
            num_pasos = int(sys.argv[2])
            semilla = int(sys.argv[3])
            
            if num_particulas <= 0 or num_pasos <= 0:
                print("Error: NUM_PARTICULAS y NUM_PASOS deben ser números positivos")
                sys.exit(1)
                
            run_simulation(num_particulas, num_pasos, semilla)
        except ValueError:
            print("Error: Todos los argumentos deben ser números enteros")
            mostrar_ayuda()
            sys.exit(1)
    else:
        print("Error: Número incorrecto de argumentos")
        mostrar_ayuda()
        sys.exit(1)