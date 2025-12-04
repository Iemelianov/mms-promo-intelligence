# Documentation Summary

This document provides an overview of all available documentation for the Promo Scenario Co-Pilot project.

## Documentation Structure

```
docs/
├── README.md              # This file - documentation index
├── architecture.md        # System architecture and design
├── data-models.md         # Data schemas and structures
├── api/                   # API documentation
│   └── README.md          # API endpoints and usage
├── ui-specs.md            # UI/UX specifications
├── development.md         # Development guide
├── setup.md               # Setup and installation
├── hackathon-plan.md      # Hackathon build plan
└── promo-data-processing.md  # Promo catalog processing guide
```

## Quick Links

### For Developers

- **[Setup Guide](./setup.md)**: Get started quickly
- **[Development Guide](./development.md)**: Development workflow and best practices
- **[Architecture](./architecture.md)**: Understand system design
- **[API Reference](./api/README.md)**: API endpoints and integration

### For Product/Design

- **[UI Specifications](./ui-specs.md)**: Screen designs and components
- **[Data Models](./data-models.md)**: Data structures and schemas

### For Hackathon

- **[Hackathon Plan](./hackathon-plan.md)**: 14-hour build plan
- **[Quick Start](./setup.md#quick-start-hackathon)**: Fast setup for hackathon

### For Data Processing

- **[Promo Data Processing](./promo-data-processing.md)**: Guide for processing promotional catalog XLSB files

## Key Concepts

### System Overview

Promo Scenario Co-Pilot is an AI-powered system that helps promotional leads:
1. **Discover** opportunities through data analysis
2. **Model** multiple promotional scenarios
3. **Optimize** scenarios for business impact
4. **Generate** creative briefs and assets
5. **Learn** from post-campaign performance

### Architecture Layers

1. **UI Layer**: React-based interface with chat co-pilot
2. **Agent Layer**: LangChain-powered orchestrators
3. **Engine Layer**: Business logic and computation
4. **Tools Layer**: Data access and external integrations

### Core Components

- **7 Agents**: Discovery, Scenario Lab, Optimization, Creative, Post-Mortem, Validation, Co-Pilot
- **9 Engines**: Context, Forecast, Uplift, Evaluation, Optimization, Validation, Creative, Post-Mortem, Learning
- **6 Tools**: Sales Data, Promo Catalog, CDP, Context Data, Weather, Targets/Config

## Getting Started

1. **Read [README.md](../README.md)** for project overview
2. **Follow [Setup Guide](./setup.md)** to get environment running
3. **Review [Architecture](./architecture.md)** to understand design
4. **Check [Development Guide](./development.md)** for coding standards

## Documentation by Role

### Backend Developer

Start with:
1. [Architecture](./architecture.md) - Understand system design
2. [Development Guide](./development.md) - Coding standards and workflow
3. [API Reference](./api/README.md) - Endpoint specifications
4. [Data Models](./data-models.md) - Data structures

### Frontend Developer

Start with:
1. [UI Specifications](./ui-specs.md) - Screen designs and components
2. [Development Guide](./development.md) - Frontend setup and workflow
3. [API Reference](./api/README.md) - API integration
4. [Data Models](./data-models.md) - TypeScript types

### Product Manager

Start with:
1. [README.md](../README.md) - Product overview
2. [Architecture](./architecture.md) - System capabilities
3. [UI Specifications](./ui-specs.md) - User experience
4. [Hackathon Plan](./hackathon-plan.md) - MVP scope

### Data Scientist

Start with:
1. [Architecture](./architecture.md) - Engine design
2. [Data Models](./data-models.md) - Data structures
3. [Development Guide](./development.md) - Adding new engines
4. [Hackathon Plan](./hackathon-plan.md) - Uplift model approach

## Common Tasks

### Setting Up Development Environment

See [Setup Guide](./setup.md)

### Adding a New Feature

1. Review [Development Guide](./development.md#adding-new-features)
2. Check [Architecture](./architecture.md) for integration points
3. Update [Data Models](./data-models.md) if needed
4. Update [API Reference](./api/README.md) if adding endpoints
5. Update [UI Specifications](./ui-specs.md) if adding screens

### Understanding a Component

1. Check [Architecture](./architecture.md) for component role
2. Review [Data Models](./data-models.md) for data structures
3. See [Development Guide](./development.md) for examples

### Preparing for Demo

1. Review [Hackathon Plan](./hackathon-plan.md)
2. Follow [Setup Guide](./setup.md#quick-start-hackathon)
3. Test demo script from hackathon plan

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Code standards
- Testing requirements
- Pull request process
- Commit message format

## Support

- **Issues**: Check logs and error messages
- **Questions**: Review relevant documentation section
- **Bugs**: Check [Development Guide](./development.md#troubleshooting)

## Updates

Documentation is updated as the project evolves. Check git history for changes.

Last updated: 2024-10-20

