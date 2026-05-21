

## Descripcion general

- Este proyecto pertenece al backend de una aplicacion de tenis, destinada a el seguimiento de partidos, regitro de resultados y trackeo de estadistocas.
- Para mas detalle, consultar @.claude/docs/user_histories/user-histories


## Tecnologias

- Python3
- Djnago
- Djando rest framework
- PostgreSQL
- Models (Django orm)
- JWT

## Arquitectura

- Esta app esta pensada para ser un monolito modular, aprovechando la caracteristica de aplicaciones acopladas inherentes a djando
- Las apps deben dividirse POR CONTEXTO, no por tipo de datos, es decir, las estadisticas iran en una app, el registro y consulta de marcador en otro etc.
- El modelo de base de datos presenta redundancia y relaciones circulares con el fin de priorizar la velocidad de las consultas.

## Roles

- AMATEUR: Afecta el calculo de estadisticas, se pueden ligar a un entrenador
- SEMI-PRO: Afecta el calculo de estadisticas, se pueden ligar a un entrenador
- PRO: Afecta el calculo de estadisticas, se pueden ligar a un entrenador
- ENTRENADOR: Puede consultyar estadisticas de distintos jugadores, mientras esten a su nombre

## Modelo de datos

- Para mas detalles, consultar @.claude/docs/tennis-rules/data-model.sql

## Modulos

** Administracion de usuarios **

- Maneja el login y registro

**Dashboard de jugador**
- Debe poder ver sus ultimos 6 partidos
- Debe mostrar la info principal del jugador
- Debe poseer un boton para manejar un partido
- Mas informacion en @.claude/docs/user_histories/user-histories/04_historias_usuario_vistas_principales.csv

**Dashboard entrenador**

- Debe mostrar los ultimos 6 partidos de todos sus entrenados, rigiendose por la fecha de registro
- Debe mostrar un panel con los datos del entrenador
- Mas informacion en @.claude/docs/user_histories/user-histories/04_historias_usuario_vistas_principales.csv

**Registro de partido**

- Guarda toda la informacion relativa  a un partido.
- para mas info, consultar el @.claude/docs/user_histories/user-histories/02_historias_usuario_registro_marcador.csv

**Calculo de estadisticas**

- En funcion del nivel del jugador (rol) AMATEUR, SEMI-PRO, PRO, el genero y la superficie.
- Para mas detalle sobre los datos a calcular, consultar @.claude/docs/user_histories/user-histories/03_historias_usuario_estadisticas.csv
- Todas las variables y datos requeridos se pueden encontrar en @.claude/docs/tennis-math-data-and-logic/tennis-math-data-and-logic.md
- Estos valores, al ser dinamicos pero dependientes de una investigacion DEBEN SER MANEJADOS COMO VARIABLES DE ENTORNO.
           

**Consulta de estadisticas globales*

- Se debe retornar la estadisticas de los ultimos 14 partidos
- Debe retornar el ultimo resultado del jugador.
- Para mas detalle sobre como presentar los datos, consultar @.claude/docs/user_histories/user-histories/03_historias_usuario_estadisticas.csv
- Todas las variables y datos requeridos se pueden encontrar en @.claude/docs/tennis-math-data-and-logic/tennis-math-data-and-logic.md  

**Consulta de estadisticas ultimo partido**

- Se debe retornar el resultado y la estadistica del ultimo partido
- Para mas detalle sobre como presentar los datos, consultar @.claude/docs/user_histories/user-histories/03_historias_usuario_estadisticas.csv

**Gestion de amigos**

- Se debe gestionar amigos para poder agendar partidos
- Para mas detalles, consultar @.claude/docs/user_histories/user-histories/01_historias_usuario_perfil.csv

**Creacion de sesion de partidos**

- Se debe poder gestionar la creacion de un partido y enviar una notificacion al jugador invitado a la sesion.
- PAra mas detalle, consultar @.claude/docs/user_histories/user-histories/05_historias_usuario_modulo_competitivo.csv


## IMPORTANTE

- Cada vez que recurras a las hiustorias de usuario, usa la informacion relativa al modulo y la informacion del promp que se esta dando, no tomes todas las historias y el contexto completo, solo lo que se te demande.
- Cada vez que tengas dudas, cuastioname, hazme las preguntas pertinentes y establezcamos una solucion.
- El codigo se rige por los principios solid. Puedes consultarlos en @.claude/docs/solid-principles/solid-principles.md. Caundo inicie el proyecto, guarda esta orden automaticamente en tu memoria y en engram (de no existir registro)
- Archivos legibles, no kilometricos.





