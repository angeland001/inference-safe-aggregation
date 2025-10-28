"""
Implementation of inference attacks on aggregated data
"""
from typing import List, Dict, Any, Optional, Tuple
from database import db
import numpy as np


class InferenceAttack:
    """Base class for inference attacks"""
    
    def __init__(self, username: str = "attacker"):
        self.username = username
        self.db = db
    
    def execute_query(
        self,
        query: str,
        params: tuple = None,
        user: str = None,
        password: str = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Execute a query as the attacker"""
        try:
            return self.db.execute_query(query, params, user, password)
        except Exception as e:
            print(f"Attack query failed: {e}")
            return None


class DifferencingAttack(InferenceAttack):
    """
    Differencing attack: Infer individual values by comparing aggregate results
    Example: Query avg salary for department, then avg salary excluding target
    """
    
    def attack(
        self,
        target_name: str,
        department: str,
        user: str = None,
        password: str = None
    ) -> Dict[str, Any]:
        """
        Attempt to infer target's salary using differencing
        
        Args:
            target_name: Name of employee to target
            department: Department of target
            user: Database user credentials
            password: Database password
        
        Returns:
            Dictionary with attack results
        """
        print(f"\n[DIFFERENCING ATTACK] Targeting: {target_name} in {department}")
        
        # Step 1: Get department average with target
        query1 = """
            SELECT 
                AVG(salary) as avg_salary,
                COUNT(*) as emp_count
            FROM employees
            WHERE department = %s
        """
        
        results1 = self.execute_query(query1, (department,), user, password)
        
        if not results1:
            return {
                'attack_type': 'Differencing',
                'success': False,
                'reason': 'Failed to execute first query',
                'inferred_salary': None
            }
        
        avg_with_target = float(results1[0]['avg_salary'])
        total_count = results1[0]['emp_count']
        
        print(f"  Step 1: Avg salary with target = ${avg_with_target:,.2f}")
        print(f"  Total employees in department = {total_count}")
        
        # Step 2: Get department average without target
        query2 = """
            SELECT 
                AVG(salary) as avg_salary,
                COUNT(*) as emp_count
            FROM employees
            WHERE department = %s AND name != %s
        """
        
        results2 = self.execute_query(query2, (department, target_name), user, password)
        
        if not results2:
            return {
                'attack_type': 'Differencing',
                'success': False,
                'reason': 'Failed to execute second query',
                'inferred_salary': None
            }
        
        avg_without_target = float(results2[0]['avg_salary'])
        count_without = results2[0]['emp_count']
        
        print(f"  Step 2: Avg salary without target = ${avg_without_target:,.2f}")
        
        # Step 3: Calculate target's salary
        # Formula: target_salary = (avg_with * total) - (avg_without * (total-1))
        inferred_salary = (avg_with_target * total_count) - (avg_without_target * count_without)
        
        print(f"  Step 3: Inferred salary = ${inferred_salary:,.2f}")
        
        # Verify the inference
        verify_query = "SELECT salary FROM employees WHERE name = %s"
        actual = self.execute_query(verify_query, (target_name,), user, password)
        
        actual_salary = float(actual[0]['salary']) if actual else None
        
        if actual_salary:
            error = abs(inferred_salary - actual_salary)
            print(f"  Verification: Actual salary = ${actual_salary:,.2f}")
            print(f"  Error: ${error:,.2f} ({(error/actual_salary)*100:.2f}%)")
        
        return {
            'attack_type': 'Differencing',
            'success': True,
            'target': target_name,
            'department': department,
            'inferred_salary': inferred_salary,
            'actual_salary': actual_salary,
            'error': abs(inferred_salary - actual_salary) if actual_salary else None,
            'queries_used': 2
        }


class TrackerAttack(InferenceAttack):
    """
    Tracker attack: Use COUNT queries with specific conditions to infer membership
    """
    
    def attack(
        self,
        target_name: str,
        salary_threshold: float,
        user: str = None,
        password: str = None
    ) -> Dict[str, Any]:
        """
        Determine if target's salary is above threshold
        
        Args:
            target_name: Name of employee to target
            salary_threshold: Salary threshold to test
            user: Database user credentials
            password: Database password
        
        Returns:
            Dictionary with attack results
        """
        print(f"\n[TRACKER ATTACK] Testing if {target_name} earns > ${salary_threshold:,.2f}")
        
        # Get target's department first
        dept_query = "SELECT department FROM employees WHERE name = %s"
        dept_result = self.execute_query(dept_query, (target_name,), user, password)
        
        if not dept_result:
            return {
                'attack_type': 'Tracker',
                'success': False,
                'reason': 'Could not find target employee'
            }
        
        department = dept_result[0]['department']
        
        # Step 1: Count high earners in department
        query1 = """
            SELECT COUNT(*) as high_earner_count
            FROM employees
            WHERE department = %s AND salary > %s
        """
        
        result1 = self.execute_query(query1, (department, salary_threshold), user, password)
        count_with_all = result1[0]['high_earner_count'] if result1 else 0
        
        print(f"  Step 1: High earners in {department} = {count_with_all}")
        
        # Step 2: Count high earners excluding target
        query2 = """
            SELECT COUNT(*) as high_earner_count
            FROM employees
            WHERE department = %s AND salary > %s AND name != %s
        """
        
        result2 = self.execute_query(query2, (department, salary_threshold, target_name), user, password)
        count_without_target = result2[0]['high_earner_count'] if result2 else 0
        
        print(f"  Step 2: High earners excluding target = {count_without_target}")
        
        # If counts differ, target is a high earner
        is_high_earner = count_with_all > count_without_target
        
        print(f"  Inference: {target_name} {'IS' if is_high_earner else 'IS NOT'} a high earner")
        
        # Verify
        verify_query = "SELECT salary FROM employees WHERE name = %s"
        actual = self.execute_query(verify_query, (target_name,), user, password)
        actual_salary = float(actual[0]['salary']) if actual else None
        actual_is_high = actual_salary > salary_threshold if actual_salary else None
        
        if actual_salary:
            print(f"  Verification: Actual salary = ${actual_salary:,.2f}")
            print(f"  Inference {'CORRECT' if is_high_earner == actual_is_high else 'INCORRECT'}")
        
        return {
            'attack_type': 'Tracker',
            'success': True,
            'target': target_name,
            'salary_threshold': salary_threshold,
            'inferred_high_earner': is_high_earner,
            'actual_salary': actual_salary,
            'actual_high_earner': actual_is_high,
            'correct': is_high_earner == actual_is_high if actual_is_high is not None else None,
            'queries_used': 2
        }


class SumAttack(InferenceAttack):
    """
    SUM-based attack: Use SUM and COUNT to infer individual salaries
    Works best on small groups
    """
    
    def attack(
        self,
        department: str,
        known_salaries: Dict[str, float],
        user: str = None,
        password: str = None
    ) -> Dict[str, Any]:
        """
        Infer unknown salaries using SUM and known values
        
        Args:
            department: Department to attack
            known_salaries: Dictionary of {name: salary} for known employees
            user: Database user credentials
            password: Database password
        
        Returns:
            Dictionary with attack results
        """
        print(f"\n[SUM ATTACK] Targeting: {department} department")
        print(f"  Known salaries: {len(known_salaries)}")
        
        # Step 1: Get total sum and count
        query1 = """
            SELECT 
                SUM(salary) as total_salary,
                COUNT(*) as emp_count
            FROM employees
            WHERE department = %s
        """
        
        result1 = self.execute_query(query1, (department,), user, password)
        
        if not result1:
            return {
                'attack_type': 'SUM',
                'success': False,
                'reason': 'Failed to get department totals'
            }
        
        total_sum = float(result1[0]['total_salary'])
        total_count = result1[0]['emp_count']
        
        print(f"  Step 1: Total salary sum = ${total_sum:,.2f}")
        print(f"  Total employees = {total_count}")
        
        # Step 2: Calculate sum of known salaries
        known_sum = sum(known_salaries.values())
        known_count = len(known_salaries)
        
        print(f"  Known salary sum = ${known_sum:,.2f}")
        
        # Step 3: Infer unknown salaries
        unknown_sum = total_sum - known_sum
        unknown_count = total_count - known_count
        
        print(f"  Unknown employees = {unknown_count}")
        print(f"  Unknown salary sum = ${unknown_sum:,.2f}")
        
        if unknown_count > 0:
            avg_unknown = unknown_sum / unknown_count
            print(f"  Average unknown salary = ${avg_unknown:,.2f}")
        
        # If only one unknown, we can infer exact salary
        inferred_salaries = {}
        if unknown_count == 1:
            # Get the unknown employee name
            query2 = """
                SELECT name, salary
                FROM employees
                WHERE department = %s
            """
            all_emps = self.execute_query(query2, (department,), user, password)
            
            for emp in all_emps:
                if emp['name'] not in known_salaries:
                    inferred_salaries[emp['name']] = unknown_sum
                    actual_salary = float(emp['salary'])
                    error = abs(unknown_sum - actual_salary)
                    print(f"  Inferred {emp['name']}: ${unknown_sum:,.2f}")
                    print(f"  Actual: ${actual_salary:,.2f}")
                    print(f"  Error: ${error:,.2f}")
        
        return {
            'attack_type': 'SUM',
            'success': unknown_count == 1,
            'department': department,
            'total_sum': total_sum,
            'known_sum': known_sum,
            'unknown_sum': unknown_sum,
            'unknown_count': unknown_count,
            'inferred_salaries': inferred_salaries,
            'queries_used': 2
        }


class LinearSystemAttack(InferenceAttack):
    """
    Linear system attack: Build system of equations from multiple queries
    to solve for individual values
    """
    
    def attack(
        self,
        target_department: str,
        user: str = None,
        password: str = None
    ) -> Dict[str, Any]:
        """
        Build linear system to infer salaries
        
        Args:
            target_department: Department to attack
            user: Database user credentials
            password: Database password
        
        Returns:
            Dictionary with attack results
        """
        print(f"\n[LINEAR SYSTEM ATTACK] Targeting: {target_department}")
        
        # Get list of employees in department
        emp_query = """
            SELECT name, salary
            FROM employees
            WHERE department = %s
            ORDER BY name
        """
        
        employees = self.execute_query(emp_query, (target_department,), user, password)
        
        if not employees or len(employees) < 2:
            return {
                'attack_type': 'Linear System',
                'success': False,
                'reason': 'Not enough employees in department'
            }
        
        n = len(employees)
        print(f"  Employees in department: {n}")
        
        # Build system of equations
        # Each equation is a different subset average
        equations = []
        constants = []
        
        # Equation 1: All employees
        all_avg_query = """
            SELECT AVG(salary) as avg_sal
            FROM employees
            WHERE department = %s
        """
        result = self.execute_query(all_avg_query, (target_department,), user, password)
        if result:
            equations.append([1] * n)
            constants.append(float(result[0]['avg_sal']) * n)
        
        # Equation 2-N: Exclude each employee one at a time
        for i, emp in enumerate(employees):
            query = """
                SELECT AVG(salary) as avg_sal, COUNT(*) as cnt
                FROM employees
                WHERE department = %s AND name != %s
            """
            result = self.execute_query(query, (target_department, emp['name']), user, password)
            if result:
                equation = [1] * n
                equation[i] = 0  # Exclude this employee
                equations.append(equation)
                constants.append(float(result[0]['avg_sal']) * result[0]['cnt'])
        
        print(f"  Built {len(equations)} equations")
        
        # Solve system if we have enough equations
        if len(equations) >= n:
            try:
                A = np.array(equations[:n])
                b = np.array(constants[:n])
                inferred_salaries = np.linalg.solve(A, b)
                
                print("  System solved successfully!")
                
                results = {}
                for i, emp in enumerate(employees):
                    inferred = inferred_salaries[i]
                    actual = float(emp['salary'])
                    error = abs(inferred - actual)
                    error_pct = (error / actual) * 100
                    
                    results[emp['name']] = {
                        'inferred': inferred,
                        'actual': actual,
                        'error': error,
                        'error_pct': error_pct
                    }
                    
                    print(f"  {emp['name']}: Inferred=${inferred:,.2f}, Actual=${actual:,.2f}, Error={error_pct:.2f}%")
                
                return {
                    'attack_type': 'Linear System',
                    'success': True,
                    'department': target_department,
                    'employee_count': n,
                    'equations_used': len(equations),
                    'results': results,
                    'queries_used': len(equations)
                }
            except np.linalg.LinAlgError:
                print("  Failed to solve system (singular matrix)")
                return {
                    'attack_type': 'Linear System',
                    'success': False,
                    'reason': 'System is singular or unsolvable'
                }
        else:
            return {
                'attack_type': 'Linear System',
                'success': False,
                'reason': f'Not enough equations ({len(equations)} < {n})'
            }


class AttackSuite:
    """Run comprehensive attack suite"""
    
    def __init__(self, username: str = "attacker"):
        self.username = username
        self.attacks = {
            'differencing': DifferencingAttack(username),
            'tracker': TrackerAttack(username),
            'sum': SumAttack(username),
            'linear_system': LinearSystemAttack(username)
        }
    
    def run_all_attacks(
        self,
        user: str = None,
        password: str = None
    ) -> Dict[str, Any]:
        """Run all available attacks"""
        
        print("=" * 80)
        print("RUNNING COMPREHENSIVE ATTACK SUITE")
        print("=" * 80)
        
        results = {}
        
        # Attack 1: Differencing on Alice
        print("\n### Attack 1: Differencing ###")
        results['differencing_alice'] = self.attacks['differencing'].attack(
            'Alice Johnson',
            'Engineering',
            user,
            password
        )
        
        # Attack 2: Tracker on Bob
        print("\n### Attack 2: Tracker ###")
        results['tracker_bob'] = self.attacks['tracker'].attack(
            'Bob Smith',
            90000.00,
            user,
            password
        )
        
        # Attack 3: SUM on Operations (small department)
        print("\n### Attack 3: SUM ###")
        known = {'Dana Cox': 72000.00}  # Assume attacker knows one salary
        results['sum_operations'] = self.attacks['sum'].attack(
            'Operations',
            known,
            user,
            password
        )
        
        # Attack 4: Linear System on Finance
        print("\n### Attack 4: Linear System ###")
        results['linear_finance'] = self.attacks['linear_system'].attack(
            'Finance',
            user,
            password
        )
        
        print("\n" + "=" * 80)
        print("ATTACK SUITE COMPLETE")
        print("=" * 80)
        
        # Summary
        successful = sum(1 for r in results.values() if r.get('success', False))
        print(f"\nSuccessful attacks: {successful}/{len(results)}")
        
        return results