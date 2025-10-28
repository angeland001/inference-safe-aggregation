\c inference_demo;


-- SEED DEPARTMENTS


INSERT INTO departments (dept_name, budget, location) VALUES
('Engineering', 5000000.00, 'Building A'),
('Sales', 3000000.00, 'Building B'),
('Marketing', 2000000.00, 'Building B'),
('HR', 1000000.00, 'Building C'),
('Finance', 1500000.00, 'Building C'),
('Operations', 2500000.00, 'Building A');


-- SEED EMPLOYEES (60 employees across departments)


INSERT INTO employees (name, department, salary, clearance_level, hire_date, ssn_last4, phone, email) VALUES
-- Engineering (15 employees)
('Alice Johnson', 'Engineering', 95000.00, 2, '2020-01-15', '1234', '555-0101', 'alice.j@company.com'),
('Bob Smith', 'Engineering', 88000.00, 2, '2019-03-22', '2345', '555-0102', 'bob.s@company.com'),
('Carol White', 'Engineering', 105000.00, 3, '2018-06-10', '3456', '555-0103', 'carol.w@company.com'),
('David Brown', 'Engineering', 92000.00, 2, '2020-08-05', '4567', '555-0104', 'david.b@company.com'),
('Eve Davis', 'Engineering', 87000.00, 1, '2021-02-18', '5678', '555-0105', 'eve.d@company.com'),
('Frank Miller', 'Engineering', 98000.00, 2, '2019-11-30', '6789', '555-0106', 'frank.m@company.com'),
('Grace Lee', 'Engineering', 110000.00, 3, '2017-04-12', '7890', '555-0107', 'grace.l@company.com'),
('Henry Wilson', 'Engineering', 85000.00, 1, '2021-09-20', '8901', '555-0108', 'henry.w@company.com'),
('Ivy Moore', 'Engineering', 93000.00, 2, '2020-05-25', '9012', '555-0109', 'ivy.m@company.com'),
('Jack Taylor', 'Engineering', 89000.00, 2, '2019-12-08', '0123', '555-0110', 'jack.t@company.com'),
('Kate Anderson', 'Engineering', 102000.00, 3, '2018-07-15', '1235', '555-0111', 'kate.a@company.com'),
('Liam Thomas', 'Engineering', 86000.00, 1, '2021-03-10', '2346', '555-0112', 'liam.t@company.com'),
('Maya Jackson', 'Engineering', 96000.00, 2, '2019-10-22', '3457', '555-0113', 'maya.j@company.com'),
('Noah Martin', 'Engineering', 91000.00, 2, '2020-04-18', '4568', '555-0114', 'noah.m@company.com'),
('Olivia Garcia', 'Engineering', 99000.00, 2, '2019-08-30', '5679', '555-0115', 'olivia.g@company.com'),

-- Sales (15 employees)
('Paul Martinez', 'Sales', 72000.00, 1, '2020-01-20', '6780', '555-0201', 'paul.m@company.com'),
('Quinn Rodriguez', 'Sales', 75000.00, 2, '2019-06-15', '7891', '555-0202', 'quinn.r@company.com'),
('Rachel Hernandez', 'Sales', 95000.00, 3, '2018-03-08', '8902', '555-0203', 'rachel.h@company.com'),
('Sam Lopez', 'Sales', 70000.00, 1, '2021-01-12', '9013', '555-0204', 'sam.l@company.com'),
('Tina Gonzalez', 'Sales', 78000.00, 2, '2020-07-25', '0124', '555-0205', 'tina.g@company.com'),
('Uma Wilson', 'Sales', 73000.00, 1, '2020-11-05', '1236', '555-0206', 'uma.w@company.com'),
('Victor Clark', 'Sales', 88000.00, 2, '2019-04-18', '2347', '555-0207', 'victor.c@company.com'),
('Wendy Lewis', 'Sales', 92000.00, 3, '2018-09-22', '3458', '555-0208', 'wendy.l@company.com'),
('Xavier Hall', 'Sales', 71000.00, 1, '2021-05-14', '4569', '555-0209', 'xavier.h@company.com'),
('Yara Allen', 'Sales', 76000.00, 2, '2020-02-28', '5680', '555-0210', 'yara.a@company.com'),
('Zack Young', 'Sales', 74000.00, 1, '2020-10-10', '6781', '555-0211', 'zack.y@company.com'),
('Amy King', 'Sales', 85000.00, 2, '2019-07-30', '7892', '555-0212', 'amy.k@company.com'),
('Ben Wright', 'Sales', 90000.00, 3, '2018-12-15', '8903', '555-0213', 'ben.w@company.com'),
('Cara Scott', 'Sales', 72500.00, 1, '2021-03-20', '9014', '555-0214', 'cara.s@company.com'),
('Dan Green', 'Sales', 77000.00, 2, '2020-08-08', '0125', '555-0215', 'dan.g@company.com'),

