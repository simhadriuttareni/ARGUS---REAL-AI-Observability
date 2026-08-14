# 🔮 ARGUS - AI Observability Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Complete AI observability platform with real-time monitoring, cost tracking, semantic caching, and smart routing.

## 🎯 What It Does

ARGUS provides "100 eyes" of visibility into your AI infrastructure:

- **📊 Real-time Monitoring** - Track LLM calls, latency, and errors
- **💰 Cost Tracking** - Per-model and per-provider cost breakdown
- **💾 Semantic Cache** - Reduce API costs by 30-50%
- **🧠 Smart Router** - Auto-select optimal model based on task
- **🚨 Alert Engine** - Detect anomalies and cost spikes
- **📈 Dashboards** - Grafana + Phoenix + React UI



> **ARGUS** is an AI-native observability platform that provides complete visibility into your AI infrastructure. It tracks every AI API call, monitors costs in real-time, intelligently routes requests to optimal models, and alerts you when something goes wrong.

## 🎯 Why ARGUS?

Companies spend millions on AI APIs with **zero visibility**. ARGUS solves this:

| Problem | ARGUS Solution |
|---------|----------------|
| 💰 **Unknown AI costs** | Real-time cost tracking per model/provider |
| 🧠 **Wrong model selection** | Smart Router selects optimal model automatically |
| 🔄 **Duplicate API calls** | Semantic caching reduces costs by 30-50% |
| 📉 **No performance visibility** | Latency & token tracking for all calls |
| 🚨 **Surprise bills** | Anomaly detection & proactive alerts |

## ✨ Key Features

### 🤖 Smart Model Router
- Automatically selects the best LLM based on task complexity
- Simple questions → cheaper models (llama-3.1-8b-instant)
- Complex/Coding tasks → powerful models (llama-3.3-70b-versatile)
- **30-45% cost savings** on AI API calls

### 💰 Real-Time Cost Tracking
- Tracks every AI API call in real-time
- Per-model and per-provider cost breakdown
- Token usage monitoring

### 💾 Semantic Caching
- Redis-based vector similarity caching
- Returns cached responses when similarity > 0.95
- **30-50% reduction** in repeated API calls

### 📊 Interactive Dashboard
- Real-time monitoring of all AI calls
- Cost trends and model comparison
- Live WebSocket updates

### 🚨 Alert Engine
- Anomaly detection for cost spikes
- Model downtime alerts
- Budget threshold notifications

