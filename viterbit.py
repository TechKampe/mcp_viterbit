import os
import requests
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta
from statistics import mean
from dateutil import parser

# Load environment variables
load_dotenv()

API_KEY = os.getenv("VITERBIT_API_KEY")
API_BASE = os.getenv("VITERBIT_API_BASE")

if not API_KEY or not API_BASE:
    raise ValueError("API_KEY and API_BASE must be set in environment variables.")

# Correct header according to official documentation
headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

STAGES = [
    "Inscrito", "Filtro pre-selección", "Invitación Hireflix", "Recordatorio Hireflix",
    "Descartar por no hacer Hireflix", "Pre-selección", "Entrevista",
    "No-show entrevista", "Pre-Kämpe", "Contratado", "Descartar"
]

def query_candidates(stage, from_date, to_date):
    params = {
        "stage": stage,
        "created_at_from": from_date,
        "created_at_to": to_date
    }
    try:
        response = requests.get(f"{API_BASE}/candidates", headers=headers, params=params)
        response.raise_for_status()
        return len(response.json().get('data', []))
    except requests.exceptions.RequestException as e:
        logging.error(f"Error querying candidates: {e}")
        return 0

def candidates_stage_transition(stage_from, stage_to, from_date, to_date):
    params = {
        "stage_from": stage_from,
        "stage_to": stage_to,
        "updated_at_from": from_date,
        "updated_at_to": to_date
    }
    try:
        response = requests.get(f"{API_BASE}/candidates", headers=headers, params=params)
        response.raise_for_status()
        return len(response.json().get('data', []))
    except requests.exceptions.RequestException as e:
        logging.error(f"Error querying candidate stage transitions: {e}")
        return 0

def hiring_velocity(from_date, to_date):
    days = (datetime.fromisoformat(to_date) - datetime.fromisoformat(from_date)).days
    total_kampes = query_candidates("Contratado", from_date, to_date)
    velocity = total_kampes / days if days else 0
    return round(velocity, 2)

def average_stage_duration(stage, from_date, to_date):
    params = {
        "stage": stage,
        "updated_at_from": from_date,
        "updated_at_to": to_date
    }
    try:
        response = requests.get(f"{API_BASE}/candidates", headers=headers, params=params)
        response.raise_for_status()
        candidates = response.json().get('data', [])
    except requests.exceptions.RequestException as e:
        logging.error(f"Error querying average stage duration: {e}")
        return 0

    durations = []
    for candidate in candidates:
        entered = parser.isoparse(candidate['updated_at'])
        created = parser.isoparse(candidate['created_at'])
        duration = (entered - created).days
        durations.append(duration)

    return round(mean(durations), 2) if durations else 0

def historical_comparison(stage, period_days=30):
    today = datetime.utcnow().date()
    current_period_start = today - timedelta(days=period_days)
    previous_period_start = current_period_start - timedelta(days=period_days)

    current = query_candidates(stage, current_period_start.isoformat(), today.isoformat())
    previous = query_candidates(stage, previous_period_start.isoformat(), current_period_start.isoformat())

    return {
        "current_period": current,
        "previous_period": previous,
        "difference": current - previous
    }

def full_summary(period_days=7):
    today = datetime.utcnow().date()
    from_date = (today - timedelta(days=period_days)).isoformat()
    to_date = today.isoformat()

    summary = {
        "new_candidates": query_candidates("Inscrito", from_date, to_date),
        "new_kampes": query_candidates("Contratado", from_date, to_date),
        "hiring_velocity": hiring_velocity(from_date, to_date),
        "stage_durations": {
            stage: average_stage_duration(stage, from_date, to_date)
            for stage in STAGES
        },
    }
    return summary
