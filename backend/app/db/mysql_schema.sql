-- ==============================================================================
-- FreshMart Business Database Schema: company_analytics (MySQL 8.0)
-- Covers 7 Enterprise Domains: HRMS, CRM, Sales, ERP/Inventory, Purchasing, Finance, Operations
-- Single Company Architecture: FreshMart
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS company_analytics 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE company_analytics;

-- ==============================================================================
-- DOMAIN 1: HRMS (Human Resource Management System)
-- ==============================================================================

-- 1. Departments
CREATE TABLE IF NOT EXISTS departments (
    dept_id VARCHAR(10) PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(100) NOT NULL,
    budget DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Employees (Business Workforce Records - NOT Application Logins)
CREATE TABLE IF NOT EXISTS employees (
    employee_id VARCHAR(10) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(25),
    department_id VARCHAR(10) NOT NULL,
    job_title VARCHAR(100) NOT NULL,
    hire_date DATE NOT NULL,
    date_of_birth DATE NULL,
    status ENUM('Active', 'On Leave', 'Terminated') DEFAULT 'Active',
    experience_years INT DEFAULT 0,
    manager_id VARCHAR(10) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(dept_id) ON DELETE RESTRICT,
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 3. Salaries (Separate business compensation ledger)
CREATE TABLE IF NOT EXISTS salaries (
    salary_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(10) NOT NULL,
    base_salary DECIMAL(12, 2) NOT NULL,
    bonus DECIMAL(12, 2) DEFAULT 0.00,
    effective_date DATE NOT NULL,
    payment_status ENUM('Paid', 'Pending', 'Processing') DEFAULT 'Paid',
    salary_period VARCHAR(20) DEFAULT 'Monthly',
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ==============================================================================
-- DOMAIN 2: CRM (Customer Relationship Management)
-- ==============================================================================

-- 4. Customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(120) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(25),
    city VARCHAR(80) NOT NULL,
    region ENUM('North', 'South', 'East', 'West', 'Central') NOT NULL,
    industry VARCHAR(80) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 5. Leads
CREATE TABLE IF NOT EXISTS leads (
    lead_id VARCHAR(10) PRIMARY KEY,
    lead_name VARCHAR(120) NOT NULL,
    company_name VARCHAR(120),
    source ENUM('Website', 'Referral', 'Trade Show', 'Inbound Call', 'Social Media') NOT NULL,
    status ENUM('New', 'Contacted', 'Qualified', 'Lost', 'Converted') DEFAULT 'New',
    estimated_value DECIMAL(12, 2) DEFAULT 0.00,
    assigned_employee_id VARCHAR(10),
    converted_customer_id VARCHAR(10) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_employee_id) REFERENCES employees(employee_id) ON DELETE SET NULL,
    FOREIGN KEY (converted_customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 6. Customer Interactions
CREATE TABLE IF NOT EXISTS customer_interactions (
    interaction_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(10) NOT NULL,
    employee_id VARCHAR(10) NOT NULL,
    interaction_type ENUM('Call', 'Meeting', 'Email', 'Support Ticket') NOT NULL,
    notes TEXT,
    interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Compatibility View for queries requesting 'interactions'
CREATE OR REPLACE VIEW interactions AS SELECT * FROM customer_interactions;

-- ==============================================================================
-- DOMAIN 3: ERP, Purchasing & Inventory (Products, Suppliers, Stock, Purchasing)
-- ==============================================================================

-- 7. Suppliers
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id VARCHAR(10) PRIMARY KEY,
    supplier_name VARCHAR(120) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(25),
    city VARCHAR(80) NOT NULL,
    country VARCHAR(80) DEFAULT 'India',
    rating DECIMAL(3, 2) DEFAULT 4.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 8. Products
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(10) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    unit_cost DECIMAL(10, 2) NOT NULL,   -- Procurement cost
    unit_price DECIMAL(10, 2) NOT NULL,  -- Selling price
    reorder_level INT NOT NULL DEFAULT 20,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 9. Purchase Orders (Procurement Header)
CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id VARCHAR(15) PRIMARY KEY,
    supplier_id VARCHAR(10) NOT NULL,
    order_date DATE NOT NULL,
    delivery_date DATE,
    total_amount DECIMAL(15, 2) NOT NULL,
    status ENUM('Draft', 'Submitted', 'Shipped', 'Received', 'Cancelled') DEFAULT 'Received',
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 10. Purchase Order Items (Line Items connecting PO to Products)
CREATE TABLE IF NOT EXISTS purchase_order_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    po_id VARCHAR(15) NOT NULL,
    product_id VARCHAR(10) NOT NULL,
    quantity INT NOT NULL,
    unit_cost DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(12, 2) NOT NULL,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 11. Inventory
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(10) NOT NULL UNIQUE,
    warehouse_location VARCHAR(80) NOT NULL,
    quantity_on_hand INT NOT NULL DEFAULT 0,
    reserved_quantity INT NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ==============================================================================
-- DOMAIN 4: Sales
-- ==============================================================================

-- 12. Sales Orders
CREATE TABLE IF NOT EXISTS sales_orders (
    order_id VARCHAR(15) PRIMARY KEY,
    customer_id VARCHAR(10) NOT NULL,
    sales_rep_id VARCHAR(10) NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(15, 2) NOT NULL,
    region ENUM('North', 'South', 'East', 'West', 'Central') NOT NULL,
    status ENUM('Pending', 'Processing', 'Completed', 'Cancelled') DEFAULT 'Completed',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT,
    FOREIGN KEY (sales_rep_id) REFERENCES employees(employee_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 13. Sales Order Items
CREATE TABLE IF NOT EXISTS sales_order_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(15) NOT NULL,
    product_id VARCHAR(10) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(12, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES sales_orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- ==============================================================================
-- DOMAIN 5: Finance (Expenses & Company Financials)
-- ==============================================================================

-- 14. Expenses
CREATE TABLE IF NOT EXISTS expenses (
    expense_id INT AUTO_INCREMENT PRIMARY KEY,
    department_id VARCHAR(10) NOT NULL,
    category VARCHAR(100) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    expense_date DATE NOT NULL,
    description VARCHAR(255),
    payment_method ENUM('Bank Transfer', 'Credit Card', 'Direct Debit') DEFAULT 'Bank Transfer',
    FOREIGN KEY (department_id) REFERENCES departments(dept_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 15. Company Financials (Monthly Summaries for Trend & Root-Cause Analytics)
CREATE TABLE IF NOT EXISTS company_financials (
    financial_id INT AUTO_INCREMENT PRIMARY KEY,
    fiscal_year INT NOT NULL,
    month_num INT NOT NULL,
    month_name VARCHAR(15) NOT NULL,
    total_revenue DECIMAL(15, 2) NOT NULL,
    total_expenses DECIMAL(15, 2) NOT NULL,
    cogs DECIMAL(15, 2) NOT NULL,            -- Cost of Goods Sold (Procurement)
    operating_expenses DECIMAL(15, 2) NOT NULL,
    net_profit DECIMAL(15, 2) NOT NULL,
    profit_margin_pct DECIMAL(5, 2) NOT NULL,
    notes TEXT,
    UNIQUE KEY uq_year_month (fiscal_year, month_num)
) ENGINE=InnoDB;
