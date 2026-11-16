import sqlite3
import json
import hashlib
import os
from datetime import datetime, timezone
from app.config import DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed, salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    check_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return check_hash == hashed

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'customer', -- admin, staff, customer
        full_name TEXT NOT NULL,
        phone TEXT,
        company TEXT,
        created_at TEXT NOT NULL
    )
    """)

    # Services Table (6 Verticals)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vertical TEXT NOT NULL,
        title TEXT NOT NULL,
        tagline TEXT NOT NULL,
        description TEXT NOT NULL,
        starting_price REAL NOT NULL,
        price_unit TEXT NOT NULL,
        features_json TEXT NOT NULL,
        icon TEXT NOT NULL,
        popular INTEGER DEFAULT 0,
        deliverables TEXT NOT NULL
    )
    """)

    # Hardware Products & Refurbished Inventory
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hardware_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL, -- workstation, gaming_pc, server, laptop, component
        condition TEXT NOT NULL, -- new, refurbished_grade_a, certified_renewed
        price REAL NOT NULL,
        original_price REAL NOT NULL,
        stock INTEGER NOT NULL DEFAULT 5,
        warranty_months INTEGER NOT NULL DEFAULT 12,
        specs_json TEXT NOT NULL,
        image_url TEXT NOT NULL,
        description TEXT NOT NULL
    )
    """)

    # Customer Leads (Captured by Ted or web forms)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        company TEXT,
        vertical_interest TEXT NOT NULL,
        requirements_summary TEXT NOT NULL,
        estimated_budget REAL,
        timeline TEXT,
        score TEXT NOT NULL DEFAULT 'warm', -- hot, warm, cold
        status TEXT NOT NULL DEFAULT 'new', -- new, contacted, in_review, proposal_ready, won, closed
        captured_by TEXT NOT NULL DEFAULT 'ted_ai',
        ai_confidence REAL DEFAULT 0.92,
        notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    # Quotations & Proposals (Requires Human Approval for sensitive business actions)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS proposals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quote_number TEXT UNIQUE NOT NULL,
        client_name TEXT NOT NULL,
        client_email TEXT NOT NULL,
        client_company TEXT,
        project_title TEXT NOT NULL,
        vertical TEXT NOT NULL,
        scope_details TEXT NOT NULL,
        itemized_costs_json TEXT NOT NULL,
        subtotal REAL NOT NULL,
        discount REAL DEFAULT 0.0,
        tax REAL NOT NULL,
        total_amount REAL NOT NULL,
        estimated_days INTEGER NOT NULL,
        ted_summary TEXT NOT NULL,
        human_status TEXT NOT NULL DEFAULT 'pending_approval', -- pending_approval, approved, rejected, sent_to_client, signed
        approved_by TEXT,
        approved_at TEXT,
        approval_notes TEXT,
        created_at TEXT NOT NULL
    )
    """)

    # Repair & IT Support Tickets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS repair_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_code TEXT UNIQUE NOT NULL,
        customer_name TEXT NOT NULL,
        customer_email TEXT NOT NULL,
        customer_phone TEXT,
        device_model TEXT NOT NULL,
        issue_type TEXT NOT NULL, -- hardware_diagnostic, no_power, screen_damage, os_corruption, malware, custom_loop
        symptoms TEXT NOT NULL,
        diagnosis_by_ted TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'normal', -- normal, high, critical
        status TEXT NOT NULL DEFAULT 'diagnostic_pending', -- diagnostic_pending, waiting_approval, in_repair, quality_testing, completed, dispatched
        estimated_cost REAL,
        technician_notes TEXT,
        human_approved_dispatch INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    # Green Technology & E-Waste Recycling Submissions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ewaste_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submission_code TEXT UNIQUE NOT NULL,
        client_name TEXT NOT NULL,
        client_email TEXT NOT NULL,
        client_phone TEXT,
        device_type TEXT NOT NULL, -- laptop, desktop, server_rack, smartphone, monitor, mixed_lot
        quantity INTEGER NOT NULL DEFAULT 1,
        device_condition TEXT NOT NULL, -- working, damaged, dead_motherboard, scrap
        calculated_tradein_value REAL NOT NULL,
        carbon_offset_kg REAL NOT NULL,
        recycling_type TEXT NOT NULL DEFAULT 'refurbish_reuse', -- refurbish_reuse, certified_metal_recovery, secure_data_wipe
        certificate_issued INTEGER DEFAULT 0,
        certificate_number TEXT,
        status TEXT NOT NULL DEFAULT 'submitted', -- submitted, dropoff_scheduled, inspected, payout_approved, completed
        human_approval_by TEXT,
        created_at TEXT NOT NULL
    )
    """)

    # Tutorials and Tech Education
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tutorials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT NOT NULL, -- python, ai_engineering, fullstack, cybersecurity, hardware_repair
        level TEXT NOT NULL, -- beginner, intermediate, advanced
        duration_minutes INTEGER NOT NULL,
        description TEXT NOT NULL,
        lesson_content_markdown TEXT NOT NULL,
        code_example TEXT NOT NULL,
        exercise_prompt TEXT NOT NULL,
        enrolled_count INTEGER DEFAULT 142
    )
    """)

    # Ted AI Interaction Records (Transcripts & Insights)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ted_interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        visitor_name TEXT DEFAULT 'Visitor',
        visitor_email TEXT,
        messages_count INTEGER DEFAULT 1,
        summary TEXT NOT NULL,
        sentiment TEXT NOT NULL DEFAULT 'inquiring', -- positive, neutral, inquiring, urgent
        primary_intent TEXT NOT NULL,
        action_items_json TEXT,
        transcript_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    # Marketing & Business Development Campaigns
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marketing_campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        target_audience TEXT NOT NULL,
        channel TEXT NOT NULL, -- email, linkedin, x_twitter, blog_post, press_release
        generated_content TEXT NOT NULL,
        call_to_action TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'draft', -- draft, reviewed, approved, published
        projected_reach INTEGER DEFAULT 2500,
        created_at TEXT NOT NULL
    )
    """)

    # System Settings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        description TEXT
    )
    """)

    conn.commit()
    seed_data_if_needed(conn)
    conn.close()

