"""
Implementation of different aggregation methods with varying inference protection
"""
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from src.database import db
import hashlib


class AggregationMethod:
    """Base class for aggregation methods"""
    
    def __init__(self, username: str = "system"):
        self.username = username
        self.db = db
    
    def execute_with_logging(
        self,
        query: str,
        params: tuple = None,
        user: str = None,
        password: str = None
    ) -> Tuple[Optional[List[Dict[str, Any]]], bool, str]:
        """
        Execute query with logging
        
        Returns:
            Tuple of (results, was_blocked, block_reason)
        """
        try:
            results = self.db.execute_query(query, params, user, password)
            result_count = len(results) if results else 0
            
            self.db.log_query_audit(
                self.username,
                query,
                result_count,
                False,
                None
            )
            
            return results, False, None
            
        except Exception as e:
            self.db.log_query_audit(
                self.username,
                query,
                0,
                True,
                str(e)
            )
            return None, True, str(e)


class NoProtection(AggregationMethod):
    """Baseline - no inference protection"""
    
    def aggregate(
        self,
        query: str,
        params: tuple = None,
        user: str = None,
        password: str = None
    ) -> Dict[str, Any]:
        """Execute query without any protection"""
        results, blocked, reason = self.execute_with_logging(query, params, user, password)
        
        return {
            'method': 'No Protection',
            'blocked': blocked,
            'block_reason': reason,
            'results': results,
            'protection_applied': None
        }


class MinimumSizeRestriction(AggregationMethod):
    """Query restriction - minimum result set size"""
    
    def __init__(self, username: str = "system", min_size: int = 5):
        super().__init__(username)
        self.min_size = min_size
    
    def aggregate(
        self,
        query: str,
        params: tuple = None,
        user: str = None,
        password: str = None
    ) -> Dict[str, Any]:
        """Execute query only if result set is large enough"""
        
        # First, check the count
        count_query = self._convert_to_count_query(query)
        count_results, blocked, reason = self.execute_with_logging(
            count_query, params, user, password
        )
        
        if blocked:
            return {
                'method': 'Minimum Size Restriction',
                'blocked': True,
                'block_reason': reason,
                'results': None,
                'protection_applied': f'min_size={self.min_size}'
            }
        
        count = count_results[0]['count'] if count_results else 0
        
        if count < self.min_size:
            self.db.log_query_audit(
                self.username,
                query,
                count,
                True,
                f"Result set too small: {count} < {self.min_size}"
            )
            return {
                'method': 'Minimum Size Restriction',
                'blocked': True,
                'block_reason': f"Result set too small: {count} < {self.min_size}",
                'results': None,
                'protection_applied': f'min_size={self.min_size}'
            }
        
        # Execute actual query
        results, blocked, reason = self.execute_with_logging(query, params, user, password)
        
        return {
            'method': 'Minimum Size Restriction',
            'blocked': blocked,
            'block_reason': reason,
            'results': results,
            'protection_applied': f'min_size={self.min_size}, actual_size={count}'
        }
    
    def _convert_to_count_query(self, query: str) -> str:
        """Convert a SELECT query to a COUNT query"""
        # Simple conversion - wrap query in COUNT
        query_lower = query.lower().strip()
        if query_lower.startswith('select'):
            # Extract FROM clause onwards
            from_index = query_lower.find('from')
            if from_index != -1:
                return f"SELECT COUNT(*) as count FROM {query[from_index + 4:]}"
        return f"SELECT COUNT(*) as count FROM ({query}) as subquery"


class DifferentialPrivacy(AggregationMethod):
    """Add Laplacian noise to results for differential privacy"""
    
    def __init__(self, username: str = "system", epsilon: float = 1.0):
        super().__init__(username)
        self.epsilon = epsilon
    
    def aggregate(
        self,
        query: str,
        params: tuple = None,
        user: str = None,
        password: str = None
    ) -> Dict[str, Any]:
        """Execute query and add noise to numeric results"""
        
        results, blocked, reason = self.execute_with_logging(query, params, user, password)
        
        if blocked or not results:
            return {
                'method': 'Differential Privacy',
                'blocked': blocked,
                'block_reason': reason,
                'results': None,
                'protection_applied': f'epsilon={self.epsilon}'
            }
        
        # Add noise to numeric values
        noisy_results = []
        for row in results:
            noisy_row = {}
            for key, value in row.items():
                if isinstance(value, (int, float)):
                    # Add Laplacian noise
                    noise = np.random.laplace(0, 1 / self.epsilon)
                    noisy_row[key] = value + noise
                else:
                    noisy_row[key] = value
            noisy_results.append(noisy_row)
        
        return {
            'method': 'Differential Privacy',
            'blocked': False,
            'block_reason': None,
            'results': noisy_results,
            'original_results': results,
            'protection_applied': f'epsilon={self.epsilon}, laplace_noise_added'
        }


