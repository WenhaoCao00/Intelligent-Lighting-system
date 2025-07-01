(define (domain lighting)
  (:requirements :strips)

  (:predicates
    (dark)          ;; 亮度 < 100 lux
    (light-on)      ;; 灯已打开
  )

  (:action turn-on
    :parameters ()              ;; 无参数也要给空列表
    :precondition (dark)
    :effect (and
      (light-on)
      (not (dark))
    )
  )
)
