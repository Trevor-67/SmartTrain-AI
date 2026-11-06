# SmartTrain AI

**AI-Assisted Training Request Management and Scheduling System**

SmartTrain AI is a Flask-based web application prototype designed to simplify the management and scheduling of training requests. It aims to reduce manual coordination by assisting with request processing, trainer assignment, availability checking and scheduling.

The project explores how AI-assisted workflows can improve the way training requests are handled, while keeping human intervention available when automatic scheduling cannot be completed.

> **Project status:** Work in Progress 🚧  
> SmartTrain is an actively developed prototype. Some workflows are implemented, while further development and external integrations are still planned.

---

## 1. The Problem

Managing training requests manually can create administrative challenges, particularly when multiple trainers are responsible for different training sessions.

The process can involve:

- Reviewing incoming training requests.
- Identifying the type of training required.
- Checking trainer availability.
- Assigning suitable trainers.
- Coordinating training dates and times.
- Following up on missing information.
- Updating request statuses and communicating with customers.

These activities can become time-consuming when trainers have limited availability and multiple requests need attention.

## 2. The Solution

SmartTrain AI aims to streamline this process through a centralised web application that assists with training request management and scheduling.

The application uses AI-assisted request processing and automated scheduling logic to help identify training requirements, allocate trainers and handle cases that require additional attention.

When automatic processing cannot complete a request, the application provides a Human Review workflow.

## 3. Key Features

The following features are implemented in the current prototype:

### Training Request Management
- Create and manage training requests.
- Capture customer information and training requirements.
- Record training types, delivery methods, participant numbers and preferred dates.
- View individual training case details.

### AI-Assisted Request Processing
- Process training request information.
- Identify missing information.
- Generate clarification messages.
- Update cases based on additional customer information.

### Trainer Assignment and Scheduling
- Automated trainer assignment and scheduling logic.
- Trainer availability checking.
- Calendar-based availability views.
- Training booking management.

### Human Review
- Identify cases that cannot be automatically scheduled.
- Escalate cases for human intervention.
- View outstanding cases in a dedicated review queue.
- Resolve reviewed cases.

### Case Tracking and Communication
- Track case statuses.
- Maintain case activity timelines.
- Store customer and system conversation messages.
- Record booking information and training feedback.

### Dashboard
- Centralised training case overview.
- Training request statistics.
- Status tracking for scheduled, completed and outstanding cases.
- Upcoming booking information.

### Demo Data
- Generate seven synthetic training cases for demonstration and testing.
- Reset demonstration data when required.

---

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and backend development |
| Flask | Web application framework |
| SQLite | Database management and data storage |
| HTML | Web page structure |
| CSS | User interface styling |
| JavaScript | Frontend functionality |

---

## 5. Project Structure

```text
SmartTrain-AI/
│
├── services/
│   ├── ai_service.py
│   ├── availability.py
│   ├── booking.py
│   ├── conversation.py
│   ├── human_review.py
│   ├── scheduling.py
│   ├── timeline.py
│   └── trainer_assignment.py
│
├── templates/
│   └── HTML application templates
│
├── app.py
├── database.py
├── smarttrain.db
├── test_ai.py
├── test_availability.py
├── test_scheduling.py
├── .gitignore
└── README.md
```

The structure may evolve as additional functionality is introduced.

---

## 6. Getting Started

### Prerequisites

- Python 3.10 or later.
- pip (Python package installer).
- Git.
- Visual Studio Code or another Python development environment.

### Installation

**Step 1: Clone the repository**

```bash
git clone https://github.com/Trevor-67/SmartTrain-AI.git
```

**Step 2: Navigate to the project directory**

```bash
cd SmartTrain-AI
```

**Step 3: Create a virtual environment**

```bash
python -m venv .venv
```

**Step 4: Activate the virtual environment**

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

**Step 5: Install Flask**

```bash
pip install Flask
```

Additional Python packages may be required depending on the AI service implementation and its configured dependencies.

**Step 6: Run the application**

```bash
python app.py
```

**Step 7: Open the application**

Navigate to:

```text
http://127.0.0.1:5000
```

The application runs locally using Flask's development server.

---

## 7. Database

SmartTrain uses SQLite for local data storage.

The database manages information relating to:

- Training cases.
- Trainer bookings.
- Notifications.
- Outlook event records.
- Case activity timelines.
- Customer conversations.
- Training feedback.

The database schema is initialised through the application's database module.

---

## 8. Testing

The repository includes separate test scripts covering:

- AI request processing.
- Trainer availability.
- Scheduling functionality.

These scripts support ongoing development and testing of the application's individual components.

---

## 9. Development Roadmap

SmartTrain is still under development. Future improvements include:

- [ ] Complete and refine AI-assisted request processing.
- [ ] Improve automated trainer allocation and scheduling.
- [ ] Expand trainer availability management.
- [ ] Integrate WhatsApp for customer training requests.
- [ ] Implement Salesforce case integration.
- [ ] Explore Microsoft Outlook calendar integration.
- [ ] Improve notification and customer communication workflows.
- [ ] Introduce user authentication and role-based access.
- [ ] Improve error handling and application security.
- [ ] Expand automated testing.
- [ ] Prepare the application for deployment.

---

## 10. Project Purpose

SmartTrain AI is a practical software development project focused on exploring AI-assisted workflow automation, application development, database management and business process improvement.

It provides an opportunity to apply Python, Flask, SQL and software development principles to a practical scheduling and resource management problem.

The project is continuously evolving as new functionality is developed, tested and refined.

---

## 11. Repository

**GitHub:**  
https://github.com/Trevor-67/SmartTrain-AI

**Project:** SmartTrain AI

**Status:** Work in Progress

