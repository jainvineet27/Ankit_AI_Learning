-- PostgreSQL Schema & Table Setup DDL

CREATE SCHEMA IF NOT EXISTS sales;
CREATE SCHEMA IF NOT EXISTS departments;
CREATE SCHEMA IF NOT EXISTS courses;

-- 1. Sales Schema
CREATE TABLE IF NOT EXISTS sales.customers (
    customer_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sales.products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    unit_price NUMERIC(10, 2),
    stock_quantity INT
);

CREATE TABLE IF NOT EXISTS sales.orders (
    order_id INT PRIMARY KEY,
    customer_id INT REFERENCES sales.customers(customer_id),
    product_id INT REFERENCES sales.products(product_id),
    quantity INT,
    total_amount NUMERIC(10, 2),
    order_date TIMESTAMP,
    status VARCHAR(20)
);

-- 2. Departments Schema
CREATE TABLE IF NOT EXISTS departments.departments (
    department_id INT PRIMARY KEY,
    department_name VARCHAR(100),
    faculty VARCHAR(100),
    annual_budget NUMERIC(15, 2),
    building VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS departments.professors (
    professor_id INT PRIMARY KEY,
    department_id INT REFERENCES departments.departments(department_id),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    academic_rank VARCHAR(50),
    hire_date DATE
);

-- 3. Courses Schema
CREATE TABLE IF NOT EXISTS courses.courses (
    course_id INT PRIMARY KEY,
    department_id INT REFERENCES departments.departments(department_id),
    course_code VARCHAR(20) UNIQUE,
    course_title VARCHAR(150),
    credits INT
);

CREATE TABLE IF NOT EXISTS courses.course_offerings (
    offering_id INT PRIMARY KEY,
    course_id INT REFERENCES courses.courses(course_id),
    professor_id INT REFERENCES departments.professors(professor_id),
    semester VARCHAR(20),
    academic_year INT,
    classroom VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS courses.enrollments (
    enrollment_id INT PRIMARY KEY,
    offering_id INT REFERENCES courses.course_offerings(offering_id),
    student_id INT,
    grade VARCHAR(5),
    enrollment_date DATE
);