-- Marketing (10 employees)
('Emma Adams', 'Marketing', 68000.00, 1, '2020-03-15', '1237', '555-0301', 'emma.a@company.com'),
('Felix Baker', 'Marketing', 72000.00, 2, '2019-09-20', '2348', '555-0302', 'felix.b@company.com'),
('Gina Carter', 'Marketing', 82000.00, 3, '2018-05-10', '3459', '555-0303', 'gina.c@company.com'),
('Hugo Mitchell', 'Marketing', 70000.00, 1, '2020-12-01', '4570', '555-0304', 'hugo.m@company.com'),
('Iris Perez', 'Marketing', 75000.00, 2, '2019-11-18', '5681', '555-0305', 'iris.p@company.com'),
('Jake Roberts', 'Marketing', 69000.00, 1, '2021-02-22', '6782', '555-0306', 'jake.r@company.com'),
('Kira Turner', 'Marketing', 78000.00, 2, '2020-06-30', '7893', '555-0307', 'kira.t@company.com'),
('Leo Phillips', 'Marketing', 85000.00, 3, '2018-10-12', '8904', '555-0308', 'leo.p@company.com'),
('Mia Campbell', 'Marketing', 71000.00, 1, '2020-09-15', '9015', '555-0309', 'mia.c@company.com'),
('Nate Parker', 'Marketing', 76000.00, 2, '2019-12-28', '0126', '555-0310', 'nate.p@company.com'),

-- HR (8 employees)
('Oscar Evans', 'HR', 65000.00, 2, '2019-02-14', '1238', '555-0401', 'oscar.e@company.com'),
('Pam Edwards', 'HR', 70000.00, 2, '2018-08-20', '2349', '555-0402', 'pam.e@company.com'),
('Quin Collins', 'HR', 85000.00, 3, '2017-11-05', '3460', '555-0403', 'quin.c@company.com'),
('Rita Stewart', 'HR', 67000.00, 2, '2020-04-12', '4571', '555-0404', 'rita.s@company.com'),
('Sean Morris', 'HR', 72000.00, 2, '2019-10-08', '5682', '555-0405', 'sean.m@company.com'),
('Tara Rogers', 'HR', 66000.00, 1, '2021-01-25', '6783', '555-0406', 'tara.r@company.com'),
('Umar Reed', 'HR', 75000.00, 2, '2019-05-18', '7894', '555-0407', 'umar.r@company.com'),
('Vera Cook', 'HR', 80000.00, 3, '2018-09-30', '8905', '555-0408', 'vera.c@company.com'),

-- Finance (7 employees)
('Wade Morgan', 'Finance', 78000.00, 2, '2019-03-10', '9016', '555-0501', 'wade.m@company.com'),
('Xena Bell', 'Finance', 82000.00, 2, '2018-07-22', '0127', '555-0502', 'xena.b@company.com'),
('Yale Murphy', 'Finance', 95000.00, 3, '2017-12-15', '1239', '555-0503', 'yale.m@company.com'),
('Zoe Bailey', 'Finance', 76000.00, 2, '2020-02-08', '2350', '555-0504', 'zoe.b@company.com'),
('Adam Rivera', 'Finance', 80000.00, 2, '2019-08-14', '3461', '555-0505', 'adam.r@company.com'),
('Beth Cooper', 'Finance', 77000.00, 1, '2020-11-20', '4572', '555-0506', 'beth.c@company.com'),
('Carl Richardson', 'Finance', 88000.00, 3, '2018-04-05', '5683', '555-0507', 'carl.r@company.com'),

