# BOLDR Email Intake Workflow

**Workflow ID:** `Qj8sWSe9Enz7EH5Q`
**n8n URL:** http://192.168.1.85:5678/workflow/Qj8sWSe9Enz7EH5Q
**Nodes:** 3

## Step-by-Step Flow

### Step 1: Gmail Trigger 🔌
**Type:** Trigger
**Description:** Watches for new emails in the connected Gmail account (requires OAuth)

![Step 1](./email_intake_step01.png)

### Step 2: Normalize Email Data 🔄
**Type:** Transform
**Description:** Extracts sender, subject, body from email and maps to BOLDR format

![Step 2](./email_intake_step02.png)

### Step 3: Forward to Intelligence Loop ➡️
**Type:** Action
**Description:** Sends normalized email data to FastAPI /api/v1/intake for classification

![Step 3](./email_intake_step03.png)
