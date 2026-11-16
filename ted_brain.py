import re
import json
import random
from datetime import datetime, timezone
from app.database import get_db

# Knowledge Base of MaxReT3ch AI
SERVICES_KB = {
    "ai_solutions": {
        "title": "Artificial Intelligence Solutions",
        "keywords": ["ai", "artificial intelligence", "agent", "llm", "machine learning", "rag", "vision", "automation", "neural", "deep learning", "chatbot"],
        "base_rate": 320000,
        "typical_timeline_days": 21,
        "pitch": "We design and deploy custom enterprise AI systems: autonomous task-executing agents, private on-premise RAG knowledge vaults, computer vision inspection pipelines, and fine-tuned LLMs with zero data leakage."
    },
    "software_dev": {
        "title": "Website & Software Development",
        "keywords": ["web", "website", "software", "app", "mobile", "frontend", "backend", "api", "saas", "fullstack", "portal", "cloud"],
        "base_rate": 185000,
        "typical_timeline_days": 28,
        "pitch": "From high-conversion cybernetic web applications and mobile apps to fault-tolerant microservices and enterprise SaaS architectures, our engineering team builds resilient, lightning-fast digital platforms."
    },
    "hardware": {
        "title": "Computer Hardware Sales, Repair & Refurbishment",
        "keywords": ["hardware", "workstation", "repair", "pc", "laptop", "gpu", "rtx", "cpu", "motherboard", "soldering", "refurbished", "server", "thermal"],
        "base_rate": 15000,
        "typical_timeline_days": 5,
        "pitch": "We build flagship AI & gaming workstations, offer certified refurbished enterprise hardware with up to 36 months warranty, and operate an advanced component-level micro-soldering repair lab."
    },
    "it_support": {
        "title": "IT Technical Support & Managed Services",
        "keywords": ["support", "it support", "network", "firewall", "cybersecurity", "backup", "server down", "remote rescue", "managed it", "helpdesk"],
        "base_rate": 65000,
        "typical_timeline_days": 1,
        "pitch": "24/7 proactive managed IT services, endpoint protection, zero-trust network hardening, automated immutable backups, and guaranteed 15-minute emergency response."
    },
    "green_tech": {
        "title": "Green Technology & Electronic Waste Recycling",
        "keywords": ["green", "recycle", "e-waste", "ewaste", "disposal", "trade-in", "carbon", "esg", "environmental", "scrap", "buyback"],
        "base_rate": 0,
        "typical_timeline_days": 3,
        "pitch": "Certified zero-landfill electronic waste recycling, DoD 5220.22-M certified data wiping, instant cash buybacks for legacy fleets, and official ESG Carbon Offset Certificates."
    },
    "education": {
        "title": "Technology Education & Programming Tutorials",
        "keywords": ["tutorial", "education", "course", "learn", "bootcamp", "training", "python", "upskilling", "workshop", "code"],
        "base_rate": 18500,
        "typical_timeline_days": 14,
        "pitch": "Hands-on engineering masterclasses covering Autonomous AI Agents, Full-Stack FastAPI/React, Hardware Board Diagnostics, and Cloud DevOps, with Ted as your 24/7 code mentor."
    }
}

