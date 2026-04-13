# MiAcademy Standards Gap Analysis

AI-powered state education standards gap analysis tool. Crawl any state portal, ingest K-8 standards, and instantly see how MiAcademy's curriculum measures up — with clickable provenance for every requirement.

Powered by [NeuralSeek](https://neuralseek.com) AI Agents.

## Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/CerebralBlue-LOV/mia-gap-analysis)

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `NEURALSEEK_API_KEY` | Your NeuralSeek API key |
| `NEURALSEEK_PUBLIC_API_URL` | Your NeuralSeek Public API URL (e.g. `https://api-azsc.neuralseek.com/v1/your-instance`) |
| `BASIC_AUTH_USER` | Username for basic auth protection |
| `BASIC_AUTH_PASS` | Password for basic auth protection |

## Local Development

```bash
export NEURALSEEK_API_KEY="your-key"
export NEURALSEEK_PUBLIC_API_URL="https://api-azsc.neuralseek.com/v1/your-instance"
export HOST=127.0.0.1
python3 server.py
```

Open http://localhost:8080

## Architecture

- **Frontend**: Single-page HTML/CSS/JS app with MiAcademy branding
- **Backend**: Python proxy server that injects NeuralSeek API credentials server-side
- **AI Agents**: NeuralSeek mAIstro agents (MIA-Gap-Orchestrator → MIA-Standards-Crawler, MIA-Curriculum-Scraper, MIA-Gap-Analyzer) powered by Exa search API
