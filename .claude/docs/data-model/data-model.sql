enum Sex {
  "Masculino"
  "Femenino"
}

enum Role {
  "ENTRENADOR"
  "AMATEUR"
  "SEMI-PRO"
  "PRO"
}

enum BestOf {
     1
     3
     5
}


Table players {
  id_player uuid [pk]
  first_name varchar
  second_name varchar
  f_surename varchar
  s_surename varchar
  email varchar
  password varchar
  sex Sex
  age int
  height int
  weight int
  role Role
}

Table match_data {
  id_match uuid [pk]
  id_player_1 uuid [ref: > players.id_player]
  id_player_2 uuid [ref: > players.id_player]
  location varchar
  surface varchar // Clay, Grass, Hard
  id_match_score uuid [ref: - match_score.id_match_score]
  best_of BestOf
  match_State INICIADO | PAUSADO | FINALIZADA
  created_at timestamp
  updated_at timestamp
}

Table match_score {
  id_match_score uuid [pk]
  id_partido uuid
  winner_id uuid [ref: > players.id_player]
  duration int // en segundos
  created_at timestamp
  updated_at timestamp
}

Table match_set {
  id_set uuid [pk]
  id_match_score uuid [ref: > match_score.id_match_score]
  score_p1 int
  score_p2 int
  winner_id uuid [ref: > players.id_player]
  duration int
}

Table match_game {
  id_game uuid [pk]
  id_set uuid [ref: > match_set.id_set]
  p1_game_final_score int
  p2_game_final_score int
  duration int
  winner_id uuid [ref: > players.id_player]
  is_break boolean
  is_Serving  [ref: > players.id_player]
  created_at timestamp
  updated_at timestamp
}

Table match_point {
  id_point uuid [pk]
  is_serving [ref: > players.id_player]
  id_game uuid [ref: > match_game.id_game]
  id_player_1 uuid [ref: > players.id_player]
  id_player_2 uuid [ref: > players.id_player]
  winner_id uuid [ref: > players.id_player]
  score_p1 varchar // ej: "15", "40", "A"
  score_p2 varchar
  duration int
  break_point_chance boolean
  break_point boolean
  created_at timestamp
}