TROUBLESHOOTING_KB = {
    "no_power": {
        "symptoms": ["won't turn on", "no power", "no lights", "dead pc", "power cut", "burnt smell"],
        "steps": [
            "1. Verify wall outlet power & toggle the PSU rocker switch (I/O).",
            "2. Check if the 24-pin ATX and 8-pin CPU EPS power cables are seated firmly.",
            "3. Perform the PSU paperclip/jumper test (short pins 16 & 17 on the 24-pin connector) to check if the power supply fan spins.",
            "4. If power supply clicks off immediately, you likely have a short to ground on the 12V or 5V standby power rail.",
            "5. Recommendation: Bring motherboard into MaxReT3ch Lab for component-level multimeter & thermal camera inspection."
        ],
        "severity": "critical"
    },
    "no_post_display": {
        "symptoms": ["fans spin but no display", "black screen", "no post", "gpu fans at 100", "dram light", "cpu light"],
        "steps": [
            "1. Inspect motherboard diagnostic LEDs (CPU, DRAM, VGA, BOOT).",
            "2. Reseat memory: Test a single stick of RAM in the secondary slot (Slot A2).",
            "3. Clear CMOS battery for 5 minutes to reset BIOS to factory safe defaults.",
            "4. Reseat GPU and verify that separate PCIe 8-pin cables are used (not daisy-chained).",
            "5. If DRAM LED remains solid, test with alternate compatible memory or re-socket the CPU to check for bent LGA pins."
        ],
        "severity": "high"
    },
    "overheating_throttling": {
        "symptoms": ["overheating", "thermal throttling", "loud fans", "shut down while gaming", "high temps", "95c", "100c"],
        "steps": [
            "1. Check if the AIO pump tachometer registers RPM in BIOS; a dead pump is the #1 cause of sudden 100°C spikes.",
            "2. Verify thermal paste application; inspect whether the plastic peel was left on the cooler coldplate.",
            "3. Clean chassis dust filters and ensure positive pressure fan configuration.",
            "4. MaxReT3ch Service: We offer professional Honeywell PTM7950 phase-change pad installation and custom loop flushes."
        ],
        "severity": "normal"
    },
    "network_dns_drop": {
        "symptoms": ["internet disconnected", "no network", "dns error", "wifi dropping", "packet loss", "ip conflict"],
        "steps": [
            "1. Run command: 'ipconfig /flushdns' followed by 'netsh int ip reset' in an elevated terminal.",
            "2. Set primary DNS to 1.1.1.1 (Cloudflare) or 8.8.8.8 (Google).",
            "3. Check for IP address conflicts by setting DHCP lease renewal.",
            "4. Test network cable with a cable tester to ensure 8-conductor gigabit continuity."
        ],
        "severity": "normal"
    }
}

