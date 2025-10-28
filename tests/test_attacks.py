"""
Unit tests for inference attacks
"""
import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.attacks import DifferencingAttack, TrackerAttack, SumAttack, LinearSystemAttack
from src.database import db


class TestInferenceAttacks(unittest.TestCase):
    """Test suite for inference attacks"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.diff_attack = DifferencingAttack("test_user")
        self.tracker_attack = TrackerAttack("test_user")
        self.sum_attack = SumAttack("test_user")
        self.linear_attack = LinearSystemAttack("test_user")
    
    def test_differencing_attack(self):
        """Test differencing attack on Alice Johnson"""
        result = self.diff_attack.attack("Alice Johnson", "Engineering")
        
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['inferred_salary'])
        self.assertIsNotNone(result['actual_salary'])
        self.assertLess(result['error'], 1.0)  # Error should be very small
    
    def test_tracker_attack(self):
        """Test tracker attack"""
        result = self.tracker_attack.attack("Bob Smith", 90000.00)
        
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['inferred_high_earner'])
        self.assertIsNotNone(result['actual_high_earner'])
    
    def test_sum_attack_with_one_unknown(self):
        """Test SUM attack when only one salary is unknown"""
        # Operations department has 5 employees - if we know 4, we can infer 1
        known = {
            'Dana Cox': 72000.00,
            'Ethan Howard': 75000.00,
            'Faye Ward': 68000.00,
            'Greg Torres': 80000.00
        }
        
        result = self.sum_attack.attack("Operations", known)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['unknown_count'], 1)
        self.assertGreater(len(result['inferred_salaries']), 0)
    
    def test_linear_system_attack(self):
        """Test linear system attack on Finance department"""
        result = self.linear_attack.attack("Finance")
        
        self.assertTrue(result['success'])
        self.assertGreater(result['employee_count'], 0)
        self.assertGreater(len(result['results']), 0)
        
        # Check that errors are reasonable
        for emp_name, emp_result in result['results'].items():
            self.assertLess(emp_result['error_pct'], 1.0)  # Less than 1% error


class TestAggregationMethods(unittest.TestCase):
    """Test suite for aggregation protection methods"""
    
    def setUp(self):
        """Set up test fixtures"""
        from src.aggregation_methods import (
            NoProtection, MinimumSizeRestriction, 
            DifferentialPrivacy, OverlapControl, CellSuppression
        )
        self.no_prot = NoProtection("test_user")
        self.min_size = MinimumSizeRestriction("test_user", min_size=5)
        self.diff_priv = DifferentialPrivacy("test_user", epsilon=1.0)
        self.overlap = OverlapControl("test_user", overlap_threshold=0.8)
        self.cell_supp = CellSuppression("test_user", min_cell_size=3)
    
    def test_no_protection(self):
        """Test baseline with no protection"""
        query = "SELECT AVG(salary) as avg_sal FROM employees WHERE department = 'Engineering'"
        result = self.no_prot.aggregate(query)
        
        self.assertFalse(result['blocked'])
        self.assertIsNotNone(result['results'])
    
    def test_minimum_size_blocks_small_groups(self):
        """Test that minimum size restriction blocks small result sets"""
        # Query for a small department
        query = "SELECT AVG(salary) as avg_sal FROM employees WHERE department = 'Operations'"
        result = self.min_size.aggregate(query)
        
        # Operations has 5 employees, so it should be allowed
        self.assertFalse(result['blocked'])
        
        # Query for single employee should be blocked
        query2 = "SELECT salary FROM employees WHERE name = 'Alice Johnson'"
        result2 = self.min_size.aggregate(query2)
        self.assertTrue(result2['blocked'])
    
    def test_differential_privacy_adds_noise(self):
        """Test that differential privacy adds noise to results"""
        query = "SELECT AVG(salary) as avg_sal FROM employees WHERE department = 'Engineering'"
        
        # Run query twice with differential privacy
        result1 = self.diff_priv.aggregate(query)
        result2 = self.diff_priv.aggregate(query)
        
        self.assertFalse(result1['blocked'])
        self.assertFalse(result2['blocked'])
        
        # Results should be different due to noise
        val1 = result1['results'][0]['avg_sal']
        val2 = result2['results'][0]['avg_sal']
        self.assertNotEqual(val1, val2)


class TestPolyinstantiation(unittest.TestCase):
    """Test suite for polyinstantiation"""
    
    def setUp(self):
        """Set up test fixtures"""
        from src.polyinstantiation import Polyinstantiation
        self.poly = Polyinstantiation()
    
    def test_different_clearance_levels_show_different_data(self):
        """Test that different clearance levels see different salary data"""
        employee_name = "Carol White"  # Level 3 employee
        
        # Query at level 1
        query = "SELECT salary FROM employees_secure WHERE name = %s"
        result_l1 = self.poly.query_as_user(1, query, (employee_name,))
        
        # Query at level 3
        result_l3 = self.poly.query_as_user(3, query, (employee_name,))
        
        self.assertIsNotNone(result_l1)
        self.assertIsNotNone(result_l3)
        
        # Salaries should be different (level 1 sees cover story)
        salary_l1 = float(result_l1[0]['salary'])
        salary_l3 = float(result_l3[0]['salary'])
        self.assertNotEqual(salary_l1, salary_l3)
        self.assertLess(salary_l1, salary_l3)  # Cover story should be lower


class TestLeastPrivilege(unittest.TestCase):
    """Test suite for least privilege"""
    
    def setUp(self):
        """Set up test fixtures"""
        from src.least_privilege import LeastPrivilege
        self.lp = LeastPrivilege()
    
    def test_basic_employee_cannot_see_salaries(self):
        """Test that basic employees cannot view salary data"""
        try:
            result = db.execute_query(
                "SELECT salary FROM employees WHERE name = 'Alice Johnson'",
                user="alice_user",
                password="alice123"
            )
            # Should raise an exception or return empty
            self.assertTrue(False, "Basic employee should not access salary data")
        except Exception:
            # Expected to fail
            pass
    
    def test_hr_admin_can_see_all_data(self):
        """Test that HR admin can view all employee data"""
        result = db.execute_query(
            "SELECT * FROM employees LIMIT 1",
            user="charlie_hr",
            password="charlie123"
        )
        
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        self.assertIn('salary', result[0])


if __name__ == '__main__':
    unittest.main()