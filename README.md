# 🧠 RUDRA – AI Powered Smart Campus Assistant

> **Responsive Unified Digital Resource Assistant (RUDRA)** is an AI-powered Smart Campus Assistant designed to provide students, faculty, and administrators with instant, accurate, and context-aware access to campus information through a unified conversational interface.

---

## 🚀 Overview

RUDRA simplifies campus interactions by combining multiple specialized AI agents into a single intelligent assistant. Instead of searching across portals, PDFs, notices, and spreadsheets, users can simply ask questions in natural language.

Examples:

- 📚 "Who teaches Operating Systems?"
- 🚌 "Which buses pass through Karmanghat?"
- 💰 "Show my fee details."
- 🎓 "Am I eligible for placements?"
- 📅 "Explain the attendance policy."

---

# ✨ Features

- 🤖 Multi-Agent AI Architecture
- 🧠 Intelligent Query Planning & Routing
- 💬 Natural Language Conversations
- 📚 Academic Information
- 👨‍🏫 Faculty Directory
- 🚌 Transport Information
- 💰 Fee Structure & Finance
- 📖 Library Services
- 💼 Placement Information
- 📅 Academic Calendar
- 🏛️ Student Services
- 📄 Campus Policies & Handbooks
- 🧠 Conversation Memory
- ⚡ Fast Retrieval (Exact Match + Alias Resolution + RapidFuzz)
- 🌐 Streaming AI Responses
- 🔒 Secure Backend Architecture

---

# 🏗️ System Architecture

```
                User
                  │
                  ▼
        React + TypeScript Frontend
                  │
                  ▼
             FastAPI Backend
                  │
                  ▼
        Intelligent Query Planner
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
 Multi-Agent Routing     Conversation Memory
        │
        ▼
 Exact Match
        │
 Alias Resolution
        │
 RapidFuzz Search
        │
        ▼
 Context Builder
        │
        ▼
 Google Gemini 2.5 Flash
        │
        ▼
 Natural Response
```

---

# 🤖 AI Agents

RUDRA consists of specialized AI agents responsible for different campus domains:

- 🎓 Student Agent
- 👨‍🏫 Faculty Agent
- 📚 Academic Agent
- 💰 Finance Agent
- 🚌 Transport Agent
- 📖 Library Agent
- 💼 Placement Agent
- 📅 Calendar Agent
- 🏛️ Administration Agent
- 🎯 Student Services Agent
- 📄 RAG Knowledge Agent
- 🧠 Orchestrator Agent

---

# 🛠 Tech Stack

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui

## Backend

- FastAPI
- Python
- Google Gemini 2.5 Flash
- RapidFuzz
- Pandas
- AsyncIO

## AI

- Multi-Agent Architecture
- Intelligent Query Planner
- Conversation Memory
- Context Builder
- RAG-based Knowledge Retrieval

---

# 📂 Project Structure

```
RUDRA
│
├── Backend
│   ├── app
│   ├── agents
│   ├── orchestrator
│   ├── services
│   ├── memory
│   └── tests
│
├── Frontend
│   └── RUDRA-FRONTEND
│
├── AI-AGENTS
│   ├── Student_Agent
│   ├── Faculty_Agent
│   ├── Academic_Agent
│   ├── Transport_Agent
│   ├── Finance_Agent
│   ├── Library_Agent
│   ├── Placement_Agent
│   ├── RAG_Agent
│   └── ...
│
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/Hrithik-ui753/Rudra.git
cd Rudra
```

---

## Backend

```bash
cd Backend

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend runs at:

```
http://localhost:8000
```

---

## Frontend

```bash
cd Frontend/RUDRA-FRONTEND

npm install

npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

# 🔑 Environment Variables

Create a `.env` file inside the Backend folder.

Example:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

> **Do not commit your `.env` file to GitHub.**

---

# 📸 Example Queries

### Faculty

```
Who teaches Operating Systems?
```

### Student

```
Show my attendance.
```

### Finance

```
Show my fee details.
```

### Placement

```
Am I eligible for placements?
```

### Transport

```
Which buses pass through Karmanghat?
```

### Library

```
Library timings
```

### Academic

```
Explain the attendance policy.
```

---

# 🚀 Future Improvements

- Voice Assistant
- Mobile Application
- OCR-based Document Upload
- WhatsApp Integration
- Student Authentication
- Analytics Dashboard
- Notification System
- Cloud Deployment

---

# 👥 Team

Developed as part of a Smart Campus AI Hackathon Project.

---

# 📄 License

This project is intended for educational and hackathon purposes.

---

# ⭐ Support

If you found this project useful, consider giving the repository a ⭐ on GitHub.

---

## 🌟 RUDRA — Making Campus Information Smarter, Faster, and More Accessible with AI.
