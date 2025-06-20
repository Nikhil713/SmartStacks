
(define (problem smart-library)
        (:domain environment-control)
        (:objects
            room - location
        )
        (:init
            (temp-high) (normal-humidity) (dark) (noisy) (seat-empty)
        )
        (:goal

        (and
            (mold-risk-low)
            (energy-saved)
        )

        )
    )