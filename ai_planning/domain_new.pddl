(define (domain smart-environment-control)
  (:requirements :strips :typing :numeric-fluents)

  (:types
    room
  )

  (:predicates

    ;; Seat occupancy
    (seat-empty)
    (seat-occupied)

    ;; Derived/computed comfort states
    (comfortable-lighting)
    (comfortable-temph)
    (comfortable-noise-level)

    ;; Goals
    (mold-risk-low)
  )

  (:functions
    (temperature)        ;; current temperature
    (humidity)           ;; current humidity
    (light-level)        ;; current light level
    (noise-level)        ;; current sound level
    (mold-score)         ;; calculated mold risk
    (env-score)          ;; overall comfort/environment score
  )

  ;; ============ LIGHT CONTROL ============

  (:action increase-light
    :precondition (and (< (light-level) 60))
    :effect (and (increase (light-level) 20)
                 (increase (env-score) 5))
  )

  (:action decrease-light
    :precondition (and (> (light-level) 80))
    :effect (and (decrease (light-level) 20)
                 (increase (env-score) 5))
  )

  (:action mark-lighting-comfortable
    :precondition (and (>= (light-level) 60) (<= (light-level) 80))
    :effect (comfortable-lighting)
  )

  ;; ============ TEMPERATURE / HUMIDITY CONTROL ============

  (:action turn-on-fan-to-cool
    :precondition (and (> (temperature) 28))
    :effect (and (decrease (temperature) 2)
                 (increase (env-score) 5))
  )

  (:action turn-off-fan
    :precondition (and (< (temperature) 20))
    :effect (and (increase (temperature) 2)
                 (increase (env-score) 2))
  )

  (:action mark-temp-humidity-comfortable
    :precondition (and (>= (temperature) 20) (<= (temperature) 26)
                       (<= (humidity) 70))
    :effect (comfortable-temph)
  )


  ;; ============ SOUND CONTROL / ALERTING ============

  (:action acknowledge-quiet
    :precondition (and (< (noise-level) 50))
    :effect (comfortable-noise-level)
  )

  (:action alert-loud-noise
    :precondition (and (> (noise-level) 70))
    :effect (increase (env-score) -2)
  )

 ;; ============ COMFORTABLE AND MOLD PREVENTION ============

  (:action mark-mold-risk-low
    :precondition (and (< (mold-score) 30))
    :effect (mold-risk-low)
  )

  ;; ============ GOAL DISPLAY / FINAL CHECK ============

  (:action mark-environment-comfortable
    :precondition (and (comfortable-lighting)
                       (comfortable-temph)
                       (comfortable-noise-level)
                       (mold-risk-low))
    :effect (increase (env-score) 10)
  )
)