
DROP DATABASE IF EXISTS inference_demo;
CREATE DATABASE inference_demo;

\c inference_demo;

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;



-- CORE TABLES

-- Employees table 
CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    clearance_level INT NOT NULL CHECK (clearance_level IN (1, 2, 3)),
    hire_date DATE NOT NULL,
    ssn_last4 CHAR(4),
    phone VARCHAR(20),
    email VARCHAR(100)
);

-- Sales table
CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES employees(employee_id),
    amount DECIMAL(10,2) NOT NULL,
    sale_date DATE NOT NULL,
    product_category VARCHAR(50),
    region VARCHAR(50)
);

-- Departments table
CREATE TABLE departments (
    dept_id SERIAL PRIMARY KEY,
    dept_name VARCHAR(50) UNIQUE NOT NULL,
    budget DECIMAL(12,2) NOT NULL,
    manager_id INT REFERENCES employees(employee_id),
    location VARCHAR(100)
);


-- POLYINSTANTIATION TABLES


-- Polyinstantiated employees 
CREATE TABLE employees_poly (
    employee_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    clearance_level INT NOT NULL,
    visible_at_level INT NOT NULL CHECK (visible_at_level IN (1, 2, 3)),
    hire_date DATE NOT NULL,
    is_cover_story BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (employee_id, visible_at_level)
);


-- AUDIT AND TRACKING TABLES


-- Query audit log for tracking inference attempts
CREATE TABLE query_audit (
    audit_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    query_text TEXT NOT NULL,
    query_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result_count INT,
    was_blocked BOOLEAN DEFAULT FALSE,
    block_reason VARCHAR(200)
);

-- Query history for overlap detection
CREATE TABLE query_history (
    history_id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    query_hash VARCHAR(64) NOT NULL,
    query_text TEXT NOT NULL,
    result_set_hash VARCHAR(64),
    execution_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- VIEWS FOR DIFFERENT SECURITY LEVELS


-- View for basic employees (least privilege)
CREATE VIEW employees_basic AS
SELECT 
    employee_id,
    name,
    department,
    hire_date
FROM employees;

-- View for department managers
CREATE VIEW employees_manager AS
SELECT 
    employee_id,
    name,
    department,
    hire_date,
    phone,
    email
FROM employees;

-- View for HR (all data)
CREATE VIEW employees_hr AS
SELECT * FROM employees;

-- Polyinstantiation view (dynamic based on user clearance)
CREATE VIEW employees_secure AS
SELECT 
    employee_id,
    name,
    department,
    salary,
    clearance_level,
    hire_date
FROM employees_poly
WHERE visible_at_level <= COALESCE(
    current_setting('app.user_clearance', true)::INT, 
    1
);

-- FUNCTIONS FOR INFERENCE PROTECTION


-- Function to log queries
CREATE OR REPLACE FUNCTION log_query(
    p_username VARCHAR,
    p_query TEXT,
    p_result_count INT,
    p_blocked BOOLEAN,
    p_reason VARCHAR
) RETURNS VOID AS $$
BEGIN
    INSERT INTO query_audit (username, query_text, result_count, was_blocked, block_reason)
    VALUES (p_username, p_query, p_result_count, p_blocked, p_reason);
END;
$$ LANGUAGE plpgsql;

-- Function to check minimum result size
CREATE OR REPLACE FUNCTION check_min_size(p_count INT, p_min INT DEFAULT 5) 
RETURNS BOOLEAN AS $$
BEGIN
    RETURN p_count >= p_min;
END;
$$ LANGUAGE plpgsql;

-- Function to add differential privacy noise
CREATE OR REPLACE FUNCTION add_laplace_noise(p_value DECIMAL, p_epsilon DECIMAL DEFAULT 1.0)
RETURNS DECIMAL AS $$
DECLARE
    u DECIMAL;
    noise DECIMAL;
BEGIN
    -- Generate uniform random number between -0.5 and 0.5
    u := random() - 0.5;
    -- Convert to Laplace distribution
    noise := -SIGN(u) * LN(1 - 2 * ABS(u)) / p_epsilon;
    RETURN p_value + noise;
END;
$$ LANGUAGE plpgsql;


-- INDEXES FOR PERFORMANCE

CREATE INDEX idx_employees_dept ON employees(department);
CREATE INDEX idx_employees_clearance ON employees(clearance_level);
CREATE INDEX idx_sales_employee ON sales(employee_id);
CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_query_audit_user ON query_audit(username);
CREATE INDEX idx_query_audit_timestamp ON query_audit(query_timestamp);
CREATE INDEX idx_employees_poly_level ON employees_poly(visible_at_level);