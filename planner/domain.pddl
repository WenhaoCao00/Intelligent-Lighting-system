(define (domain light-control)

  (:requirements :strips)

  (:predicates
      (lamp-on ?l) (lamp-off ?l)
      (dark) (bright)                 ; 仍然用全局明暗；若要分房间可改成 (dark ?room)
  )

  (:action turn-on
    :parameters (?l)
    :precondition (and (dark) (lamp-off ?l))
    :effect       (and (lamp-on ?l) (not (lamp-off ?l)))
  )

  (:action turn-off
    :parameters (?l)
    :precondition (and (bright) (lamp-on ?l))
    :effect       (and (lamp-off ?l) (not (lamp-on ?l)))
  )
)
