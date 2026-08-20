# 🧠 RUDRA — AI-Powered Smart Campus Assistant

<p align="center">

**Responsive Unified Digital Resource Assistant**

An intelligent, multi-agent AI assistant that gives students, faculty, and administrators **instant, accurate, and context-aware access to campus information through a single conversational interface.**

<br/>

![RUDRA](https://img.shields.io/badge/RUDRA-AI%20Smart%20Campus-6366F1?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge\&logo=react\&logoColor=black)
![Gemini](https://img.shields.io/badge/Gemini%202.5%20Flash-LLM-4285F4?style=for-the-badge\&logo=google)
![TypeScript](https://img.shields.io/badge/TypeScript-Frontend-3178C6?style=for-the-badge\&logo=typescript\&logoColor=white)

</p>

---

## 🌟 What is RUDRA?

Modern campuses contain information across **websites, PDFs, spreadsheets, notices, academic records, policies, and departmental systems**.

Students often need to search through multiple sources just to answer a simple question.

### ❌ Traditional Approach

```text
Student
   │
   ├── College Website
   ├── PDF Documents
   ├── Notices
   ├── Excel / CSV Files
   ├── Department Pages
   └── Multiple Portals
```

### ✅ RUDRA Approach

```text
                         ┌─────────────────────┐
                         │       USER          │
                         │ Student / Faculty   │
                         │ / Administration    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       RUDRA         │
                         │ Conversational AI   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Intelligent Planner │
                         │ & Orchestrator      │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
               Structured        RAG / Docs      Memory
                 Data             Search         Context
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
                         ┌─────────────────────┐
                         │ Google Gemini 2.5   │
                         │       Flash        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Context-Aware       │
                         │ Natural Response    │
                         └─────────────────────┘
```

> **One interface. Multiple campus services. One intelligent assistant.**

---

# 🎯 Problem Statement

Campus information is fragmented across different sources and systems.

Students and faculty frequently face problems such as:

* 🔎 Difficulty finding the correct information
* 📄 Searching through lengthy PDFs and documents
* 🗂️ Information distributed across multiple departments
* ⏱️ Time wasted navigating different portals
* ❓ Difficulty understanding policies and procedures
* 🔄 Repeatedly asking staff the same questions
* 🧩 Lack of personalized, context-aware responses

### RUDRA solves this by providing a unified conversational interface for campus information.

---

# 💡 Proposed Solution

RUDRA combines:

* 🤖 **Multi-Agent AI**
* 🧠 **Intelligent Query Planning**
* 📚 **Retrieval-Augmented Generation (RAG)**
* 🔍 **Hybrid Information Retrieval**
* 💬 **Conversation Memory**
* ⚡ **Fast structured-data lookup**
* 🧩 **Context-aware response generation**

The system determines **what the user is asking, which information source is required, which specialized agent should handle it, and how the final answer should be generated.**

---

# 🏗️ System Architecture

```mermaid
flowchart TD

    U[👤 User]

    FE[💻 React + TypeScript Frontend]

    API[⚡ FastAPI Backend]

    OP[🧠 Intelligent Query Planner]

    OR[🎯 Orchestrator Agent]

    MEM[(🧠 Conversation Memory)]

    RET[🔎 Retrieval Layer]

    EXACT[⚡ Exact Match]

    ALIAS[🔤 Alias Resolution]

    FUZZY[🔍 RapidFuzz Search]

    RAG[📚 RAG Knowledge Retrieval]

    CB[🧩 Context Builder]

    LLM[🤖 Google Gemini 2.5 Flash]

    RESP[💬 Natural Language Response]

    U --> FE
    FE --> API
    API --> OP

    OP <--> MEM
    OP --> OR

    OR --> RET

    RET --> EXACT
    RET --> ALIAS
    RET --> FUZZY
    RET --> RAG

    EXACT --> CB
    ALIAS --> CB
    FUZZY --> CB
    RAG --> CB

    MEM --> CB
    CB --> LLM
    LLM --> RESP
    RESP --> FE
    FE --> U
```

---

# 🤖 Multi-Agent Architecture

RUDRA follows a **specialized-agent architecture**, where each agent focuses on a particular campus domain.

```mermaid
flowchart TB

    USER[👤 User Query]

    ORCH[🧠 Orchestrator Agent]

    USER --> ORCH

    ORCH --> STUDENT[🎓 Student Agent]
    ORCH --> FACULTY[👨‍🏫 Faculty Agent]
    ORCH --> ACADEMIC[📚 Academic Agent]
    ORCH --> FINANCE[💰 Finance Agent]
    ORCH --> TRANSPORT[🚌 Transport Agent]
    ORCH --> LIBRARY[📖 Library Agent]
    ORCH --> PLACEMENT[💼 Placement Agent]
    ORCH --> CALENDAR[📅 Calendar Agent]
    ORCH --> ADMIN[🏛️ Administration Agent]
    ORCH --> SERVICES[🎯 Student Services Agent]
    ORCH --> RAG[📄 RAG Knowledge Agent]

    STUDENT --> DATA[(Campus Data)]
    FACULTY --> DATA
    ACADEMIC --> DATA
    FINANCE --> DATA
    TRANSPORT --> DATA
    LIBRARY --> DATA
    PLACEMENT --> DATA
    CALENDAR --> DATA
    ADMIN --> DATA
    SERVICES --> DATA
    RAG --> DOCS[(📚 Documents / PDFs)]
```

---

# 🧩 AI Agents

| Agent                         | Responsibility                                        |
| ----------------------------- | ----------------------------------------------------- |
| 🎓 **Student Agent**          | Student-related information and services              |
| 👨‍🏫 **Faculty Agent**       | Faculty directory, subjects and schedules             |
| 📚 **Academic Agent**         | Courses, subjects, academic information               |
| 💰 **Finance Agent**          | Fees and finance-related information                  |
| 🚌 **Transport Agent**        | Bus routes, stops and transport information           |
| 📖 **Library Agent**          | Library timings, services and resources               |
| 💼 **Placement Agent**        | Placement information and eligibility                 |
| 📅 **Calendar Agent**         | Academic calendar and important dates                 |
| 🏛️ **Administration Agent**  | Administrative information                            |
| 🎯 **Student Services Agent** | Campus/student support services                       |
| 📄 **RAG Knowledge Agent**    | Document and policy-based question answering          |
| 🧠 **Orchestrator Agent**     | Understands intent and coordinates specialized agents |

---

# 🔄 End-to-End Query Flow

Suppose a student asks:

> **"Who teaches Operating Systems?"**

RUDRA processes the request through multiple stages.

```mermaid
sequenceDiagram

    participant U as 👤 User
    participant F as 💻 Frontend
    participant B as ⚡ FastAPI
    participant O as 🧠 Orchestrator
    participant A as 👨‍🏫 Faculty Agent
    participant R as 🔎 Retrieval
    participant L as 🤖 Gemini
    participant M as 🧠 Memory

    U->>F: Who teaches Operating Systems?
    F->>B: Send user query
    B->>O: Analyze intent

    O->>O: Detect domain = Faculty
    O->>A: Route request

    A->>R: Search faculty data
    R->>R: Exact Match
    R->>R: Alias Resolution
    R->>R: RapidFuzz

    R-->>A: Relevant faculty information
    A-->>O: Retrieved context

    O->>M: Retrieve conversation context
    M-->>O: Relevant history

    O->>L: Context + User Query
    L-->>O: Natural language answer

    O-->>B: Final response
    B-->>F: Stream response
    F-->>U: Display answer
```

---

# 🔎 Hybrid Retrieval System

RUDRA does not rely solely on an LLM to find information.

Instead, it combines **deterministic retrieval techniques with generative AI**.

```mermaid
flowchart LR

    Q[❓ User Query]

    Q --> PRE[Query Normalization]

    PRE --> EXACT{Exact Match?}

    EXACT -->|Yes| RESULT[✅ Retrieved Data]

    EXACT -->|No| ALIAS[🔤 Alias Resolution]

    ALIAS --> FUZZY[🔍 RapidFuzz]

    FUZZY --> SCORE{Similarity Score}

    SCORE -->|High| RESULT

    SCORE -->|Low| RAG[📚 RAG Retrieval]

    RAG --> RESULT

    RESULT --> CONTEXT[🧩 Context Builder]

    CONTEXT --> LLM[🤖 Gemini]

    LLM --> ANSWER[💬 Final Answer]
```

### Why this approach?

| Technique            | Purpose                                             |
| -------------------- | --------------------------------------------------- |
| **Exact Match**      | Fast and deterministic retrieval                    |
| **Alias Resolution** | Handles abbreviations and alternate names           |
| **RapidFuzz**        | Handles spelling variations and approximate queries |
| **RAG**              | Retrieves information from documents                |
| **Gemini**           | Converts retrieved context into natural language    |

This reduces unnecessary LLM reasoning and improves **speed, grounding, and reliability**.

---

# 📚 RAG Pipeline

For policies, handbooks, notices, and other unstructured documents, RUDRA uses Retrieval-Augmented Generation.

```mermaid
flowchart TD

    DOC[📄 Campus Documents]

    DOC --> EXTRACT[Text Extraction]

    EXTRACT --> CHUNK[✂️ Document Chunking]

    CHUNK --> EMB[🧠 Embeddings]

    EMB --> STORE[(🗄️ Vector Database)]

    QUERY[❓ User Question]

    QUERY --> QEMB[🧠 Query Embedding]

    QEMB --> SEARCH[🔎 Similarity Search]

    STORE --> SEARCH

    SEARCH --> TOP[📑 Relevant Chunks]

    TOP --> CONTEXT[🧩 Context Builder]

    CONTEXT --> LLM[🤖 Gemini]

    LLM --> RESPONSE[💬 Grounded Response]
```

### RAG in RUDRA

```text
Documents
   ↓
Text Extraction
   ↓
Chunking
   ↓
Embeddings
   ↓
Vector Storage
   ↓
Semantic Retrieval
   ↓
Relevant Context
   ↓
Gemini
   ↓
Grounded Answer
```

> RAG allows RUDRA to answer questions from campus documents without expecting the LLM to memorize the entire knowledge base.

---

# 🧠 Conversation Memory

RUDRA maintains relevant conversational context to support follow-up questions.

### Example

```text
User:
Who teaches Operating Systems?

RUDRA:
Dr. XYZ teaches Operating Systems.

User:
What is their qualification?

RUDRA:
Dr. XYZ holds a Ph.D. in Computer Science.
```

The second query can use the context established by the first interaction.

```mermaid
flowchart LR

    Q1[Question 1]
    A1[Answer 1]

    Q2[Follow-up Question]

    MEM[(🧠 Conversation Memory)]

    Q1 --> A1
    A1 --> MEM

    Q2 --> MEM
    MEM --> CTX[Context Resolution]

    CTX --> LLM[🤖 Gemini]
    LLM --> A2[Context-Aware Answer]
```

---

# ⚡ Intelligent Query Planning

The Query Planner determines how the request should be processed.

```mermaid
flowchart TD

    Q[User Query]

    Q --> N[Normalize Query]

    N --> I[Intent Detection]

    I --> D{Determine Domain}

    D -->|Faculty| F[Faculty Agent]
    D -->|Academic| A[Academic Agent]
    D -->|Finance| FN[Finance Agent]
    D -->|Transport| T[Transport Agent]
    D -->|Library| L[Library Agent]
    D -->|Placement| P[Placement Agent]
    D -->|Calendar| C[Calendar Agent]
    D -->|Student| S[Student Agent]
    D -->|Policy / Document| R[RAG Agent]

    F --> RET[Retrieve Information]
    A --> RET
    FN --> RET
    T --> RET
    L --> RET
    P --> RET
    C --> RET
    S --> RET
    R --> RET

    RET --> CTX[Build Context]
    CTX --> LLM[Gemini]
    LLM --> ANSWER[Final Response]
```

---

# 🎯 Example Use Cases

## 👨‍🏫 Faculty

```text
"Who teaches Operating Systems?"
"Show the faculty handling Data Structures."
"Who is the HOD of CSE?"
```

## 🎓 Students

```text
"Show my attendance."
"What subjects do I have today?"
"Where can I find my academic information?"
```

## 💰 Finance

```text
"What is the tuition fee?"
"Show my fee details."
"What are the payment deadlines?"
```

## 🚌 Transport

```text
"Which buses pass through Karmanghat?"
"What is the route for Bus 12?"
"Where is the nearest bus stop?"
```

## 💼 Placements

```text
"Am I eligible for placements?"
"What are the placement requirements?"
"Which companies are visiting?"
```

## 📖 Library

```text
"What are the library timings?"
"How can I access library resources?"
"What are the library rules?"
```

## 📅 Academic

```text
"When are the semester exams?"
"Explain the attendance policy."
"When does the semester begin?"
```

---

# 🛠️ Technology Stack

## Frontend

| Technology      | Purpose                        |
| --------------- | ------------------------------ |
| ⚛️ React        | UI development                 |
| 📘 TypeScript   | Type-safe frontend development |
| ⚡ Vite          | Development and build tooling  |
| 🎨 Tailwind CSS | Styling                        |
| 🧩 shadcn/ui    | Reusable UI components         |

## Backend

| Technology   | Purpose                       |
| ------------ | ----------------------------- |
| 🐍 Python    | Core backend language         |
| ⚡ FastAPI    | REST API and backend services |
| 🐼 Pandas    | Structured data processing    |
| 🔤 RapidFuzz | Fuzzy matching                |
| ⚙️ AsyncIO   | Asynchronous processing       |

## AI Layer

| Technology                  | Purpose                            |
| --------------------------- | ---------------------------------- |
| 🤖 Google Gemini 2.5 Flash  | Response generation                |
| 🧠 Multi-Agent Architecture | Domain specialization              |
| 📚 RAG                      | Document-based knowledge retrieval |
| 🔎 Hybrid Retrieval         | Accurate information lookup        |
| 🧠 Conversation Memory      | Context-aware conversations        |

---

# 🏛️ Layered Architecture

```mermaid
flowchart TB

    subgraph PRESENTATION["🎨 Presentation Layer"]
        UI[React + TypeScript]
        CHAT[Conversational UI]
    end

    subgraph APPLICATION["⚡ Application Layer"]
        API[FastAPI]
        PLANNER[Query Planner]
        ORCH[Orchestrator]
    end

    subgraph AGENT["🤖 Agent Layer"]
        AGENTS[Specialized AI Agents]
    end

    subgraph RETRIEVAL["🔎 Retrieval Layer"]
        EXACT[Exact Search]
        ALIAS[Alias Resolution]
        FUZZY[RapidFuzz]
        RAG[RAG Retrieval]
    end

    subgraph KNOWLEDGE["🗄️ Knowledge Layer"]
        CSV[CSV / Structured Data]
        DOCS[PDF / Documents]
        VECTOR[Vector Store]
    end

    subgraph AI["🧠 Intelligence Layer"]
        MEMORY[Conversation Memory]
        CONTEXT[Context Builder]
        GEMINI[Gemini 2.5 Flash]
    end

    PRESENTATION --> APPLICATION
    APPLICATION --> AGENT
    AGENT --> RETRIEVAL
    RETRIEVAL --> KNOWLEDGE
    RETRIEVAL --> AI
    KNOWLEDGE --> AI
    AI --> PRESENTATION
```

---

# 📂 Project Structure

```text
RUDRA/
│
├── Backend/
│   ├── app/
│   │   ├── main.py
│   │   └── ...
│   │
│   ├── agents/
│   │   ├── student_agent/
│   │   ├── faculty_agent/
│   │   ├── academic_agent/
│   │   ├── finance_agent/
│   │   ├── transport_agent/
│   │   ├── library_agent/
│   │   ├── placement_agent/
│   │   ├── calendar_agent/
│   │   ├── administration_agent/
│   │   ├── student_services_agent/
│   │   └── rag_agent/
│   │
│   ├── orchestrator/
│   ├── services/
│   ├── memory/
│   ├── tests/
│   ├── requirements.txt
│   └── .env
│
├── Frontend/
│   └── RUDRA-FRONTEND/
│       ├── src/
│       ├── public/
│       ├── package.json
│       └── ...
│
├── AI-AGENTS/
│   ├── Student_Agent/
│   ├── Faculty_Agent/
│   ├── Academic_Agent/
│   ├── Transport_Agent/
│   ├── Finance_Agent/
│   ├── Library_Agent/
│   ├── Placement_Agent/
│   ├── RAG_Agent/
│   └── ...
│
└── README.md
```

---

# 🔄 Request Lifecycle

```text
┌───────────────────────────────────────────────────────┐
│                     USER QUERY                        │
└──────────────────────────┬────────────────────────────┘
                           ↓
┌───────────────────────────────────────────────────────┐
│                  QUERY NORMALIZATION                  │
└──────────────────────────┬────────────────────────────┘
                           ↓
┌───────────────────────────────────────────────────────┐
│              INTENT + DOMAIN DETECTION                │
└──────────────────────────┬────────────────────────────┘
                           ↓
┌───────────────────────────────────────────────────────┐
│                 ORCHESTRATOR AGENT                    │
└──────────────────────────┬────────────────────────────┘
                           ↓
                  ┌────────┴────────┐
                  ↓                 ↓
          Structured Data        Documents
                  ↓                 ↓
          Exact / Fuzzy           RAG
             Search             Retrieval
                  └────────┬────────┘
                           ↓
┌───────────────────────────────────────────────────────┐
│                    CONTEXT BUILDER                    │
└──────────────────────────┬────────────────────────────┘
                           ↓
┌───────────────────────────────────────────────────────┐
│                GEMINI 2.5 FLASH                       │
└──────────────────────────┬────────────────────────────┘
                           ↓
┌───────────────────────────────────────────────────────┐
│              CONTEXT-AWARE RESPONSE                   │
└───────────────────────────────────────────────────────┘
```

---

# 🔐 Security & Reliability

RUDRA is designed with backend security and response reliability in mind.

### 🔒 Security

* Environment-based API key management
* `.env` excluded from version control
* Backend-controlled access to AI services
* Input validation through FastAPI
* Separation of frontend and backend responsibilities

### 🎯 Reliability

* Deterministic exact-match retrieval
* Alias resolution
* Fuzzy matching
* RAG grounding
* Context-aware generation
* Agent specialization
* Automated testing

---

# 📊 Why Multi-Agent AI?

A single general-purpose LLM can answer questions, but it does not provide the same level of **domain separation, controllability, and extensibility**.

### Traditional Single-Agent Approach

```text
User
 ↓
One LLM
 ↓
Generic Answer
```

### RUDRA Multi-Agent Approach

```text
                         User
                           │
                           ▼
                    Orchestrator
                           │
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
     Academic          Finance          Transport
       Agent             Agent             Agent
          ↓                ↓                ↓
       Academic          Fee              Bus
        Data             Data            Data
          └────────────────┼────────────────┘
                           ↓
                    Context Builder
                           ↓
                       Gemini
                           ↓
                    Final Answer
```

### Benefits

* 🎯 Domain-specific reasoning
* 🧩 Modular architecture
* 🔄 Easier maintenance
* 📈 Scalable to additional services
* 🔐 Better control over data access
* 🧪 Easier testing
* ⚡ Efficient query routing

---

# 🌟 Key Features

* 🤖 **12-Agent Multi-Agent Architecture**
* 🧠 **Intelligent Query Planning**
* 📚 **Retrieval-Augmented Generation**
* 🔎 **Hybrid Search**
* ⚡ **Exact Match Retrieval**
* 🔤 **Alias Resolution**
* 🔍 **RapidFuzz Similarity Search**
* 🧠 **Conversation Memory**
* 🧩 **Context Builder**
* 🌐 **Streaming AI Responses**
* 💬 **Natural Language Interface**
* 🔒 **Secure Backend Architecture**
* 📊 **Structured + Unstructured Data Support**
* 🧪 **Testing and Validation**

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Hrithik-ui753/Rudra.git

cd Rudra
```

---

## 2. Backend Setup

```bash
cd Backend

pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

---

## 3. Frontend Setup

Open a new terminal:

```bash
cd Frontend/RUDRA-FRONTEND

npm install

npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# 🔑 Environment Variables

Create a `.env` file inside the `Backend` directory.

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

> ⚠️ **Never commit API keys or `.env` files to GitHub.**

Recommended `.gitignore`:

```gitignore
.env
__pycache__/
*.pyc
node_modules/
dist/
```

---

# 🧪 Testing

RUDRA includes backend testing for critical components such as:

```text
API Endpoints
     ↓
Agent Routing
     ↓
Retrieval
     ↓
Fuzzy Matching
     ↓
RAG
     ↓
Memory
     ↓
Response Generation
```

Run backend tests with:

```bash
pytest
```

---

# 📸 Demo Scenarios

### Scenario 1 — Faculty Search

```text
👤 User:
Who teaches Operating Systems?

🤖 RUDRA:
Operating Systems is handled by Dr. ______.
```

### Scenario 2 — Transport

```text
👤 User:
Which buses pass through Karmanghat?

🤖 RUDRA:
The following campus buses serve routes passing
through Karmanghat: ______.
```

### Scenario 3 — Policy Question

```text
👤 User:
Explain the attendance policy.

🤖 RUDRA:
According to the retrieved academic policy...
```

### Scenario 4 — Contextual Follow-up

```text
👤 User:
Who teaches Operating Systems?

🤖 RUDRA:
Dr. XYZ teaches Operating Systems.

👤 User:
What is their qualification?

🤖 RUDRA:
Dr. XYZ holds a Ph.D. in Computer Science.
```

---

# 🚀 Future Roadmap

```mermaid
timeline

    title RUDRA Future Roadmap

    Phase 1 : Core Multi-Agent System
             : Query Planning
             : Agent Routing
             : RAG
             : Conversation Memory

    Phase 2 : Personalization
             : Student Authentication
             : Personalized Responses
             : User Profiles

    Phase 3 : Multimodal AI
             : Voice Assistant
             : OCR
             : Document Upload
             : Image Understanding

    Phase 4 : Accessibility
             : Mobile Application
             : WhatsApp Integration
             : Notifications

    Phase 5 : Intelligence
             : Analytics Dashboard
             : Predictive Insights
             : Proactive Campus Notifications

    Phase 6 : Deployment
             : Cloud Infrastructure
             : Production Monitoring
             : Scalable Agent Services
```

### Planned Improvements

* 🎙️ Voice Assistant
* 📱 Mobile Application
* 📄 OCR-based Document Upload
* 💬 WhatsApp Integration
* 🔐 Student Authentication
* 📊 Analytics Dashboard
* 🔔 Notification System
* ☁️ Cloud Deployment
* 🤝 More specialized agents
* 🧠 Advanced personalization

---

# 🏆 Impact

## For Students

* ⚡ Faster access to information
* 🔎 Less manual searching
* 💬 Natural-language interaction
* 🧠 Context-aware conversations
* 📚 Centralized campus knowledge

## For Faculty

* 📋 Easier access to academic information
* 🗂️ Reduced repetitive queries
* ⚡ Faster information retrieval

## For Administration

* 📉 Reduced support workload
* 📊 Better information accessibility
* 🧩 Centralized campus knowledge system

## For the Institution

* 🚀 Digital transformation
* 🤖 AI-powered campus services
* 📈 Scalable architecture
* 🌐 Unified information access

---

# 💎 What Makes RUDRA Different?

RUDRA is more than a chatbot.

```text
                 CHATBOT
                    │
          ┌─────────┴─────────┐
          ↓                   ↓
       LLM Only          Generic FAQ
          │
          │
          ▼
        RUDRA
          │
   ┌──────┼──────┐
   ↓      ↓      ↓
 Agents   RAG   Memory
   │      │      │
   └──────┼──────┘
          ↓
    Query Planning
          ↓
   Hybrid Retrieval
          ↓
   Context Building
          ↓
   Grounded Response
```

### RUDRA combines:

> **Multi-Agent Intelligence + RAG + Hybrid Retrieval + Conversation Memory + Structured Campus Data**

into one unified campus assistant.

---

# 👥 Team

Developed as part of a **Smart Campus AI Hackathon Project**.

### Team RUDRA

> Building intelligent, accessible, and scalable AI solutions for smarter campuses.

---

# 📄 License

This project is developed for **educational and hackathon purposes**.

---

# ⭐ Support the Project

If you found RUDRA useful or interesting, consider giving the repository a ⭐ on GitHub.

---

<div align="center">

## 🧠 RUDRA

### **Making Campus Information Smarter, Faster, and More Accessible with AI.**

**Ask. Retrieve. Understand. Respond.**

</div>
