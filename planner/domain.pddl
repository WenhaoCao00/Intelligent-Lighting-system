;; ---------- domain.pddl ----------
(define (domain smart-lighting)
  ;; 需要负前件和数值函数
  (:requirements :strips :negative-preconditions :numeric-fluents)

  (:predicates
    (lamp-on)                     ; 灯当前是否已开
  )

  (:functions
    (lum)                         ; 房间亮度 (整数 lux)
  )

  ;; --- 开灯 ---
  (:action turn-on
    :parameters ()
    :precondition (not (lamp-on))
    :effect (and
      (lamp-on)
      (increase (lum) 200)        ; STEP：一次开灯 +200 lux
    )
  )

  ;; --- 关灯 ---
  (:action turn-off
    :parameters ()
    :precondition (lamp-on)
    :effect (and
      (not (lamp-on))
      (decrease (lum) 200)        ; STEP：关灯 -200 lux
    )
  )
)
