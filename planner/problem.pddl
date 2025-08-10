(define (problem light-problem)
  (:domain light-control)
  (:objects l1 l2)
  (:init (dark) (lamp-off l1) (lamp-off l2))
  (:goal (and (lamp-on l1) (lamp-on l2)))
)


(define (problem light-problem)
  (:domain light-control)
  (:objects l1 l2)
  (:init (bright) (lamp-on l1) (lamp-on l2))
  (:goal (and (lamp-off l1) (lamp-off l2)))
)
