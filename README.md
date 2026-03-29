# 🍽️ NLP Chatbot for Food Ordering Website

A conversational food ordering chatbot built with **Dialogflow**, **FastAPI**, and **MySQL**. Users can place orders, modify them, and track their status through a natural language chat interface embedded in a plain HTML/CSS/JS frontend.

---

## Project Overview

This chatbot allows customers to:
- 🛒 Add or remove items from their order via natural conversation
- ✅ Complete and confirm their order
- 📦 Track the status of an existing order by order ID

Dialogflow handles intent recognition and passes requests to a FastAPI webhook backend, which communicates with a MySQL database to manage orders.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Chatbot / NLP | Dialogflow |
| Backend | Python, FastAPI |
| Database | MySQL |
| Frontend | HTML, CSS, JavaScript |
| HTTPS Tunneling | ngrok |

---

## Folder Structure

| Path | Description |
|------|-------------|
| `backend/` | FastAPI backend — webhook handler, DB helper, and utility functions |
| `db/` | MySQL database dump — import this to set up your database |
| `dialogflow_assets/` | Dialogflow training phrases, intents, and agent config |
| `frontend/` | Website code (HTML/CSS/JS) |

---

## Setup Instructions

### 1. Import the Database

1. Open **MySQL Workbench**
2. Import the dump file found in the `db/` folder into your MySQL instance
3. The database is named `pandeyji_eatery`

### 2. Configure the Database Connection

In `backend/db_helper.py`, update the connection credentials to match your local MySQL setup:

```python
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='your_password',
    database='pandeyji_eatery'
)
```

### 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

Or install manually:

```bash
pip install mysql-connector
pip install "fastapi[all]"
```

### 4. Start the FastAPI Backend

```bash
cd backend
uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000/`

---

## Setting Up ngrok (HTTPS Tunneling)

Dialogflow requires a public HTTPS URL to reach your local webhook. Use ngrok for this.

1. Download ngrok from [https://ngrok.com/download](https://ngrok.com/download) and extract the zip
2. Open a command prompt in the ngrok folder and run:

```bash
ngrok http 8000
```

3. Copy the generated `https://` URL and set it as the webhook URL in your Dialogflow agent settings

> ⚠️ **Note:** ngrok sessions can expire. If you see a "session expired" message, restart ngrok and update the webhook URL in Dialogflow.

---

## Dialogflow Intents

The backend handles the following intents:

| Intent | Description |
|--------|-------------|
| `order.add` | Adds food items to the current order |
| `order.remove` | Removes food items from the current order |
| `order.complete` | Finalizes and saves the order to the database |
| `track.order` | Returns the status of an order by ID |

Training phrases and intent configurations can be found in the `dialogflow_assets/` folder.
