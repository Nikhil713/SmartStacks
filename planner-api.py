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
            './ff',           # your Metric-FF binary
            '-o', domain_path,
            '-f', problem_path,
            '-s', '0'  # standard FF search: EHC+H then BFS without cost optimization
        ]

        try:
            # Set cwd to where your ff binary is located if needed
            result = subprocess.run(cmd, cwd='/home/pi/Metric-FF-v2.1',
                                    capture_output=True, text=True, timeout=30)
            output = result.stdout
            print("Planner Output:\n\n", output, "\n\n")

            if 'found legal plan' in output.lower() or 'found plan' in output.lower():
                # Extract plan lines, usually the lines after "found legal plan"
                plan = []
                recording = False
                for line in output.splitlines():
                    line = line.strip()
                    if 'found legal plan' in line.lower() or 'found plan' in line.lower():
                        recording = True
                        continue
                    if recording:
                        if line == '':
                            break
                        plan.append(line)
                return jsonify({'plan': plan})
            else:
                return jsonify({'plan': None, 'error': 'No plan found'})
        except Exception as e:
            return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