def seed_data_if_needed(conn):
    cursor = conn.cursor()

    # Check if users exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        now = datetime.now(timezone.utc).isoformat()
        
        # Admin
        h1, s1 = hash_password("Admin123!")
        cursor.execute("""
        INSERT INTO users (username, email, password_hash, salt, role, full_name, phone, company, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("admin", "admin@maxret3ch.ai", h1, s1, "admin", "Max Reynolds", "+254 111 641 296", "MaxReT3ch AI Exec", now))

        # Staff (Repair & AI Engineer)
        h2, s2 = hash_password("Staff123!")
        cursor.execute("""
        INSERT INTO users (username, email, password_hash, salt, role, full_name, phone, company, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("sarah.tech", "sarah@maxret3ch.ai", h2, s2, "staff", "Sarah Vance (Lead Hardware Specialist)", "+254 111 641 296", "MaxReT3ch Technical Ops", now))

        # Client Demo
        h3, s3 = hash_password("Client123!")
        cursor.execute("""
        INSERT INTO users (username, email, password_hash, salt, role, full_name, phone, company, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("david.innovate", "david@apexsystems.io", h3, s3, "customer", "David K. Sterling", "+254 700 890 210", "Apex Systems Inc.", now))

    # Seed Services across 6 verticals
    cursor.execute("SELECT COUNT(*) FROM services")
    if cursor.fetchone()[0] == 0:
        services_data = [
            # 1. AI Solutions
            (
                "ai_solutions",
                "Custom AI Agent Systems & Enterprise LLMs",
                "Autonomous digital employees, smart workflow automation, and custom neural models",
                "We engineer enterprise-grade multi-agent AI ecosystems, proprietary retrieval-augmented generation (RAG) knowledge vaults, and computer vision automation pipelines tailored specifically to your business operations.",
                320000.00,
                "per deployment",
                json.dumps([
                    "Autonomous Task-Executing AI Agents",
                    "Enterprise RAG with Zero Data Leakage",
                    "Fine-tuned Local & Cloud LLMs (Llama, Gemini, Claude)",
                    "Automated Lead & Support Cognitive Workers",
                    "API Integration & Real-Time Monitoring Telemetry"
                ]),
                "brain-circuit",
                1,
                "Fully deployed AI agent cluster, API endpoints, orchestration dashboard, 90 days hypercare support."
            ),
            (
                "ai_solutions",
                "Computer Vision & Predictive Analytics Engine",
                "Real-time visual defect detection, customer flow tracking, and forecasting",
                "Harness edge-accelerated computer vision models for factory QA, security surveillance, inventory tracking, and dynamic pricing forecasts.",
                450000.00,
                "project base",
                json.dumps([
                    "Edge AI Deployments on Jetson/TensorRT",
                    "Sub-10ms Inference Speed Pipelines",
                    "Automated Quality Inspection & Defect Anomaly Detection",
                    "Custom Dataset Labeling & Continuous Learning"
                ]),
                "eye",
                0,
                "Trained vision models, edge hardware configuration scripts, web telemetry dashboard."
            ),
            # 2. Website & Software Development
            (
                "software_dev",
                "Full-Stack Web Platforms & SaaS Architecture",
                "Ultra-fast, high-converting digital platforms engineered with modern resilient stacks",
                "We build scalable web portals, SaaS platforms, and internal enterprise dashboards with responsive cybernetic UI, robust REST/WebSocket APIs, and cloud-native resilience.",
                185000.00,
                "starting package",
                json.dumps([
                    "Responsive Mobile-First Architecture",
                    "High-Security Role Based Authentication (RBAC)",
                    "Sub-Second Page Load Optimization",
                    "M-Pesa, Stripe & Crypto Gateway Integrations",
                    "Automated CI/CD Deployment Pipelines"
                ]),
                "code-xml",
                1,
                "Full source code ownership, Dockerized deployment, database schema, automated backups."
            ),
            (
                "software_dev",
                "Custom Enterprise Software & API Microservices",
                "Tailored ERP, CRM, and cloud integrations solving complex automation workflows",
                "Transform legacy bottlenecks with bespoke software architectures that integrate your disparate data sources into a synchronized high-velocity workflow.",
                480000.00,
                "per sprint",
                json.dumps([
                    "Microservice Architecture with gRPC / REST",
                    "Real-Time WebSocket Synchronization",
                    "Automated ETL Data Ingestion Pipelines",
                    "Enterprise Single Sign-On (SAML / OAuth2)"
                ]),
                "server",
                0,
                "Production microservices cluster, OpenAPI specs, documentation, unit & integration test suite."
            ),
            # 3. Computer Hardware Sales, Repair & Refurbishment
            (
                "hardware",
                "AI Workstation & High-Performance Custom Builds",
                "Extreme-performance computing rigs engineered for machine learning, 3D rendering & CAD",
                "Engineered with liquid cooling, binned CPUs, dual/quad GPU topology, and ultra-quiet acoustic dampening. Every machine undergoes 72 hours of stress testing.",
                350000.00,
                "custom build base",
                json.dumps([
                    "Dual RTX 4090 / 5090 Ready Power Architectures",
                    "Custom Hard-Tube Liquid Cooling Loop Option",
                    "ECC / High-Speed DDR5 Memory Configurations",
                    "3-Year On-Site Hardware Replacement Warranty"
                ]),
                "cpu",
                1,
                "Turnkey pre-configured workstation, thermal benchmark report, OS + AI toolkit pre-installed."
            ),
            (
                "hardware",
                "Component-Level Hardware Diagnostic & Board Repair",
                "Micro-soldering, liquid spill recovery, GPU re-balling, and thermal overhaul",
                "Don't replace an entire high-end laptop or server board when a minor SMD capacitor or power MOSFET is faulty. Our micro-soldering lab saves up to 75% compared to OEM replacement.",
                5000.00,
                "diagnostic bench intake",
                json.dumps([
                    "Component-Level Board Micro-soldering",
                    "Thermal Repaste with Honeywell PTM7950 / Liquid Metal",
                    "GPU VRAM Reballing & Power Rail Triage",
                    "Zero-Data-Loss Motherboard Revival Guarantee"
                ]),
                "wrench",
                0,
                "Fixed hardware, 180-day repair warranty, detailed before/after thermal and voltage log."
            ),
            # 4. IT Technical Support
            (
                "it_support",
                "24/7 Managed IT & Cyber Defense Shield",
                "Proactive network monitoring, cybersecurity audits, and rapid remote rescue",
                "Complete managed IT infrastructure for SMEs and tech startups. We protect your endpoints, automate secure backups, maintain zero-trust networks, and provide 15-minute response times.",
                65000.00,
                "per month (up to 15 seats)",
                json.dumps([
                    "15-Minute Guaranteed Incident Response",
                    "Zero-Trust Network Access & Firewall Hardening",
                    "Automated Immutable Cloud & Local Backups",
                    "Phishing Simulations & Employee Security Training"
                ]),
                "shield-check",
                1,
                "24/7 monitoring agent, monthly vulnerability report, priority Ted AI ticketing desk."
            ),
            # 5. Green Tech & Electronic Waste Recycling
            (
                "green_tech",
                "Certified E-Waste Recycling & Trade-In Buyback",
                "Zero-landfill green disposal, DoD 5220.22-M certified data destruction, cash buybacks",
                "Turn discarded enterprise laptops, servers, and GPUs into capital while reducing your company's carbon footprint. We provide official Green Carbon Offset Certificates for ESG compliance.",
                0.00,
                "free pickup + cash payout",
                json.dumps([
                    "DoD & NIST 800-88 Compliant Data Destruction Certificate",
                    "Zero-Landfill Certified Environmental Processing",
                    "Instant Trade-In Valuation Calculator",
                    "ESG Carbon Credit Offsetting Documentation"
                ]),
                "recycle",
                1,
                "Physical collection manifest, serialized data destruction certificate, green ESG certificate."
            ),
            # 6. Technology Education & Programming Tutorials
            (
                "education",
                "Interactive AI & Full-Stack Engineering Masterclasses",
                "Hands-on coding bootcamps, AI engineer certification, and corporate tech upskilling",
                "Learn directly through real-world scenarios: building autonomous agents, reverse engineering hardware protocols, and deploying production SaaS applications with Ted as your 24/7 AI tutor.",
                18500.00,
                "course access",
                json.dumps([
                    "Interactive Browser-Based Code Sandbox",
                    "Ted 24/7 AI Personalized Code Reviewer",
                    "Real Production Architectural Case Studies",
                    "Official MaxReT3ch Industry Certificate"
                ]),
                "graduation-cap",
                1,
                "Lifetime curriculum access, downloadable project repositories, 1-on-1 mentor session."
            )
        ]
        cursor.executemany("""
        INSERT INTO services (vertical, title, tagline, description, starting_price, price_unit, features_json, icon, popular, deliverables)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, services_data)

    # Seed Hardware Products
    cursor.execute("SELECT COUNT(*) FROM hardware_products")
    if cursor.fetchone()[0] == 0:
        hardware_items = [
            (
                "MaxReT3ch AI Titan Workstation Alpha",
                "workstation",
                "new",
                580000.00,
                650000.00,
                4,
                36,
                json.dumps({
                    "CPU": "AMD Ryzen 9 9950X (16 cores, 32 threads @ 5.7GHz)",
                    "GPU": "NVIDIA GeForce RTX 4090 24GB GDDR6X",
                    "RAM": "128GB DDR5-6000MHz Kingston Fury Beast",
                    "Storage": "4TB PCIe Gen5 NVMe M.2 (14,000 MB/s)",
                    "Cooling": "Arctic Liquid Freezer III 420mm AIO",
                    "PSU": "Seasonic Vertex GX-1200W ATX 3.0 Platinum",
                    "OS": "Ubuntu 24.04 LTS + Windows 11 Pro Dual Boot (CUDA Pre-configured)"
                }),
                "/static/img/titan_workstation.png",
                "Ultimate workstation tailored for LLM fine-tuning, autonomous agent hosting, and 8K visual rendering."
            ),
            (
                "MaxReT3ch CyberNexus Gaming Rig Pro",
                "gaming_pc",
                "new",
                285000.00,
                320000.00,
                7,
                24,
                json.dumps({
                    "CPU": "Intel Core i7-14700K (20 cores, up to 5.6GHz)",
                    "GPU": "NVIDIA GeForce RTX 4070 Ti SUPER 16GB",
                    "RAM": "64GB DDR5-5600MHz RGB",
                    "Storage": "2TB Crucial T700 Gen5 NVMe",
                    "Chassis": "Lian Li O11 Dynamic EVO RGB (Custom Dark Navy Glass)",
                    "PSU": "Corsair RM850e 80+ Gold Fully Modular"
                }),
                "/static/img/gaming_rig.png",
                "High-framerate 4K gaming powerhouse with futuristic aesthetic lighting and whisper-quiet acoustic profiling."
            ),
            (
                "Dell Precision 7770 Mobile AI Workstation (Certified Refurbished)",
                "laptop",
                "refurbished_grade_a",
                168000.00,
                360000.00,
                11,
                12,
                json.dumps({
                    "CPU": "Intel Core i9-12950HX vPro",
                    "GPU": "NVIDIA RTX A4500 16GB ECC Dedicated",
                    "Display": "17.3\" 4K UHD (3840x2160) 120Hz 100% DCI-P3 500 nits",
                    "RAM": "64GB DDR5 CAMM memory",
                    "Storage": "2TB NVMe SSD Class 40",
                    "Battery": "New 93Wh battery (100% health tested)",
                    "Condition": "Grade A+ Pristine, zero cosmetic blemishes, certified thermal overhaul"
                }),
                "/static/img/dell_workstation.png",
                "Certified refurbished high-mobility CAD & deep learning station with brand-new high capacity battery and fresh thermal paste."
            ),
            (
                "Supermicro 2U Dual Xeon Enterprise Server (Green Recycled & Certified)",
                "server",
                "certified_renewed",
                245000.00,
                700000.00,
                3,
                18,
                json.dumps({
                    "CPU": "Dual Intel Xeon Silver 4314 (32 total cores, 64 threads)",
                    "RAM": "256GB DDR4-3200MHz ECC Registered",
                    "Storage": "8x 3.84TB Enterprise NVMe U.2 in RAID 10",
                    "Network": "Quad 10GbE SFP+ + Dual 1GbE IPMI",
                    "Redundancy": "Dual 1200W Titanium Hot-Swap Redundant PSUs"
                }),
                "/static/img/server_rack.png",
                "High-density cloud hosting & local database server thoroughly reconditioned and stress-tested in our clean-room facility."
            ),
            (
                "NVIDIA RTX 3080 Ti 12GB Founders Edition (Certified Refurbished)",
                "component",
                "refurbished_grade_a",
                58000.00,
                155000.00,
                14,
                12,
                json.dumps({
                    "VRAM": "12GB GDDR6X",
                    "Memory Bus": "384-bit",
                    "CUDA Cores": "10,240",
                    "Thermal Service": "Re-padded with Gelid Ultimate 15W/mK and Arctic MX-6 paste",
                    "Benchmark": "100% TimeSpy stability pass (max temp 67°C)"
                }),
                "/static/img/rtx_gpu.png",
                "Ultraclean, reconditioned graphics card with newly replaced high-performance thermal pads and ultrasonic PCB clean."
            )
        ]
        cursor.executemany("""
        INSERT INTO hardware_products (name, category, condition, price, original_price, stock, warranty_months, specs_json, image_url, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, hardware_items)

    # Seed Leads
    cursor.execute("SELECT COUNT(*) FROM leads")
    if cursor.fetchone()[0] == 0:
        now = datetime.now(timezone.utc).isoformat()
        leads_data = [
            (
                "Dr. Marcus Vance",
                "m.vance@neurotechlabs.com",
                "+254 712 432 887",
                "NeuroTech Genomics Labs",
                "ai_solutions",
                "Requires a private local LLM agent to analyze proprietary patient biomedical trial records without exposing any data to public cloud APIs.",
                1800000.00,
                "Within 30 days",
                "hot",
                "in_review",
                "ted_ai",
                0.97,
                "Ted qualified client's privacy compliance requirement. Budget verified.",
                now,
                now
            ),
            (
                "Elena Rostova",
                "elena@hyperionlogistic.net",
                "+254 722 912 300",
                "Hyperion Logistics Global",
                "software_dev",
                "Needs an automated logistics dispatch portal with real-time GPS fleet tracking and automated customs PDF generation.",
                850000.00,
                "6-8 weeks",
                "hot",
                "proposal_ready",
                "ted_ai",
                0.94,
                "Ted drafted quotation MRT-2026-1002. Awaiting human approval.",
                now,
                now
            ),
            (
                "Kevin Chen",
                "kchen@startuplink.io",
                "+254 733 678 223",
                "LinkCraft Studios",
                "hardware",
                "Looking to purchase 5 custom high-performance AI developer rigs and dispose of 12 legacy iMacs through certified e-waste recycling.",
                1950000.00,
                "Immediate (2 weeks)",
                "hot",
                "contacted",
                "ted_ai",
                0.96,
                "Combined hardware purchase and green tech trade-in inquiry.",
                now,
                now
            ),
            (
                "Samantha Wright",
                "swright@wrightaccounting.biz",
                "+254 744 234 998",
                "Wright Accounting Group",
                "it_support",
                "Firm has 22 employees requiring 24/7 managed IT support, ransomware protection, and automated nightly offsite encrypted backups.",
                120000.00,
                "Flexible / Next month",
                "warm",
                "new",
                "web_form",
                0.88,
                "Follow up with managed service level agreement terms.",
                now,
                now
            )
        ]
        cursor.executemany("""
        INSERT INTO leads (name, email, phone, company, vertical_interest, requirements_summary, estimated_budget, timeline, score, status, captured_by, ai_confidence, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, leads_data)

    # Seed Proposals (Including one Pending Human Approval)
    cursor.execute("SELECT COUNT(*) FROM proposals")
    if cursor.fetchone()[0] == 0:
        now = datetime.now(timezone.utc).isoformat()
        
        # Proposal 1: Pending Approval
        p1_items = [
            {"item": "Enterprise Private LLM Orchestration Cluster", "qty": 1, "rate": 550000.00, "total": 550000.00},
            {"item": "Proprietary Biomedical Vector Database (RAG) Architecture", "qty": 1, "rate": 420000.00, "total": 420000.00},
            {"item": "Custom Role-Based Web Interface & Audit Logging", "qty": 1, "rate": 280000.00, "total": 280000.00},
            {"item": "Local Hardware Setup & Hypercare Support (90 Days)", "qty": 1, "rate": 150000.00, "total": 150000.00}
        ]
        cursor.execute("""
        INSERT INTO proposals (quote_number, client_name, client_email, client_company, project_title, vertical, scope_details, itemized_costs_json, subtotal, discount, tax, total_amount, estimated_days, ted_summary, human_status, approved_by, approved_at, approval_notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "MRT-2026-1001",
            "Dr. Marcus Vance",
            "m.vance@neurotechlabs.com",
            "NeuroTech Genomics Labs",
            "On-Premise Private Clinical LLM Intelligence System",
            "ai_solutions",
            "Design and deployment of an on-premise air-gapped LLM agent capable of semantic querying across 200,000+ clinical trial documents with zero public internet data transmission.",
            json.dumps(p1_items),
            1400000.00,
            100000.00, # Ted proposed introductory discount
            208000.00, # 16% VAT
            1508000.00,
            24,
            "Client operates under strict HIPAA & GDPR requirements. Ted drafted an air-gapped on-premise solution using local quant models with high margin. Human verification of server specs recommended.",
            "pending_approval",
            None,
            None,
            None,
            now
        ))

        # Proposal 2: Approved
        p2_items = [
            {"item": "Logistics Dispatch Core Web Platform & Real-Time Fleet Map", "qty": 1, "rate": 450000.00, "total": 450000.00},
            {"item": "Automated Multi-Jurisdiction Customs PDF Generator", "qty": 1, "rate": 220000.00, "total": 220000.00},
            {"item": "Carrier API Integration (FedEx, Maersk, DHL)", "qty": 1, "rate": 180000.00, "total": 180000.00}
        ]
        cursor.execute("""
        INSERT INTO proposals (quote_number, client_name, client_email, client_company, project_title, vertical, scope_details, itemized_costs_json, subtotal, discount, tax, total_amount, estimated_days, ted_summary, human_status, approved_by, approved_at, approval_notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "MRT-2026-1002",
            "Elena Rostova",
            "elena@hyperionlogistic.net",
            "Hyperion Logistics Global",
            "Hyperion Real-Time Logistics & Customs Automation Portal",
            "software_dev",
            "Full-stack responsive freight management web application with interactive live route map, client tracking portal, and automatic bill of lading generation.",
            json.dumps(p2_items),
            850000.00,
            50000.00,
            128000.00, # 16% VAT
            928000.00,
            30,
            "Ted verified requirements. High feasibility with standard microservice stack.",
            "approved",
            "Max Reynolds (Managing Director)",
            now,
            "Standard scope approved. Payment terms 50% upfront, 50% on milestone acceptance.",
            now
        ))

    # Seed Repair Tickets
    cursor.execute("SELECT COUNT(*) FROM repair_tickets")
    if cursor.fetchone()[0] == 0:
        now = datetime.now(timezone.utc).isoformat()
        tickets = [
            (
                "REP-8821",
                "Thomas Sterling",
                "t.sterling@renderworks.tv",
                "+254 722 349 112",
                "Custom Workstation (ASUS ProArt X670E, RTX 4090)",
                "no_power",
                "PC fails to power on; slight burning smell reported after voltage spike during storm.",
                "Ted Diagnostic Triage: Symptoms indicate blown 12V transient voltage suppression (TVS) diode or primary 5V standby rail short on motherboard. PSU safety trip engaged. Recommended component-level motherboard bench test.",
                "high",
                "diagnostic_pending",
                28000.00,
                "Board received on bench 2. Multimeter probe shows short on 12V_SB rail.",
                0,
                now
            ),
            (
                "REP-8822",
                "Clara Bennett",
                "clara.b@apexdesign.studio",
                "+254 711 765 432",
                "MacBook Pro 16\" M2 Max (A2780)",
                "screen_damage",
                "Internal display lines and black spot after small object closed in lid. External monitor works perfectly.",
                "Ted Diagnostic Triage: Display matrix cracked; T-CON and GPU operational. Requires tier-1 OEM Retina display assembly replacement.",
                "normal",
                "in_repair",
                65000.00,
                "OEM screen assembly unboxed and tested. Installing TrueTone sensor calibration.",
                1,
                now
            )
        ]
        cursor.executemany("""
        INSERT INTO repair_tickets (ticket_code, customer_name, customer_email, customer_phone, device_model, issue_type, symptoms, diagnosis_by_ted, priority, status, estimated_cost, technician_notes, human_approved_dispatch, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tickets)

    # Seed E-Waste Submissions
    cursor.execute("SELECT COUNT(*) FROM ewaste_submissions")
    if cursor.fetchone()[0] == 0:
        now = datetime.now(timezone.utc).isoformat()
        ewaste_records = [
            (
                "GRN-2026-901",
                "Horizon FinTech Corp",
                "procurement@horizonfin.com",
                "+254 700 888 012",
                "laptop",
                15,
                "working",
                352500.00,
                480.5,
                "refurbish_reuse",
                1,
                "ECO-CERT-901-2026-NZ",
                "completed",
                "Max Reynolds",
                now
            ),
            (
                "GRN-2026-902",
                "Beacon Media Group",
                "admin@beaconmedia.com",
                "+254 722 222 771",
                "desktop",
                8,
                "damaged",
                79200.00,
                245.0,
                "certified_metal_recovery",
                0,
                None,
                "inspected",
                None,
                now
            )
        ]
        cursor.executemany("""
        INSERT INTO ewaste_submissions (submission_code, client_name, client_email, client_phone, device_type, quantity, device_condition, calculated_tradein_value, carbon_offset_kg, recycling_type, certificate_issued, certificate_number, status, human_approval_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ewaste_records)

    # Seed Tutorials
    cursor.execute("SELECT COUNT(*) FROM tutorials")
    if cursor.fetchone()[0] == 0:
        tutorials_data = [
            (
                "Building Autonomous AI Agents with Tool Calling in Python",
                "ai_engineering",
                "intermediate",
                45,
                "Learn how to construct resilient, task-oriented AI agents equipped with custom execution tools, state persistence, and guardrails.",
                """# Autonomous AI Agents 101

In this masterclass by MaxReT3ch AI, you will build an autonomous agent that receives natural language goals, decides on required API tools, executes them safely, and synthesizes results.

### Key Concepts:
1. **Tool Definition**: Creating JSON schema definitions for agent actions.
2. **Context Orchestration**: Maintaining conversation scratchpads and execution traces.
3. **Guardrails**: Intercepting destructive commands before execution.

```python
import json

class AgentTool:
    def __init__(self, name, description, func):
        self.name = name
        self.description = description
        self.func = func

    def execute(self, **kwargs):
        return self.func(**kwargs)
```
""",
                """def check_server_status(host: str) -> dict:
    # Simulated server ping check
    return {"host": host, "status": "ONLINE", "latency_ms": 14.2}

tools = {
    "ping": AgentTool("ping", "Checks if server is reachable", check_server_status)
}

# Ted Agent decision simulator
print("Agent initialized with 1 active tool.")
result = tools["ping"].execute(host="nexus.maxret3ch.ai")
print("Execution Result:", result)
""",
                "Extend the AgentTool class to support an 'approval_required: bool' flag that halts execution until an admin confirms.",
                218
            ),
            (
                "Full-Stack Real-Time Telemetry with FastAPI & WebSockets",
                "fullstack",
                "intermediate",
                35,
                "Build a high-throughput, low-latency live streaming telemetry dashboard for industrial IoT or AI inference monitoring.",
                """# Real-Time Telemetry Dashboard

FastAPI provides ultra-fast native ASGI asynchronous WebSocket endpoints. This tutorial demonstrates streaming server metrics to a futuristic front-end UI.

```python
from fastapi import FastAPI, WebSocket
import asyncio, random

app = FastAPI()

@app.websocket("/ws/telemetry")
async def telemetry_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        data = {"cpu_pct": random.randint(15, 85), "temp_c": 52.4}
        await ws.send_json(data)
        await asyncio.sleep(1)
```
""",
                """# Client connection test
import asyncio
import json

async def mock_telemetry_stream():
    for tick in range(3):
        metric = {"tick": tick, "power_watts": 420.5 + tick * 2.1}
        print(f"Dispatched metric: {metric}")
        await asyncio.sleep(0.5)

asyncio.run(mock_telemetry_stream())
""",
                "Add a memory usage metric and an alert if CPU exceeds 90%.",
                164
            ),
            (
                "Hardware Triage: Multi-Rail Power Diagnostics & Micro-soldering",
                "hardware_repair",
                "advanced",
                50,
                "Master diagnosing shorted 12V, 5V, and 3.3V power rails on high-end motherboards and GPUs using thermal imaging and current injection.",
                """# Motherboard Power Rail Diagnostics

When a high-performance computer fails to power on (No POST), 80% of issues reside in the power sequencing circuit.

### Diagnostic Flow:
1. Check **Standby 3.3V / 5V** rails with DMM in resistance mode.
2. If resistance is under 2 Ohms on a main rail, you have a short to ground.
3. Use a regulated bench DC power supply set to 1.0V (limit to 2A) to inject current.
4. Observe the PCB under a thermal camera; the shorted component (e.g. cracked ceramic bypass capacitor) will glow bright immediately.
""",
                """def diagnose_rail(rail_name: str, resistance_ohms: float):
    thresholds = {
        "12V_MAIN": 500.0,
        "5V_STANDBY": 300.0,
        "3.3V_SB": 150.0,
        "VCORE_GPU": 0.3  # Low resistance normal for modern GPUs!
    }
    expected = thresholds.get(rail_name, 100.0)
    if rail_name == "VCORE_GPU" and resistance_ohms >= 0.2:
        return "NORMAL (High-current core plane)"
    if resistance_ohms < 5.0 and rail_name != "VCORE_GPU":
        return "CRITICAL SHORT DETECTED: Do NOT apply full voltage! Use 1V current injection."
    return "HEALTHY IMPEDANCE"

print("12V Rail Test:", diagnose_rail("12V_MAIN", 1.2))
""",
                "Implement a diagnostic check for RAM VDDQ (1.1V for DDR5).",
                97
            )
        ]
        cursor.executemany("""
        INSERT INTO tutorials (title, category, level, duration_minutes, description, lesson_content_markdown, code_example, exercise_prompt, enrolled_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tutorials_data)

    # Seed Ted AI Interactions
    cursor.execute("SELECT COUNT(*) FROM ted_interactions")
    if cursor.fetchone()[0] == 0:
        now = datetime.now(timezone.utc).isoformat()
        interactions = [
            (
                "sess_88192a",
                "Dr. Marcus Vance",
                "m.vance@neurotechlabs.com",
                6,
                "Visitor asked about building private AI agents that comply with HIPAA. Ted answered security specs, estimated cost ($14,000), collected contact details, and created quotation MRT-2026-1001 for human approval.",
                "positive",
                "request_ai_quote",
                json.dumps(["Verify server rack space with client", "Review proposal MRT-2026-1001 in Admin Dashboard"]),
                json.dumps([
                    {"sender": "ted", "text": "Greetings! I am Ted, your autonomous operations specialist at MaxReT3ch AI. How may I accelerate your technological goals today?"},
                    {"sender": "user", "text": "We need an AI agent to index clinical genomics papers, but we cannot use ChatGPT due to patient data regulations."},
                    {"sender": "ted", "text": "Understood, Dr. Vance. At MaxReT3ch AI, we specialize in private, air-gapped on-premise LLM clusters with zero cloud leakage. We can deploy a 70B parameter model with quantized vector RAG on your local servers. What is your estimated timeline and volume of records?"},
                    {"sender": "user", "text": "We have ~200,000 documents and want this operational within 3-4 weeks. Can you generate a quotation?"},
                    {"sender": "ted", "text": "I have structured quotation MRT-2026-1001 totaling $14,040 (including a $1,000 introductory discount). This has been submitted to Max Reynolds for executive human sign-off!"}
                ]),
                now
            )
        ]
        cursor.executemany("""
        INSERT INTO ted_interactions (session_id, visitor_name, visitor_email, messages_count, summary, sentiment, primary_intent, action_items_json, transcript_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, interactions)

    # Seed Marketing Campaigns
    cursor.execute("SELECT COUNT(*) FROM marketing_campaigns")
    if cursor.fetchone()[0] == 0:
        now = datetime.now(timezone.utc).isoformat()
        campaigns = [
            (
                "Q4 Enterprise AI Transformation & E-Waste Credit Initiative",
                "CTOs, VP of Engineering & Operations Directors",
                "linkedin",
                "Is legacy hardware and disconnected AI tools draining your engineering velocity? \n\nAt MaxReT3ch AI, we bridge the physical and autonomous digital worlds: \n1. Deploy private, autonomous AI employees (like me, Ted!) that handle your customer onboarding and proposal workflows.\n2. Trade-in depreciated servers and laptops for certified ESG carbon credits and instant capital.\n\nDiscover the next generation of computing at MaxReT3ch AI.",
                "Schedule a 15-Minute Technical Consultation with Ted",
                "approved",
                4200,
                now
            ),
            (
                "Zero-Landfill Green Tech Revolution: Recycle & Upgrade",
                "Sustainability Officers & IT Asset Managers",
                "email",
                "Subject: MaxReT3ch AI: Turn Depreciated IT Assets into Certified Carbon Credits\n\nDear Technology Leader,\n\nDid you know enterprise electronic waste accounts for over 70% of heavy metal toxic waste in landfills? MaxReT3ch AI provides DoD-certified zero-landfill electronic recycling with complete serial-tracked chain of custody.\n\nCalculate your instant trade-in value and ESG offset certificate directly on our portal.",
                "Calculate Your Carbon Offset & Trade-In Payout",
                "reviewed",
                1800,
                now
            )
        ]
        cursor.executemany("""
        INSERT INTO marketing_campaigns (title, target_audience, channel, generated_content, call_to_action, status, projected_reach, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, campaigns)

    # Seed System Settings
    cursor.execute("SELECT COUNT(*) FROM system_settings")
    if cursor.fetchone()[0] == 0:
        settings = [
            ("company_name", "MaxReT3ch AI", "Official business legal name"),
            ("gemini_api_key", "", "Optional Google Gemini API Key for dynamic LLM generation"),
            ("auto_quote_threshold", "500000", "Proposals above this KSh value strictly require human admin approval"),
            ("support_hotline", "+254 111 641 296", "Official 24/7 Technical Hotline (Direct & WhatsApp)"),
            ("currency", "KSh", "Active operating currency"),
            ("ted_voice_enabled", "true", "Enable interactive speech synthesis for Ted"),
            ("system_version", "2.4.0-Futuristic-KE", "Core application version")
        ]
        cursor.executemany("""
        INSERT INTO system_settings (key, value, description)
        VALUES (?, ?, ?)
        """, settings)

    conn.commit()
