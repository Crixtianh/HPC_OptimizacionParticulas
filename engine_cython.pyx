import numpy as np
cimport numpy as cnp
import cython

@cython.boundscheck(False)
@cython.wraparound(False)
def run_collision_cython(cnp.ndarray[cnp.float64_t, ndim=2] posiciones,
                         cnp.ndarray[cnp.float64_t, ndim=2] velocidades,
                         int NUM_PARTICULAS,
                         double RADIO_PARTICULA,
                         double COEF_RESTITUCION_PARTICULA):

    cdef int i, j
    cdef int colisiones_particula_particula = 0
    cdef cnp.ndarray[cnp.float64_t, ndim=1] dist_vec_check
    cdef double dist_sq_check, dist_mag, overlap
    cdef double v1_normal, v2_normal
    cdef cnp.ndarray[cnp.float64_t, ndim=1] normal_vec
    cdef cnp.ndarray[cnp.float64_t, ndim=1] vel1, vel2
    cdef cnp.ndarray[cnp.float64_t, ndim=1] correction
    cdef double RADIOS_AL_CUADRADO = (2 * RADIO_PARTICULA)**2

    for i in range(NUM_PARTICULAS):
        for j in range(i + 1, NUM_PARTICULAS):
            dist_vec_check = posiciones[i] - posiciones[j]
            dist_sq_check = dist_vec_check[0]**2 + dist_vec_check[1]**2
            
            if dist_sq_check < RADIOS_AL_CUADRADO:
                vel1 = velocidades[i]
                vel2 = velocidades[j]

                if not(dist_vec_check[0] * (vel1[0] - vel2[0]) + dist_vec_check[1] * (vel1[1] - vel2[1]) > 0):
                    colisiones_particula_particula += 1

                    dist_mag = np.sqrt(dist_sq_check)
                    if dist_mag > 0:
                        normal_vec = dist_vec_check / dist_mag

                        v1_normal = vel1[0] * normal_vec[0] + vel1[1] * normal_vec[1]
                        v2_normal = vel2[0] * normal_vec[0] + vel2[1] * normal_vec[1]

                        velocidades[i] += (v2_normal - v1_normal) * normal_vec * COEF_RESTITUCION_PARTICULA
                        velocidades[j] += (v1_normal - v2_normal) * normal_vec * COEF_RESTITUCION_PARTICULA

                        overlap = 2 * RADIO_PARTICULA - dist_mag
                        correction = 0.5 * overlap * normal_vec
                        posiciones[i] += correction
                        posiciones[j] -= correction

    return colisiones_particula_particula
