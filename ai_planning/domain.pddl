(define (domain environment-control)
  (:requirements :strips :typing :fluents)

  (:types
    location
  )

  (:predicates
    ;; Environmental categorization
    (very-dark-light)
    (dark-light)
    (normal-light)
    (bright-light)

    ;; Temperature
    (temp-low)
    (temp-normal)
    (temp-high)

    ;; Humidity
    (high-humidity)
    (normal-humidity)

    ;; Sound levels
    (quiet)
    (normal)
    (loud)

    ;; Seat occupancy
    (seat-occupied)
    (seat-empty)

    ;; Derived/computed
    (mold-risk-low-lighting)
    (mold-risk-low-temph)
    (comfortable-lighting)
    (comfortable-temph)

    (mold-risk-small)
    (mold-risk-medium)
    (mold-risk-high)

    (comfortable-noise-level)
    (mold-risk-low)
    (comfortable)

  )

  (:functions
    (temperature ?r - location)
    (humidity ?r - location)
    (light-level ?r - location)
    (sound-level ?r - location)
    (mold-risk ?r - location)
    (ultrasonic-distance ?r - location)

  )

  ;; Light classification
  (:action classify-very-dark
    :parameters (?r - location)
    :precondition (< (light-level ?r) 200)
    :effect (very-dark-light)
  )

  (:action classify-dark
    :parameters (?r - location)
    :precondition (and (>= (light-level ?r) 200) (< (light-level ?r) 500))
    :effect (dark-light)
  )

  (:action classify-normal-light
    :parameters (?r - location)
    :precondition (and (>= (light-level ?r) 500) (< (light-level ?r) 800))
    :effect (normal-light)
  )

  (:action classify-bright
    :parameters (?r - location)
    :precondition (>= (light-level ?r) 800)
    :effect (bright-light)
  )

  ;; Temperature classification
  (:action classify-temp-low
    :parameters (?r - location)
    :precondition (< (temperature ?r) 18)
    :effect (temp-low)
  )

  (:action classify-temp-normal
    :parameters (?r - location)
    :precondition (and (>= (temperature ?r) 18) (<= (temperature ?r) 26))
    :effect (temp-normal)
  )

  (:action classify-temp-high
    :parameters (?r - location)
    :precondition (> (temperature ?r) 26)
    :effect (temp-high)
  )

  ;; Humidity classification
  (:action classify-humidity-high
    :parameters (?r - location)
    :precondition (> (humidity ?r) 60)
    :effect (high-humidity)
  )

  (:action classify-humidity-normal
    :parameters (?r - location)
    :precondition (<= (humidity ?r) 60)
    :effect (normal-humidity)
  )

  (:action classify-mold-risk-small
    :parameters (?r - location)
    :precondition (= (mold-risk ?r) 1)
    :effect (mold-risk-small)
  )
  (:action classify-mold-risk-medium
    :parameters (?r - location)
    :precondition (= (mold-risk ?r) 2)
    :effect (mold-risk-medium)
  )
  (:action classify-mold-risk-high
    :parameters (?r - location)
    :precondition (= (mold-risk ?r) 3)
    :effect (mold-risk-high)
  )

  ;; Sound level classification
  (:action classify-sound-quiet
    :parameters (?r - location)
    :precondition (< (sound-level ?r) 40)
    :effect (quiet)
  )

  (:action classify-sound-normal
    :parameters (?r - location)
    :precondition (and (>= (sound-level ?r) 40) (<= (sound-level ?r) 70))
    :effect (normal)
  )

  (:action classify-sound-loud
    :parameters (?r - location)
    :precondition (> (sound-level ?r) 70)
    :effect (loud)
  )

  ;;occupancy classification

  (:action classify-seat-vacant
    :parameters (?r - location)
    :precondition (> (ultrasonic-distance ?r) 20)
    :effect (seat-empty)
  )

  (:action classify-seat-occupied
    :parameters (?r - location)
    :precondition (<= (ultrasonic-distance ?r) 20)
    :effect (seat-occupied)
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
    :effect (comfortable-noise-level) ;; Placeholder effect
  )
  (:action nothing-to-do-for-normal-sound
    :precondition (and (normal))
    :effect (comfortable-noise-level) ;; Placeholder effect
  )
  (:action alert-in-lcd-for-noise-level
    :precondition (and (loud))
    :effect (comfortable-noise-level) ;; Placeholder effect
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