# 🚀 AIBench – AI Evaluation & Benchmarking Platform
![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![AI](https://img.shields.io/badge/AI-NLP-orange)
> **Production-grade AI evaluation system** that generates responses using Groq (LLaMA 3.1), evaluates them with hybrid NLP metrics, and provides real-time benchmarking dashboards.

---

## 🌟 Overview

**AIBench** is a full-stack AI benchmarking platform designed to simulate **enterprise-level LLM evaluation systems**.

It allows you to:

* ⚡ Generate responses using **Groq API (LLaMA 3.1)**
* 🧠 Evaluate outputs using NLP + rule-based scoring
* 📊 Track performance via real-time dashboards
* 🗂️ Store and analyze historical benchmarks

---

## 🎯 Key Features

### 🧪 AI Playground

* Input prompt → generate response via **Groq (LLaMA 3.1-8B)**
* Instant evaluation:

  * Semantic similarity
  * Keyword relevance
  * Coherence
  * Length & quality

---

### 📊 Real-Time Dashboard

* Total requests
* Average score
* Average latency
* System health

---

### 🗂️ Benchmark History

* Stores:

  * Prompt
  * Response
  * Score
  * Latency
  * Timestamp

---

### ⚡ Hybrid Evaluation Engine

```text
Semantic Similarity  → Sentence Transformers
Keyword Relevance    → Lexical overlap
Coherence Score      → Sentence consistency
Length Score         → Structural quality
Error Detection      → Rule-based filtering
```

---

## 🧠 Architecture

```text
Frontend (Vanilla JS)
        ↓
FastAPI Backend
        ↓
Groq API (LLaMA 3.1-8B Instant)
        ↓
Evaluation Engine (Hybrid NLP + Rules)
        ↓
Database (SQLite / PostgreSQL)
        ↓
Dashboard + Analytics
```

---

## 🛠️ Tech Stack

| Layer      | Technology                          |
| ---------- | ----------------------------------- |
| Backend    | FastAPI                             |
| AI API     | Groq API (LLaMA 3.1-8B Instant)     |
| NLP        | sentence-transformers, scikit-learn |
| Database   | SQLite / PostgreSQL                 |
| ORM        | SQLAlchemy                          |
| Frontend   | HTML, CSS, Vanilla JS               |
| Deployment | Docker, Uvicorn                     |

---

## ⚡ Quick Start

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2️⃣ Setup environment

```bash
cp .env.example .env
```

Add your Groq API key:

```env
GROQ_API_KEY=your_api_key_here
MODEL=llama-3.1-8b-instant
```

---

### 3️⃣ Run server

```bash
python -m uvicorn app.main:app --reload
```

---

### 🌐 Open in browser

* App → http://localhost:8000
* Docs → http://localhost:8000/docs

---

## 📡 API Endpoints

### 🔹 Generate & Evaluate

```http
POST /api/generate
```

```json
{
  "input": "Explain quantum computing in simple terms"
}
```

---

### 🔹 Fetch History

```http
GET /api/history
```

---

### 🔹 Metrics

```http
GET /api/metrics
```

---

### 🔹 Health Check

```http
GET /health
```

---

## 🐳 Docker Setup

```bash
docker-compose up --build
```

---

## 📈 Performance Highlights

* ⚡ Ultra-low latency via **Groq inference engine**
* 🧠 Hybrid evaluation pipeline
* 📊 Real-time analytics
* 🔁 RLHF-ready architecture

---

## 🧠 What Makes This Special

✔ Uses **real LLM inference (Groq)**
✔ Implements **evaluation pipeline like enterprise AI labs**
✔ Combines **ML + backend + product design**

---

## 🚀 Future Improvements

* 🔁 RLHF-based feedback learning
* 📊 Model comparison leaderboard
* ⚡ Batch evaluation pipelines
* 🧠 Custom fine-tuned scoring models

---

## 👨‍💻 Author

**Shivansh Thakur**
[Linkedin](https://linkedin.com/in/thakur-shivansh)

---

## ⭐ If you like this project

Give it a ⭐ and share 🚀

