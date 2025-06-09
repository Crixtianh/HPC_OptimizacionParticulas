import numpy as np
import time

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

def run_simulation():
    print("Iniciando benchmark")

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

        for i in range(NUM_PARTICULAS):
            for j in range(i + 1, NUM_PARTICULAS):
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
    print(f"Simulación completada en {total_time:.4f} segundos, con semilla {SEMILLA}.")
    print(f"Total pasos: {NUM_PASOS}, Partículas: {NUM_PARTICULAS}")
    print(f"Total colisiones Partícula-Partícula: {colisiones_particula_particula}")
    print(f"Total colisiones con Pared: {colisiones_con_pared}")
    print("-" * 30)

if __name__ == "__main__":
    run_simulation()