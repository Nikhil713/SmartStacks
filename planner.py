import subprocess

def write_problem_pddl(temp, humidity, light, sound, filepath='problem.pddl'):
    with open(filepath, 'w') as f:
        f.write(f"""
                (define (problem smart-library)
                (:domain environment-control)
                (:objects
                    room - location
                )
                (:init
                    (temperature {temp})
                    (humidity {humidity})
                    (light-level {light})
                    (noise-level {sound})
                )
                (:goal
                    (and (mold-risk-low) (comfortable))
                )
                )
                """
        )

def run_planner(domain_file, problem_file):
    plan_response = send_pddl_files_and_get_plan(domainname, problem)
    actions = parse_plan_response(plan_response)
    return actions
        
