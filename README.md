# Research Assistant

A generative AI-powered research assistant for scientific journal publishers that enables users to ask plain-English questions and receive grounded, well-sourced answers from their private archive of technical documents.

## Project Overview

You've been approached by a large scientific journal publisher to help prototype a research assistant powered by generative AI. Their vision is straightforward:

**Let users ask plain-English questions and get grounded, well-sourced answers from their private archive of technical documents.**

Every day, their system deposits newly uploaded journal files to a secure location you can access. You are not expected to scrape or crawl — the content arrives pre-uploaded.

The system demonstrates the core functionality of a tool that:
- **Ingests new content** → Embeds it into a searchable format
- **Answers questions with citations** → Shows which articles are being referenced most often

## Project Structure

```
research-assistant/
├── backend/
│   ├── src/
│   └── chroma_db/
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── upload/
│       │   └── document/
│       │       └── [id]/
│       ├── components/
│       ├── lib/
│       └── types/
├── docs/
└── sample_data/
```

