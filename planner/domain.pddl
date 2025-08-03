(define (domain light-control)

  (:requirements :strips)           ; 只用 STRIPS 即可，负效应合法

  (:predicates
      (lamp-on) (lamp-off) (dark) (bright)
  )

  (:action turn-on
    :parameters ()                 
    :precondition (and (dark) (lamp-off))
    :effect       (and (lamp-on) (not (lamp-off)))
  )

  (:action turn-off
    :parameters ()
    :precondition (and (bright) (lamp-on))
    :effect       (and (lamp-off) (not (lamp-on)))
  )
)
