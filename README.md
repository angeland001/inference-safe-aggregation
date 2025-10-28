# Inference-Safe Aggregation Project

Database Security Project demonstrating inference attacks and protection mechanisms.

**Authors:** Ammar Tojaga & Andres Angel

## Overview

This project demonstrates how attackers can infer sensitive information from database aggregation queries and explores various methods to prevent such attacks through:

1. **Inference Attacks**: Various techniques to deduce sensitive data
2. **Aggregation Methods**: Different protection mechanisms
3. **Polyinstantiation**: Multiple data versions for different clearance levels
4. **Least Privilege**: Role-based access control

## Setup Instructions

### Prerequisites

- PostgreSQL 12+
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd inference-safe-aggregation
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure database**

Create a `.env` file in the project root:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=inference_demo
DB_USER=postgres
DB_PASSWORD=your_password
SECRET_KEY=your-secret-key-here
```

4. **Initialize database**
```bash
# Create database and schema
psql -U postgres -f database/schema.sql

# Load seed data
psql -U postgres -d inference_demo -f database/seed_data.sql

# Set up roles and users
psql -U postgres -d inference_demo -f database/setup_roles.sql
```

### Running the Application

**Web Interface:**
```bash
python web/app.py
```
Then open http://localhost:5000 in your browser.

**Command Line Tests:**
```bash
# Run unit tests
python -m pytest tests/

# Run specific attack demonstrations
python -c "from src.attacks import AttackSuite; AttackSuite().run_all_attacks()"
```

## Project Structure
```
inference-safe-aggregation/
├── database/           # Database setup scripts
├── src/               # Core Python modules
├── web/               # Flask web application
├── tests/             # Unit tests
├── config.py          # Configuration
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Features

### 1. Inference Attacks

- **Differencing Attack**: Infer individual values by comparing aggregates
- **Tracker Attack**: Use COUNT queries to determine membership
- **SUM Attack**: Deduce individual salaries using totals
- **Linear System Attack**: Build equations to solve for unknowns

### 2. Protection Methods

- **No Protection**: Baseline (vulnerable)
- **Minimum Size Restriction**: Require minimum result set size
- **Differential Privacy**: Add statistical noise
- **Overlap Control**: Detect and block similar queries
- **Cell Suppression**: Hide small cells in results

### 3. Polyinstantiation

- Multiple data versions at different clearance levels
- Cover stories for sensitive information
- Prevents inference through false data

### 4. Least Privilege

- **Basic Employee**: Minimal access
- **Department Manager**: Moderate access
- **HR Administrator**: Full access
- **Data Analyst**: Aggregate-only access

## Usage Examples

### Run Differencing Attack
```python
from src.attacks import DifferencingAttack

attack = DifferencingAttack()
result = attack.attack("Alice Johnson", "Engineering")
print(f"Inferred salary: ${result['inferred_salary']:,.2f}")
```

### Compare Aggregation Methods
```python
from src.aggregation_methods import AggregationComparator

comparator = AggregationComparator()
query = "SELECT AVG(salary) FROM employees WHERE department = 'Sales'"
results = comparator.compare_all(query)
```

### Demonstrate Polyinstantiation
```python
from src.polyinstantiation import Polyinstantiation

poly = Polyinstantiation()
result = poly.demonstrate_polyinstantiation("Carol White")
```

## Test Users

| Username | Password | Role | Clearance |
|----------|----------|------|-----------|
| alice_user | alice123 | Basic Employee | Level 1 |
| bob_manager | bob123 | Dept Manager | Level 2 |
| charlie_hr | charlie123 | HR Admin | Level 3 |
| dana_analyst | dana123 | Analyst | Level 2 |
| eve_attacker | eve123 | Attacker | Level 1 |

## Database Schema

- **employees**: Main employee data
- **sales**: Sales transactions
- **departments**: Department information
- **employees_poly**: Polyinstantiated employee data
- **query_audit**: Query logging
- **query_history**: Query history for overlap detection

## Report Sections

The final report should cover:

1. **Introduction**: Define inference attacks and their relevance
2. **Background**: Explain least privilege, polyinstantiation, aggregation
3. **Methodology**: Database design, attack scenarios, protection methods
4. **Implementation**: Code walkthrough and architecture
5. **Results**: Attack success rates, protection effectiveness
6. **Analysis**: Which methods work best and why
7. **Conclusion**: Best practices for inference-safe aggregation

## License

This project is for educational purposes as part of a database security course.

## References

- Database Security and Inference Control
- Polyinstantiation in Multilevel Secure Databases
- Differential Privacy in Statistical Databases
- Role-Based Access Control (RBAC)
```

### 16. .env.example
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=inference_demo
DB_USER=postgres
DB_PASSWORD=your_password_here
SECRET_KEY=your-secret-key-change-in-production