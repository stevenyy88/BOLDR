# BOLDR — Architecture Documentation

**Project:** BOLDR — Self-Improving Customer Intelligence Engine  
**Track:** REVENUE ROCKET — Sales, Marketing, and Customer Acquisition  
**Author:** Steve Ng, Founder and CEO — Digital Futures Consultancy LLP  
**Date:** 2026-05-17

---

## 1. System Architecture

The BOLDR Intelligence Engine is a containerised, self-hosted system with three core services orchestrated by Docker Compose.

```mermaid
graph TB
    subgraph External Channels
        EMAIL[Gmail Inbox]
        IG[Instagram DM]
        WA[WhatsApp]
        CHAT[Chat Webhook]
    end

    subgraph Docker Compose Environment
        subgraph n8n["n8n Workflow Engine"]
            TRIGGER[Multi-Channel Trigger]
            CLASSIFY[Intent & Persona Classifier]
            RETRIEVE[KB Retriever]
            DRAFT[Reply Drafter]
            GAP[Gap Detector]
            UPDATE[KB Auto-Updater]
            CLUSTER[Theme Clusterer]
            BRIEF[Marketing Brief Generator]
            SENTIMENT[Sentiment Benchmarker]
        end

        subgraph APP["Python App (Streamlit + Processing)"]
            DASHBOARD[Approval Queue Dashboard]
            KBINDEX[KB Indexer]
            EMBED[Embedding Pipeline]
            LLM[LLM Integration<br/>GLM-5.1 / Claude]
        end

        subgraph CHROMA["ChromaDB"]
            VECTORS[Vector Index<br/>BGE-m3 / all-MiniLM-L6-v2]
            KEYWORDS[Keyword Index]
        end

        subgraph KBSTORE["Knowledge Base (Git)"]
            FAQ[FAQ Entries<br/>Markdown]
            PRODUCTS[Product Specs<br/>Markdown + JSON]
            RATES[Rate Cards<br/>CSV]
            SOP[CS SOP<br/>Markdown]
        end
    end

    EMAIL --> TRIGGER
    IG --> TRIGGER
    WA --> TRIGGER
    CHAT --> TRIGGER

    TRIGGER --> CLASSIFY
    CLASSIFY --> RETRIEVE
    RETRIEVE -->|Answer Found| DRAFT
    RETRIEVE -->|No Answer| GAP
    DRAFT --> DASHBOARD
    DASHBOARD -->|Approved| EMAIL
    GAP -->|Escalate to CS| DASHBOARD
    GAP --> CLUSTER
    CLUSTER --> BRIEF
    UPDATE --> KBSTORE
    KBSTORE --> KBINDEX
    KBINDEX --> VECTORS
    KBINDEX --> KEYWORDS

    CLASSIFY -.->|LLM API| LLM
    RETRIEVE -.->|Hybrid Search| CHROMA
    DRAFT -.->|LLM API| LLM
    GAP -.->|LLM API| LLM
    CLUSTER -.->|LLM API| LLM
    BRIEF -.->|LLM API| LLM
    SENTIMENT -.->|NLP + Web| LLM

    style EMAIL fill:#4285F4,color:#fff
    style IG fill:#E1306C,color:#fff
    style WA fill:#25D366,color:#fff
    style CHAT fill:#FF6B6B,color:#fff
    style n8n fill:#FF6D5A,color:#fff
    style APP fill:#1E88E5,color:#fff
    style CHROMA fill:#7C4DFF,color:#fff
    style KBSTORE fill:#66BB6A,color:#fff
```

### Component Summary

| Component | Technology | Role | Docker Image |
|---|---|---|---|
| **Workflow Engine** | n8n (self-hosted) | Orchestrates the entire intelligence loop | `n8nio/n8n:latest` |
| **Vector Store** | ChromaDB | Stores and retrieves KB document embeddings | `chromadb/chroma:latest` |
| **LLM** | GLM-5.1 (API) + Claude (fallback) | Classification, drafting, clustering, gap detection | Cloud API (no container) |
| **Embedding** | BGE-m3 / all-MiniLM-L6-v2 | Document and query embedding | Built into Python app |
| **App Server** | Python 3.12 + Streamlit | Dashboard, KB processing, approval queues | `python:3.12-slim` (custom) |
| **Knowledge Base** | Markdown + JSON + CSV | Source documents, version-controlled in Git | Volume mount |

