(define (domain light-control)
  (:predicates
    (dark)
    (lamp-on)
  )

  (:action turn-on
    :parameters ()
    :precondition (dark)
    :effect (lamp-on)
  )
)
