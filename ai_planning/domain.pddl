(define (domain environment-control)
  (:requirements :strips :typing)

  (:types
    location
  )

  (:predicates
    ;; Temperature states
    (temp-very-low)
    (temp-low)
    (temp-normal)
    (temp-high)

    ;; Humidity
    (normal-humidity)
    (high-humidity)

    ;; Light levels
    (very-dark-light)
    (dark-light)
    (normal-light)
    (bright-light)

    ;; Sound levels
    (quiet)
    (normal)
    (loud)

    ;; Seat occupancy
    (seat-empty)
    (seat-occupied)

    ;; Derived/computed comfort states
    (comfortable-lighting)
    (comfortable-temph)
    (comfortable-noise-level)
    (no-light)

    ;; Goals
    (mold-risk-low)
    (mold-risk-low-lighting) 
    (mold-risk-low-temph)
    (comfortable)
  )

 ;; Light control
  (:action turn-on-light-to-level-one-very-dark
    :precondition (and (very-dark-light) (seat-empty))
    :effect (and (mold-risk-low-lighting))
  )
  (:action turn-on-light-to-level-one-dark
    :precondition (and (dark-light) (seat-empty))
    :effect (and (mold-risk-low-lighting))
  )
  (:action nothing-to-do-for-normal-light
    :precondition (and (normal-light))
    :effect (and (mold-risk-low-lighting))
  )

  (:action adjust-light-to-level-three
    :precondition (and (very-dark-light) (seat-occupied))
    :effect (and (comfortable-lighting))
  )
  (:action adjust-light-to-level-two
    :precondition (and (dark-light) (seat-occupied))
    :effect (and (comfortable-lighting))
  )
  (:action adjust-light-to-level-one
    :precondition (and (normal-light) (seat-occupied))
    :effect (and (comfortable-lighting))
  )
  (:action turn-off-light
    :precondition (and (bright-light))
    :effect (and (comfortable-lighting)(mold-risk-low-lighting))
  )


  ;; Fan control (extend as needed)
  
  (:action turn-off-fan
    :precondition (and (temp-low))
    :effect (and (temp-normal))
  )

  (:action adjust-fan-to-reduce-temp
    :precondition (and (temp-high) (seat-occupied))
    :effect (and (temp-normal))
  )

  (:action adjust-fan-to-reduce-humidity
    :precondition (and (high-humidity))
    :effect (and (normal-humidity)(mold-risk-low-temph))
  )

  (:action comfortable-temp-and-humidity
    :precondition (and (temp-normal) (normal-humidity))
    :effect (and (comfortable-temph)(mold-risk-low-temph))
  )

  ;; Noise alert
  (:action nothing-to-do-for-quiet-sound
  :precondition (and (quiet))
  :effect (comfortable-noise-level)  ;; Placeholder effect
  )
  (:action nothing-to-do-for-normal-sound
  :precondition (and (normal))
  :effect (comfortable-noise-level)  ;; Placeholder effect
  )
  (:action alert-in-lcd-for-noise-level
    :precondition (and (loud))
    :effect (comfortable-noise-level)  ;; Placeholder effect
  )

  ;; LCD display
  (:action display-message
    :precondition (and (seat-occupied))
    :effect (comfortable)
  )

  (:action environment-is-mold-risk-low
    :precondition (and (mold-risk-low-lighting) (mold-risk-low-temph))
    :effect (and (mold-risk-low))
  )
  
)
