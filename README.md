# 🚀 Team Task Manager (Full-Stack Python Application)

A robust, full-stack collaborative workspace application built entirely within the **Python ecosystem**. This application enables organization teams to initialize project containers, provision deliverables, and track operational progress in real-time utilizing strict **Role-Based Access Control (RBAC)** filters (Admin vs. Member privileges).

## 🔗 Submission Deliverables
* **Live Application URL:** [Insert your Railway app live link here, e.g., https://team-task-manager.up.railway.app]
* **GitHub Repository:** [Insert your GitHub repo link here]
* **Walkthrough Demo Video:** [Insert Loom/YouTube link here]

---

## 🛠️ Unified Python Tech Stack

To meet rapid delivery metrics without introducing heavy JavaScript overhead, the platform architecture utilizes a decoupled API-first design written 100% in Python:

* **Backend Engine (REST APIs):** **FastAPI** — Chosen for its performance, automatic OpenAPI (Swagger) documentation generation, and native asynchronous execution capabilities.
* **Frontend Interface (UI):** **Streamlit** — Leveraged to build highly responsive, state-driven user management dashboards directly out of clean Python logic files.
* **Database Layer:** **SQLite / PostgreSQL** mapped seamlessly through **SQLAlchemy Object-Relational Mapper (ORM)** to manage cascaded data relationships.
* **Data Verification:** **Pydantic v2** — Enforces runtime schema type-casting and valid email constraints (`EmailStr`).
* **Security Layer:** **Passlib (Bcrypt)** for cryptographic password hashing and **PyJWT** for generating secure JSON Web Tokens.

---

## 🔑 Operational Architecture & Feature Set

### 1. Verification & Security Layer
* Register accounts with designated security roles (`Admin` or `Member`).
* Secure credential extraction via OAuth2 password flows exchanging short-lived JWT tokens.

### 2. Role-Based Access Control (RBAC) Matrix
* **Administrators:** Hold complete read/write clearance across the platform workspace. Admins can initialize brand new Project portfolios, provision tasks, assign operations to any team asset, and view system-wide cross-team analytical dashboards.
* **Members:** Restrictive access filters. Members see a customized workspace populated solely with task cards explicitly assigned to their specific user ID. They carry clearance to transition their assigned task states but cannot access structural administrative configuration blocks.

### 3. Analytics & Dashboard Metrics
* Real-time workspace aggregation displaying **Total Scope, Pending Deliverables, Active In-Progress Tasks**, and **Completed Deliverables**.
* **🚨 Overdue Indicator Logic:** System automatically cross-checks live calendar instances (`datetime.today()`) against unfinished deliverables to instantly isolate lagging tasks.

---

## 📂 Project Directory Breakdown

```text
team-task-manager/
├── backend/
│   ├── database.py      # SQLAlchemy connection settings & request engines
│   ├── main.py          # FastAPI application controllers, security & endpoints
│   ├── models.py        # Relational database table structural maps
│   └── schemas.py       # Pydantic payloads data-validation guidelines
├── frontend/
│   └── app.py           # Streamlit UI layouts & API requester modules
├── Dockerfile           # Multistage container production packaging instructions
├── requirements.txt     # Global Python environment dependencies checklist
├── start.sh             # Combined background production runtime supervisor script
└── README.md            # Execution documentation