-- Operations (5 employees)
('Dana Cox', 'Operations', 72000.00, 2, '2019-06-28', '6784', '555-0601', 'dana.c@company.com'),
('Ethan Howard', 'Operations', 75000.00, 2, '2019-01-10', '7895', '555-0602', 'ethan.h@company.com'),
('Faye Ward', 'Operations', 68000.00, 1, '2020-09-22', '8906', '555-0603', 'faye.w@company.com'),
('Greg Torres', 'Operations', 80000.00, 3, '2018-03-18', '9017', '555-0604', 'greg.t@company.com'),
('Holly Peterson', 'Operations', 73000.00, 2, '2020-05-30', '0128', '555-0605', 'holly.p@company.com');

-- Update department managers
UPDATE departments SET manager_id = (SELECT employee_id FROM employees WHERE name = 'Grace Lee') WHERE dept_name = 'Engineering';
UPDATE departments SET manager_id = (SELECT employee_id FROM employees WHERE name = 'Rachel Hernandez') WHERE dept_name = 'Sales';
UPDATE departments SET manager_id = (SELECT employee_id FROM employees WHERE name = 'Gina Carter') WHERE dept_name = 'Marketing';
UPDATE departments SET manager_id = (SELECT employee_id FROM employees WHERE name = 'Quin Collins') WHERE dept_name = 'HR';
UPDATE departments SET manager_id = (SELECT employee_id FROM employees WHERE name = 'Yale Murphy') WHERE dept_name = 'Finance';
UPDATE departments SET manager_id = (SELECT employee_id FROM employees WHERE name = 'Greg Torres') WHERE dept_name = 'Operations';

-- ============================================================================
-- SEED SALES DATA (200+ records)
-- ============================================================================

INSERT INTO sales (employee_id, amount, sale_date, product_category, region)
SELECT 
    e.employee_id,
    (random() * 50000 + 5000)::DECIMAL(10,2),
    DATE '2023-01-01' + (random() * 700)::INT,
    CASE (random() * 4)::INT
        WHEN 0 THEN 'Software'
        WHEN 1 THEN 'Hardware'
        WHEN 2 THEN 'Services'
        ELSE 'Consulting'
    END,
    CASE (random() * 4)::INT
        WHEN 0 THEN 'North'
        WHEN 1 THEN 'South'
        WHEN 2 THEN 'East'
        ELSE 'West'
    END
FROM employees e
WHERE e.department IN ('Sales', 'Engineering')
CROSS JOIN generate_series(1, 4);


-- SEED POLYINSTANTIATION DATA


--copy all real employee data (visible at their actual clearance level)
INSERT INTO employees_poly (employee_id, name, department, salary, clearance_level, visible_at_level, hire_date, is_cover_story)
SELECT 
    employee_id,
    name,
    department,
    salary,
    clearance_level,
    clearance_level,  -- Real data visible at actual clearance level
    hire_date,
    FALSE
FROM employees;

-- Now add cover stories for high-clearance employees (visible at lower levels)
-- For clearance level 3 employees, add fake data visible at level 1 and 2
INSERT INTO employees_poly (employee_id, name, department, salary, clearance_level, visible_at_level, hire_date, is_cover_story)
SELECT 
    employee_id,
    name,
    department,
    salary * 0.5,  -- Cover story: show much lower salary
    clearance_level,
    1,  -- Visible at level 1
    hire_date,
    TRUE
FROM employees
WHERE clearance_level = 3;

INSERT INTO employees_poly (employee_id, name, department, salary, clearance_level, visible_at_level, hire_date, is_cover_story)
SELECT 
    employee_id,
    name,
    department,
    salary * 0.7,  -- Cover story: show somewhat lower salary
    clearance_level,
    2,  -- Visible at level 2
    hire_date,
    TRUE
FROM employees
WHERE clearance_level = 3;

-- For clearance level 2 employees, add fake data visible at level 1
INSERT INTO employees_poly (employee_id, name, department, salary, clearance_level, visible_at_level, hire_date, is_cover_story)
SELECT 
    employee_id,
    name,
    department,
    salary * 0.8,  -- Cover story: show lower salary
    clearance_level,
    1,  -- Visible at level 1
    hire_date,
    TRUE
FROM employees
WHERE clearance_level = 2;