# Especificación Técnica: Sistema de Puntuación de Tenis (Protocolo para Agentes IA)

Este documento define las reglas estrictas para el cálculo y actualización del marcador en un partido de tenis. El agente debe seguir estas reglas sin inferencias externas. SI no encuentra la respuesta a la orden dentro de esta logica, esta autorizado para cuestionar la peticion del usuario.

## 1. Jerarquía de Puntuación
Un partido se divide en:
1.  **Puntos** (Puntuación mínima dentro de un juego).
2.  **Juegos** (Compuestos por puntos).
3.  **Sets** (Compuestos por juegos).
4.  **Partido** (Compuesto por sets).

## 2. Lógica de Puntos (Juego Estándar)
La secuencia de puntos es fija y obligatoria:
- **0 puntos**: "Love"
- **1 punto**: "15"
- **2 puntos**: "30"
- **3 puntos**: "40"
- **4 puntos**: "Game" (Si el oponente tiene 30 o menos).

### 2.1. Situación de Deuce (Iguales)
Si ambos jugadores alcanzan 3 puntos (40 - 40), se activa el estado de **Deuce**.
- **Punto siguiente**: El ganador obtiene "Ventaja" (Advantage).
- **Si el jugador con Ventaja gana el siguiente punto**: Gana el Juego.
- **Si el jugador con Ventaja pierde el siguiente punto**: El marcador regresa a "Deuce".
- **Nota**: El juego no puede terminar desde Deuce sin que un jugador gane dos puntos consecutivos.

## 3. Lógica de Juegos (Set Estándar)
Un set se gana bajo las siguientes condiciones:
1.  Un jugador llega a **6 juegos** con una diferencia mínima de **2 juegos** (ej. 6-0, 6-4).
2.  Si el marcador llega a **5-5**, se debe jugar hasta que alguien gane 7-5.
3.  Si el marcador llega a **6-6**, se activa obligatoriamente el **Tie-break**.

## 4. Protocolo de Tie-break (Puntuación Numérica)
En el tie-break, la puntuación cambia a formato numérico (1, 2, 3...):
- **Objetivo**: Ganar **7 puntos**.
- **Condición de victoria**: Debe haber una diferencia mínima de **2 puntos** (ej. 7-5, 10-8). No hay límite de puntuación máxima.
- **Cambio de lado**: Los jugadores cambian de lado de la pista cada 6 puntos acumulados.

## 5. Estructura del Partido
- **Best of 1 (set unico)**: 
- **Best of 3 (Al mejor de 3)**: El primero en ganar 2 sets gana el partido.
- **Best of 5 (Al mejor de 5)**: El primero en ganar 3 sets gana el partido (Común en Grand Slams masculinos).

## 6. Formato de Salida Obligatorio
Al reportar el marcador, el servidor siempre debe mencionarse primero:
`[Puntos del Servidor] - [Puntos del Receptor]`
O en términos de sets:
`[Sets Jugador A] - [Sets Jugador B] ([Juegos Set Actual])`

## 7. Restricciones Críticas para la IA
- **PROHIBIDO** asumir que un set termina en 6-5.
- **PROHIBIDO** usar "45" en lugar de "40".
- **PROHIBIDO** omitir el estado de Deuce en el seguimiento de puntos.
- **OBLIGATORIO** verificar la diferencia de 2 puntos/juegos en situaciones de cierre de set o tie-break.
  """
## Chnace de break

ocurre cuando el jugador que está recibiendo el saque se encuentra a un solo punto de ganar el juego (game).

Normalmente, el jugador que saca tiene una ventaja estadística y táctica; por eso, ganar un juego cuando el oponente saca se llama "quebrar" o "romper" el servicio.

¿Cuándo ocurre exactamente?
Para que exista una chance de break, el marcador del game debe favorecer al restador de la siguiente manera:

0-40: El restador tiene tres chances de break consecutivas (triple break point).

15-40: El restador tiene dos chances de break (doble break point).

30-40: El restador tiene una chance de break.

Ventaja al resto (Ad-Out): En caso de haber llegado a 40-40 (Deuce), si el restador gana el siguiente punto, tiene una chance de break.

## Logica de servicio

1. Lógica en un Set Normal (Service Game)En un game estándar, un solo jugador realiza todos los saques de principio a fin.Posicionamiento:El primer punto de cada game siempre se saca desde el lado derecho (lado de "Deuce") hacia el cuadro de saque diagonal opuesto.Se alterna el lado (derecha/izquierda) después de cada punto disputado.Rotación del saque:Al terminar un game, el servicio pasa al oponente.Cambio de lado de pista: Los jugadores cambian de lado cada vez que la suma de los games del set sea un número impar (ej: 1-0, 2-1, 5-4).La Regla del Let: Si la pelota toca la red pero cae en el cuadro de saque correcto, el saque se repite sin penalización.2. Lógica en el Tie-break (Desempate)Cuando el set llega a 6-6, se juega un tie-break para decidir quién gana el set por 7-6. Aquí la lógica de quién sirve cambia drásticamente para mantener la equidad.Puntuación: Se cuenta en números naturales (1, 2, 3...). Gana el primero en llegar a 7 puntos con diferencia de 2.Rotación del Servicio (Sistema 1-2-2):Jugador A (el que le tocaba sacar): Saca 1 vez desde el lado derecho.Jugador B: Saca 2 veces. El primero desde el lado izquierdo y el segundo desde el derecho.Jugador A: Saca 2 veces. Primero izquierda, luego derecha.Se mantiene este patrón de 2 saques por jugador hasta el final.Cambio de lado de pista: Se cambia de lado cada vez que la suma de los puntos sea múltiplo de 6 (ej: 3-3, 6-6, 9-3).Tabla Comparativa de LógicaCaracterísticaSet Normal (Game)Tie-breakQuién sacaUn solo jugador todo el game.Rotativo (1 saque el primero, luego 2 cada uno).Puntuación0, 15, 30, 40, Juego.1, 2, 3, 4, 5, 6, 7...Cambio de ladoAl sumar games impares (1, 3, 5...).Cada 6 puntos disputados.Lado inicialSiempre derecha.Siempre derecha (para el 1er saque de cada turno).Un detalle técnico de arquitectura de juego:Si tú ganas el tie-break habiendo empezado sacando tú, en el siguiente set le tocará empezar sacando a tu oponente. El tie-break se considera, a efectos de rotación, como un "game de saque" para el que lo empezó.¿Te sirve este desglose para la lógica de la aplicación que estás armando o necesitas que profundice en algún caso de borde (como el super tie-break)?