---

## 2. Data Flow — Ticket Processing Pipeline

This diagram shows the complete journey of a customer ticket from intake to resolution.

```mermaid
flowchart TD
    START([Customer Enquiry Received]) --> INGEST{Channel?}
    
    INGEST -->|Email| GMAIL[Gmail API Trigger]
    INGEST -->|Instagram| IG[n8n Instagram DM Trigger]
    INGEST -->|WhatsApp| WA[n8n WhatsApp Trigger]
    INGEST -->|Chat| CHAT[n8n Webhook Trigger]
    
    GMAIL --> NORMALIZE[Normalize & Clean Input]
    IG --> NORMALIZE
    WA --> NORMALIZE
    CHAT --> NORMALIZE
    
    NORMALIZE --> EXTRACT[Extract Subject + Body]
    EXTRACT --> PII[Strip PII<br/>Names, emails, addresses]
    
    PII --> CLASSIFY[Intent Classification<br/>LLM structured output]
    CLASSIFY --> PERSONA[Persona Tagging<br/>7-persona taxonomy]
    PERSONA --> SCORE[Confidence Scoring<br/>0.0 - 1.0]
    
    SCORE --> RETRIEVE[Hybrid KB Search]
    RETRIEVE --> VECTOR[Vector Search<br/>ChromaDB semantic match]
    RETRIEVE --> KEYWORD[Keyword Search<br/>Exact match fallback]
    
    VECTOR --> MERGE[Merge & Rank Results]
    KEYWORD --> MERGE
    
    MERGE --> CHECK{Confidence ≥ 0.5?}
    
    CHECK -->|Yes - Answer Found| DRAFT[Draft Reply<br/>BOLDR brand voice]
    CHECK -->|No - Gap Detected| GAPTYPE{Gap Type?}
    
    GAPTYPE -->|Order Operations<br/>Needs Shopify| SHOPIFY[Route to CS<br/>+ Shopify lookup prompt]
    GAPTYPE -->|Knowledge Gap<br/>Needs new KB entry| ESCALATE[Escalate to CS<br/>+ Pre-filled draft]
    GAPTYPE -->|Escalation Trigger<br/>SOP Section 7| ESCALATE2[Escalate to CS<br/>Priority routing]
    
    DRAFT --> QUEUE[Human Approval Queue<br/>Streamlit Dashboard]
    SHOPIFY --> QUEUE
    ESCALATE --> QUEUE
    ESCALATE2 --> QUEUE
    
    QUEUE --> REVIEW{Human Reviews}
    REVIEW -->|Approve| SEND[Send Reply<br/>via original channel]
    REVIEW -->|Edit & Approve| SEND
    REVIEW -->|Reject| REJECT[Discard Draft<br/>Manual handling]
    
    SEND --> LOG[Log Interaction<br/>Intent + persona + source]
    REJECT --> LOG
    
    LOG --> THEME[Feed to Theme Clusterer<br/>Weekly batch]
    THEME --> BRIEF[Monthly Marketing Brief<br/>Persona-tagged actions]
    
    ESCALATE --> RESOLVE{CS Resolves}
    RESOLVE -->|Answer Found| AUTODRAFT[Auto-Draft KB Entry<br/>LLM generates entry]
    RESOLVE -->|Needs investigation| PENDING[Add to Knowledge Gap Log]
    
    AUTODRAFT --> KBAPPROVAL[1-Click KB Approval<br/>Streamlit Dashboard]
    KBAPPROVAL -->|Approved| INDEX[Index in ChromaDB<br/>System is now smarter]
    KBAPPROVAL -->|Rejected| PENDING
    
    PENDING --> WATCHLIST[Watch for Resolution<br/>Manual KB update]
    
    style START fill:#4CAF50,color:#fff
    style SEND fill:#2196F3,color:#fff
    style INDEX fill:#FF9800,color:#fff
    style BRIEF fill:#9C27B0,color:#fff
    style QUEUE fill:#FF5722,color:#fff
```

