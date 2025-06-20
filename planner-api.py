from flask import Flask, request, jsonify
import subprocess
import tempfile
import os

app = Flask(__name__)

@app.route('/plan', methods=['POST'])
def plan():
    domain = request.files['domain']
    problem = request.files['problem']

    with tempfile.TemporaryDirectory() as tmpdir:
        domain_path = os.path.join(tmpdir, 'domain.pddl')
        problem_path = os.path.join(tmpdir, 'problem.pddl')

        domain.save(domain_path)
        problem.save(problem_path)

        cmd = [
            './fast-downward.py',
            domain_path,
            problem_path,
            '--search', 'lazy_greedy([ff()], preferred=[ff()])'
        ]

        try:
            result = subprocess.run(cmd, cwd='/home/pi/downward',
                                    capture_output=True, text=True, timeout=30)
            output = result.stdout
            print("Planner Output:\n", output)

            if 'Solution found' in output:
                # Extract actual plan lines from output
                plan = []
                for line in output.splitlines():
                    line = line.strip()
                    if line and not line.startswith("[") and not line.startswith("INFO") and not line.startswith("search") and not line.startswith("translate") and not line.startswith("Parsing") and "exit code" not in line and "time" not in line and not line.startswith("Peak memory") and "memory" not in line:
                        # this filters out logs and keeps only actual plan steps like: turn-on (1)
                        if "Solution found!" not in line and "Solution found." not in line:
                            plan.append(line)

                return jsonify({'plan': plan})
            else:
                return jsonify({'plan': None, 'error': 'No plan found'})
        except Exception as e:
            return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
