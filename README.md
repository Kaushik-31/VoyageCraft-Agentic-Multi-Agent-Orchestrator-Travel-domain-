

# 🚀 VoyageCraft – End-to-End Multi-Agent Orchestrator (Travel Domain)

VoyageCraft is an **end-to-end AI system** that combines a **multi-agent LLM backend** with a **modern web frontend**.  
It demonstrates how to design, orchestrate, and evaluate intelligent agents working together to solve a real-world problem — **personalized travel planning**.

---

## ✨ Key Highlights
- **End-to-End System**: From request → orchestration → reasoning trace → frontend visualization.  
- **Multi-Agent Orchestration**: Planner, Critic, Budget, and extensible agents coordinate via ReAct-style loops (and later, graph orchestration).  
- **Explainability Built-In**: Every decision logged in a transparent trace.  
- **LLM-First Design**: Supports both local models (Ollama) and cloud APIs (OpenAI, Claude, Gemini).  
- **Scalable Architecture**: Modular backend with API layer + Next.js frontend.  

---

## 🧩 Architecture

```

voyagecraft/
├─ backend/                  # Multi-agent + API layer (FastAPI)
│  ├─ agents/                # Planner, Budget, Critic, etc.
│  ├─ orchestrators/         # Coordination strategies (ReAct, Graph, Debate)
│  ├─ tools/                 # External APIs (maps, weather, events)
│  └─ app/                   # FastAPI routes, models, config
├─ frontend/                 # Next.js + Tailwind web app
│  ├─ src/app/               # Pages (trip form, itinerary display)
│  └─ components/            # Reusable UI components
├─ evaluations/              # Scenario-based testing & rubric evals
└─ utils/                    # Shared schemas, trace logs, helpers

````

---

## 🏗️ System Architecture

```mermaid
flowchart LR
    subgraph Frontend [🌐 Frontend – Next.js + Tailwind]
        UI[User Interface]
        Form[Trip Form Input]
        Itinerary[Itinerary Display + Trace Logs]
    end

    subgraph Backend [⚙️ Backend – FastAPI]
        API[/REST API/]
        Orchestrator[Multi-Agent Orchestrator]
    end

    subgraph Agents [🤖 Agents Layer]
        Planner[🧭 Planner Agent]
        Critic[🔎 Critic Agent]
        Budget[💰 Budget Agent]
        Weather[☁️ Weather Agent]
        Events[🎭 Event Agent]
        Memory[🧠 Memory Agent]
    end

    subgraph Tools [🔌 Tools & External Data]
        LLM[(LLM – Ollama / OpenAI / Claude / Gemini)]
        Maps[(OpenTripMap API)]
        WeatherAPI[(OpenWeatherMap API)]
        EventsAPI[(Ticketmaster API)]
    end

    %% Connections
    UI --> Form --> API
    Itinerary <-- API
    API --> Orchestrator
    Orchestrator --> Planner
    Orchestrator --> Critic
    Orchestrator --> Budget
    Orchestrator --> Weather
    Orchestrator --> Events
    Orchestrator --> Memory

    Planner --> LLM
    Critic --> LLM
    Budget --> LLM
    Weather --> WeatherAPI
    Events --> EventsAPI
    Planner --> Maps

    Orchestrator --> Itinerary
````

---

## 🔄 Workflow (Sequence)

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Orchestrator
    participant Planner
    participant Critic
    participant Budget

    User->>Frontend: Submit trip request
    Frontend->>Backend: Send request via REST API
    Backend->>Orchestrator: Pass TripRequest
    Orchestrator->>Planner: Generate draft itinerary
    Planner->>Orchestrator: Return draft plan
    Orchestrator->>Critic: Analyze & flag issues
    Critic->>Orchestrator: Return feedback
    Orchestrator->>Budget: Estimate total cost
    Budget->>Orchestrator: Return cost estimate
    Orchestrator->>Backend: Final Plan + Trace
    Backend->>Frontend: JSON response
    Frontend->>User: Display itinerary + decision trace
```

---

## 🛠 Tech Stack

* **Backend:** Python 3.11+, FastAPI, Pydantic, Typer, Rich
* **Frontend:** Next.js (App Router), TailwindCSS, Framer Motion
* **LLM Integration:**

  * Local → [Ollama](https://ollama.ai) (LLaMA, Mistral, Phi)
  * Cloud → OpenAI, Claude, Gemini
* **External APIs (free tiers):** OpenTripMap, OpenWeatherMap, Ticketmaster
* **Evaluation:** pytest + rubric harness

---

## 🚦 Quickstart

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open: [http://localhost:3000](http://localhost:3000)

---

## 🔮 Roadmap

* [x] Core orchestration (Planner, Critic, Budget agents)
* [x] FastAPI backend with schemas + traces
* [x] Next.js frontend for end-user interaction
* [ ] Weather + Event agents for contextual re-planning
* [ ] Real-time tool integration (flights, weather, events)
* [ ] Debate & consensus orchestration strategies
* [ ] Persistent memory agents
* [ ] End-to-end evaluation harness
* [ ] Deployment (Vercel + Render/Fly.io)

---

## 📚 What This Project Demonstrates

* **Advanced LLM Orchestration** → multi-agent collaboration, critique loops.
* **End-to-End Design** → full-stack system (backend + frontend).
* **Scalability** → modular agents, orchestration strategies, pluggable LLMs.
* **Evaluation Rigor** → reproducible scenarios, decision trace logs, rubrics.

---

## 📄 License

MIT – free for academic, personal, or commercial use.

```