class TedAIEngine:
    def __init__(self):
        self.name = "Ted"
        self.role = "Chief Autonomous AI Operations Specialist at MaxReT3ch AI"

    def analyze_intent(self, text: str) -> str:
        text_lower = text.lower().strip()

        # Proposal or quote request
        if any(w in text_lower for w in ["quote", "quotation", "proposal", "estimate", "pricing for project", "how much would it cost", "bill of work", "scope"]):
            return "request_proposal"
        
        # Troubleshooting request
        if any(w in text_lower for w in ["troubleshoot", "fix", "repair", "broken", "won't boot", "blue screen", "bsod", "overheat", "crashed", "diagnostic", "black screen", "dead", "fans spin", "fans at 100", "no display", "no post", "won't post", "shuts down", "sparks", "smoke"]):
            return "hardware_troubleshooting"

        # E-Waste / Recycling
        if any(w in text_lower for w in ["recycle", "e-waste", "ewaste", "trade in", "scrap", "carbon offset", "old laptop", "old computer", "disposal"]):
            return "ewaste_recycling"

        # Education / Tutorials
        if any(w in text_lower for w in ["learn", "tutorial", "course", "bootcamp", "training", "teach me", "education"]):
            return "education_inquiry"

        # Marketing & BizDev assistance
        if any(w in text_lower for w in ["marketing", "campaign", "bizdev", "business development", "cold email", "outreach", "social post", "press release"]):
            return "marketing_bizdev"

        # Business performance report
        if any(w in text_lower for w in ["report", "analytics", "performance", "revenue", "how is business", "sales metrics", "pipeline"]):
            return "business_report"

        # Lead / Contact Info
        if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text_lower) or any(w in text_lower for w in ["my name is", "reach me at", "contact me", "here is my email", "phone number"]):
            return "contact_lead"

        # Service inquiries
        for vert, data in SERVICES_KB.items():
            if any(k in text_lower for k in data["keywords"]):
                return f"inquiry_{vert}"

        # Greetings
        if any(w in text_lower for w in ["hello", "hi", "hey", "greetings", "good morning", "good evening", "ted"]):
            return "greeting"

        return "general_inquiry"

    def extract_contact_info(self, text: str) -> dict:
        info = {}
        # Email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match:
            info["email"] = email_match.group(0)
        
        # Phone
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}', text)
        if phone_match and len(phone_match.group(0).strip()) >= 7:
            info["phone"] = phone_match.group(0).strip()
            
        # Name heuristics
        name_match = re.search(r'(?:my name is|i am|this is|i\'m)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', text, re.IGNORECASE)
        if name_match:
            info["name"] = name_match.group(1).title()

        # Company heuristics
        comp_match = re.search(r'(?:company is|work at|from|at)\s+([A-Z0-9][\w\s&]+?)(?:\.|\,|$|\s+and)', text, re.IGNORECASE)
        if comp_match:
            cand = comp_match.group(1).strip()
            if len(cand) > 2 and cand.lower() not in ["home", "work", "school", "office"]:
                info["company"] = cand

        # Budget heuristics
        budget_match = re.search(r'\$?(\d{1,3}(?:,\d{3})*|\d+)(?:\s*(?:k|thousand|usd|\$))', text, re.IGNORECASE)
        if budget_match:
            raw = budget_match.group(1).replace(",", "")
            val = float(raw)
            if "k" in budget_match.group(0).lower() or "thousand" in budget_match.group(0).lower():
                val *= 1000
            info["budget"] = val

        return info

    def generate_automated_proposal(self, client_name: str, client_email: str, client_company: str, text: str) -> dict:
        # Detect vertical
        vertical = "ai_solutions"
        text_lower = text.lower()
        for vert, data in SERVICES_KB.items():
            if any(k in text_lower for k in data["keywords"]):
                vertical = vert
                break

        quote_num = f"MRT-{datetime.now().year}-{random.randint(1010, 9999)}"
        
        # Build tailored itemized items based on vertical & user inquiry
        items = []
        if vertical == "ai_solutions":
            title = f"Enterprise AI System & Intelligent Workflow Automation ({client_company or 'Custom Deployment'})"
            items = [
                {"item": "Autonomous AI Agent Cluster & Tool Calling Architecture", "qty": 1, "rate": 350000.00, "total": 350000.00},
                {"item": "Enterprise RAG Vector Database & Document Vault Setup", "qty": 1, "rate": 240000.00, "total": 240000.00},
                {"item": "Role-Based Web Cockpit & Telemetry Dashboards", "qty": 1, "rate": 180000.00, "total": 180000.00},
                {"item": "Model Fine-Tuning & Quantized Local Deployment", "qty": 1, "rate": 220000.00, "total": 220000.00},
                {"item": "Hypercare Security Hardening & 60-Day SLA Support", "qty": 1, "rate": 110000.00, "total": 110000.00}
            ]
            est_days = 25
        elif vertical == "software_dev":
            title = f"Full-Stack Web Platform & Cloud Infrastructure ({client_company or 'Modern Platform'})"
            items = [
                {"item": "Futuristic Responsive Frontend (Tailwind/Cybernetic UI)", "qty": 1, "rate": 280000.00, "total": 280000.00},
                {"item": "FastAPI / Node.js High-Concurrency Backend Microservices", "qty": 1, "rate": 320000.00, "total": 320000.00},
                {"item": "Database Architecture, Migrations & Real-Time WebSockets", "qty": 1, "rate": 160000.00, "total": 160000.00},
                {"item": "CI/CD Deployment, Automated Backups & SSL Hardening", "qty": 1, "rate": 120000.00, "total": 120000.00}
            ]
            est_days = 30
        elif vertical == "hardware":
            title = f"High-Performance AI Workstations & Refurbished Hardware Fleet"
            items = [
                {"item": "MaxReT3ch AI Titan Workstation Alpha (RTX 4090, 128GB DDR5)", "qty": 1, "rate": 580000.00, "total": 580000.00},
                {"item": "Dell Precision 7770 Mobile AI Workstation (Certified)", "qty": 2, "rate": 168000.00, "total": 336000.00},
                {"item": "Thermal Optimization & 72-Hour Rigorous Burn-In Test", "qty": 1, "rate": 35000.00, "total": 35000.00}
            ]
            est_days = 7
        elif vertical == "it_support":
            title = f"24/7 Managed IT Infrastructure, Zero-Trust & Endpoint Defense"
            items = [
                {"item": "24/7 Endpoint Monitoring & Incident Response (Quarterly)", "qty": 3, "rate": 65000.00, "total": 195000.00},
                {"item": "Zero-Trust Network Perimeter & Firewall Hardening", "qty": 1, "rate": 120000.00, "total": 120000.00},
                {"item": "Automated Immutable Cloud Backup & Disaster Recovery Runbook", "qty": 1, "rate": 85000.00, "total": 85000.00}
            ]
            est_days = 5
        elif vertical == "green_tech":
            title = f"Certified Corporate E-Waste Recycling & Hardware Buyback"
            items = [
                {"item": "DoD 5220.22-M Certified Magnetic & Multi-Pass Data Destruction", "qty": 15, "rate": 4500.00, "total": 67500.00},
                {"item": "Zero-Landfill Environmental Refining & Material Recovery", "qty": 15, "rate": 2800.00, "total": 42000.00},
                {"item": "Official ESG Carbon Offset Certificate Issuance", "qty": 1, "rate": 0.00, "total": 0.00}
            ]
            est_days = 4
        else:
            title = f"Corporate Engineering Upskilling & AI Apprenticeship Program"
            items = [
                {"item": "AI Agent Engineering & Tool Calling Masterclass (10 Seats)", "qty": 10, "rate": 18500.00, "total": 185000.00},
                {"item": "Dedicated Live Interactive Labs & Ted 24/7 Code Review", "qty": 1, "rate": 85000.00, "total": 85000.00}
            ]
            est_days = 14

        subtotal = sum(i["total"] for i in items)
        discount = round(subtotal * 0.08, 2) # Ted automatically applies an 8% promotional loyalty discount
        taxable = subtotal - discount
        tax = round(taxable * 0.16, 2) # 16% Kenya VAT
        total = round(taxable + tax, 2)

        scope = f"Comprehensive project scope covering all engineering deliverables for {client_company or client_name}. Includes quality verification, test suites, architecture documentation, and complete human executive review by MaxReT3ch leadership."
        ted_summary = f"Ted AI automatically analyzed client inquiry '{text[:120]}...'. Structured itemized estimate with 8% incentive discount. Flagged for Human Executive Approval prior to binding contract dispatch."

        # Insert into database with human_status = 'pending_approval'
        conn = get_db()
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
        INSERT INTO proposals (quote_number, client_name, client_email, client_company, project_title, vertical, scope_details, itemized_costs_json, subtotal, discount, tax, total_amount, estimated_days, ted_summary, human_status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            quote_num, client_name, client_email, client_company, title, vertical,
            scope, json.dumps(items), subtotal, discount, tax, total, est_days,
            ted_summary, "pending_approval", now
        ))
        conn.commit()
        conn.close()

        return {
            "quote_number": quote_num,
            "project_title": title,
            "vertical": vertical,
            "client_name": client_name,
            "client_email": client_email,
            "subtotal": subtotal,
            "discount": discount,
            "tax": tax,
            "total_amount": total,
            "estimated_days": est_days,
            "items": items,
            "human_status": "pending_approval"
        }

    def process_troubleshooting(self, text: str) -> dict:
        text_lower = text.lower()
        matched_cat = None
        for cat, data in TROUBLESHOOTING_KB.items():
            if any(s in text_lower for s in data["symptoms"]):
                matched_cat = (cat, data)
                break

        if not matched_cat:
            matched_cat = ("general_hardware", {
                "symptoms": ["general glitch"],
                "steps": [
                    "1. Isolate the problem: Disconnect all non-essential peripherals (USB drives, webcams, capture cards).",
                    "2. Check Windows Event Viewer / Linux dmesg for Kernel-Power (Event ID 41) or WHEA-Logger errors.",
                    "3. Monitor temperatures with HWInfo64 or lm-sensors.",
                    "4. Run Windows Memory Diagnostic (mdsched.exe) or MemTest86 to rule out faulty DDR memory.",
                    "5. Book an in-depth bench diagnosis with MaxReT3ch hardware lab."
                ],
                "severity": "normal"
            })

        cat_name, cat_data = matched_cat
        return {
            "category": cat_name,
            "severity": cat_data["severity"],
            "steps": cat_data["steps"],
            "triage_summary": f"Ted automated hardware triage completed for detected pattern: '{cat_name.replace('_', ' ').title()}'."
        }

    def generate_marketing_campaign(self, title: str, audience: str, channel: str, goal: str = "") -> dict:
        channel_lower = channel.lower()
        if "linkedin" in channel_lower:
            content = f"""🚀 Accelerating Enterprise Tech with Autonomous Intelligence & Sustainable Computing

To all {audience}: 
Are operational bottlenecks and mounting electronic waste holding back your technical velocity? 

At MaxReT3ch AI, we engineer high-performance systems for modern technology leaders:
⚡ Autonomous AI Digital Employees (Custom RAG & Multi-Agent Systems)
💻 Extreme Computing Workstations & Certified Refurbished Hardware
🌱 Certified DoD-Compliant E-Waste Recycling & Instant ESG Carbon Offsets
🛡️ 24/7 Proactive Managed IT & Cyber Defense

Discover how MaxReT3ch AI can streamline your operations while hitting your sustainability benchmarks.

Connect with Ted, our Autonomous AI Operations Specialist, to configure your tailored quotation today."""
            cta = "Connect with Ted & Claim Your Free Architecture Assessment"
        elif "email" in channel_lower:
            content = f"""Subject: Transforming {audience}'s Technology Infrastructure with MaxReT3ch AI

Dear Technology Executive,

I am writing from MaxReT3ch AI, where we partner with forward-thinking organizations to deploy next-generation AI solutions, high-performance computing, and certified green e-waste recycling.

Key capabilities we deliver:
1. Private On-Premise AI Agents: Zero data leakage, full HIPAA/GDPR compliance.
2. Custom AI Workstations: Liquid-cooled, multi-GPU compute rigs pre-configured with CUDA.
3. ESG Carbon Credits: Cash buybacks for legacy fleets with DoD 5220.22-M certified data wipe.

We would welcome the opportunity to review your technical requirements. Our AI Operations Specialist, Ted, can provide an itemized project quotation within 60 seconds."""
            cta = "Review Your Instant Proposal with Ted"
        elif "twitter" in channel_lower or "x" in channel_lower:
            content = f"""Modern tech requires modern infrastructure. 

At @MaxReT3chAI, we deliver:
🔹 Enterprise AI Agents & Fine-Tuned Local LLMs
🔹 Flagship Custom Compute Workstations
🔹 Zero-Landfill Certified E-Waste Recycling

Ready to upgrade your stack? Chat with Ted 24/7 on our platform: maxret3ch.ai"""
            cta = "Chat with Ted on MaxReT3ch.ai"
        else: # Blog / Press Release
            content = f"""[FOR IMMEDIATE RELEASE]

MaxReT3ch AI Unveils Next-Generation Technology Ecosystem: Bridging Autonomous AI, High-Performance Hardware, and Certified Green Recycling.

Tech Corridor, Silicon Nexus — MaxReT3ch AI today announced the deployment of its comprehensive technology platform operated by Ted, the company's autonomous digital employee.

By uniting enterprise artificial intelligence development, custom computing hardware sales and micro-soldering repairs, and certified zero-landfill electronic waste recycling, MaxReT3ch AI provides technology leaders with a closed-loop ecosystem for sustainable, high-velocity computing."""
            cta = "Visit maxret3ch.ai to Learn More"

        conn = get_db()
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute("""
        INSERT INTO marketing_campaigns (title, target_audience, channel, generated_content, call_to_action, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'draft', ?)
        """, (title or f"Campaign for {audience}", audience, channel, content, cta, now))
        camp_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return {
            "id": camp_id,
            "title": title,
            "target_audience": audience,
            "channel": channel,
            "content": content,
            "call_to_action": cta,
            "status": "draft"
        }

    def generate_business_report(self) -> dict:
        conn = get_db()
        cursor = conn.cursor()

        # Leads count & score breakdown
        cursor.execute("SELECT COUNT(*), SUM(CASE WHEN score='hot' THEN 1 ELSE 0 END), SUM(CASE WHEN score='warm' THEN 1 ELSE 0 END) FROM leads")
        row = cursor.fetchone()
        total_leads = row[0] or 0
        hot_leads = row[1] or 0
        warm_leads = row[2] or 0

        # Proposals metrics
        cursor.execute("""
        SELECT COUNT(*), 
               SUM(CASE WHEN human_status='pending_approval' THEN 1 ELSE 0 END),
               SUM(CASE WHEN human_status='approved' THEN 1 ELSE 0 END),
               SUM(total_amount),
               SUM(CASE WHEN human_status='approved' THEN total_amount ELSE 0 END)
        FROM proposals
        """)
        p_row = cursor.fetchone()
        total_proposals = p_row[0] or 0
        pending_approval = p_row[1] or 0
        approved_proposals = p_row[2] or 0
        total_pipeline_val = p_row[3] or 0.0
        approved_revenue = p_row[4] or 0.0

        # Repairs
        cursor.execute("SELECT COUNT(*), SUM(CASE WHEN status='in_repair' OR status='diagnostic_pending' THEN 1 ELSE 0 END) FROM repair_tickets")
        r_row = cursor.fetchone()
        total_repairs = r_row[0] or 0
        active_repairs = r_row[1] or 0

        # E-Waste
        cursor.execute("SELECT COUNT(*), SUM(carbon_offset_kg), SUM(calculated_tradein_value) FROM ewaste_submissions")
        e_row = cursor.fetchone()
        total_ewaste = e_row[0] or 0
        total_carbon_offset = e_row[1] or 0.0
        total_tradein_val = e_row[2] or 0.0

        # Ted Interactions
        cursor.execute("SELECT COUNT(*) FROM ted_interactions")
        interactions_count = cursor.fetchone()[0] or 0

        conn.close()

        summary_text = f"""📊 **MaxReT3ch AI Executive Operations Report**
- **Sales & Proposals Pipeline**: KSh {total_pipeline_val:,.2f} total across {total_proposals} proposals (KSh {approved_revenue:,.2f} approved and signed).
- **Human Approval Queue**: {pending_approval} proposal(s) currently awaiting executive sign-off.
- **Lead Flow**: {total_leads} qualified leads captured ({hot_leads} Hot, {warm_leads} Warm).
- **Hardware Bench & Repair Lab**: {active_repairs} active service tickets in triage or micro-soldering.
- **Sustainability & E-Waste**: {total_carbon_offset:,.1f} kg CO2 offset achieved across {total_ewaste} corporate recycling batches.
- **Ted Autonomous AI Employee**: Successfully handled {interactions_count} customer sessions with automated triage and proposal drafting."""

        return {
            "summary_text": summary_text,
            "total_leads": total_leads,
            "hot_leads": hot_leads,
            "total_proposals": total_proposals,
            "pending_approval": pending_approval,
            "approved_proposals": approved_proposals,
            "total_pipeline_val": total_pipeline_val,
            "approved_revenue": approved_revenue,
            "total_repairs": total_repairs,
            "total_carbon_offset": total_carbon_offset,
            "interactions_count": interactions_count
        }

    def chat(self, user_message: str, session_id: str = None, visitor_name: str = "Visitor", visitor_email: str = None) -> dict:
        if not session_id:
            session_id = f"sess_{random.randint(100000, 999999)}"

        intent = self.analyze_intent(user_message)
        extracted = self.extract_contact_info(user_message)
        if extracted.get("name"):
            visitor_name = extracted["name"]
        if extracted.get("email"):
            visitor_email = extracted["email"]

        reply = ""
        suggested_actions = []
        generated_proposal = None
        diagnostic_result = None
        lead_captured = False
        requires_human_approval = False
        sentiment = "neutral"

        # Check intent branch
        if intent == "greeting":
            reply = (
                f"Hello and welcome to **MaxReT3ch AI**! I am **Ted**, the company's autonomous digital employee.\n\n"
                f"I am here to assist you with our six core technological pillars:\n"
                f"1. **Artificial Intelligence Solutions** (Agents, LLMs, Computer Vision)\n"
                f"2. **Website & Software Development** (Full-Stack, SaaS, Cloud APIs)\n"
                f"3. **Computer Hardware** (Custom Workstations, Repairs, Certified Refurbished)\n"
                f"4. **IT Technical Support** (24/7 Managed IT, Security Defense)\n"
                f"5. **Green Tech & E-Waste Recycling** (Zero-Landfill, Instant Buyback, ESG Offsets)\n"
                f"6. **Technology Education** (Interactive Coding Tutorials & Masterclasses)\n\n"
                f"How may I engineer a solution for you today? Would you like a project quotation, hardware diagnosis, or service overview?"
            )
            suggested_actions = [
                {"label": "💡 Request Project Quotation", "action": "request_quote"},
                {"label": "🔧 Diagnose Hardware Issue", "action": "troubleshoot"},
                {"label": "🌱 E-Waste Trade-In Estimator", "action": "ewaste"},
                {"label": "💻 Explore Custom Workstations", "action": "hardware"}
            ]

        elif intent == "request_proposal":
            sentiment = "positive"
            # Did user provide email/details?
            effective_name = visitor_name if visitor_name != "Visitor" else (extracted.get("name") or "Valued Client")
            effective_email = visitor_email or extracted.get("email") or "client.inquiry@maxret3ch.ai"
            effective_comp = extracted.get("company", "Client Enterprise")

            generated_proposal = self.generate_automated_proposal(
                client_name=effective_name,
                client_email=effective_email,
                client_company=effective_comp,
                text=user_message
            )
            requires_human_approval = True
            reply = (
                f"Understood! I have analyzed your project requirements and generated an itemized engineering quotation: **{generated_proposal['quote_number']}**.\n\n"
                f"📋 **Project:** {generated_proposal['project_title']}\n"
                f"⏱️ **Estimated Turnaround:** {generated_proposal['estimated_days']} business days\n"
                f"💵 **Subtotal:** KSh {generated_proposal['subtotal']:,.2f}\n"
                f"🎁 **Ted Loyalty Discount (8%):** -KSh {generated_proposal['discount']:,.2f}\n"
                f"💳 **Estimated Total (incl. 16% VAT):** **KSh {generated_proposal['total_amount']:,.2f}**\n\n"
                f"⚠️ **Human Approval Protocol**: In accordance with MaxReT3ch AI governance standards, this quotation has been entered into our **Executive Human Approval Queue** for Managing Director sign-off. "
                f"You can review the full itemized breakdown below or download the formal proposal."
            )
            suggested_actions = [
                {"label": "📄 View Formal Quotation", "action": f"view_proposal_{generated_proposal['quote_number']}"},
                {"label": "📞 Schedule Consultation Call", "action": "book_consultation"},
                {"label": "💬 Modify Requirements", "action": "modify_scope"}
            ]

        elif intent == "hardware_troubleshooting":
            sentiment = "urgent"
            diag = self.process_troubleshooting(user_message)
            diagnostic_result = diag
            steps_joined = "\n".join(diag["steps"])
            reply = (
                f"I am initiating MaxReT3ch Technical Diagnostic Triage for: **{diag['category'].replace('_', ' ').title()}** (Severity: {diag['severity'].upper()}).\n\n"
                f"Here are my recommended troubleshooting triage steps:\n\n"
                f"{steps_joined}\n\n"
                f"Would you like me to book a prioritized bench repair ticket with our micro-soldering laboratory for physical multimeter/thermal camera analysis?"
            )
            suggested_actions = [
                {"label": "🎫 Book Hardware Repair Ticket", "action": "book_repair"},
                {"label": "🔍 Speak with Hardware Engineer", "action": "contact_support"},
                {"label": "🛒 View Replacement Hardware", "action": "view_hardware"}
            ]

        elif intent == "ewaste_recycling":
            reply = (
                f"MaxReT3ch AI operates a certified **Zero-Landfill Green Tech Facility** with DoD 5220.22-M data sanitization!\n\n"
                f"Here is how we assist your organization:\n"
                f"• **Instant Fleet Trade-In**: We buy back enterprise laptops, servers, and GPUs at top market rates.\n"
                f"• **ESG Carbon Offset Certification**: Every kilogram of hardware recycled earns you documented environmental carbon credits.\n"
                f"• **Free Pickup**: Complimentary logistics for lots of 5+ units.\n\n"
                f"Use our instant green trade-in calculator or tell me what equipment you would like to responsibly recycle!"
            )
            suggested_actions = [
                {"label": "🌱 Open Trade-In Calculator", "action": "open_ewaste_calculator"},
                {"label": "🚚 Schedule Corporate Pickup", "action": "schedule_ewaste_pickup"}
            ]

        elif intent == "education_inquiry":
            reply = (
                f"Welcome to **MaxReT3ch AI Education Hub**! I provide 24/7 interactive code mentoring and feedback.\n\n"
                f"Our curriculum covers:\n"
                f"1. **Autonomous AI Agents & Tool Calling in Python** (Intermediate)\n"
                f"2. **Real-Time FastAPI & WebSocket Telemetry** (Intermediate)\n"
                f"3. **Component-Level Multi-Rail Power Diagnostics & Micro-soldering** (Advanced)\n\n"
                f"Every course includes interactive sandbox exercises, real-world case studies, and official MaxReT3ch accreditation."
            )
            suggested_actions = [
                {"label": "🎓 Browse Tutorial Catalog", "action": "view_tutorials"},
                {"label": "🚀 Launch Agent Coding Sandbox", "action": "launch_sandbox"}
            ]

        elif intent == "marketing_bizdev":
            camp = self.generate_marketing_campaign("AI & Sustainable Tech Leadership", "CTOs & Tech Founders", "linkedin")
            reply = (
                f"I have initialized a marketing & business development campaign for MaxReT3ch AI!\n\n"
                f"**Channel:** {camp['channel'].upper()}\n"
                f"**Target Audience:** {camp['target_audience']}\n\n"
                f"**Draft Copy:**\n{camp['content']}\n\n"
                f"This draft has been stored in your Admin Marketing Studio for team review."
            )
            suggested_actions = [
                {"label": "📢 View Marketing Studio", "action": "view_marketing"},
                {"label": "✉️ Generate Cold Email Draft", "action": "generate_email_campaign"}
            ]

        elif intent == "business_report":
            report = self.generate_business_report()
            reply = report["summary_text"]
            suggested_actions = [
                {"label": "📊 Open Full Executive Dashboard", "action": "open_dashboard"},
                {"label": "✅ Review Pending Approvals", "action": "open_approvals"}
            ]

        elif intent.startswith("inquiry_"):
            vert_key = intent.replace("inquiry_", "")
            vert_info = SERVICES_KB.get(vert_key, SERVICES_KB["ai_solutions"])
            reply = (
                f"**{vert_info['title']}** is one of our flagship specialties at MaxReT3ch AI.\n\n"
                f"{vert_info['pitch']}\n\n"
                f"• Starting pricing: from **KSh {vert_info['base_rate']:,}**\n"
                f"• Average turnaround: **{vert_info['typical_timeline_days']} business days**\n\n"
                f"Tell me about your specific requirements, and I can generate an exact scope and quotation for human approval!"
            )
            suggested_actions = [
                {"label": f"📑 Get Quote for {vert_info['title']}", "action": f"quote_{vert_key}"},
                {"label": "📞 Contact Specialist", "action": "contact_lead"}
            ]

        else:
            # General inquiry
            reply = (
                f"Thank you for contacting MaxReT3ch AI. As the autonomous operations specialist, I am configured to assist with any of our services: "
                f"Artificial Intelligence, Software Engineering, Hardware Sales & Component Repair, Managed IT Support, Green E-Waste Recycling, and Tech Education.\n\n"
                f"Feel free to ask a specific technical question, request a proposal, or report a hardware issue!"
            )
            suggested_actions = [
                {"label": "💡 Request a Project Proposal", "action": "request_quote"},
                {"label": "🔧 Troubleshoot a PC Issue", "action": "troubleshoot"},
                {"label": "📊 View Business Performance", "action": "business_report"}
            ]

        # Auto-capture lead if contact details were provided or project discussed
        if extracted.get("email") or (intent == "request_proposal" and visitor_email):
            lead_email = extracted.get("email") or visitor_email
            lead_name = extracted.get("name") or visitor_name
            lead_comp = extracted.get("company", "Inquiring Enterprise")
            lead_budget = extracted.get("budget", 350000.0)

            score = "hot" if (lead_budget >= 300000 or intent == "request_proposal") else "warm"

            conn = get_db()
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            
            # Check if lead exists
            cursor.execute("SELECT id FROM leads WHERE email = ?", (lead_email,))
            existing = cursor.fetchone()
            if not existing:
                cursor.execute("""
                INSERT INTO leads (name, email, phone, company, vertical_interest, requirements_summary, estimated_budget, score, status, captured_by, ai_confidence, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'new', 'ted_ai', 0.95, ?, ?, ?)
                """, (
                    lead_name, lead_email, extracted.get("phone", ""), lead_comp,
                    intent.replace("inquiry_", "") if intent.startswith("inquiry_") else "ai_solutions",
                    user_message[:300], lead_budget, score, f"Captured via Ted interactive session {session_id}", now, now
                ))
                lead_captured = True
            conn.commit()
            conn.close()

        # Log Ted Interaction
        try:
            conn = get_db()
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            transcript_item = [
                {"sender": "user", "text": user_message},
                {"sender": "ted", "text": reply}
            ]
            cursor.execute("""
            INSERT INTO ted_interactions (session_id, visitor_name, visitor_email, messages_count, summary, sentiment, primary_intent, action_items_json, transcript_json, created_at)
            VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, visitor_name, visitor_email or "",
                f"Session handled by Ted. Intent: {intent}. Actions suggested.",
                sentiment, intent, json.dumps([a["label"] for a in suggested_actions]),
                json.dumps(transcript_item), now
            ))
            conn.commit()
            conn.close()
        except Exception:
            pass

        return {
            "reply": reply,
            "session_id": session_id,
            "detected_intent": intent,
            "suggested_actions": suggested_actions,
            "generated_proposal": generated_proposal,
            "diagnostic_result": diagnostic_result,
            "lead_captured": lead_captured,
            "requires_human_approval": requires_human_approval,
            "sentiment": sentiment
        }

ted_engine = TedAIEngine()
