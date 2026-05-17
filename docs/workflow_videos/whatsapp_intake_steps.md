# BOLDR WhatsApp Intake Workflow

**Workflow ID:** `9Z1ZC5CMijLlTRiJ`
**n8n URL:** http://192.168.1.85:5678/workflow/9Z1ZC5CMijLlTRiJ
**Nodes:** 4

## Step-by-Step Flow

### Step 1: WhatsApp Webhook 🔌
**Type:** Trigger
**Description:** Receives incoming WhatsApp messages via POST /webhook/whatsapp

![Step 1](./whatsapp_intake_step01.png)

### Step 2: Normalize WhatsApp Data 🔄
**Type:** Transform
**Description:** Maps WhatsApp payload fields to BOLDR standard format

![Step 2](./whatsapp_intake_step02.png)

### Step 3: Forward to Intelligence Loop ➡️
**Type:** Action
**Description:** Sends normalized data to FastAPI /api/v1/intake for classification

![Step 3](./whatsapp_intake_step03.png)

### Step 4: Respond to WhatsApp ✉️
**Type:** Response
**Description:** Returns acknowledgment to the customer via WhatsApp

![Step 4](./whatsapp_intake_step04.png)
