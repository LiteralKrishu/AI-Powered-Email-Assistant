# 📧 AI-Powered-Email-Assistant

> 🤖 Intelligent email management system for modern organizations.  
> Fetches, categorizes, prioritizes, and drafts AI-powered responses to customer support emails.  

![Build](https://img.shields.io/badge/build-MVP-informational?style=flat-square)
![Tech Stack](https://img.shields.io/badge/stack-FastAPI%2C%20React%2C%20Postgres-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## 🚀 Project Objective

**AI-Powered-Email-Assistant** is designed to help support teams manage **hundreds (or thousands) of daily emails** efficiently.  
It automatically **retrieves support emails, analyzes sentiment, assigns priority, extracts key details, and generates context-aware replies** using LLMs.  

This ensures **faster, empathetic, and accurate responses**, reducing manual effort while boosting customer satisfaction.

---

## 🧱 Architecture & Workflow

```text
     ┌ ───────────────────── ┐
     │     Email Server      │
     │ (Gmail/Outlook/IMAP)  │
     └ ───────────────────── ┘
                 │
     ┌───────────▼───────────┐
     │ Email Retrieval Layer │
     │ (IMAP/Gmail API)      │
     └───────────┬───────────┘
                 │
             Raw Emails
                 │
     ┌───────────▼───────────┐
     │ Preprocessing & NLP   │
     │ - Filtering           │
     │ - Sentiment Analysis  │
     │ - Priority Detection  │
     │ - Info Extraction     │
     └───────────┬───────────┘
                 │
     ┌───────────▼───────────┐
     │ AI Response Generator │
     │ - Context Embedding   │
     │ - RAG (Knowledge Base)│
     │ - LLM Draft Replies   │
     └───────────┬───────────┘
                 │
     ┌───────────▼───────────┐
     │ Database (Postgres)   │
     │ Emails + Metadata     │
     └───────────┬───────────┘
                 │
     ┌───────────▼───────────┐
     │ Dashboard (React/Next)│
     │ - Email List + Details│
     │ - Analytics & Stats   │
     │ - Draft Reply Review  │
     └───────────────────────┘
```

---

## 📦 Tech Stack

| Layer       | Technology                           |
|-------------|---------------------------------------|
| Backend     | Python, FastAPI, Uvicorn             |
| NLP / AI    | Hugging Face (DistilBERT, RoBERTa), OpenAI GPT, FAISS for RAG |
| Database    | PostgreSQL                           |
| Frontend    | React / Next.js, TailwindCSS, Recharts |
| Deployment  | Docker, docker-compose               |

---

## 🗂 Project Phases & Deliverables

### Phase 1: Planning & Setup
- Define requirements  
- Setup repo, `.env`, base project structure  
📁 Deliverables:  
`README.md`, base FastAPI app, frontend scaffold

---

### Phase 2: Email Retrieval & Storage
- Connect to Gmail/Outlook IMAP API  
- Filter subjects: *Support, Query, Request, Help*  
- Store raw + metadata in PostgreSQL  
📁 Deliverables:  
`/backend/email_service.py`, database schema

---

### Phase 3: NLP Processing
- Sentiment classification (Positive/Negative/Neutral)  
- Urgency detection (keywords: *immediately, critical, cannot access*)  
- Information extraction (phone, product, requirements)  
📁 Deliverables:  
`/backend/nlp_pipeline.py`, test data runs

---

### Phase 4: AI-Powered Responses
- RAG layer for contextual replies (knowledge base + embeddings)  
- LLM draft reply generation (empathetic + product-aware)  
📁 Deliverables:  
`/backend/ai_responder.py`, OpenAI integration

---

### Phase 5: Dashboard Development
- List emails (sortable by priority)  
- Email detail view (raw + extracted info + AI draft)  
- Analytics: total emails, sentiment breakdown, pending vs resolved  
📁 Deliverables:  
`/frontend/pages/*.tsx`, `Recharts` graphs

---

### Phase 6: Final Integration & Testing
- SMTP/Gmail API for sending replies  
- Docker-compose setup for full stack  
📁 Deliverables:  
Working end-to-end MVP  

---

## ⚙️ Setup Instructions

### Backend Setup
1. Navigate to project:
   ```bash
   cd AI-Powered-Email-Assistant
   ```
2. Create virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate environment:
   - Windows: `venv\Scripts\activate`  
   - macOS/Linux: `source venv/bin/activate`  
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Update `.env` with actual credentials.  
6. Run app:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup
1. Navigate to frontend:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Install Recharts:
   ```bash
   npm install recharts
   ```
4. Start dev server:
   ```bash
   npm run dev
   ```

### Docker Setup (Optional)
1. Update `.env` with credentials.  
2. Run:
   ```bash
   docker-compose up
   ```

---

## 🌐 Access the Application
- Backend API → [http://localhost:8000](http://localhost:8000)  
- Frontend → [http://localhost:3000](http://localhost:3000)  
- API Docs → [http://localhost:8000/docs](http://localhost:8000/docs)  

---

## ⚠️ Notes
- Enable **IMAP** and generate an **App Password** for Gmail.  
- Requires **OpenAI API key** (or custom LLM endpoint).  
- Ensure **PostgreSQL** is running and accessible.  

---

## 📧 Example Email Flow

**Raw Email**  
```
From: diana@client.co  
Subject: URGENT - General query about subscription
Body: Hi team, I am unable to log into my account since yesterday. Please fix this immediately. My phone number is 9876543210.  
```

**Extracted Info**  
- Sender: `diana@client.co`  
- Subject: "URGENT - General query about subscription"  
- Sentiment: Negative  
- Priority: Urgent  
- Phone: 9876543210  
- Requirement: Account recovery  

**AI Draft Response**  
```
Hi [Customer Name],

I understand how frustrating it must be to be locked out of your account, and I sincerely apologize for the inconvenience.  
Our support team is already looking into this issue, and we will help restore your account access as quickly as possible.  

I will personally ensure this case is treated with top priority. Meanwhile, could you please confirm the last login attempt (date/time) for verification?  

Thank you for your patience.  

Best regards,  
[Your Support Team]  
```

---
