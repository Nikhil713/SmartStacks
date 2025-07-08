domain = '''
(define (domain office)
  (:requirements :strips)
  
  (:types
    room heater light occupancy window - object
  )
  
  (:predicates
    (on-light ?l - light)
    (low-light ?r - room)
    (high-light ?r - room)
    (optimum-light ?r - room)
    (on-heater ?h - heater)
    (low-temperature ?r - room)
    (high-temperature ?r - room)
    (optimum-temperature ?r - room)
    (presence ?p - occupancy)
    (open ?w - window)
    (low-air-quality ?r - room)
    (high-air-quality ?r - room)
    (optimum-air-quality ?r - room)
  )

  (:action open-window
    :parameters (?w - window ?r - room)
    :precondition (and (not (open ?w)) (high-air-quality ?r) (not(optimum-air-quality ?r)))
    :effect (and (open ?w) (optimum-air-quality ?r))
  )

  (:action close-window
    :parameters (?w - window ?r - room)
    :precondition (and (open ?w) (low-air-quality ?r) (not(optimum-air-quality ?r)))
    :effect (and (not(open ?w)) (optimum-air-quality ?r))
  )
  
  (:action switch-off-light
    :parameters (?l - light ?r - room ?p - occupancy)
    :precondition (and (on-light ?l) (high-light ?r) (not(presence ?p)) (not(optimum-light ?r)))
    :effect (and (optimum-light ?r) (not (on-light ?l)))
  )


  (:action switch-on-light
    :parameters (?l - light ?r - room ?p - occupancy)
    :precondition (and (not (on-light ?l)) (low-light ?r) (not(optimum-light ?r)) (presence ?p))
    :effect (and (on-light ?l) (optimum-light ?r))
  )

  (:action switch-off-light
    :parameters (?l - light ?r - room ?p - occupancy)
    :precondition (and (on-light ?l) (high-light ?r) (not(presence ?p)) (not(optimum-light ?r)))
    :effect (and (optimum-light ?r) (not (on-light ?l)))
  )

  (:action switch-on-heater
    :parameters (?h - heater ?r - room)
    :precondition (and (not (on-heater ?h)) (low-temperature ?r) (not(optimum-temperature ?r)))
    :effect (and (on-heater ?h) (optimum-temperature ?r))
  )

  
  
  (:action switch-off-heater
    :parameters (?h - heater ?r - room)
    :precondition (and (on-heater ?h) (high-temperature ?r) (not(optimum-temperature ?r)))
    :effect (and (optimum-temperature ?r) (not (on-heater ?h)))
  )
)

'''



start = '''
(define (problem office_problem)
  (:domain office)
  
  (:objects
    l - light
    h - heater
    r1 - room
    p - occupancy
    w - window
  )
  (:init
'''

end = '''
(:goal
    (and (optimum-temperature r1) (optimum-light r1) (optimum-air-quality r1))
  )
)
'''

def problemGeneration(sensorDict, message_buffer):
    problem = ''' '''
    for topic in sensorDict:
        if message_buffer[topic] is not None:
          if topic == "iot/sensor/temperature":
              if int(message_buffer[topic])>sensorDict[topic]["upper_bound"]:
                  problem += "(high-temperature r1) "
                  problem += "(on-heater h) "
              elif int(message_buffer[topic])<sensorDict[topic]["lower_bound"]:
                  problem += "(low-temperature r1) "
              else:
                  problem += "(optimum-temperature r1) "
          if topic == "iot/sensor/airquality":
              if int(message_buffer[topic])>sensorDict[topic]["upper_bound"]:
                  problem += "(high-air-quality r1) "
              elif int(message_buffer[topic])<sensorDict[topic]["lower_bound"]:
                  problem += "(open w) "
                  problem += "(low-air-quality r1) "
              else:
                  problem += "(optimum-air-quality r1) "
          if topic =="iot/sensor/presence":
              if int(message_buffer[topic])==0:
                  problem += "(not(presence p)) "
              if int(message_buffer[topic])==1:
                  problem += "(presence p) "
          if topic =="iot/sensor/luminosity":
              if int(message_buffer[topic])<sensorDict[topic]["lower_bound"]:
                  problem += "(low-light r1) "
              elif int(message_buffer[topic])>sensorDict[topic]["lower_bound"]:
                  problem += "(on-light l) "
                  problem += "(high-light r1) "
              else:
                  problem += "(optimum-light r1) "
    problem +=") "
    return start + problem + end, problem