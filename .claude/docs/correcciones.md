

## Nueva feature de entrenador

- Usaran los mismos datos, pero, no se exigira el peso, altura y sexo.
- Debe tener la capacidad de asociarse a muchos jugadores.
  - Se debe agregra una nueva columna a los jugadores, que contenga el id del entrenador.
- Entrenador y jugador seran los nuevos roles que viajaran en la metada del jwt
- nivelUsuario ya no sera el rol, pero seguira tal como esta en la metadata del token, eliminando la posibilidad de ser entrenador.

## Correcciones registro

- No pedir edad, pedir la fecha de nacimiento
- Dar la posibilidad extra de jugar sin necesariamente ligarse a un oponente, que se guarde el nombre del ultimo, pero no sus estadisticas (Implica que el id del invitado sea nullable y que si eso pasa, el back ataja eso y simplemente , en el match data, no queda asociado un oponente, solo un nombre para el sumario del partido).
- Esos partidos agendados, deben quedar en la pestaña ya existente de partidos agendadados.
- El entrenador es el que le debe asignar el rol de nivel al jugador. El jugador simplemente se inscribe como eso, jugador, busca, en una barra buscadora , a su entrenador y le envia una solicitud. Cuando este la acepte, debe desplegarse un modal, con los 3 roles y los mismos botones que solian salir en el registro inicial, con una pequeña descripcion de a quien le podria corresponder dicho nivel.
- Dashboard del entrenador, debe mostrar el historial de partidos de sus entrenados registrados, ordenados por fecha y una pestaña donde ver las notificaciones de solicitud de asociacion.
