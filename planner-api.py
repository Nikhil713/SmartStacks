from flask import Flask, request, jsonify
import subprocess
import os
import uuid

app = Flask(__name__)

PLANNER_PATH = "/full/path/to/downward/fast-downward.py"  # <-- Update this

@app.route('/plan', methods=['POST'])
def plan():
    domain_file = request.files['domain']
    problem_file = request.files['problem']

    # Save to temp files
    uid = str(uuid.uuid4())
    domain_path = f"/tmp/domain_{uid}.pddl"
    problem_path = f"/tmp/problem_{uid}.pddl"

    domain_file.save(domain_path)
    problem_file.save(problem_path)

    output_file = f"/tmp/plan_{uid}.txt"
    
    try:
        result = subprocess.run([
            "python3", PLANNER_PATH,
            domain_path, problem_path,
            "--search", "lazy_greedy([ff()], preferred=[ff()])",
            "--plan-file", output_file
        ], capture_output=True, timeout=10)

        if not os.path.exists(output_file):
            return jsonify({"plan": None, "error": "No plan found"}), 200

        with open(output_file, 'r') as f:
            plan = f.read()

        return jsonify({"plan": plan})
    
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Planning timed out"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Cleanup
        for f in [domain_path, problem_path, output_file]:
            try:
                os.remove(f)
            except:
                pass

if __name__ == '__main__':
    app.run(debug=True)
