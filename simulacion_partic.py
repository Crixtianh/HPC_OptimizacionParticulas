#Codigo de simulacion visual, ignorelo profesor, es solo para ver el contador de colisiones y como se comporta 
import numpy as np
import time
import pygame

# --- Parámetros de la Simulación ---
NUM_PARTICULAS = 100
ANCHO_MUNDO = 800.0
ALTO_MUNDO = 600.0
RADIO_PARTICULA = 5.0
MASA_PARTICULA = 1.0
DT = 0.1
NUM_PASOS = 2000
VELOCIDAD_INICIAL_MAX = 20.0
COEF_RESTITUCION_PARED = 0.8
COEF_RESTITUCION_PARTICULA = 0.9
SEMILLA = 42 

# --- Parámetros de Visualización (Pygame) ---
FPS = 60
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
COLOR_PARTICULA = AZUL
COLOR_BORDE = NEGRO
COLOR_TEXTO = (10, 10, 10) 

# --- Inicialización de Pygame ---
pygame.init()
pantalla = pygame.display.set_mode((int(ANCHO_MUNDO), int(ALTO_MUNDO)))
pygame.display.set_caption("Simulación de Partículas con Contador de Colisiones")
reloj = pygame.time.Clock()
fuente = pygame.font.Font(None, 30) 

# --- Contadores de Colisiones ---
colisiones_particula_particula = 0
colisiones_con_pared = 0

# --- Inicialización de las Partículas ---
np.random.seed(SEMILLA)
posiciones = np.random.rand(NUM_PARTICULAS, 2) * [ANCHO_MUNDO - 2*RADIO_PARTICULA, ALTO_MUNDO - 2*RADIO_PARTICULA] + RADIO_PARTICULA
velocidades = (np.random.rand(NUM_PARTICULAS, 2) - 0.5) * (2 * VELOCIDAD_INICIAL_MAX)


def resolver_colision_particulas(p1_idx, p2_idx, posiciones, velocidades):
    global colisiones_particula_particula 
    
    pos1, vel1 = posiciones[p1_idx], velocidades[p1_idx]
    pos2, vel2 = posiciones[p2_idx], velocidades[p2_idx]

    dist_vec = pos2 - pos1
    dist_mag_sq = np.sum(dist_vec**2)

    if dist_mag_sq == 0 or dist_mag_sq > (2 * RADIO_PARTICULA)**2 or np.dot(dist_vec, vel1 - vel2) > 0:
        return False 

    colisiones_particula_particula += 1

    dist_mag = np.sqrt(dist_mag_sq)
    normal_vec = dist_vec / dist_mag

    v1_normal = np.dot(vel1, normal_vec)
    v2_normal = np.dot(vel2, normal_vec)

    v1_normal_final = v2_normal
    v2_normal_final = v1_normal

    velocidades[p1_idx] += (v1_normal_final - v1_normal) * normal_vec * COEF_RESTITUCION_PARTICULA
    velocidades[p2_idx] += (v2_normal_final - v2_normal) * normal_vec * COEF_RESTITUCION_PARTICULA
    
    overlap = 2 * RADIO_PARTICULA - dist_mag
    if overlap > 0:
        correction = overlap / 2 * normal_vec
        posiciones[p1_idx] -= correction
        posiciones[p2_idx] += correction
    return True 


print("Iniciando simulación con visualización y contador de colisiones...")
start_time = time.time()
corriendo = True

for paso in range(NUM_PASOS):
    if not corriendo:
        break

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

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
                 resolver_colision_particulas(i, j, posiciones, velocidades) 


    pantalla.fill(BLANCO)
    pygame.draw.rect(pantalla, COLOR_BORDE, (0, 0, ANCHO_MUNDO, ALTO_MUNDO), 1)

    for i in range(NUM_PARTICULAS):
        pos_x = int(posiciones[i, 0])
        pos_y = int(posiciones[i, 1])
        pygame.draw.circle(pantalla, COLOR_PARTICULA, (pos_x, pos_y), int(RADIO_PARTICULA))

    texto_col_particulas = fuente.render(f"Colisiones Partícula-Partícula: {colisiones_particula_particula}", True, COLOR_TEXTO)
    texto_col_pared = fuente.render(f"Colisiones con Pared: {colisiones_con_pared}", True, COLOR_TEXTO)
    texto_col_semilla = fuente.render(f"Semilla número: {SEMILLA}", True, COLOR_TEXTO)
    pantalla.blit(texto_col_semilla, (10, 50)) 
    pantalla.blit(texto_col_particulas, (10, 10))
    pantalla.blit(texto_col_pared, (10, 30))


    pygame.display.flip()
    reloj.tick(FPS)

    if (paso + 1) % (NUM_PASOS // 10) == 0 and (NUM_PASOS // 10) > 0 and corriendo: # Imprimir 10 veces durante la sim
         print(f"Paso {paso+1}/{NUM_PASOS} - Colisiones P-P: {colisiones_particula_particula}, Colisiones Pared: {colisiones_con_pared}")


end_time = time.time()
total_time = end_time - start_time

print("-" * 30)
if corriendo:
    print(f"Simulación completada en {total_time:.2f} segundos.")
else:
    print(f"Simulación terminada por el usuario después de {total_time:.2f} segundos.")

print(f"Total colisiones Partícula-Partícula: {colisiones_particula_particula}")
print(f"Total colisiones con Pared: {colisiones_con_pared}")
print("-" * 30)

pygame.quit()