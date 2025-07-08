
    (define (problem smart-library)
        (:domain environment-control)
        (:objects
            room - location
        )
        (:init
            (temp-normal) (normal-humidity) (dark-light) (normal) (seat-empty)
        )
        (:goal
            
        (and
            (mold-risk-low)
        )
    
        )
    )
    