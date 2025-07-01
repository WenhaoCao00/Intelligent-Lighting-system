(define (domain lighting)
  (:requirements :strips)

  (:predicates
    (dark)          
    (light-on)      
  )

  (:action turn-on
    :parameters ()              
    :precondition (dark)
    :effect (and
      (light-on)
      (not (dark))
    )
  )
)
