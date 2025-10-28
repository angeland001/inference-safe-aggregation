"""
Flask web application for interactive demonstration
"""
from flask import Flask, render_template, request, jsonify, session
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import db
from src.aggregation_methods import AggregationComparator
from src.attacks import AttackSuite
from src.polyinstantiation import Polyinstantiation
from src.least_privilege import LeastPrivilege
from config import Config

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialize components
agg_comparator = AggregationComparator()
attack_suite = AttackSuite()
poly = Polyinstantiation()
lp = LeastPrivilege()


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/api/employees')
def get_employees():
    """Get list of employees"""
    try:
        employees = db.get_table_data('employees')
        return jsonify({'success': True, 'data': employees})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/departments')
def get_departments():
    """Get list of departments"""
    try:
        departments = db.get_table_data('departments')
        return jsonify({'success': True, 'data': departments})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/aggregation/compare', methods=['POST'])
def compare_aggregation():
    """Compare aggregation methods"""
    try:
        data = request.json
        query = data.get('query')
        user = data.get('user')
        password = data.get('password')
        
        results = agg_comparator.compare_all(query, user=user, password=password)
        
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/attacks/differencing', methods=['POST'])
def run_differencing_attack():
    """Run differencing attack"""
    try:
        data = request.json
        target = data.get('target_name')
        department = data.get('department')
        user = data.get('user')
        password = data.get('password')
        
        from src.attacks import DifferencingAttack
        attack = DifferencingAttack()
        result = attack.attack(target, department, user, password)
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/attacks/tracker', methods=['POST'])
def run_tracker_attack():
    """Run tracker attack"""
    try:
        data = request.json
        target = data.get('target_name')
        threshold = float(data.get('salary_threshold'))
        user = data.get('user')
        password = data.get('password')
        
        from src.attacks import TrackerAttack
        attack = TrackerAttack()
        result = attack.attack(target, threshold, user, password)
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/attacks/all', methods=['POST'])
def run_all_attacks():
    """Run comprehensive attack suite"""
    try:
        data = request.json
        user = data.get('user')
        password = data.get('password')
        
        results = attack_suite.run_all_attacks(user, password)
        
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/polyinstantiation/demonstrate', methods=['POST'])
def demonstrate_poly():
    """Demonstrate polyinstantiation"""
    try:
        data = request.json
        employee_name = data.get('employee_name')
        user = data.get('user')
        password = data.get('password')
        
        result = poly.demonstrate_polyinstantiation(employee_name, user, password)
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/polyinstantiation/test-attack', methods=['POST'])
def test_poly_attack():
    """Test inference attack with polyinstantiation"""
    try:
        data = request.json
        department = data.get('department')
        clearance = int(data.get('clearance_level'))
        user = data.get('user')
        password = data.get('password')
        
        result = poly.test_inference_with_polyinstantiation(
            department, clearance, user, password
        )
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/least-privilege/demonstrate', methods=['POST'])
def demonstrate_lp():
    """Demonstrate least privilege for a role"""
    try:
        data = request.json
        role = data.get('role')
        user = data.get('user')
        password = data.get('password')
        
        result = lp.demonstrate_role_access(role, user, password)
        
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/least-privilege/compare', methods=['GET'])
def compare_lp():
    """Compare all roles"""
    try:
        result = lp.compare_all_roles()
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)