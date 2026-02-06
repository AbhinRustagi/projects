---
title: LLM Judge
date: 2026-01-30
description: An evaluation platform that uses LLMs to score question-answer pairs against custom, domain-specific criteria. Supports multiple providers (OpenAI, Anthropic, Google, DeepSeek) and includes lightweight safety checks for adversarial patterns and bias.
tags:
  - FastAPI
  - Next.js
  - LLM
  - Evaluation
  - Python
  - TypeScript
slug: llm-judge
thumbnail: projects/assets/llm-judge/thumbnail.png
published: true
canonical_url: https://www.abhin.dev/projects/llm-judge
github_url: https://github.com/AbhinRustagi/llm-judge
---

## Overview

LLM Judge is a web-based evaluation platform for scoring question-answer pairs using LLMs as judges. It targets regulated domains (legal, medical, finance) where QA quality matters and automated evaluation needs to be both rigorous and transparent.

Users upload a file of Q&A pairs, configure weighted evaluation criteria with optional hard minimums, pick a judge model, and get back per-pair scores with reasoning, a pass/fail verdict, and any safety warnings.

## Problem Statement

Evaluating the quality of question-answer content at scale is tedious and subjective when done manually. In regulated domains, the stakes are higher — a medical Q&A dataset with inaccurate answers is dangerous, not just unhelpful. Existing LLM evaluation tools tend to be either too simplistic (single-score, single-provider) or too opinionated about criteria.

The goal was to build a flexible evaluation tool that supports multiple LLM providers, domain-aware criteria, and a transparent scoring breakdown — so users can understand *why* something passed or failed, not just whether it did.

## Solution

A two-part system: a FastAPI backend that handles file parsing, safety checks, and LLM-based evaluation, and a Next.js frontend that guides users through a step-by-step wizard.

The evaluation engine runs all criteria concurrently for each Q&A pair using asyncio, with retry logic and exponential backoff per LLM call. Safety checks (jailbreak detection, bias detection) run independently using pattern matching — no LLM calls required — and are reported separately from quality scores.

The verdict logic combines weighted criterion scores with hard minimums: an answer can fail even if its overall weighted score is above the threshold, if any single criterion falls below its hard minimum. This is important for domains like medical, where safety can't be traded off against other criteria.

## Tech Stack

- **Backend:** FastAPI, Pydantic, Uvicorn
- **Frontend:** Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS, DaisyUI
- **LLM Providers:** OpenAI SDK, Anthropic SDK, Google GenAI SDK, DeepSeek (via OpenAI-compatible client)
- **File Processing:** PyMuPDF4LLM (PDF to Markdown), regex-based Q&A extraction
- **Resilience:** Tenacity (exponential backoff retries)
- **Deployment:** Docker, Google Cloud Run, Amazon Fargate

## Key Features

- **Multi-provider model selection** across OpenAI (GPT-4o), Anthropic (Claude Sonnet 4), Google (Gemini 2.0/2.5), and DeepSeek (V3, R1), with per-model cost and context window visibility
- **Domain-aware evaluation** with tailored system prompts and default criteria templates for legal, medical, finance, and general domains
- **Weighted criteria with hard minimums** — criteria weights must sum to 100, and individual criteria can enforce minimum score thresholds independent of the overall score
- **Lightweight safety checks** for jailbreak/prompt injection patterns (many-shot attacks, sycophancy, manipulation keywords) and bias detection (gender, racial, age, socioeconomic, ability) using pattern matching only
- **Concurrent async evaluation** — asyncio.gather over Q&A pairs and criteria, maximizing throughput while respecting rate limits via retry logic
- **Flexible file parsing** supporting PDF and TXT with multiple Q&A format detection (Q:/A:, numbered, markdown) and validation
- **Saveable evaluation templates** (CRUD) for reusing criteria configurations across runs
- **BFF proxy layer** in Next.js API routes, keeping the backend URL out of the client and handling multipart form-data forwarding
- **Rate limiting** (30 req/min global, 5 req/min on /api/evaluate) and security headers middleware

## Architecture

The frontend is a step-by-step wizard (domain → upload → criteria → model → evaluate → results) built with React 19 and DaisyUI components. It communicates with the FastAPI backend exclusively through a Next.js BFF proxy layer.

On the backend, the evaluation flow is:

1. Parse the uploaded file into Q&A pairs
2. Run safety checks (jailbreak + bias) concurrently on each pair
3. For each pair, evaluate all criteria concurrently — each criterion triggers an LLM call that returns a score (0-100), reasoning, and issues
4. Aggregate weighted scores, apply hard minimum logic, determine pass/fail verdict
5. Return the full evaluation response with per-pair results, summary statistics, and safety warnings

Provider abstraction maps model IDs to the correct SDK client, with a unified response format across all providers. Errors in individual evaluations are caught and reported as REJECT verdicts without failing the entire batch.

## Challenges & Learnings

**Parsing real-world Q&A formats:** Q&A pairs in the wild come in many formats — numbered, labeled, markdown-headed, inconsistently spaced. A multi-regex fallback strategy with best-match selection handles this reasonably well, though it's inherently heuristic.

**Verdict logic design:** Simple weighted averages aren't enough for regulated domains. A medical answer that scores 95 overall but 40 on safety should fail. Hard minimums per criterion solve this, but the interaction between weights, thresholds, and hard minimums required careful thought to keep the UX understandable.

**Multi-provider consistency:** Different LLM providers return JSON in slightly different ways. Standardizing the response parsing (with fallback regex extraction for malformed JSON) was necessary to keep the scoring comparable across models.

**Cost transparency:** Showing per-model pricing upfront turned out to be important. The cost difference between providers is dramatic (DeepSeek is ~100x cheaper than GPT-4o), and batch evaluation on large Q&A sets can get expensive without visibility.

## Outcome

A working evaluation platform that can score Q&A datasets across multiple LLM providers with domain-specific criteria, transparent reasoning, and safety checks. Deployed via Docker with support for both Google Cloud Run and Amazon Fargate.
