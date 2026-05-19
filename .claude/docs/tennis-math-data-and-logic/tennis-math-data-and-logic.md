# Anexo: Datos extraídos y creación de fórmula para el cálculo de la distancia total recorrida

## Distancias por superficie y nivel de juego

### Cancha de Arcilla — Amateurs

| Género    | Distancia por Set (Media) | Distancia por Minuto | Metros por Punto       | Tiempo de juego efectivo |
|-----------|---------------------------|----------------------|------------------------|--------------------------|
| Hombres   | 1.100 m – 1.450 m         | 25 – 32 m/min        | 10.5 m – 12.8 m        | 23% ± 2%                 |
| Mujeres   | 950 m – 1.250 m           | 22 – 28 m/min        | 9.2 m – 11.5 m         | 21% ± 3%                 |

---

### Cancha Dura — Amateurs

| Género    | Distancia por Set (Media) | Distancia por Minuto | Metros por Punto       | Tiempo de juego efectivo |
|-----------|---------------------------|----------------------|------------------------|--------------------------|
| Hombres   | 850 m – 1.100 m           | 30 – 38 m/min        | 8.4 m – 9.8 m          | 17% ± 1%                 |
| Mujeres   | 780 m – 1.000 m           | 26 – 32 m/min        | 7.5 m – 9.0 m          | 13% ± 2%                 |

---

### Cancha de Arcilla — Semiprofesionales

| Género    | Distancia por Set (Media) | Distancia por Minuto | Metros por Punto       | Tiempo de juego efectivo |
|-----------|---------------------------|----------------------|------------------------|--------------------------|
| Hombres   | 1.400 m – 1.750 m         | 32 – 40 m/min        | 11.5 m – 14.5 m        | 31% ± 2%                 |
| Mujeres   | 1.250 m – 1.550 m         | 28 – 35 m/min        | 10.2 m – 13.0 m        | 28% ± 3%                 |

---

### Cancha Dura — Semiprofesionales

| Género    | Distancia por Set (Media) | Distancia por Minuto | Metros por Punto       | Tiempo de juego efectivo |
|-----------|---------------------------|----------------------|------------------------|--------------------------|
| Hombres   | 1.100 m – 1.400 m         | 38 – 48 m/min        | 9.5 m – 11.8 m         | 22% ± 2%                 |
| Mujeres   | 1.000 m – 1.250 m         | 34 – 42 m/min        | 8.8 m – 10.5 m         | 20% ± 2%                 |

---

### Cancha de Arcilla — Profesionales

| Género         | Distancia por Set (Media) | Distancia por Minuto | Metros por Punto       | Tiempo de juego efectivo |
|----------------|---------------------------|----------------------|------------------------|--------------------------|
| Hombres (ATP)  | 1.600 m – 2.100 m         | 35 – 45 m/min        | 14.5 m – 17.5 m        | 40% ± 3%                 |
| Mujeres (WTA)  | 1.400 m – 1.850 m         | 32 – 42 m/min        | 13.0 m – 16.0 m        | 35% ± 3%                 |

---

### Cancha Dura — Profesionales

| Género         | Distancia por Set (Media) | Distancia por Minuto | Metros por Punto       | Tiempo de juego efectivo |
|----------------|---------------------------|----------------------|------------------------|--------------------------|
| Hombres (ATP)  | 1.200 m – 1.600 m         | 42 – 55 m/min        | 11.0 m – 13.5 m        | 27% ± 3%                 |
| Mujeres (WTA)  | 1.100 m – 1.450 m         | 38 – 50 m/min        | 10.5 m – 12.5 m        | 25% ± 3%                 |

---

## Fórmula de cálculo

```
D (m) = Tiempo_total_punto × (Tiempo_efectivo_juego / 100) × (Promedio_metros_por_minuto / 60)
```

### Variables

| Variable                     | Descripción                                                                 |
|------------------------------|-----------------------------------------------------------------------------|
| `Tiempo_total_punto`         | Duración total del punto en segundos                                        |
| `Tiempo_efectivo_juego`      | Porcentaje de tiempo efectivo según género, superficie y nivel (ver tablas) |
| `Promedio_metros_por_minuto` | Promedio del rango `Distancia por Minuto` según género, superficie y nivel  |

### Ejemplo de uso

Para un jugador **hombre amateur en arcilla**, punto de **60 segundos**:

- Tiempo efectivo: 23% → `0.23`
- Metros por minuto promedio: `(25 + 32) / 2 = 28.5 m/min`

```
D = 60 × 0.23 × (28.5 / 60)
D = 60 × 0.23 × 0.475
D ≈ 6.555 metros por punto
```

---

## Bibliografía

- Kovalchik, S. A., & Ingram, M. (2018). *Estimating the distribution of shots per point in professional tennis.* Journal of Quantitative Analysis in Sports, 14(1), 17–31.
- Fernandez-Fernandez, J., et al. (2009). *Intensity of finishing shots and activity patterns in elite and amateur tennis players.*
- Pereira, T. J. C., et al. (2016). *Analysis of the distances covered and technical actions performed by tennis players.* (Comparativa Clay vs Hard)
- Kilit, B., & Arslan, E. (2018). *Playing tennis matches on clay court surfaces are associated with more perceived enjoyment but less exertion compared to hard courts.*
- Hoppe, M. W., et al. (2014). *Relationship between internal and external training load in elite and sub-elite tennis players.*
- Li, Y., et al. (2020). *The Comparison of Movement Patterns between Professional and Junior Tennis Players.*
- Torres-Luque, G., et al. (2011). *Statistical differences in court surfaces in professional tennis.*
- Johnson, C. D., & McHugh, M. P. (2006). *Performance analysis of professional tennis on different surfaces.*
- Li, R., et al. (2024). *Using Hawk-Eye data to quantify physical demands in professional tennis.*
- Reid, M., et al. (2016). *Service speed and match characteristics of professional tennis.* Journal of Sports Sciences.
- Gallo-Salazar, C., et al. (2017). *Physical and physiological demands of female tennis players in different competitive levels.*
