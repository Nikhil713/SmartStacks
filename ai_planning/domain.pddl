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
    (energy-saved)
    (comfortable)
  )

 ;; Light control
  (:action turn-on-light-from-very-dark
    :precondition (and (very-dark-light) (seat-occupied))
    :effect (and (bright-light) (comfortable-lighting))
  )

  (:action turn-on-light-from-dark
    :precondition (and (dark-light) (seat-occupied))
    :effect (and (bright-light) (comfortable-lighting))
  )

  (:action turn-off-light
    :precondition (and (seat-empty))
    :effect (and (no-light) (energy-saved))
  )


  ;; Fan control (extend as needed)
  
  (:action turn-off-fan
    :precondition (and (temp-low))
    :effect (and (temp-normal) (comfortable-temph))
  )

  (:action adjust-fan-to-reduce-temp
    :precondition (and (temp-high) (seat-occupied))
    :effect (and (temp-normal))
  )

  (:action adjust-fan-to-reduce-humidity
    :precondition (and (high-humidity))
    :effect (and (normal-humidity))
  )

  (:action comfortable-temp-and-humidity
    :precondition (and (temp-normal) (normal-humidity))
    :effect (and (comfortable-temph))
  )

  ;; Noise alert
  (:action alert-noise
    :precondition (and (loud) (seat-occupied))
    :effect (comfortable-noise-level)  ;; Placeholder effect
  )

  ;; LCD display
  (:action display-message
    :precondition (and (seat-occupied))
    :effect (comfortable)
  )

  (:action environment-is-comfortable
    :precondition (and (comfortable-lighting) (comfortable-temph) (comfortable-noise-level))
    :effect (and (comfortable))
  )
  
)