### Decision Points

| Decision | Logic | Routing |
|---|---|---|
| **Confidence ≥ 0.5?** | Hybrid retrieval confidence score | Yes → Draft reply. No → Gap detection. |
| **Gap type?** | SOP-derived classification | Order ops → Shopify prompt. Knowledge gap → CS escalation. Escalation trigger → Priority routing. |
| **Human review?** | All drafted replies require human approval | Approve/Edit → Send. Reject → Manual handling. |
| **KB approval?** | Auto-drafted KB entries require human approval | Approved → Index in ChromaDB. Rejected → Pending investigation. |

---

## 3. KB Update Loop — Gap Detection to Knowledge Growth

This diagram shows how knowledge gaps are detected, resolved, and fed back into the system.

```mermaid
flowchart LR
    subgraph Detection
        A[Low-Confidence<br/>KB Retrieval] --> B[Gap Detector<br/>LLM Classification]
        B --> C{Gap Type?}
        C -->|Order Operations| D[Shopify Dependency<br/>Not a KB gap]
        C -->|Knowledge Gap| E[True KB Gap]
        C -->|Escalation Trigger| F[SOP Rule<br/>Priority Escalation]
    end
    
    subgraph Resolution
        E --> G[CS Team Resolves<br/>Manually]
        G --> H[Resolution Documented<br/>Answer + sources]
        D --> I[CS Team Handles<br/>+ Shopify lookup]
        I --> J[Optional: Create<br/>Order FAQ KB entry]
        F --> K[CS Team Handles<br/>Per SOP protocol]
    end
    
    subgraph Auto-Draft
        H --> L[LLM Auto-Drafts<br/>KB Entry]
        L --> M[Pre-filled Template<br/>Title + content + sources + tags]
        M --> N[1-Click Approval<br/>Streamlit Dashboard]
        N -->|Approved| O[KB Entry Committed<br/>Markdown + JSON]
        N -->|Edit & Approve| P[Modified Entry<br/>Committed]
        N -->|Reject| Q[Discarded<br/>Gap stays in log]
    end
    
    subgraph Indexing
        O --> R[Parse & Chunk<br/>KB Indexer]
        P --> R
        R --> S[Generate Embeddings<br/>BGE-m3 / all-MiniLM]
        S --> T[Index in ChromaDB<br/>Vector + keyword]
        T --> U([System Now Smarter<br/>Gap Closed!])
    end
    
    subgraph Version Control
        O --> V[Git Commit<br/>KB version history]
        P --> V
        V --> W[Diff View Available<br/>Rollback capability]
        W --> X[Approval Timestamp<br/>+ Editor logged]
    end
    
    style U fill:#4CAF50,color:#fff
    style T fill:#7C4DFF,color:#fff
    style O fill:#FF9800,color:#fff
    style N fill:#FF5722,color:#fff
```

### Gap Classification Logic

| Gap Type | Signal | Action | KB Update? |
|---|---|---|---|
| **Order Operations** | Order tracking, shipping, refunds, address changes | Route to CS with Shopify lookup prompt | Optional (FAQ-style entry) |
| **True Knowledge Gap** | Product specs, sustainability, niche compatibility | Escalate to CS, auto-draft KB entry on resolution | Yes — auto-drafted |
| **Escalation Trigger** | Angry customer, chargeback, warranty >10 days, corporate >5 units, press | Priority route per SOP Section 7 | No — handled per protocol |

### Confidence Threshold

| Confidence Score | Range | Action |
|---|---|---|
| **High** | 0.8–1.0 | Auto-draft reply with source citation |
| **Medium** | 0.5–0.79 | Draft reply, flag for careful review |
| **Low** | 0.3–0.49 | Route to gap detection, provide pre-filled draft to CS |
| **Very Low** | 0.0–0.29 | Route directly to CS, no draft attempt |

