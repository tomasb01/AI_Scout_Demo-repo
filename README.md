# Acme Insurance — Internal Tools Monorepo

> **⚠️ This is a fictional demo repository** for demonstrating
> [AI Scout](https://github.com/tomasb01/AI_Scout) — an enterprise AI discovery
> and security assessment tool. All company names, data, and API keys are fake.
> The security issues in this repo are **planted on purpose**.

Internal tooling of the fictional *Acme Insurance a.s.* — a mid-size European
insurer whose teams have been quietly adopting AI. Sound familiar?

## What's inside (and what AI Scout finds)

| Directory | What the team thinks it is | What Scout sees |
|-----------|---------------------------|-----------------|
| `customer-chatbot/` | Support chatbot PoC | Personal data (name, email, birth date) sent to OpenAI · hardcoded API key |
| `claims-rag/` | Claims-handling knowledge base | LangChain + Chroma RAG, OpenAI embeddings, key handled properly (env var) |
| `risk-scoring/` | Underwriting risk experiment | Financial data (IBAN, balances) analyzed by **local** Ollama — stays in perimeter |
| `marketing-classifier/` | Lead scoring script | Customer emails sent to HuggingFace inference API · hardcoded token |
| `agents/policy-review-agent/` | "Automation helper" | **Autonomous agent loop** (LangGraph) with file & DB tools, no human in the loop |
| `.mcp.json` | Dev convenience | MCP servers with filesystem and database access |

## Try it yourself

```bash
pip install ai-scout   # or: uv tool install ai-scout

# Full scan, no LLM needed — rule-based analysis only
aiscout scan --local . --no-llm --output report.html

# Developer guardrail — fails CI on leaked keys / sensitive egress
aiscout check --path .

# Diff demo: compare against the baseline branch
git checkout baseline && aiscout scan --local . --no-llm --output baseline.json
git checkout main     && aiscout scan --local . --no-llm --output current.json
```

The `baseline` branch represents the repo *before* the last quarter:
one leaked key has since been fixed, and the autonomous agent is new.
