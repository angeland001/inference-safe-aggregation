"""
Least privilege implementation and demonstration
"""
from typing import Dict, Any, List
from src.database import db


class LeastPrivilege:
    """Demonstrate least privilege principles"""
    
    def __init__(self):
        self.db = db
        self.roles = {
            'basic_employee': {
                'description': 'Basic employee with minimal access',
                'can_view': ['employee_id', 'name', 'department', 'hire_date'],
                'tables': ['employees_basic', 'departments']
            },
            'dept_manager': {
                'description': 'Department manager with moderate access',
                'can_view': ['employee_id', 'name', 'department', 'hire_date', 'phone', 'email'],
                'tables': ['employees_manager', 'sales', 'departments']
            },
            'hr_admin': {
                'description': 'HR administrator with full access',
                'can_view': ['all columns'],
                'tables': ['all tables']
            },
            'analyst': {
                'description': 'Data analyst with aggregate-only access',
                'can_view': ['aggregate functions only'],
                'tables': ['sales', 'departments']
            }
        }
    
    def demonstrate_role_access(
        self,
        role: str,
        user: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Demonstrate what each role can access
        
        Args:
            role: Role name
            user: Database user with that role
            password: Database password
        
        Returns:
            Dictionary of access test results
        """
        print(f"\n{'='*80}")
        print(f"LEAST PRIVILEGE DEMONSTRATION: {role.upper()}")
        print(f"{'='*80}\n")
        
        if role not in self.roles:
            return {'error': 'Unknown role'}
        
        role_info = self.roles[role]
        print(f"Description: {role_info['description']}")
        print(f"Allowed columns: {', '.join(role_info['can_view'])}")
        print(f"Allowed tables: {', '.join(role_info['tables'])}\n")
        
        results = {
            'role': role,
            'queries': []
        }
        
        # Test 1: Try to view employees table
        print("Test 1: Query employees table")
        query1 = "SELECT * FROM employees LIMIT 5"
        try:
            data = self.db.execute_query(query1, user=user, password=password)
            print(f"  [OK] SUCCESS: Retrieved {len(data)} records")
            print(f"    Columns visible: {list(data[0].keys()) if data else 'none'}")
            results['queries'].append({
                'query': query1,
                'success': True,
                'records': len(data),
                'columns': list(data[0].keys()) if data else []
            })
        except Exception as e:
            print(f"  [X] DENIED: {str(e)[:100]}")
            results['queries'].append({
                'query': query1,
                'success': False,
                'error': str(e)
            })
        
        print()
        
        # Test 2: Try to view specific employee data
        print("Test 2: Query specific employee salary")
        query2 = "SELECT name, salary FROM employees WHERE name = 'Alice Johnson'"
        try:
            data = self.db.execute_query(query2, user=user, password=password)
            print(f"  [OK] SUCCESS: Retrieved salary data")
            if data:
                print(f"    {data[0]['name']}: ${data[0]['salary']:,.2f}")
            results['queries'].append({
                'query': query2,
                'success': True,
                'data': data
            })
        except Exception as e:
            print(f"  [X] DENIED: {str(e)[:100]}")
            results['queries'].append({
                'query': query2,
                'success': False,
                'error': str(e)
            })
        
        print()
        
        # Test 3: Try to view role-appropriate data
        print("Test 3: Query role-appropriate view")
        if role == 'basic_employee':
            query3 = "SELECT * FROM employees_basic LIMIT 5"
        elif role == 'dept_manager':
            query3 = "SELECT * FROM employees_manager LIMIT 5"
        elif role == 'hr_admin':
            query3 = "SELECT * FROM employees_hr LIMIT 5"
        else:  # analyst
            query3 = "SELECT AVG(amount) as avg_sale FROM sales"
        
        try:
            data = self.db.execute_query(query3, user=user, password=password)
            print(f"  [OK] SUCCESS: Retrieved {len(data) if isinstance(data, list) else 1} records")
            if data:
                print(f"    Columns: {list(data[0].keys())}")
            results['queries'].append({
                'query': query3,
                'success': True,
                'records': len(data) if isinstance(data, list) else 1
            })
        except Exception as e:
            print(f"  [X] DENIED: {str(e)[:100]}")
            results['queries'].append({
                'query': query3,
                'success': False,
                'error': str(e)
            })
        
        print()
        
        # Test 4: Try aggregate query
        print("Test 4: Aggregate query")
        query4 = "SELECT department, AVG(salary) as avg_sal FROM employees GROUP BY department"
        try:
            data = self.db.execute_query(query4, user=user, password=password)
            print(f"  [OK] SUCCESS: Retrieved aggregate data")
            for row in data[:3]:
                print(f"    {row['department']}: ${row['avg_sal']:,.2f}")
            results['queries'].append({
                'query': query4,
                'success': True,
                'data': data
            })
        except Exception as e:
            print(f"  [X] DENIED: {str(e)[:100]}")
            results['queries'].append({
                'query': query4,
                'success': False,
                'error': str(e)
            })
        
        print(f"\n{'='*80}\n")
        
        return results
    
    def compare_all_roles(self) -> Dict[str, Any]:
        """
        Compare access levels across all roles
        
        Returns:
            Comparison results
        """
        print(f"\n{'='*80}")
        print("ROLE COMPARISON MATRIX")
        print(f"{'='*80}\n")
        
        test_users = {
            'basic_employee': ('alice_user', 'alice123'),
            'dept_manager': ('bob_manager', 'bob123'),
            'hr_admin': ('charlie_hr', 'charlie123'),
            'analyst': ('dana_analyst', 'dana123')
        }
        
        comparison = {}
        
        for role, (user, password) in test_users.items():
            print(f"\nTesting {role}...")
            comparison[role] = self.demonstrate_role_access(role, user, password)
        
        # Create summary table
        print("\n" + "="*80)
        print("SUMMARY: Access Control Matrix")
        print("="*80)
        print(f"{'Action':<40} {'Basic':<10} {'Manager':<10} {'HR':<10} {'Analyst':<10}")
        print("-"*80)
        
        actions = [
            "View all employee records",
            "View individual salaries",
            "View role-appropriate data",
            "Perform aggregate queries"
        ]
        
        for i, action in enumerate(actions):
            row = f"{action:<40}"
            for role in ['basic_employee', 'dept_manager', 'hr_admin', 'analyst']:
                success = comparison[role]['queries'][i]['success']
                row += f" {'[OK]':<10}" if success else f" {'[X]':<10}"
            print(row)
        
        print("="*80 + "\n")
        
        return comparison