---

## 4. Theme Clustering Pipeline

This diagram shows how unresolved tickets are clustered into themes and surfaced as marketing intelligence.

```mermaid
flowchart TD
    subgraph Input
        A[Resolved Tickets<br/>Intent + persona tags] 
        B[Unresolved Tickets<br/>Gap classifications]
        C[New Questions Log<br/>From SOP]
    end
    
    A --> D[Weekly Batch Collection]
    B --> D
    C --> D
    
    D --> E[Embedding Generation<br/>BGE-m3 vector embeddings]
    E --> F[Similarity Clustering<br/>Cosine similarity + LLM labeling]
    
    F --> G{Cluster Significance?}
    G -->|Recurring Theme<br/>≥3 tickets| H[Significant Cluster]
    G -->|One-off<br/><3 tickets| I[Anomaly Watch<br/>No action yet]
    
    H --> J[LLM Cluster Labeling<br/>E.g., 'BPA-free straps']
    J --> K[Persona Distribution<br/>E.g., 70% Health-Conscious]
    K --> L[Marketing Action Mapping<br/>Persona → action]
    
    subgraph Actions
        L --> M[Product Badge<br/>E.g., 'BPA-Free Straps']
        L --> N[Content Gap<br/>E.g., 'Vegan materials FAQ']
        L --> O[Campaign Idea<br/>E.g., 'Corporate gifting page']
        L --> P[Pricing Insight<br/>E.g., 'Bulk discount tiers']
    end
    
    M --> Q[Weekly Theme Report<br/>Auto-generated]
    N --> Q
    O --> Q
    P --> Q
    
    Q --> R[Monthly Marketing Brief<br/>Synthesised from 4 weekly reports]
    
    R --> S[Action Items<br/>Prioritised by persona frequency]
    R --> T[Revenue Signals<br/>New segments + campaign ideas]
    R --> U[KB Gaps to Close<br/>Suggested KB entries]
    R --> V[Competitive Intelligence<br/>Cross-referenced with external sentiment]
    
    subgraph Sentiment Bonus
        W[Reddit r/Watches<br/>WatchUSeek<br/>Competitor Reviews] --> X[External Sentiment Analysis<br/>NLP + scraping]
        X --> Y{Internal matches<br/>external themes?}
        Y -->|Yes| Z[Cross-validated Signal<br/>Higher priority]
        Y -->|No| AA[Market-wide Trend<br/>Not BOLDR-specific]
        Z --> V
        AA --> V
    end
    
    style R fill:#9C27B0,color:#fff
    style Q fill:#FF9800,color:#fff
    style H fill:#4CAF50,color:#fff
    style Z fill:#2196F3,color:#fff
```

### Persona-to-Action Mapping

| Buyer Persona | Recurring Theme | Marketing Action |
|---|---|---|
| Health-Conscious | BPA-free straps, nickel allergy, skin reactions | Add "BPA-Free" & "Hypoallergenic" product badges |
| Gifter | Engraving options, gift wrap, birthday urgency | Create "Gift Guide" landing page with engraving upsell |
| Enthusiast | Strap compatibility, model specs, swimming suitability | Build "Compatibility Checker" tool on product pages |
| Niche Buyer | Magnetic fields, altitude, extreme sports, collaborations | Develop "Technical Specs" deep-dive content |
| Owner Aftercare | Servicing older models, regulation, battery replacement | Publish "Watch Care" guide + servicing FAQ |
| Prospect | Price matching, model comparison, warranty | Add comparison table + warranty FAQ |
| Transactional | Order tracking, shipping, refunds | Improve order status page + shipping FAQ |

### Anomaly Detection

