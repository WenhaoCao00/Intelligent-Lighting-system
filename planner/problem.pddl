(define (problem lighting-now)
  (:domain smart-lighting)

  (:init
    (= (lum) 23)         
  )

  (:goal (>= (lum) 100))
)