class OverlapControl(AggregationMethod):
    """Control query overlap to prevent inference"""
    
    def __init__(self, username: str = "system", overlap_threshold: float = 0.8):
        super().__init__(username)
        self.overlap_threshold = overlap_threshold
    
    def aggregate(
        self,
        query: str,
        params: tuple = None,
        user: str = None,
        password: str = None
    ) -> Dict[str, Any]:
        """Execute query only if overlap with history is acceptable"""
        
        # Get query history
        history = self.db.get_query_history(self.username, limit=20)
        
        # Execute query to get results
        results, blocked, reason = self.execute_with_logging(query, params, user, password)
        
        if blocked or not results:
            return {
                'method': 'Overlap Control',
                'blocked': blocked,
                'block_reason': reason,
                'results': None,
                'protection_applied': f'threshold={self.overlap_threshold}'
            }
        
        # Calculate result set hash
        result_str = str(sorted([str(sorted(r.items())) for r in results]))
        current_hash = hashlib.sha256(result_str.encode()).hexdigest()
        
        # Check overlap with history
        for hist_entry in history:
            if hist_entry.get('result_set_hash'):
                overlap = self._calculate_overlap(current_hash, hist_entry['result_set_hash'])
                if overlap > self.overlap_threshold:
                    self.db.log_query_audit(
                        self.username,
                        query,
                        len(results),
                        True,
                        f"Query overlap too high: {overlap:.2f} > {self.overlap_threshold}"
                    )
                    return {
                        'method': 'Overlap Control',
                        'blocked': True,
                        'block_reason': f"Query overlap too high: {overlap:.2f}",
                        'results': None,
                        'protection_applied': f'threshold={self.overlap_threshold}'
                    }
        
        # Store in history
        self.db.store_query_history(self.username, query, results)
        
        return {
            'method': 'Overlap Control',
            'blocked': False,
            'block_reason': None,
            'results': results,
            'protection_applied': f'threshold={self.overlap_threshold}, overlap_acceptable'
        }
    
    def _calculate_overlap(self, hash1: str, hash2: str) -> float:
        """
        Calculate similarity between two hashes
        Simple implementation - in practice, would compare actual result sets
        """
        # Convert hashes to binary and calculate Hamming distance
        bin1 = bin(int(hash1, 16))[2:].zfill(256)
        bin2 = bin(int(hash2, 16))[2:].zfill(256)
        
        matches = sum(b1 == b2 for b1, b2 in zip(bin1, bin2))
        return matches / 256


class CellSuppression(AggregationMethod):
    """Suppress cells in results that could lead to inference"""
    
    def __init__(self, username: str = "system", min_cell_size: int = 3):
        super().__init__(username)
        self.min_cell_size = min_cell_size
    
    def aggregate(
        self,
        query: str,
        params: tuple = None,
        user: str = None,
        password: str = None,
        group_by_column: str = None
    ) -> Dict[str, Any]:
        """Execute query and suppress small cells"""
        
        results, blocked, reason = self.execute_with_logging(query, params, user, password)
        
        if blocked or not results:
            return {
                'method': 'Cell Suppression',
                'blocked': blocked,
                'block_reason': reason,
                'results': None,
                'protection_applied': f'min_cell_size={self.min_cell_size}'
            }
        
        # Check if this is a grouped query with counts
        suppressed_results = []
        suppressed_count = 0
        
        for row in results:
            # Look for count column
            count_col = None
            for key in row.keys():
                if 'count' in key.lower():
                    count_col = key
                    break
            
            if count_col and row[count_col] < self.min_cell_size:
                # Suppress this cell
                suppressed_count += 1
                suppressed_row = {k: ('SUPPRESSED' if k != count_col else None) for k in row.keys()}
                suppressed_results.append(suppressed_row)
            else:
                suppressed_results.append(row)
        
        return {
            'method': 'Cell Suppression',
            'blocked': False,
            'block_reason': None,
            'results': suppressed_results,
            'original_results': results,
            'protection_applied': f'min_cell_size={self.min_cell_size}, suppressed={suppressed_count}'
        }


class AggregationComparator:
    """Compare different aggregation methods"""
    
    def __init__(self, username: str = "system"):
        self.username = username
        self.methods = {
            'no_protection': NoProtection(username),
            'min_size': MinimumSizeRestriction(username, min_size=5),
            'differential_privacy': DifferentialPrivacy(username, epsilon=1.0),
            'overlap_control': OverlapControl(username, overlap_threshold=0.8),
            'cell_suppression': CellSuppression(username, min_cell_size=3)
        }
    
    def compare_all(
        self,
        query: str,
        params: tuple = None,
        user: str = None,
        password: str = None
    ) -> Dict[str, Dict[str, Any]]:
        """Run query through all aggregation methods and compare results"""
        
        results = {}
        for method_name, method_obj in self.methods.items():
            results[method_name] = method_obj.aggregate(query, params, user, password)
        
        return results