| Signal | Threshold | Action |
|---|---|---|
| **Volume spike** | Theme count > 2× weekly average | Immediate alert (don't wait for monthly brief) |
| **New theme** | Cluster not seen in previous 4 weeks | Flag for CS team review |
| **Escalation cluster** | 3+ escalations on same theme in 1 week | Priority KB update + SOP review |

---

## 5. Multi-Channel Intake Architecture

This diagram shows how enquiries from different channels are ingested, normalised, and routed into the intelligence loop.

```mermaid
flowchart TD
    subgraph External Channels
        EMAIL[📧 Gmail Inbox<br/>IMAP + OAuth2]
        IG[📸 Instagram DM<br/>Meta Graph API]
        WA[💬 WhatsApp<br/>WhatsApp Business API]
        CHAT[🌐 Website Chat<br/>Webhook POST]
    end
    
    subgraph n8n Intake Layer
        EMAIL --> ETRIGGER[Gmail Trigger Node<br/>n8n built-in]
        IG --> IGTRIGGER[Instagram Trigger Node<br/>n8n built-in]
        WA --> WATRIGGER[WhatsApp Trigger Node<br/>n8n built-in]
        CHAT --> WEBTRIGGER[Webhook Trigger Node<br/>n8n HTTP endpoint]
    end
    
    subgraph Normalisation
        ETRIGGER --> NORM[Normalise Input]
        IGTRIGGER --> NORM
        WATRIGGER --> NORM
        WEBTRIGGER --> NORM
        
        NORM --> STRIP[Strip PII<br/>Emails, names, addresses]
        STRIP --> FORMAT[Unified Format<br/>JSON: channel, subject, body, timestamp, metadata]
        FORMAT --> ENRICH[Enrich with Channel Context<br/>e.g., IG = visual-first, WA = conversational]
    end
    
    subgraph Routing
        ENRICH --> ROUTE{SOP Routing Rules}
        
        ROUTE -->|Materials & Safety| MAT[Product One-Pager<br/>Lookup]
        ROUTE -->|Engraving| ENG[Rate Card<br/>Engraving lookup]
        ROUTE -->|Strap Compatibility| STRAP[Product Spec<br/>20mm lug width check]
        ROUTE -->|Servicing| SVC[Rate Card<br/>Servicing tier lookup]
        ROUTE -->|Order / Shipping| ORD[Shopify Dependency<br/>Escalate to CS]
        ROUTE -->|Returns / Warranty| RET[SOP Rules<br/>14-day, engraved, 2-year warranty]
        ROUTE -->|New / Unknown| NEW[Gap Detection<br/>+ CS escalation]
        ROUTE -->|Escalation Trigger| ESC[Priority Route<br/>SOP Section 7]
    end
    
    MAT --> PROCESS[Enter Intelligence Loop]
    ENG --> PROCESS
    STRAP --> PROCESS
    SVC --> PROCESS
    ORD --> PROCESS
    RET --> PROCESS
    NEW --> PROCESS
    ESC --> PROCESS
    
    subgraph Escalation Triggers
        ESC1[😠 Angry Customer<br/>Immediate priority]
        ESC2[💳 Chargeback<br/>Finance team alert]
        ESC3[🔧 Warranty > 10 days<br/>Manager escalation]
        ESC4[🏢 Corporate > 5 units<br/>Sales team route]
        ESC5[📰 Press Enquiry<br/>PR team route]
    end
    
    ESC1 --> ESC
    ESC2 --> ESC
    ESC3 --> ESC
    ESC4 --> ESC
    ESC5 --> ESC
    
    subgraph Response Routing
        PROCESS --> DRAFTED[Drafted Reply]
        DRAFTED --> APPROVED{Human Approved?}
        APPROVED -->|Yes| SEND[Send via<br/>Original Channel]
        APPROVED -->|No| MANUAL[Manual Handling]
        
        SEND --> EMAIL_REPLY[📧 Gmail Reply]
        SEND --> IG_REPLY[📸 Instagram DM Reply]
        SEND --> WA_REPLY[💬 WhatsApp Reply]
        SEND --> CHAT_REPLY[🌐 Chat Widget Reply]
    end
    
    style EMAIL fill:#4285F4,color:#fff
    style IG fill:#E1306C,color:#fff
    style WA fill:#25D366,color:#fff
    style CHAT fill:#FF6B6B,color:#fff
    style PROCESS fill:#FF9800,color:#fff
    style SEND fill:#4CAF50,color:#fff
    style ESC fill:#F44336,color:#fff
```

### Channel Characteristics

| Channel | Volume | Tone | Key Consideration |
|---|---|---|---|
| **Gmail** | 18/70 (26%) | Formal, detailed | Full email thread context; attachments possible |
| **Instagram DM** | 19/70 (27%) | Casual, visual-first | Short messages; may reference images |
| **WhatsApp** | 16/70 (23%) | Conversational, urgent | Real-time expectation; shorter response window |
| **Chat** | 17/70 (24%) | Mixed, task-focused | Mid-conversation context; may have browsing history |

### PII Handling Per Channel

| Channel | PII Collected | PII Stripped | Stored? |
|---|---|---|---|
| **Gmail** | Name, email address, phone (in signature) | Email address, phone, full name | No — only intent + persona tags |
| **Instagram DM** | IG handle, display name | IG handle, display name | No — only intent + persona tags |
| **WhatsApp** | Phone number, display name | Phone number, display name | No — only intent + persona tags |
| **Chat** | Session ID, optional name | Session ID, name | No — only intent + persona tags |

---

## 6. Deployment Architecture

```mermaid
graph LR
    subgraph Host Machine
        subgraph Docker Compose
            N8N[n8n Container<br/>Port 5678]
            CHROMA[ChromaDB Container<br/>Port 8000]
            APP[Python App Container<br/>Port 8501<br/>Streamlit + Processing]
        end
        
        subgraph Volumes
            N8N_DATA[n8n_data<br/>Workflows + Credentials]
            CHROMA_DATA[chroma_data<br/>Vector Index + Metadata]
            KB_VOL[kb/<br/>Knowledge Base Files]
            DATA_VOL[data/<br/>Input Data Files]
        end
    end
    
    subgraph External APIs
        GLM[GLM-5.1 API<br/>Primary LLM]
        CLAUDE[Claude API<br/>Fallback LLM<br/>Low-confidence only]
    end
    
    N8N --- N8N_DATA
    CHROMA --- CHROMA_DATA
    APP --- KB_VOL
    APP --- DATA_VOL
    
    N8N <-->|Workflow calls| APP
    APP <-->|Hybrid search| CHROMA
    APP <-->|Classification + Drafting| GLM
    APP -.->|Low-confidence fallback| CLAUDE
    N8N -.->|Edge case routing| GLM
    
    style N8N fill:#FF6D5A,color:#fff
    style CHROMA fill:#7C4DFF,color:#fff
    style APP fill:#1E88E5,color:#fff
    style GLM fill:#4CAF50,color:#fff
    style CLAUDE fill:#FF9800,color:#fff
```

### Service Dependencies

| Service | Depends On | Health Check |
|---|---|---|
| **n8n** | ChromaDB, App | `wget http://localhost:5678/healthz` |
| **App** | ChromaDB | `requests.get('http://localhost:8501/_stcore/health')` |
| **ChromaDB** | None (standalone) | `curl http://localhost:8000/api/v1/heartbeat` |

### Data Flow Summary

```mermaid
graph LR
    A[Customer Enquiry] --> B[n8n Intake]
    B --> C[Python App<br/>Classify + Retrieve]
    C --> D{Answer Found?}
    D -->|Yes| E[Draft Reply]
    D -->|No| F[Gap Detection]
    E --> G[Human Approval]
    F --> H[CS Escalation]
    G --> I[Send Reply]
    H --> J[CS Resolves]
    J --> K[Auto-Draft KB Entry]
    K --> L[Human KB Approval]
    L --> M[ChromaDB Updated]
    M -.->|System is smarter| C
    
    style A fill:#4CAF50,color:#fff
    style I fill:#2196F3,color:#fff
    style M fill:#FF9800,color:#fff
```

---

*Prepared by Digital Futures Consultancy LLP for ECHELON 2026 AI Workflow Competition*