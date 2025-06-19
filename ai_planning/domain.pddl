(define (domain smart-library)
  (:requirements :strips :typing)

  (:types
    area
    sensor actuator
    temperature-sensor - sensor
    humidity-sensor - sensor
    sound-sensor - sensor
    light-sensor - sensor
    motion-sensor - sensor
    weather-api - sensor
    fan light-display notification oled-display - actuator
  )

  (:predicates
    (sensor-active ?s - sensor)
    (actuator-ready ?a - actuator)
    (occupied ?a - area)
    (too-hot ?a - area)
    (too-humid ?a - area)
    (too-loud ?a - area)
    (too-dark ?a - area)
    (mold-risk ?a - area)
    (ventilated ?a - area)
    (illuminated ?a - area)
    (alert-sent ?a - area)
  )

  (:action activate-ventilation
    :parameters (?a - area ?f - fan)
    :precondition (and (too-humid ?a) (actuator-ready ?f))
    :effect (and (ventilated ?a) (not (too-humid ?a)))
  )

  (:action activate-lighting
    :parameters (?a - area ?l - light-display)
    :precondition (and (too-dark ?a) (actuator-ready ?l))
    :effect (and (illuminated ?a) (not (too-dark ?a)))
  )

  (:action send-mold-alert
    :parameters (?a - area ?n - notification)
    :precondition (and (mold-risk ?a) (actuator-ready ?n))
    :effect (alert-sent ?a)
  )

  (:action cool-area
    :parameters (?a - area ?f - fan)
    :precondition (and (too-hot ?a) (actuator-ready ?f))
    :effect (not (too-hot ?a))
  )

  (:action reduce-noise
    :parameters (?a - area ?o - oled-display)
    :precondition (and (too-loud ?a) (actuator-ready ?o))
    :effect (not (too-loud ?a))
  )
)
