# Immigration Platform Documentation

Welcome to the Immigration Platform documentation! This platform helps users discover visa requirements across multiple countries using automated crawling, classification, intelligent matching, and AI-powered assistance.

## Table of Contents

### Getting Started
- [Quick Start Guide](guides/quick-start.md) - Get up and running in 5 minutes
- [Configuration Guide](guides/configuration.md) - Complete configuration reference
- [Installation](guides/installation.md) - Detailed installation instructions

### Services Documentation
- [Crawler Service](services/crawler.md) - Web crawling and data collection
- [Classifier Service](services/classifier.md) - Requirement extraction and structuring
- [Matcher Service](services/matcher.md) - Eligibility scoring and visa ranking
- [Assistant Service](services/assistant.md) - AI-powered Q&A system

### Guides
- [User Workflows](guides/workflows.md) - Common usage scenarios
- [API Reference](guides/api-reference.md) - CLI command reference
- [Data Flow](guides/data-flow.md) - Understanding the pipeline

### Troubleshooting
- [Common Issues](troubleshooting.md) - Solutions to frequently encountered problems
- [Error Messages](guides/error-messages.md) - Understanding error messages
- [Performance Tips](guides/performance.md) - Optimization strategies

## Quick Links

### For New Users
1. [Installation Guide](guides/installation.md) → Install dependencies
2. [Quick Start](guides/quick-start.md) → Run your first query
3. [Workflows](guides/workflows.md) → Learn common usage patterns

### For Developers
1. [Architecture Overview](../ARCHITECTURE.md) → System design
2. [Contributing](guides/contributing.md) → Development guidelines
3. [Testing](guides/testing.md) → Running tests

### For System Administrators
1. [Configuration](guides/configuration.md) → Setup and tuning
2. [Deployment](guides/deployment.md) → Production setup
3. [Monitoring](guides/monitoring.md) → Logging and metrics

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│   Crawler   │────▶│  Classifier  │────▶│   Matcher   │────▶│  Assistant  │
│   Service   │     │   Service    │     │   Service   │     │   Service   │
└─────────────┘     └──────────────┘     └─────────────┘     └─────────────┘
      │                     │                     │                   │
      ▼                     ▼                     ▼                   ▼
   Raw Data          Structured Data        User Matching        AI Responses
```

### Data Flow
1. **Crawler** → Scrapes government immigration websites → Stores raw HTML/text
2. **Classifier** → Extracts requirements from raw data → Structures visa information
3. **Matcher** → Scores user eligibility → Ranks visas by fit
4. **Assistant** → Retrieves context → Generates AI-powered answers

## Key Features

### Crawler Service
- Multi-country web crawling
- Keyword-based relevance filtering
- PDF/document detection
- Rate limiting and respectful crawling
- Breadcrumb extraction

### Classifier Service
- Automatic visa categorization (work, study, family, etc.)
- Age, education, and experience extraction
- Fee and processing time detection
- Language requirement parsing (IELTS, TOEFL, PTE)
- Multi-page visa grouping

### Matcher Service
- Weighted eligibility scoring
- Age, education, and experience matching
- Gap identification (what's missing)
- Country-specific filtering
- Interactive profile builder

### Assistant Service
- Context-aware Q&A
- Multiple LLM providers (OpenRouter, OpenAI)
- Source citation
- User profile integration
- Free tier available (OpenRouter)

## Platform Status

| Service | Status | Tests | Documentation |
|---------|--------|-------|---------------|
| Crawler | ✅ Complete | ✅ Passing | ✅ Available |
| Classifier | ✅ Complete | ✅ Passing | ✅ Available |
| Matcher | ✅ Complete | ✅ Passing | ✅ Available |
| Assistant | ✅ Complete | ✅ Passing | ✅ Available |
| Integration | ✅ Complete | ✅ Passing | ✅ Available |

## System Requirements

### Minimum Requirements
- Python 3.8+
- 2GB RAM
- 1GB disk space
- Internet connection

### Recommended Requirements
- Python 3.10+
- 4GB RAM
- 5GB disk space (for multiple countries)
- Stable internet connection

### Optional Requirements
- OpenRouter API key (free) or OpenAI API key (paid) for Assistant service
- GPU for faster local LLM processing (future)

## Quick Commands

```bash
# Crawl government websites
python main.py crawl --all
python main.py crawl --countries australia canada

# Extract and structure visa requirements
python main.py classify --all
python main.py classify --country australia

# Match user profile to visas
python main.py match --interactive
python main.py match --profile user_profile.json

# Ask questions about visas
python main.py assist --query "What work visas are available in Canada?"
python main.py assist --chat

# Run tests
python tests/test_crawler.py
python tests/test_classifier.py
python tests/test_matcher.py
python tests/test_assistant.py
python tests/test_integration.py
python tests/test_e2e_workflows.py
```

## Support

### Documentation
- Full documentation in `/docs` directory
- Service-specific guides in `/docs/services`
- Configuration examples in each service's `config.yaml`

### Issues
- Check [Troubleshooting Guide](troubleshooting.md) first
- Review [Common Issues](troubleshooting.md#common-issues)
- Check service logs in project root (e.g., `crawler.log`)

### Community
- GitHub Issues for bug reports
- GitHub Discussions for questions
- Contributing guidelines in [CONTRIBUTING.md](guides/contributing.md)

## License

This project is part of an immigration information platform designed to help users navigate complex visa requirements across multiple countries.

---

## Next Steps

1. **New Users**: Start with [Quick Start Guide](guides/quick-start.md)
2. **Configure Services**: Read [Configuration Guide](guides/configuration.md)
3. **Run Your First Crawl**: Follow [Crawler Documentation](services/crawler.md)
4. **Match Your Profile**: Try [Matcher Service](services/matcher.md)
5. **Ask Questions**: Use [Assistant Service](services/assistant.md)

Happy visa hunting! 🌍✈️
