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

    ;; Goals
    (mold-risk-low)
    (energy-saved)
    (comfortable)
  )

  ;; Light control
  (:action turn-on-light
    :precondition (and (very-dark-light) (seat-occupied))
    :effect (and (bright-light)(comfortable-lighting))
  )

  (:action turn-on-light
    :precondition (and (dark-light) (seat-occupied))
    :effect (and (bright-light)(comfortable-lighting))
  )

  (:action turn-on-light
    :precondition (and (very-dark-light) (seat-occupied))
    :effect (and (bright-light)(comfortable-lighting))
  )

  (:action turn-off-light
    :precondition ((seat-empty))
    :effect (and (no-light) (energy-saved))
  )

  ;; Fan control (extend as needed)
  (:action reduce-fan-speed
    :precondition (and (temp-very-low)(seat-occupied))
    :effect (and (temp-normal) (comfortable-temp))
  )
  
  (:action reduce-fan-speed
    :precondition (and (temp-low)(seat-occupied))
    :effect (and (temp-normal) (comfortacomfortable-tempble))
  )

  (:action turn-on-fan
    :precondition (and (temp-high) (seat-occupied))
    :effect (and (temp-normal) (comfortable-temp))
  )

  (:action turn-off-fan
    :precondition (and (temp-low) (seat-empty))
    :effect (and (energy-saved))
  )

  ;; Humidity control
  (:action reduce-humidity
    :precondition (and (high-humidity))
    :effect (and (normal-humidity) (mold-risk-low))
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
    :precondition (and (comfortable-lighting) (comfortable-temp) (comfortable-noise-level))
    :effect (and (comfortable))
  )
  
)
