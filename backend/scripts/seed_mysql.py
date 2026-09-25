"""
Deterministic MySQL Database Initialization & Seeding Script for FreshMart
Populates company_analytics with enterprise-grade connected records across 7 business domains:
- HRMS: Departments (10), Employees (~500), Salaries (~500)
- CRM: Customers (~320), Leads (~550), Customer Interactions (~1200)
- Products & Inventory: Products (~220), Inventory (~220)
- Purchasing: Suppliers (~40), Purchase Orders (~550), Purchase Order Items (~1400+)
- Sales: Sales Orders (~2400), Sales Order Items (~5500+)
- Finance: Department Expenses (~360), Monthly Financials (21 months with August profit drop)

Ensures 100% deterministic seeding using fixed seed (seed=42).
"""

import os
import sys
import random
from datetime import date, datetime, timedelta
from decimal import Decimal

# Add backend directory to sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import pymysql
from app.core.config import settings

def run_seed():
    # Set deterministic random seed
    random.seed(42)

    print("\n============================================================")
    print("  INITIALIZING & SEEDING FRESHMART BUSINESS DATABASE (MySQL)")
    print(f"  Host: {settings.MYSQL_HOST}:{settings.MYSQL_PORT} | DB: {settings.MYSQL_DB}")
    print("============================================================\n")

    # 1. Connect to MySQL server
    conn = pymysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        autocommit=True
    )
    cursor = conn.cursor()

    # 2. Ensure database exists and reset tables
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cursor.execute(f"USE {settings.MYSQL_DB};")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    tables = [
        "sales_order_items", "sales_orders", "purchase_order_items", "purchase_orders",
        "customer_interactions", "leads", "customers", "inventory", "products",
        "suppliers", "salaries", "employees", "expenses", "company_financials", "departments"
    ]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table};")
    cursor.execute("DROP VIEW IF EXISTS interactions;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    print("[1/9] Cleaned and dropped any existing tables for clean schema re-creation.")

    # 3. Read and execute mysql_schema.sql
    schema_path = os.path.join(BACKEND_DIR, "app", "db", "mysql_schema.sql")
    print(f"[2/9] Executing schema DDL from: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    for statement in schema_sql.split(";"):
        stmt = statement.strip()
        if stmt:
            cursor.execute(stmt)
    cursor.execute(f"USE {settings.MYSQL_DB};")


    # --------------------------------------------------------------------------
    # 3. Seed Departments (10 Enterprise Departments)
    # --------------------------------------------------------------------------
    print("[3/9] Seeding 10 Departments...")
    departments = [
        ("D01", "Sales & Marketing", "Tower A, 4th Floor", 18000000.00),
        ("D02", "Human Resources", "Tower B, 2nd Floor", 6500000.00),
        ("D03", "Finance & Accounts", "Tower A, 5th Floor", 8000000.00),
        ("D04", "Engineering & IT", "Tower C, 3rd Floor", 32000000.00),
        ("D05", "Inventory & Logistics", "Central Distribution Hub 1", 16000000.00),
        ("D06", "Executive Leadership", "Tower A, 7th Floor", 12000000.00),
        ("D07", "Retail Store Operations", "Regional Hub North", 22000000.00),
        ("D08", "Procurement & Sourcing", "Central Distribution Hub 2", 14000000.00),
        ("D09", "Quality Assurance & Food Safety", "Testing Lab 1", 7500000.00),
        ("D10", "Customer Relations & CRM", "Tower B, 3rd Floor", 9000000.00),
    ]
    cursor.executemany(
        "INSERT INTO departments (dept_id, dept_name, location, budget) VALUES (%s, %s, %s, %s)",
        departments
    )

    # --------------------------------------------------------------------------
    # 4. Seed Employees & Salaries (~500 Employees)
    # --------------------------------------------------------------------------
    print("[4/9] Generating and seeding 500 Employees & Salaries...")

    first_names_pool = [
        "Aarav", "Aditi", "Ajay", "Alok", "Amit", "Ananya", "Anil", "Anita", "Ankit", "Ansh",
        "Arjun", "Arun", "Ashok", "Bhavna", "Chetan", "Deepa", "Deepak", "Dev", "Divya", "Gaurav",
        "Geeta", "Harish", "Isha", "Jay", "Jyoti", "Karan", "Karthik", "Kavita", "Kishore", "Kunal",
        "Madhav", "Manish", "Meera", "Mohan", "Mukesh", "Naveen", "Neha", "Nikhil", "Nisha", "Nitin",
        "Pankaj", "Pooja", "Pradeep", "Prakash", "Pranav", "Prateek", "Priya", "Rahul", "Raj", "Rajesh",
        "Rakesh", "Ramesh", "Ravi", "Ritu", "Rohan", "Rohit", "Sachin", "Sameer", "Sanjay", "Saurabh",
        "Shalini", "Shashi", "Shikha", "Shiv", "Shreya", "Siddharth", "Sneha", "Sonam", "Suresh", "Swati",
        "Tanvi", "Tarun", "Umesh", "Varun", "Vikas", "Vikram", "Vinay", "Vishal", "Vivek", "Yash"
    ]

    last_names_pool = [
        "Agarwal", "Bansal", "Bhatia", "Chauhan", "Chopra", "Das", "Desai", "Dutta", "Gandhi", "Ghosh",
        "Gowda", "Gupta", "Iyer", "Jain", "Jha", "Joshi", "Kapoor", "Kashyap", "Kaul", "Khan",
        "Kulkarni", "Kumar", "Malhotra", "Mehta", "Mishra", "Mukherjee", "Nair", "Pandey", "Patel", "Patil",
        "Pillai", "Prasad", "Purohit", "Raj", "Rao", "Reddy", "Roy", "Sahay", "Saxena", "Sen",
        "Shah", "Sharma", "Shetty", "Singh", "Singhania", "Soni", "Srivastava", "Suri", "Trivedi", "Varma",
        "Venkatesh", "Verma", "Yadav"
    ]

    # Predefined Key Executive & Department Managers (E001 - E010)
    # E006 is CEO (Vikram Malhotra). E001-E005, E007-E010 report to E006.
    key_executives = [
        # (emp_id, first, last, email, phone, dept_id, title, hire_date, dob, status, exp, manager_id, base_salary, bonus)
        ("E006", "Vikram", "Malhotra", "vikram.malhotra@freshmart.local", "+91-9811000001", "D06", "Chief Executive Officer", "2020-01-15", "1978-04-12", "Active", 22, None, 350000.00, 100000.00),
        ("E001", "Arun", "Kumar", "arun.kumar@freshmart.local", "+91-9811000002", "D01", "Sales Manager", "2021-03-10", "1984-06-25", "Active", 16, "E006", 125000.00, 25000.00),
        ("E002", "Priya", "Sharma", "priya.sharma@freshmart.local", "+91-9811000003", "D02", "HR Manager", "2021-04-12", "1986-09-18", "Active", 14, "E006", 110000.00, 15000.00),
        ("E003", "Rahul", "Kumar", "rahul.kumar@freshmart.local", "+91-9811000004", "D03", "Finance Manager", "2021-02-01", "1983-11-05", "Active", 17, "E006", 130000.00, 20000.00),
        ("E004", "Sneha", "Iyer", "sneha.iyer@freshmart.local", "+91-9811000005", "D04", "Engineering Director", "2021-05-20", "1982-03-14", "Active", 18, "E006", 180000.00, 30000.00),
        ("E005", "Karthik", "Raj", "karthik.raj@freshmart.local", "+91-9811000006", "D05", "Inventory Manager", "2021-06-15", "1985-08-22", "Active", 15, "E006", 105000.00, 15000.00),
        ("E007", "Anita", "Desai", "anita.desai@freshmart.local", "+91-9811000007", "D05", "ERP Operations Manager", "2021-07-01", "1987-12-30", "Active", 13, "E006", 120000.00, 18000.00),
        ("E008", "Rohan", "Mehta", "rohan.mehta@freshmart.local", "+91-9811000008", "D07", "Retail Store Operations Manager", "2021-08-10", "1986-02-17", "Active", 14, "E006", 115000.00, 16000.00),
        ("E009", "Kavita", "Reddy", "kavita.reddy@freshmart.local", "+91-9811000009", "D08", "Procurement & Sourcing Manager", "2021-09-01", "1988-07-09", "Active", 12, "E006", 115000.00, 15000.00),
        ("E010", "Suresh", "Gowda", "suresh.gowda@freshmart.local", "+91-9811000010", "D09", "Quality Assurance & Food Safety Manager", "2021-10-15", "1984-01-20", "Active", 16, "E006", 110000.00, 14000.00),
        ("E011", "Meera", "Nair", "meera.nair@freshmart.local", "+91-9811000011", "D10", "Customer Relations Manager", "2021-11-01", "1989-05-11", "Active", 11, "E006", 100000.00, 12000.00),
    ]

    dept_titles = {
        "D01": ["Senior Sales Representative", "Enterprise Account Executive", "Regional Sales Associate", "Digital Marketing Specialist", "Field Sales Officer"],
        "D02": ["HR Talent Specialist", "Recruiter", "Employee Relations Lead", "Payroll Specialist", "Training & Onboarding Coordinator"],
        "D03": ["Senior Financial Analyst", "Accounts Payable Officer", "Audit Specialist", "Staff Accountant", "Financial Operations Analyst"],
        "D04": ["Senior Full-Stack Engineer", "DevOps Engineer", "Backend Python Developer", "Database Administrator", "QA Automation Engineer"],
        "D05": ["Warehouse Operations Supervisor", "Inventory Controller", "Cold-Chain Logistics Specialist", "Fulfillment Associate", "Dispatch Coordinator"],
        "D06": ["Executive Assistant to CEO", "Chief of Staff", "Strategy & Planning Analyst"],
        "D07": ["Supermarket Store Supervisor", "Fresh Section Lead", "Merchandising Specialist", "Inventory Stockist", "Customer Service Desk Lead"],
        "D08": ["Strategic Sourcing Specialist", "Vendor Relations Executive", "Agri-Procurement Officer", "Contract Negotiator", "Supply Chain Planner"],
        "D09": ["Food Safety Compliance Inspector", "HACCP Quality Officer", "Laboratory Technician", "Quality Audit Specialist", "Perishables Inspection Lead"],
        "D10": ["Customer Support Lead", "Client Retention Specialist", "Omnichannel CRM Agent", "Customer Service Representative", "Escalations Specialist"],
    }

    dept_mgr_map = {
        "D01": "E001",
        "D02": "E002",
        "D03": "E003",
        "D04": "E004",
        "D05": "E005",
        "D06": "E006",
        "D07": "E008",
        "D08": "E009",
        "D09": "E010",
        "D10": "E011",
    }

    employees_data = []
    salaries_data = []

    # Insert pre-defined managers first
    for emp in key_executives:
        employees_data.append(emp[:12])
        salaries_data.append((emp[0], emp[12], emp[13], "2026-01-01", "Paid", "Monthly"))

    # Generate remaining employees E012 to E500
    used_emails = set(e[3] for e in employees_data)
    dept_distribution = (
        ["D01"] * 85 +   # Sales & Marketing (85)
        ["D02"] * 30 +   # HR (30)
        ["D03"] * 40 +   # Finance (40)
        ["D04"] * 65 +   # IT & Eng (65)
        ["D05"] * 80 +   # Logistics (80)
        ["D06"] * 5 +    # Exec Staff (5)
        ["D07"] * 95 +   # Store Ops (95)
        ["D08"] * 35 +   # Procurement (35)
        ["D09"] * 25 +   # QA (25)
        ["D10"] * 29     # CRM (29)
    )  # Total 489 + 11 = 500

    random.shuffle(dept_distribution)

    for i in range(12, 501):
        emp_id = f"E{i:03d}"
        first_name = random.choice(first_names_pool)
        last_name = random.choice(last_names_pool)
        
        email_cand = f"{first_name.lower()}.{last_name.lower()}@freshmart.local"
        suffix = 1
        while email_cand in used_emails:
            email_cand = f"{first_name.lower()}.{last_name.lower()}{suffix}@freshmart.local"
            suffix += 1
        used_emails.add(email_cand)

        dept_id = dept_distribution[i - 12]
        title = random.choice(dept_titles[dept_id])
        manager_id = dept_mgr_map[dept_id]

        hire_year = random.randint(2021, 2025)
        hire_month = random.randint(1, 12)
        hire_day = random.randint(1, 28)
        hire_date = f"{hire_year}-{hire_month:02d}-{hire_day:02d}"

        birth_year = random.randint(1985, 2002)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        dob = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"

        exp = max(1, 2026 - birth_year - 22)
        phone = f"+91-98{random.randint(10000000, 99999999)}"
        status = "Active" if random.random() < 0.94 else random.choice(["On Leave", "Terminated"])

        # Base salary realistic by department & experience
        base_salary = round(35000.00 + (exp * 3200.00) + (random.randint(0, 15) * 1000.00), 2)
        bonus = round(base_salary * random.choice([0.05, 0.08, 0.10, 0.12]), 2) if status == "Active" else 0.00

        employees_data.append((emp_id, first_name, last_name, email_cand, phone, dept_id, title, hire_date, dob, status, exp, manager_id))
        salaries_data.append((emp_id, base_salary, bonus, "2026-01-01", "Paid", "Monthly"))

    cursor.executemany(
        """INSERT INTO employees (employee_id, first_name, last_name, email, phone, department_id, job_title, hire_date, date_of_birth, status, experience_years, manager_id)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        employees_data
    )

    cursor.executemany(
        """INSERT INTO salaries (employee_id, base_salary, bonus, effective_date, payment_status, salary_period)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        salaries_data
    )

    # --------------------------------------------------------------------------
    # 5. Seed CRM: Customers (~320), Leads (~550), Customer Interactions (~1200)
    # --------------------------------------------------------------------------
    print("[5/9] Seeding CRM (320 Customers, 550 Leads, 1200 Customer Interactions)...")

    regions = ["North", "South", "East", "West", "Central"]
    cities_by_region = {
        "North": ["New Delhi", "Gurugram", "Noida", "Chandigarh", "Jaipur", "Lucknow"],
        "South": ["Bengaluru", "Chennai", "Hyderabad", "Kochi", "Coimbatore", "Mysuru"],
        "East": ["Kolkata", "Bhubaneswar", "Patna", "Ranchi", "Guwahati"],
        "West": ["Mumbai", "Pune", "Ahmedabad", "Surat", "Vadodara", "Nagpur"],
        "Central": ["Bhopal", "Indore", "Raipur", "Gwalior", "Jabalpur"]
    }

    industries = [
        "Supermarket Retail Chain", "Hotel & Luxury Resorts", "Fine Dining Restaurants",
        "Corporate Food Services", "Hospitality & Catering", "Organic Grocers",
        "Educational Institutions", "E-Grocery Platform", "Wholesale Food Distribution"
    ]

    company_prefixes = [
        "GreenLeaf", "Sunrise", "Royal", "Apex", "Heritage", "Metro", "Prime", "Organic Oasis",
        "Grand", "Bliss", "Golden Harvest", "PurePantry", "Urban Kitchen", "Elite Foods",
        "NatureCrest", "FarmToFork", "DailyFresh", "Evergreen", "KitchenCraft", "BlueSky"
    ]

    company_suffixes = [
        "Enterprises", "Retail Corp", "Hospitality Ltd", "Supermarkets", "Foods & Beverages",
        "Gourmet Mart", "Food Services", "Boutique Stays", "Organics", "Supply Chain Ltd"
    ]

    customers_data = []
    used_cust_emails = set()

    for c_idx in range(1, 321):
        cust_id = f"C{c_idx:03d}"
        c_name = f"{random.choice(company_prefixes)} {random.choice(company_suffixes)} {c_idx}"
        contact_first = random.choice(first_names_pool)
        contact_last = random.choice(last_names_pool)
        contact_person = f"{contact_first} {contact_last}"
        reg = random.choice(regions)
        city = random.choice(cities_by_region[reg])
        ind = random.choice(industries)
        
        c_email = f"contact@{contact_first.lower()}{contact_last.lower()}{c_idx}.com"
        used_cust_emails.add(c_email)
        c_phone = f"+91-98{random.randint(10000000, 99999999)}"

        customers_data.append((cust_id, c_name, contact_person, c_email, c_phone, city, reg, ind))

    cursor.executemany(
        """INSERT INTO customers (customer_id, company_name, contact_person, email, phone, city, region, industry)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        customers_data
    )

    # Filter Sales Representatives for CRM assignments
    sales_reps = [e[0] for e in employees_data if e[5] == "D01" and "Sales" in e[6] or e[0] == "E001"]

    lead_sources = ["Website", "Referral", "Trade Show", "Inbound Call", "Social Media"]
    lead_statuses = ["New", "Contacted", "Qualified", "Lost", "Converted"]

    leads_data = []
    for l_idx in range(1, 551):
        lead_id = f"L{l_idx:03d}"
        lead_name = f"{random.choice(company_prefixes)} Prospect {l_idx}"
        comp_name = f"{random.choice(company_prefixes)} Foods Group {l_idx}"
        src = random.choice(lead_sources)
        status = random.choice(lead_statuses)
        est_val = round(Decimal(random.randint(50000, 2500000)), 2)
        assigned_rep = random.choice(sales_reps)
        
        # If converted, assign to a valid customer ID
        conv_cust_id = f"C{random.randint(1, 320):03d}" if status == "Converted" else None

        leads_data.append((lead_id, lead_name, comp_name, src, status, est_val, assigned_rep, conv_cust_id))

    cursor.executemany(
        """INSERT INTO leads (lead_id, lead_name, company_name, source, status, estimated_value, assigned_employee_id, converted_customer_id)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        leads_data
    )

    # Customer Interactions (1200 records)
    interaction_types = ["Call", "Meeting", "Email", "Support Ticket"]
    interaction_notes = [
        "Quarterly wholesale pricing and rebate discussion. Client requested 15% bulk discount.",
        "Inquired about cold-chain organic produce delivery schedule for weekend banquet.",
        "Reported delivery lead time extension during August monsoon transit rerouting.",
        "Resolved billing discrepancy regarding carton handling fee on dairy shipment.",
        "Discussed upcoming festive seasonal order for dry fruits, confectionery, and gift baskets.",
        "Customer commended prompt replacement of fragile produce batch.",
        "Negotiated long-term contract renewal for corporate cafeteria supply.",
        "Presented FreshMart premium organic farm-to-table catalog to purchasing executive.",
        "Routine check-in call regarding weekly inventory delivery cadence.",
        "Escalated perishable shelf-life inquiry to QA and food safety team."
    ]

    interactions_data = []
    start_date = datetime(2025, 1, 5)
    for i_idx in range(1, 1201):
        cust_id = f"C{random.randint(1, 320):03d}"
        emp_id = random.choice(sales_reps)
        i_type = random.choice(interaction_types)
        note = random.choice(interaction_notes)
        
        # Interspersed across 2025-2026
        dt = start_date + timedelta(days=random.randint(0, 620), hours=random.randint(8, 18), minutes=random.randint(0, 59))
        interactions_data.append((cust_id, emp_id, i_type, note, dt.strftime("%Y-%m-%d %H:%M:%S")))

    cursor.executemany(
        """INSERT INTO customer_interactions (customer_id, employee_id, interaction_type, notes, interaction_date)
           VALUES (%s, %s, %s, %s, %s)""",
        interactions_data
    )

    # --------------------------------------------------------------------------
    # 6. Seed Suppliers (~40), Products (~220), Inventory (~220)
    # --------------------------------------------------------------------------
    print("[6/9] Seeding 40 Suppliers, 220 Products, and 220 Inventory Records...")

    supplier_names = [
        ("S001", "Sahyadri Farmers Producer Co", "Suresh Patil", "sahyadri@agri.coop", "Nashik", "India", 4.85),
        ("S002", "Nilgiri Organic Tea & Herbs", "Arvind Nair", "contact@nilgiriorganics.in", "Ooty", "India", 4.70),
        ("S003", "Anand Dairy Producers Federation", "Mahesh Dave", "info@ananddairy.coop", "Anand", "India", 4.90),
        ("S004", "Punjab Golden Harvest Grains", "Harpreet Gill", "harpreet@goldenharvest.in", "Ludhiana", "India", 4.60),
        ("S005", "Malabar Spice Traders", "Biju Varghese", "biju@malabarspice.com", "Kochi", "India", 4.80),
        ("S006", "Himalayan Apple Orchards", "Rajinder Thakur", "orchards@himalayanfresh.in", "Shimla", "India", 4.75),
        ("S007", "Konkan Mango Growers Syndicate", "Prashant Joshi", "konkan@mangoes.org", "Ratnagiri", "India", 4.95),
        ("S008", "Krishna Valley Sugar & Jaggery", "Santosh Kulkarni", "info@krishnavalleysugar.com", "Kolhapur", "India", 4.40),
        ("S009", "Coastal Seafood Harvesters", "Denzil Fernandes", "denzil@coastalseafood.in", "Mangaluru", "India", 4.55),
        ("S010", "Dindigul Poultry & Farms", "M. Ramaswamy", "ramaswamy@dindigulfarms.com", "Dindigul", "India", 4.65),
    ]

    # Generate 30 more realistic suppliers
    for s_idx in range(11, 41):
        s_id = f"S{s_idx:03d}"
        s_name = f"{random.choice(company_prefixes)} Agro & Supplies {s_idx}"
        contact_person = f"{random.choice(first_names_pool)} {random.choice(last_names_pool)}"
        s_email = f"supply{s_idx}@vendorpartners.in"
        city = random.choice(["Bengaluru", "Pune", "Jaipur", "Surat", "Indore", "Nagpur", "Dehradun", "Karnal", "Salem", "Vijayawada"])
        rating = round(random.uniform(3.8, 4.95), 2)
        supplier_names.append((s_id, s_name, contact_person, s_email, city, "India", rating))

    suppliers_data = []
    for s in supplier_names:
        phone = f"+91-97{random.randint(10000000, 99999999)}"
        suppliers_data.append((s[0], s[1], s[2], s[3], phone, s[4], s[5], s[6]))

    cursor.executemany(
        """INSERT INTO suppliers (supplier_id, supplier_name, contact_person, email, phone, city, country, rating)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        suppliers_data
    )

    # 220 Catalog Products across 10 FreshMart grocery & retail categories
    categories = [
        "Fresh Produce", "Dairy & Eggs", "Bakery & Breads", "Beverages",
        "Packaged & Canned Foods", "Meat & Seafood", "Snacks & Confectionery",
        "Personal Care", "Household Essentials", "Organic & Health"
    ]

    catalog_templates = {
        "Fresh Produce": [
            ("Organic Alphonso Mangoes (1kg)", 350.00, 520.00),
            ("Farm Fresh Red Tomatoes (1kg)", 25.00, 48.00),
            ("Shimla Crisp Royal Apples (1kg)", 120.00, 195.00),
            ("Hydroponic Baby Spinach (250g)", 35.00, 65.00),
            ("Fresh Button Mushrooms (200g)", 42.00, 75.00),
            ("Cavendish Bananas (1 Dozen)", 38.00, 65.00),
            ("Fresh Hass Avocado Pack of 2", 140.00, 240.00),
            ("Organic Bell Peppers Tri-Color (500g)", 65.00, 115.00),
            ("Seedless Green Grapes (500g)", 55.00, 95.00),
            ("Fresh Broccoli Florets (500g)", 45.00, 85.00),
            ("Red Onions Premium (5kg)", 130.00, 210.00),
            ("Baby Potatoes (1kg)", 28.00, 50.00),
            ("Fresh Pomegranate Pearls (250g)", 70.00, 120.00),
            ("Sweet Corn Kernels (500g)", 35.00, 65.00),
            ("Fresh English Cucumber (1kg)", 30.00, 55.00),
        ],
        "Dairy & Eggs": [
            ("Pasteurized Farm Fresh Milk 1L", 48.00, 68.00),
            ("Fresh Malai Paneer 500g", 145.00, 220.00),
            ("Artisanal Greek Yogurt Plain 400g", 90.00, 150.00),
            ("Organic Free-Range Brown Eggs (Pack of 12)", 95.00, 155.00),
            ("Salted Table Butter 500g", 180.00, 275.00),
            ("A2 Cow Desi Ghee 500ml", 420.00, 650.00),
            ("Cheddar Cheese Block 250g", 130.00, 215.00),
            ("Fresh Whipping Cream 250ml", 65.00, 105.00),
            ("Probiotic Buttermilk 1L", 35.00, 55.00),
            ("Mozzarella Pizza Cheese 400g", 160.00, 260.00),
        ],
        "Bakery & Breads": [
            ("Artisan Sourdough Boule 400g", 85.00, 145.00),
            ("Whole Wheat Multigrain Bread 400g", 40.00, 68.00),
            ("French Butter Croissants (Pack of 4)", 110.00, 185.00),
            ("Sesame Seed Bagels (Pack of 4)", 75.00, 130.00),
            ("Garlic Herb Bread Loaf", 45.00, 80.00),
            ("Classic Vanilla Sponge Cake 500g", 220.00, 380.00),
            ("Multigrain Pav / Buns (Pack of 6)", 28.00, 50.00),
            ("Gluten-Free Almond Flour Bread", 140.00, 235.00),
        ],
        "Beverages": [
            ("Cold-Pressed Pure Valencia Orange Juice 1L", 110.00, 185.00),
            ("Roasted Arabica Whole Coffee Beans 500g", 320.00, 520.00),
            ("Darjeeling First Flush Green Tea 100 Tea Bags", 180.00, 310.00),
            ("Sparkling Natural Mineral Water 750ml", 55.00, 95.00),
            ("Alphonso Mango Nectar 1L", 65.00, 110.00),
            ("Organic Apple Cider Vinegar 500ml", 190.00, 320.00),
            ("Cold-Pressed Tender Coconut Water 200ml", 30.00, 50.00),
            ("Almond Milk Unsweetened 1L", 160.00, 260.00),
        ],
        "Packaged & Canned Foods": [
            ("Royal Aged Basmati Rice 5kg", 450.00, 695.00),
            ("Extra Virgin Spanish Olive Oil 1L", 650.00, 980.00),
            ("Organic Rolled Oats 1kg", 130.00, 220.00),
            ("Sona Masoori Raw Rice 10kg", 520.00, 780.00),
            ("Unpolished Toor Dal 1kg", 115.00, 175.00),
            ("Organic Moong Dal Yellow 1kg", 105.00, 160.00),
            ("Italian Whole Peeled Plum Tomatoes 800g", 110.00, 180.00),
            ("Penne Rigate Durum Wheat Pasta 500g", 75.00, 130.00),
        ],
        "Meat & Seafood": [
            ("Fresh Farm Chicken Breast Boneless 1kg", 180.00, 290.00),
            ("Premium Atlantic Salmon Fillet 500g", 650.00, 990.00),
            ("Tender Goat Mutton Curry Cut 1kg", 480.00, 720.00),
            ("Fresh Peeled & Deveined White Prawns 500g", 280.00, 440.00),
            ("Farm Fresh Chicken Drumsticks 1kg", 160.00, 260.00),
        ],
        "Snacks & Confectionery": [
            ("Roasted California Salted Almonds 500g", 360.00, 550.00),
            ("Belgian Dark Chocolate Bar 70% Cocoa 100g", 120.00, 195.00),
            ("Multigrain Fiber Digestive Biscuits 400g", 65.00, 110.00),
            ("Artisanal Roasted Salted Cashews 500g", 390.00, 590.00),
            ("Sea Salted Baked Pita Chips 150g", 55.00, 95.00),
        ],
        "Personal Care": [
            ("Herbal Neem & Aloe Vera Handwash 500ml", 85.00, 145.00),
            ("Organic Moisturizing Body Lotion 400ml", 175.00, 295.00),
            ("Eco Bamboo Charcoal Toothbrush (Pack of 4)", 90.00, 160.00),
            ("Gentle Coconut Milk Shampoo 300ml", 140.00, 240.00),
        ],
        "Household Essentials": [
            ("Bio-Degradable Citrus Dishwash Gel 1L", 110.00, 185.00),
            ("Natural Disinfectant Floor Cleaner 2L", 140.00, 230.00),
            ("Microfiber Cleaning Cloths (Pack of 5)", 80.00, 140.00),
            ("Aromatherapy Lavender Room Spray 250ml", 95.00, 165.00),
        ],
        "Organic & Health": [
            ("Cold-Pressed Virgin Coconut Oil 500ml", 180.00, 295.00),
            ("Raw Wild Forest Multifloral Honey 500g", 240.00, 390.00),
            ("Organic Raw Chia Seeds 250g", 95.00, 165.00),
            ("Royal White Quinoa Grain 1kg", 220.00, 360.00),
            ("Organic Flax Seeds 250g", 50.00, 90.00),
        ]
    }

    products_data = []
    p_counter = 1

    # Add all template items first
    for cat, items in catalog_templates.items():
        for name, cost, price in items:
            p_id = f"P{p_counter:03d}"
            reorder_lvl = random.choice([15, 20, 25, 30, 40])
            products_data.append((p_id, name, cat, round(Decimal(cost), 2), round(Decimal(price), 2), reorder_lvl, True))
            p_counter += 1

    # Expand up to 220 products
    qualifiers = ["Organic", "Farm-Fresh", "Gourmet", "Select", "Natural", "Artisanal", "Pure", "Export-Quality"]
    while p_counter <= 220:
        p_id = f"P{p_counter:03d}"
        cat = random.choice(categories)
        template_name, base_cost, base_price = random.choice(catalog_templates[cat])
        p_name = f"{random.choice(qualifiers)} {template_name.split('(')[0].strip()} Var-{p_counter}"
        cost = round(Decimal(base_cost * random.uniform(0.9, 1.2)), 2)
        price = round(Decimal(base_price * random.uniform(0.9, 1.25)), 2)
        reorder_lvl = random.choice([15, 20, 25, 30])
        products_data.append((p_id, p_name, cat, cost, price, reorder_lvl, True))
        p_counter += 1

    cursor.executemany(
        """INSERT INTO products (product_id, product_name, category, unit_cost, unit_price, reorder_level, is_active)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        products_data
    )

    # Seed Inventory (220 rows - exactly one per product)
    # Deliberately seed:
    # 1. Low stock products (e.g. P001, P003, P005, P012, P025)
    # 2. Out of stock products (e.g. P007, P018)
    # 3. Normal / high stock products
    warehouse_locations = [
        "Hub 1 - Rack A1 (Cold Room)", "Hub 1 - Rack A2 (Cold Room)",
        "Hub 1 - Rack B1 (Dry Storage)", "Hub 1 - Rack B2 (Dry Storage)",
        "Hub 2 - Rack C1 (Perishables)", "Hub 2 - Rack D1 (Ambient)",
        "Hub 2 - Rack E2 (Packaging & FMCG)", "Hub 3 - Rack F1 (Refrigerated)"
    ]

    inventory_data = []
    low_stock_pids = {"P001", "P003", "P005", "P012", "P025", "P034", "P048", "P062"}
    out_of_stock_pids = {"P007", "P018", "P055"}

    for p in products_data:
        p_id = p[0]
        reorder = p[5]
        loc = random.choice(warehouse_locations)
        
        if p_id in out_of_stock_pids:
            qty = 0
            res = 0
        elif p_id in low_stock_pids:
            qty = random.randint(2, max(3, reorder - 5))
            res = random.randint(1, 2)
        else:
            qty = random.randint(reorder + 15, reorder + 280)
            res = random.randint(2, 25)

        inventory_data.append((p_id, loc, qty, res))

    cursor.executemany(
        """INSERT INTO inventory (product_id, warehouse_location, quantity_on_hand, reserved_quantity)
           VALUES (%s, %s, %s, %s)""",
        inventory_data
    )

    # --------------------------------------------------------------------------
    # 7. Seed Purchase Orders (~550) & Purchase Order Items (~1400+)
    # --------------------------------------------------------------------------
    print("[7/9] Seeding 550 Purchase Orders & ~1400 Purchase Order Items...")

    supplier_ids = [s[0] for s in suppliers_data]
    po_data = []
    po_items_data = []

    po_start = date(2025, 1, 10)
    for po_idx in range(1, 551):
        po_id = f"PO-20{po_idx:04d}"
        s_id = random.choice(supplier_ids)
        
        # Distribute over 2025-2026
        po_date = po_start + timedelta(days=int((po_idx / 550.0) * 615))
        deliv_date = po_date + timedelta(days=random.randint(4, 14))

        # Items for this PO
        num_items = random.randint(2, 4)
        po_prods = random.sample(products_data, num_items)
        
        # Notice: In August 2026, component/produce prices rose!
        is_august_2026 = (po_date.year == 2026 and po_date.month == 8)
        cost_multiplier = 1.30 if is_august_2026 else 1.0

        po_total = Decimal("0.00")
        for prod in po_prods:
            p_id = prod[0]
            qty = random.randint(25, 200)
            unit_c = round(Decimal(float(prod[3]) * cost_multiplier), 2)
            subtot = round(Decimal(qty) * unit_c, 2)
            po_total += subtot
            po_items_data.append((po_id, p_id, qty, unit_c, subtot))

        status = "Received" if po_date <= date(2026, 9, 20) else "Submitted"
        po_data.append((po_id, s_id, po_date.strftime("%Y-%m-%d"), deliv_date.strftime("%Y-%m-%d"), po_total, status))

    cursor.executemany(
        """INSERT INTO purchase_orders (po_id, supplier_id, order_date, delivery_date, total_amount, status)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        po_data
    )

    cursor.executemany(
        """INSERT INTO purchase_order_items (po_id, product_id, quantity, unit_cost, subtotal)
           VALUES (%s, %s, %s, %s, %s)""",
        po_items_data
    )

    # --------------------------------------------------------------------------
    # 8. Seed Sales Orders (~2400) & Sales Order Items (~5500+)
    # --------------------------------------------------------------------------
    print("[8/9] Seeding 2400 Sales Orders & ~5500 Sales Order Items...")

    cust_ids = [c[0] for c in customers_data]
    cust_region_map = {c[0]: c[6] for c in customers_data}

    orders_data = []
    order_items_data = []

    so_start = date(2025, 1, 2)
    for so_idx in range(1, 2401):
        so_id = f"SO-20{so_idx:04d}"
        c_id = random.choice(cust_ids)
        sales_rep = random.choice(sales_reps)
        region = cust_region_map[c_id]

        # Spread over 21 months (Jan 2025 to Sep 2026)
        order_date = so_start + timedelta(days=int((so_idx / 2400.0) * 630))

        # Items
        num_items = random.randint(2, 4)
        chosen_prods = random.sample(products_data, num_items)
        
        # High sales products logic: P001, P003 are frequently bought!
        if random.random() < 0.25:
            p_special = products_data[0] if random.random() < 0.5 else products_data[2]
            if p_special not in chosen_prods:
                chosen_prods.append(p_special)

        order_total = Decimal("0.00")
        for prod in chosen_prods:
            p_id = prod[0]
            unit_p = prod[4]
            qty = random.randint(2, 20)
            subtot = round(Decimal(qty) * unit_p, 2)
            order_total += subtot
            order_items_data.append((so_id, p_id, qty, unit_p, subtot))

        status = "Completed" if order_date <= date(2026, 9, 20) else "Processing"
        orders_data.append((so_id, c_id, sales_rep, order_date.strftime("%Y-%m-%d"), order_total, region, status))

    cursor.executemany(
        """INSERT INTO sales_orders (order_id, customer_id, sales_rep_id, order_date, total_amount, region, status)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        orders_data
    )

    cursor.executemany(
        """INSERT INTO sales_order_items (order_id, product_id, quantity, unit_price, subtotal)
           VALUES (%s, %s, %s, %s, %s)""",
        order_items_data
    )

    # --------------------------------------------------------------------------
    # 9. Seed Finance: Expenses (~360) & Monthly Financials (21 Months)
    # --------------------------------------------------------------------------
    print("[9/9] Seeding 360 Department Expenses and 21 Monthly P&L Financials...")

    expense_categories = [
        "Salaries", "Rent & Utilities", "Marketing", "Software & IT",
        "Logistics & Shipping", "Emergency Shipping", "Procurement", "Maintenance", "Quality & Compliance"
    ]

    dept_ids = [d[0] for d in departments]
    expenses_data = []

    # Generate regular monthly expenses across all 21 months (Jan 2025 to Sep 2026)
    for yr in [2025, 2026]:
        max_m = 12 if yr == 2025 else 9
        for m in range(1, max_m + 1):
            # Fixed payroll expense per month
            payroll_date = f"{yr}-{m:02d}-28"
            expenses_data.append((
                "D02", "Salaries", round(Decimal(1650000.00 + random.randint(10000, 30000)), 2),
                payroll_date, f"{date(yr, m, 1).strftime('%B %Y')} Company-wide Workforce Payroll", "Bank Transfer"
            ))

            # Rent & Utilities for warehouses and hubs
            rent_date = f"{yr}-{m:02d}-05"
            expenses_data.append((
                "D05", "Rent & Utilities", round(Decimal(280000.00 + random.randint(5000, 15000)), 2),
                rent_date, "Distribution Hubs & Cold Storage Lease and Power", "Direct Debit"
            ))

            # Marketing
            mktg_date = f"{yr}-{m:02d}-12"
            expenses_data.append((
                "D01", "Marketing", round(Decimal(220000.00 + random.randint(10000, 40000)), 2),
                mktg_date, "Digital Omnichannel & Local Supermarket Promotions", "Credit Card"
            ))

            # Software & IT
            it_date = f"{yr}-{m:02d}-15"
            expenses_data.append((
                "D04", "Software & IT", round(Decimal(145000.00 + random.randint(2000, 8000)), 2),
                it_date, "Cloud ERP, Database Infrastructure & POS Software", "Direct Debit"
            ))

            # Standard Logistics & Shipping
            log_date = f"{yr}-{m:02d}-20"
            expenses_data.append((
                "D05", "Logistics & Shipping", round(Decimal(120000.00 + random.randint(5000, 20000)), 2),
                log_date, "Standard Fleet Transport & Regional Hub Transfers", "Bank Transfer"
            ))

            # QA & Safety
            qa_date = f"{yr}-{m:02d}-22"
            expenses_data.append((
                "D09", "Quality & Compliance", round(Decimal(65000.00 + random.randint(2000, 5000)), 2),
                qa_date, "Third-party Food Safety & FSSAI Lab Testing", "Bank Transfer"
            ))

            # Store operations maintenance
            maint_date = f"{yr}-{m:02d}-25"
            expenses_data.append((
                "D07", "Maintenance", round(Decimal(75000.00 + random.randint(3000, 8000)), 2),
                maint_date, "Refrigeration Chiller Maintenance & Routine Store Upkeep", "Bank Transfer"
            ))

    # CRITICAL ROOT-CAUSE ANOMALY: August 2026 Emergency Expenses
    # Emergency refrigerated air freight and urgent cold-chain rerouting
    expenses_data.append((
        "D05", "Emergency Shipping", 250000.00, "2026-08-14",
        "Emergency refrigerated air freight transport for fresh produce due to regional highway disruption and monsoon supplier delays", "Bank Transfer"
    ))
    expenses_data.append((
        "D05", "Emergency Shipping", 180000.00, "2026-08-22",
        "Expedited cold-chain re-routing and secondary fleet carrier surcharges", "Bank Transfer"
    ))
    expenses_data.append((
        "D08", "Procurement", 280000.00, "2026-08-18",
        "Emergency spot-market spot procurement premium for organic dairy and perishables shortfall", "Bank Transfer"
    ))

    # Add extra realistic operational expenses to reach ~360 total expenses
    for extra_idx in range(len(expenses_data), 365):
        d_id = random.choice(dept_ids)
        cat = random.choice(expense_categories)
        amt = round(Decimal(random.randint(15000, 95000)), 2)
        ex_year = random.choice([2025, 2026])
        ex_month = random.randint(1, 12 if ex_year == 2025 else 9)
        ex_day = random.randint(1, 28)
        ex_date = f"{ex_year}-{ex_month:02d}-{ex_day:02d}"
        desc = f"Departmental operational expense - {cat} (Batch {extra_idx})"
        pay_method = random.choice(["Bank Transfer", "Credit Card", "Direct Debit"])
        expenses_data.append((d_id, cat, amt, ex_date, desc, pay_method))

    cursor.executemany(
        """INSERT INTO expenses (department_id, category, amount, expense_date, description, payment_method)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        expenses_data
    )

    # Monthly Company Financials (21 months: Jan 2025 to Sep 2026)
    # Explicitly designed with strict mathematical consistency:
    # total_expenses = cogs + operating_expenses
    # net_profit = total_revenue - total_expenses
    # profit_margin_pct = (net_profit / total_revenue) * 100
    #
    # Highlighted Root-Cause Scenario:
    # July 2026: Revenue Rs. 4,200,000 | COGS Rs. 1,800,000 | OpEx Rs. 1,200,000 | Net Profit Rs. 1,200,000 (28.57% Margin)
    # August 2026: Revenue Rs. 3,850,000 | COGS Rs. 1,950,000 | OpEx Rs. 1,300,000 | Net Profit Rs. 600,000 (15.58% Margin)
    # -> Profit dropped by 50% from July to August due to spike in COGS (+Rs. 150k) and Emergency Shipping / OpEx (+Rs. 100k).
    month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    company_financials = [
        # 2025 Full Year
        (2025, 1, "January", 3200000.00, 2480000.00, 1400000.00, 1080000.00, 720000.00, 22.50, "FreshMart New Year promotional campaign kickoff"),
        (2025, 2, "February", 3350000.00, 2550000.00, 1450000.00, 1100000.00, 800000.00, 23.88, "Steady store footfall and wholesale partner additions"),
        (2025, 3, "March", 3600000.00, 2700000.00, 1550000.00, 1150000.00, 900000.00, 25.00, "Q1 financial target achieved with strong organic sales"),
        (2025, 4, "April", 3450000.00, 2620000.00, 1500000.00, 1120000.00, 830000.00, 24.06, "Early summer beverage and fresh produce demand"),
        (2025, 5, "May", 3700000.00, 2780000.00, 1600000.00, 1180000.00, 920000.00, 24.86, "Peak mango season wholesale distribution surge"),
        (2025, 6, "June", 3800000.00, 2850000.00, 1650000.00, 1200000.00, 950000.00, 25.00, "Mid-year corporate cafeteria contracts expanded"),
        (2025, 7, "July", 3750000.00, 2820000.00, 1630000.00, 1190000.00, 930000.00, 24.80, "Consistent operational profitability across all hubs"),
        (2025, 8, "August", 3650000.00, 2800000.00, 1620000.00, 1180000.00, 850000.00, 23.29, "Slight monsoon transport delays in West region"),
        (2025, 9, "September", 3900000.00, 2900000.00, 1680000.00, 1220000.00, 1000000.00, 25.64, "Pre-festive retail stocking by supermarket clients"),
        (2025, 10, "October", 4200000.00, 3100000.00, 1820000.00, 1280000.00, 1100000.00, 26.19, "Diwali festive gifting and dry fruit sales peak"),
        (2025, 11, "November", 4100000.00, 3050000.00, 1790000.00, 1260000.00, 1050000.00, 25.61, "Post-festive steady reorder volume"),
        (2025, 12, "December", 4350000.00, 3200000.00, 1880000.00, 1320000.00, 1150000.00, 26.44, "Year-end holiday feasts and luxury resort hospitality surge"),

        # 2026 (Jan to Sep)
        (2026, 1, "January", 3600000.00, 2750000.00, 1600000.00, 1150000.00, 850000.00, 23.61, "Strong start to Q1 with healthy margins"),
        (2026, 2, "February", 3750000.00, 2800000.00, 1650000.00, 1150000.00, 950000.00, 25.33, "Enterprise sales growth across North and West regions"),
        (2026, 3, "March", 4100000.00, 3000000.00, 1800000.00, 1200000.00, 1100000.00, 26.83, "Q1 financial target achieved ahead of schedule"),
        (2026, 4, "April", 3900000.00, 2900000.00, 1720000.00, 1180000.00, 1000000.00, 25.64, "Stable early Q2 run-rate and robust supply pipeline"),
        (2026, 5, "May", 4050000.00, 2980000.00, 1780000.00, 1200000.00, 1070000.00, 26.42, "Strong dairy and organic farm goods demand"),
        (2026, 6, "June", 4150000.00, 3050000.00, 1820000.00, 1230000.00, 1100000.00, 26.51, "Mid-year targets surpassed across all retail categories"),
        (2026, 7, "July", 4200000.00, 3000000.00, 1800000.00, 1200000.00, 1200000.00, 28.57, "Peak monthly profit for 2026 prior to monsoon disruption"),
        (2026, 8, "August", 3850000.00, 3250000.00, 1950000.00, 1300000.00, 600000.00, 15.58, "Profit dropped sharply: COGS escalated due to weather-induced procurement spot premiums; Operating expenses rose sharply from Rs. 430,000 in emergency refrigerated air freight and expedited cold-chain logistics"),
        (2026, 9, "September", 4500000.00, 3150000.00, 1900000.00, 1250000.00, 1350000.00, 30.00, "Strong rebound across all regions as supply chains stabilized"),
    ]

    cursor.executemany(
        """INSERT INTO company_financials (fiscal_year, month_num, month_name, total_revenue, total_expenses, cogs, operating_expenses, net_profit, profit_margin_pct, notes)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        company_financials
    )

    cursor.close()
    conn.close()

    print("\n============================================================")
    print("  FRESHMART DATABASE SUCCESSFULLY INITIALIZED AND SEEDED!")
    print(f"  - Departments        : {len(departments)}")
    print(f"  - Employees          : {len(employees_data)}")
    print(f"  - Salaries           : {len(salaries_data)}")
    print(f"  - Customers          : {len(customers_data)}")
    print(f"  - Leads              : {len(leads_data)}")
    print(f"  - Interactions       : {len(interactions_data)}")
    print(f"  - Suppliers          : {len(suppliers_data)}")
    print(f"  - Products           : {len(products_data)}")
    print(f"  - Inventory          : {len(inventory_data)}")
    print(f"  - Purchase Orders    : {len(po_data)}")
    print(f"  - PO Items           : {len(po_items_data)}")
    print(f"  - Sales Orders       : {len(orders_data)}")
    print(f"  - Sales Order Items  : {len(order_items_data)}")
    print(f"  - Expenses           : {len(expenses_data)}")
    print(f"  - Financial Records  : {len(company_financials)} (21 months)")
    print("============================================================\n")

if __name__ == "__main__":
    run_seed()
