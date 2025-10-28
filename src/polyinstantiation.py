"""
Polyinstantiation implementation and demonstration
"""
from typing import Dict, Any, List, Optional
from src.database import db


class Polyinstantiation:
    """Handle polyinstantiation operations"""
    
    def __init__(self):
        self.db = db
    
    def query_as_user(
        self,
        clearance_level: int,
        query: str,
        params: tuple = None,
        user: str = None,
        password: str = None
    ) -> List[Dict[str, Any]]:
        """
        Execute query with specific clearance level
        
        Args:
            clearance_level: User's clearance level (1, 2, or 3)
            query: SQL query to execute
            params: Query parameters
            user: Database user
            password: Database password
        
        Returns:
            Query results filtered by clearance level
        """
        # Set clearance level for session
        self.db.set_user_clearance(clearance_level, user, password)
        
        # Execute query
        results = self.db.execute_query(query, params, user, password)
        
        return results
    
    def demonstrate_polyinstantiation(
        self,
        employee_name: str,
        user: str = None,
        password: str = None
    ) -> Dict[str, Any]:
        """
        Demonstrate how polyinstantiation works by showing different
        data views at different clearance levels
        
        Args:
            employee_name: Name of employee to query
            user: Database user
            password: Database password
        
        Returns:
            Dictionary showing data at each clearance level
        """
        print(f"\n{'='*80}")
        print(f"POLYINSTANTIATION DEMONSTRATION: {employee_name}")
        print(f"{'='*80}\n")
        
        query = """
            SELECT 
                employee_id,
                name,
                department,
                salary,
                clearance_level,
                hire_date
            FROM employees_secure
            WHERE name = %s
        """
        
        results = {}
        
        for level in [1, 2, 3]:
            print(f"--- Clearance Level {level} View ---")
            
            data = self.query_as_user(level, query, (employee_name,), user, password)
            
            if data:
                record = data[0]
                print(f"  Employee ID: {record['employee_id']}")
                print(f"  Name: {record['name']}")
                print(f"  Department: {record['department']}")
                print(f"  Salary: ${record['salary']:,.2f}")
                print(f"  Clearance: {record['clearance_level']}")
                print(f"  Hire Date: {record['hire_date']}")
                
                results[f'level_{level}'] = record
            else:
                print("  No data visible at this level")
                results[f'level_{level}'] = None
            
            print()
        
        # Show actual data
        actual_query = "SELECT * FROM employees WHERE name = %s"
        actual_data = self.db.execute_query(actual_query, (employee_name,))
        
        if actual_data:
            print("--- Actual Data (Ground Truth) ---")
            actual = actual_data[0]
            print(f"  Actual Salary: ${actual['salary']:,.2f}")
            print(f"  Actual Clearance: {actual['clearance_level']}")
            results['actual'] = actual
        
        print(f"\n{'='*80}\n")
        
        return results
    
    def test_inference_with_polyinstantiation(
        self,
        department: str,
        clearance_level: int,
        user: str = None,
        password: str = None
    ) -> Dict[str, Any]:
        """
        Test if inference attacks work against polyinstantiated data
        
        Args:
            department: Department to attack
            clearance_level: Attacker's clearance level
            user: Database user
            password: Database password
        
        Returns:
            Attack results
        """
        print(f"\n{'='*80}")
        print(f"INFERENCE ATTACK WITH POLYINSTANTIATION")
        print(f"Department: {department}, Attacker Clearance: {clearance_level}")
        print(f"{'='*80}\n")
        
        # Set attacker's clearance
        self.db.set_user_clearance(clearance_level, user, password)
        
        # Try differencing attack
        query1 = """
            SELECT AVG(salary) as avg_salary, COUNT(*) as cnt
            FROM employees_secure
            WHERE department = %s
        """
        
        result1 = self.db.execute_query(query1, (department,), user, password)
        
        if not result1:
            return {'success': False, 'reason': 'Query failed'}
        
        avg_all = float(result1[0]['avg_salary'])
        count_all = result1[0]['cnt']
        
        print(f"Average salary (all): ${avg_all:,.2f}")
        print(f"Employee count: {count_all}")
        
        # Get an employee to target
        emp_query = """
            SELECT name FROM employees_secure
            WHERE department = %s
            LIMIT 1
        """
        target = self.db.execute_query(emp_query, (department,), user, password)
        
        if not target:
            return {'success': False, 'reason': 'No employees visible'}
        
        target_name = target[0]['name']
        
        # Try to infer target's salary
        query2 = """
            SELECT AVG(salary) as avg_salary, COUNT(*) as cnt
            FROM employees_secure
            WHERE department = %s AND name != %s
        """
        
        result2 = self.db.execute_query(query2, (department, target_name), user, password)
        
        if not result2:
            return {'success': False, 'reason': 'Second query failed'}
        
        avg_without = float(result2[0]['avg_salary'])
        count_without = result2[0]['cnt']
        
        # Infer salary
        inferred_salary = (avg_all * count_all) - (avg_without * count_without)
        
        print(f"\nTarget: {target_name}")
        print(f"Inferred salary: ${inferred_salary:,.2f}")
        
        # Check actual salary
        actual_query = "SELECT salary FROM employees WHERE name = %s"
        actual_data = self.db.execute_query(actual_query, (target_name,))
        
        if actual_data:
            actual_salary = float(actual_data[0]['salary'])
            error = abs(inferred_salary - actual_salary)
            error_pct = (error / actual_salary) * 100
            
            print(f"Actual salary: ${actual_salary:,.2f}")
            print(f"Error: ${error:,.2f} ({error_pct:.2f}%)")
            
            # Check if polyinstantiation protected the data
            protected = error_pct > 10  # If error > 10%, polyinstantiation worked
            
            print(f"\nPolyinstantiation {'PROTECTED' if protected else 'FAILED TO PROTECT'} the data")
            
            return {
                'success': True,
                'target': target_name,
                'inferred_salary': inferred_salary,
                'actual_salary': actual_salary,
                'error': error,
                'error_pct': error_pct,
                'protected': protected,
                'clearance_level': clearance_level
            }
        
        return {
            'success': True,
            'target': target_name,
            'inferred_salary': inferred_salary,
            'clearance_level': clearance_level
        }