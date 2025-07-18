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
    (temp-very-high)
    (temp-max)
    

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
    (comfortable-temp)
    (comfortable-temph)

    (mold-risk-index-small)
    (mold-risk-index-medium)
    (mold-risk-index-high)
    (mold-risk-index-ok)
    (mold-risk-low-sound)

    (comfortable-noise-level)
    (mold-risk-low)
    (comfortable)

    
    (ideal-env)

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
    :precondition (and (>= (light-level ?r) 500) (< (light-level ?r) 699))
    :effect (normal-light)
  )

  (:action classify-bright
    :parameters (?r - location)
    :precondition (>= (light-level ?r) 700)
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
    :precondition (and (> (temperature ?r) 26) (<= (temperature ?r) 28))
    :effect (temp-high)
  )  
  
  (:action classify-temp-very-high
    :parameters (?r - location)
    :precondition (and (> (temperature ?r) 28) (<= (temperature ?r) 30))
    :effect (temp-very-high)
  )

  (:action classify-temp-max
    :parameters (?r - location)
    :precondition (> (temperature ?r) 30)
    :effect (temp-max)
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
    :precondition (= (mold-risk ?r) 0)
    :effect (mold-risk-index-ok)
  )
  (:action classify-mold-risk-medium
    :parameters (?r - location)
    :precondition (= (mold-risk ?r) 1)
    :effect (mold-risk-index-ok)
  )
  (:action classify-mold-risk-high
    :parameters (?r - location)
    :precondition (and (> (mold-risk ?r) 1) (<= (mold-risk ?r) 3))
    :effect (mold-risk-index-high)
  )

  ;; Sound level classification
  (:action classify-sound-quiet
    :parameters (?r - location)
    :precondition (< (sound-level ?r) 100)
    :effect (quiet)
  )

  (:action classify-sound-normal
    :parameters (?r - location)
    :precondition (and (>= (sound-level ?r) 100) (<= (sound-level ?r) 250))
    :effect (normal)
  )

  (:action classify-sound-loud
    :parameters (?r - location)
    :precondition (> (sound-level ?r) 251)
    :effect (loud)
  )

  ;;occupancy classification

  (:action display-seat-vacant
    :parameters (?r - location)
    :precondition (> (ultrasonic-distance ?r) 20)
    :effect (seat-empty)
  )

  (:action display-seat-occupied
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

  ;; Fan control

  (:action turn-off-fan
    :precondition (and (temp-low))
    :effect (and (comfortable-temp))
  )

  (:action nothing-to-do-for-normal-temp
    :precondition (and (temp-normal))
    :effect (comfortable-temp)
  )

  (:action nothing-to-do-for-high-temp-empty-seat
    :precondition (and (temp-normal))
    :effect (comfortable-temp)
  )

  (:action turn-on-fan-to-level-one
    :precondition (and (temp-high) (seat-occupied))
    :effect (and (temp-normal))
  )

  (:action turn-on-fan-to-level-two
    :precondition (and (temp-very-high) (seat-occupied))
    :effect (and (temp-normal))
  )

  (:action turn-on-fan-to-level-three
    :precondition (and (temp-max) (seat-occupied))
    :effect (and (temp-normal))
  )

  (:action nothing-to-do-for-normal-humidity
    :precondition (and (normal-humidity))
    :effect (and (mold-risk-low-temph))
  )
  (:action turn-on-fan-to-reduce-humidity
    :precondition (and (high-humidity))
    :effect (and (normal-humidity)(mold-risk-low-temph))
  )

  (:action comfortable-temp-and-humidity
    :precondition (and (temp-normal) (normal-humidity))
    :effect (and (comfortable-temph)(mold-risk-low-temph))
  )

  ;; Noise alert
  (:action display-quiet-in-lcd-display
    :precondition (and (quiet))
    :effect (comfortable-noise-level)
  )

  (:action display-normal-in-lcd-display
    :precondition (and (normal))
    :effect (comfortable-noise-level)
  )
  
  (:action display-loud-in-lcd-display
    :precondition (and (loud))
    :effect (comfortable-noise-level)
  )

  (:action turn-off-lcd-display
    :precondition (and (seat-empty))
    :effect (mold-risk-low-sound)
  )

  (:action send-email-for-high-mold-index
    :precondition (and (mold-risk-index-high))
    :effect (mold-risk-index-ok)
  )

  (:action environment-is-mold-risk-low
    :precondition (and (mold-risk-low-lighting) (mold-risk-low-temph)(mold-risk-low-sound)(mold-risk-index-ok))
    :effect (and (mold-risk-low))
  )

  (:action ideal-env-unoccupied
    :precondition (and (mold-risk-low) (seat-empty))
    :effect (and (ideal-env))
  )

  (:action ideal-env-occupied
    :precondition (and (comfortable-lighting) (comfortable-temph) (comfortable-noise-level)(seat-occupied)(mold-risk-index-ok))
    :effect (and (ideal-env))
  )
)