(define (problem smart-library)
    (:domain environment-control)
    (:objects
        room - location
    )
    (:init
        (= (temperature room) 27.0)
        (= (humidity room) 69.0)
        (= (light-level room) 474)
        (= (sound-level room) 193)
        (= (mold-risk room) 1)
        (= (ultrasonic-distance room) 17)
    )
    (:goal
        (and
            (ideal-env)
        )
    )
)