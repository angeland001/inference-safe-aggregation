\c inference_demo;


-- DROP EXISTING ROLES IF THEY EXIST


DROP ROLE IF EXISTS basic_employee;
DROP ROLE IF EXISTS dept_manager;
DROP ROLE IF EXISTS hr_admin;
DROP ROLE IF EXISTS analyst;
DROP ROLE IF EXISTS attacker;

-- Drop test users if they exist
DROP ROLE IF EXISTS alice_user;
DROP ROLE IF EXISTS bob_manager;
DROP ROLE IF EXISTS charlie_hr;
DROP ROLE IF EXISTS dana_analyst;
DROP ROLE IF EXISTS eve_attacker;


-- CREATE ROLES


-- Role 1: Basic Employee (lowest privilege)
CREATE ROLE basic_employee;
GRANT CONNECT ON DATABASE inference_demo TO basic_employee;
GRANT USAGE ON SCHEMA public TO basic_employee;
GRANT SELECT ON employees_basic TO basic_employee;
GRANT SELECT ON departments TO basic_employee;

-- Role 2: Department Manager (medium privilege)
CREATE ROLE dept_manager;
GRANT CONNECT ON DATABASE inference_demo TO dept_manager;
GRANT USAGE ON SCHEMA public TO dept_manager;
GRANT SELECT ON employees_manager TO dept_manager;
GRANT SELECT ON sales TO dept_manager;
GRANT SELECT ON departments TO dept_manager;

-- Role 3: HR Admin (high privilege)
CREATE ROLE hr_admin;
GRANT CONNECT ON DATABASE inference_demo TO hr_admin;
GRANT USAGE ON SCHEMA public TO hr_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO hr_admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO hr_admin;

-- Role 4: Analyst (can see aggregates but not individual records)
CREATE ROLE analyst;
GRANT CONNECT ON DATABASE inference_demo TO analyst;
GRANT USAGE ON SCHEMA public TO analyst;
GRANT SELECT ON sales TO analyst;
GRANT SELECT ON departments TO analyst;

-- Role 5: Attacker (simulates malicious user with basic access)
CREATE ROLE attacker;
GRANT CONNECT ON DATABASE inference_demo TO attacker;
GRANT USAGE ON SCHEMA public TO attacker;
GRANT SELECT ON employees_basic TO attacker;
GRANT SELECT ON sales TO attacker;

-- CREATE TEST USERS


-- User 1: Alice - Basic Employee
CREATE USER alice_user WITH PASSWORD 'alice123';
GRANT basic_employee TO alice_user;
-- Set clearance level for Alice
ALTER ROLE alice_user SET app.user_clearance = '1';

-- User 2: Bob - Department Manager
CREATE USER bob_manager WITH PASSWORD 'bob123';
GRANT dept_manager TO bob_manager;
ALTER ROLE bob_manager SET app.user_clearance = '2';

-- User 3: Charlie - HR Admin
CREATE USER charlie_hr WITH PASSWORD 'charlie123';
GRANT hr_admin TO charlie_hr;
ALTER ROLE charlie_hr SET app.user_clearance = '3';

-- User 4: Dana - Analyst
CREATE USER dana_analyst WITH PASSWORD 'dana123';
GRANT analyst TO dana_analyst;
ALTER ROLE dana_analyst SET app.user_clearance = '2';

-- User 5: Eve - Attacker
CREATE USER eve_attacker WITH PASSWORD 'eve123';
GRANT attacker TO eve_attacker;
ALTER ROLE eve_attacker SET app.user_clearance = '1';


-- ROW LEVEL SECURITY (RLS) POLICIES


-- Enable RLS on employees table
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;

-- Policy: Basic employees can only see their own department's names
CREATE POLICY basic_employee_policy ON employees
    FOR SELECT
    TO basic_employee
    USING (department IN (
        SELECT department FROM employees WHERE name = current_user
    ));

-- Policy: Managers can see all employees in their department
CREATE POLICY manager_policy ON employees
    FOR SELECT
    TO dept_manager
    USING (TRUE);  -- View handles the restriction

-- Policy: HR can see everything
CREATE POLICY hr_policy ON employees
    FOR ALL
    TO hr_admin
    USING (TRUE);

-- Enable RLS on sales table
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;

-- Policy: Analysts can see all sales data
CREATE POLICY analyst_sales_policy ON sales
    FOR SELECT
    TO analyst
    USING (TRUE);

-- Policy: Managers can see sales for their department
CREATE POLICY manager_sales_policy ON sales
    FOR SELECT
    TO dept_manager
    USING (TRUE);


-- GRANT EXECUTE ON FUNCTIONS


GRANT EXECUTE ON FUNCTION log_query TO PUBLIC;
GRANT EXECUTE ON FUNCTION check_min_size TO PUBLIC;
GRANT EXECUTE ON FUNCTION add_laplace_noise TO PUBLIC;

-- SUMMARY

\echo 'Database setup complete!'

\echo 'Roles created:'
\echo '  - basic_employee (lowest privilege)'
\echo '  - dept_manager (medium privilege)'
\echo '  - hr_admin (highest privilege)'
\echo '  - analyst (aggregate queries only)'
\echo '  - attacker (for testing inference attacks)'
\echo ''
\echo 'Test users created:'
\echo '  - alice_user (clearance: 1, password: alice123)'
\echo '  - bob_manager (clearance: 2, password: bob123)'
\echo '  - charlie_hr (clearance: 3, password: charlie123)'
\echo '  - dana_analyst (clearance: 2, password: dana123)'
\echo '  - eve_attacker (clearance: 1, password: eve123)'
