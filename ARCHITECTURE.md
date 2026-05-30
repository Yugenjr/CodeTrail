# CodeTrail - Production Architecture Design

**Document Version:** 1.0  
**Date:** May 2026  
**Status:** Architecture Design (Pre-Implementation)

---

## Table of Contents
1. [Complete Folder Structure](#1-complete-folder-structure)
2. [Folder Responsibilities](#2-folder-responsibilities)
3. [Domain Model Design](#3-domain-model-design)
4. [Service Layer Architecture](#4-service-layer-architecture)
5. [Database Schema](#5-database-schema)
6. [API Design](#6-api-design)
7. [CLI Design](#7-cli-design)
8. [VS Code Extension Architecture](#8-vs-code-extension-architecture)
9. [Scalability Considerations](#9-scalability-considerations)
10. [Development Roadmap](#10-development-roadmap)

---

## 1. Complete Folder Structure

```
codetrail/
├── apps/
│   ├── api/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                      # FastAPI application factory
│   │   │   ├── config.py                    # API configuration
│   │   │   ├── asgi.py                      # ASGI entry point
│   │   │   │
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health.py               # Health check endpoints
│   │   │   │   ├── auth.py                 # /auth/* endpoints
│   │   │   │   ├── profile.py              # /profile/* endpoints
│   │   │   │   ├── recommendations.py      # /recommendations/* endpoints
│   │   │   │   ├── issues.py               # /issues/* endpoints
│   │   │   │   └── roadmaps.py             # /roadmaps/* endpoints
│   │   │   │
│   │   │   ├── middleware/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── error_handler.py        # Global error handling
│   │   │   │   ├── logging.py              # Request/response logging
│   │   │   │   ├── rate_limiter.py         # Rate limiting middleware
│   │   │   │   └── auth.py                 # JWT authentication middleware
│   │   │   │
│   │   │   ├── dependencies/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py                 # Dependency: authenticated user
│   │   │   │   ├── database.py             # Dependency: DB session
│   │   │   │   ├── cache.py                # Dependency: cache client
│   │   │   │   └── services.py             # Dependency: service instances
│   │   │   │
│   │   │   ├── schemas/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py                 # Base Pydantic models
│   │   │   │   ├── auth.py                 # Auth request/response schemas
│   │   │   │   ├── profile.py              # Profile schemas
│   │   │   │   ├── recommendations.py      # Recommendation schemas
│   │   │   │   ├── issues.py               # Issue schemas
│   │   │   │   ├── roadmaps.py             # Roadmap schemas
│   │   │   │   └── errors.py               # Error response schemas
│   │   │   │
│   │   │   └── handlers/
│   │       ├── __init__.py
│   │       └── exception_handlers.py       # Custom exception handlers
│   │   │
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py                 # Pytest fixtures
│   │   │   ├── test_health.py
│   │   │   ├── test_auth.py
│   │   │   ├── test_profile.py
│   │   │   ├── test_recommendations.py
│   │   │   ├── test_issues.py
│   │   │   └── test_roadmaps.py
│   │   │
│   │   ├── pyproject.toml                  # API package dependencies
│   │   └── README.md
│   │
│   ├── cli/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── __main__.py                 # Entry point: codetrail command
│   │   │   ├── config.py                   # CLI configuration
│   │   │   │
│   │   │   ├── commands/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py                 # Base command class
│   │   │   │   ├── auth.py                 # login, logout commands
│   │   │   │   ├── profile.py              # profile show, profile update commands
│   │   │   │   ├── recommend.py            # recommend command
│   │   │   │   ├── analyze.py              # analyze command
│   │   │   │   └── roadmap.py              # roadmap command
│   │   │   │
│   │   │   ├── formatters/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py                 # Base formatter
│   │   │   │   ├── json.py                 # JSON formatter
│   │   │   │   ├── table.py                # Table formatter (Rich)
│   │   │   │   └── markdown.py             # Markdown formatter
│   │   │   │
│   │   │   ├── prompts/
│   │   │   │   ├── __init__.py
│   │   │   │   └── interactive.py          # Interactive prompts (Rich)
│   │   │   │
│   │   │   └── utils/
│   │       ├── __init__.py
│   │       ├── api_client.py               # HTTP client to API
│   │       ├── storage.py                  # Local config/token storage
│   │       └── logger.py                   # CLI logging setup
│   │   │
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   └── test_commands.py
│   │   │
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── vscode-extension/
│   │   ├── src/
│   │   │   ├── extension.ts                # Extension entry point
│   │   │   ├── config.ts                   # Extension config
│   │   │   │
│   │   │   ├── commands/
│   │   │   │   ├── auth.ts
│   │   │   │   ├── profile.ts
│   │   │   │   ├── recommendations.ts
│   │   │   │   └── navigation.ts
│   │   │   │
│   │   │   ├── views/
│   │   │   │   ├── skillDashboard.ts       # Skill display panel
│   │   │   │   ├── issueExplorer.ts        # Issue list tree view
│   │   │   │   ├── roadmapView.ts          # Roadmap visualization
│   │   │   │   └── detailsPanel.ts         # Details sidebar
│   │   │   │
│   │   │   ├── webview/
│   │   │   │   ├── skillDashboard/
│   │   │   │   ├── roadmapView/
│   │   │   │   └── detailsPanel/
│   │   │   │
│   │   │   ├── providers/
│   │   │   │   ├── issueExplorerProvider.ts
│   │   │   │   └── treeDataProvider.ts
│   │   │   │
│   │   │   └── utils/
│   │       ├── api.ts                      # VS Code API client
│   │       ├── storage.ts                  # VS Code storage
│   │       └── logger.ts
│   │   │
│   │   ├── tests/
│   │   │   └── suite/
│   │   │
│   │   ├── webview-ui/
│   │   │   ├── src/
│   │   │   │   ├── dashboard.tsx
│   │   │   │   ├── roadmap.tsx
│   │   │   │   └── components/
│   │   │   ├── public/
│   │   │   └── package.json
│   │   │
│   │   ├── assets/
│   │   │   ├── icons/
│   │   │   └── images/
│   │   │
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── README.md
│   │
│   └── github-action/
│       ├── src/
│       │   ├── main.ts                     # Action entry point
│       │   ├── config.ts
│       │   ├── handlers/
│       │   │   ├── issueHandler.ts
│       │   │   ├── prHandler.ts
│       │   │   └── commentHandler.ts
│       │   └── utils/
│       │       └── api.ts
│       │
│       ├── dist/
│       │   └── index.js                    # Compiled action
│       │
│       ├── action.yml                      # Action definition
│       ├── package.json
│       └── README.md
│
├── packages/
│   │
│   ├── core-domain/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── entities/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── user.py                 # User entity
│   │   │   │   ├── repository.py           # Repository entity
│   │   │   │   ├── skill.py                # Skill entity
│   │   │   │   ├── issue.py                # Issue entity
│   │   │   │   ├── recommendation.py       # Recommendation entity
│   │   │   │   ├── roadmap.py              # Roadmap entity
│   │   │   │   └── learning_concept.py     # LearningConcept entity
│   │   │   │
│   │   │   ├── value_objects/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── skill_level.py          # SkillLevel VO
│   │   │   │   ├── difficulty.py           # Difficulty VO
│   │   │   │   ├── language.py             # Language VO
│   │   │   │   └── matching_score.py       # MatchingScore VO
│   │   │   │
│   │   │   ├── interfaces/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── repository.py           # Repository interface
│   │   │   │   ├── service.py              # Service interface
│   │   │   │   ├── cache.py                # Cache interface
│   │   │   │   └── event_bus.py            # Event bus interface
│   │   │   │
│   │   │   ├── exceptions/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── domain.py               # Domain exceptions
│   │   │   │   └── not_found.py
│   │   │   │
│   │   │   └── events/
│   │       ├── __init__.py
│   │       ├── user_events.py
│   │       ├── skill_events.py
│   │       └── recommendation_events.py
│   │   │
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   └── test_entities.py
│   │   │
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── github-client/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   │
│   │   │   ├── auth/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── oauth.py                # GitHub OAuth flow
│   │   │   │   ├── token_manager.py        # Token storage/refresh
│   │   │   │   └── scopes.py               # OAuth scopes definition
│   │   │   │
│   │   │   ├── repositories/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── client.py               # Repo API calls
│   │   │   │   ├── models.py               # Repo data models
│   │   │   │   └── cache.py                # Repo caching
│   │   │   │
│   │   │   ├── issues/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── client.py               # Issue API calls
│   │   │   │   ├── models.py               # Issue data models
│   │   │   │   └── filters.py              # Issue filtering
│   │   │   │
│   │   │   ├── contributors/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── client.py               # Contributor API calls
│   │   │   │   ├── models.py
│   │   │   │   └── activity.py             # Activity analysis
│   │   │   │
│   │   │   ├── graphql/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── queries.py              # GraphQL queries
│   │   │   │   └── client.py               # GraphQL client wrapper
│   │   │   │
│   │   │   └── exceptions/
│   │       ├── __init__.py
│   │       └── github_errors.py
│   │   │
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   └── test_clients.py
│   │   │
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── skill-engine/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── analyzers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── language_analyzer.py    # Detect languages used
│   │   │   │   ├── framework_analyzer.py   # Detect frameworks
│   │   │   │   ├── contribution_analyzer.py # Analyze contributions
│   │   │   │   └── repository_analyzer.py  # Analyze repositories
│   │   │   │
│   │   │   ├── detectors/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── language_detector.py
│   │   │   │   ├── framework_detector.py
│   │   │   │   └── pattern_detector.py
│   │   │   │
│   │   │   ├── scoring/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── skill_scorer.py         # Score individual skills
│   │   │   │   ├── confidence_scorer.py    # Confidence scoring
│   │   │   │   └── algorithms.py           # Scoring algorithms
│   │   │   │
│   │   │   └── models/
│   │       ├── __init__.py
│   │       └── skill_profile.py            # Skill profile model
│   │   │
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   └── test_skill_analysis.py
│   │   │
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── issue-engine/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── analyzer/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── content_analyzer.py     # Parse issue content
│   │   │   │   ├── requirement_extractor.py # Extract requirements
│   │   │   │   └── context_analyzer.py     # Analyze context
│   │   │   │
│   │   │   ├── classifier/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── category_classifier.py  # Classify issue type
│   │   │   │   └── priority_classifier.py  # Classify priority
│   │   │   │
│   │   │   ├── difficulty/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── scorer.py               # Score difficulty
│   │   │   │   ├── indicators.py           # Difficulty indicators
│   │   │   │   └── algorithms.py
│   │   │   │
│   │   │   ├── extractor/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── skill_extractor.py      # Extract required skills
│   │   │   │   ├── file_extractor.py       # Extract relevant files
│   │   │   │   └── concept_extractor.py    # Extract learning concepts
│   │   │   │
│   │   │   └── models/
│   │       ├── __init__.py
│   │       └── issue_analysis.py
│   │   │
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   └── test_issue_analysis.py
│   │   │
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── recommendation-engine/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── matcher/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── skill_matcher.py        # Match user skills to issues
│   │   │   │   ├── similarity.py           # Similarity calculation
│   │   │   │   └── algorithms.py
│   │   │   │
│   │   │   ├── ranking/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ranker.py               # Rank recommendations
│   │   │   │   ├── strategies.py           # Ranking strategies
│   │   │   │   └── weights.py              # Weighting configuration
│   │   │   │
│   │   │   ├── scoring/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── recommendation_scorer.py # Score recommendations
│   │   │   │   └── factors.py              # Scoring factors
│   │   │   │
│   │   │   └── models/
│   │       ├── __init__.py
│   │       └── recommendation.py
│   │   │
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   └── test_recommendations.py
│   │   │
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── roadmap-engine/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── planner/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── roadmap_planner.py      # Generate roadmaps
│   │   │   │   ├── sequencer.py            # Sequence learning steps
│   │   │   │   └── strategies.py
│   │   │   │
│   │   │   ├── file_mapper/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── file_crawler.py         # Traverse file structure
│   │   │   │   ├── relevance_scorer.py     # Score file relevance
│   │   │   │   └── file_model.py
│   │   │   │
│   │   │   ├── concept_mapper/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── concept_extractor.py    # Extract concepts
│   │   │   │   ├── dependency_mapper.py    # Map concept dependencies
│   │   │   │   └── concept_model.py
│   │   │   │
│   │   │   ├── generators/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── markdown_generator.py   # Generate markdown roadmaps
│   │   │   │   ├── json_generator.py       # Generate JSON roadmaps
│   │   │   │   └── html_generator.py       # Generate HTML roadmaps
│   │   │   │
│   │   │   └── models/
│   │       ├── __init__.py
│   │       ├── roadmap.py
│   │       ├── step.py
│   │       └── learning_resource.py
│   │   │
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   └── test_roadmap_generation.py
│   │   │
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── ai-core/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── providers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py                 # Abstract provider
│   │   │   │   ├── openai_provider.py      # OpenAI implementation
│   │   │   │   ├── gemini_provider.py      # Gemini implementation
│   │   │   │   ├── anthropic_provider.py   # Anthropic implementation (future)
│   │   │   │   └── local_provider.py       # Local LLM implementation (future)
│   │   │   │
│   │   │   ├── prompts/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── prompt_templates.py     # Jinja2 prompt templates
│   │   │   │   ├── skill_analysis_prompts.py
│   │   │   │   ├── issue_analysis_prompts.py
│   │   │   │   ├── roadmap_prompts.py
│   │   │   │   └── extraction_prompts.py
│   │   │   │
│   │   │   ├── orchestrator/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── llm_orchestrator.py     # Route between providers
│   │   │   │   ├── cache_layer.py          # LLM call caching
│   │   │   │   ├── retry_policy.py         # Retry logic
│   │   │   │   └── cost_tracker.py         # Track AI costs
│   │   │   │
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chat_response.py
│   │   │   │   ├── completion_params.py
│   │   │   │   └── token_usage.py
│   │   │   │
│   │   │   └── exceptions/
│   │       ├── __init__.py
│   │       └── ai_errors.py
│   │   │
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   └── test_providers.py
│   │   │
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   ├── shared/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── constants/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── languages.py            # Supported languages
│   │   │   │   ├── frameworks.py           # Supported frameworks
│   │   │   │   └── skill_categories.py     # Skill categories
│   │   │   │
│   │   │   ├── exceptions/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py                 # Base exception
│   │   │   │   ├── http_errors.py
│   │   │   │   ├── validation_errors.py
│   │   │   │   └── external_errors.py
│   │   │   │
│   │   │   ├── logging/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── logger.py               # Logging setup
│   │   │   │   ├── formatters.py           # Log formatters
│   │   │   │   └── filters.py              # Log filters
│   │   │   │
│   │   │   ├── utils/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── string_utils.py
│   │   │   │   ├── date_utils.py
│   │   │   │   ├── hash_utils.py
│   │   │   │   └── collection_utils.py
│   │   │   │
│   │   │   └── config/
│   │       ├── __init__.py
│   │       ├── settings.py                 # Pydantic settings
│   │       ├── env_vars.py                 # Environment variables
│   │       └── secrets.py                  # Secret management
│   │   │
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   └── test_shared.py
│   │   │
│   │   ├── pyproject.toml
│   │   └── README.md
│   │
│   └── integration/
│       ├── src/
│       │   ├── __init__.py
│       │   │
│       │   ├── workflows/
│       │   │   ├── __init__.py
│       │   │   ├── profile_analysis_workflow.py    # Orchestrate profile analysis
│       │   │   ├── issue_recommendation_workflow.py # Orchestrate recommendations
│       │   │   ├── issue_analysis_workflow.py      # Orchestrate issue analysis
│       │   │   └── roadmap_workflow.py             # Orchestrate roadmap generation
│       │   │
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── profile_service.py              # Profile analysis service
│       │   │   ├── recommendation_service.py       # Recommendation service
│       │   │   ├── issue_analysis_service.py       # Issue analysis service
│       │   │   └── roadmap_service.py              # Roadmap service
│       │   │
│       │   └── cache/
│       │       ├── __init__.py
│       │       ├── cache_keys.py
│       │       └── cache_strategies.py
│       │
│       ├── tests/
│       │   ├── __init__.py
│       │   └── test_workflows.py
│       │
│       ├── pyproject.toml
│       └── README.md
│
├── infrastructure/
│   ├── database/
│   │   ├── migrations/
│   │   │   ├── versions/
│   │   │   │   ├── 001_initial_schema.py
│   │   │   │   ├── 002_add_recommendations.py
│   │   │   │   └── ...
│   │   │   ├── env.py                      # Alembic env configuration
│   │   │   ├── script.py.mako              # Alembic script template
│   │   │   └── alembic.ini                 # Alembic configuration
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                     # Base SQLAlchemy model
│   │   │   ├── user.py                     # User table model
│   │   │   ├── user_skill.py               # UserSkill table model
│   │   │   ├── repository.py               # Repository table model
│   │   │   ├── issue.py                    # Issue table model
│   │   │   ├── recommendation.py           # Recommendation table model
│   │   │   ├── roadmap.py                  # Roadmap table model
│   │   │   ├── roadmap_step.py             # RoadmapStep table model
│   │   │   ├── learning_concept.py         # LearningConcept table model
│   │   │   └── audit_log.py                # Audit log table model
│   │   │
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base_repository.py          # Abstract repository
│   │   │   ├── user_repository.py
│   │   │   ├── skill_repository.py
│   │   │   ├── issue_repository.py
│   │   │   ├── recommendation_repository.py
│   │   │   └── roadmap_repository.py
│   │   │
│   │   ├── connection.py                   # Database connection setup
│   │   ├── session.py                      # Session factory
│   │   └── README.md
│   │
│   ├── redis/
│   │   ├── __init__.py
│   │   ├── client.py                       # Redis client setup
│   │   ├── cache_manager.py                # Cache operations
│   │   └── pubsub.py                       # Pub/Sub operations
│   │
│   ├── celery/
│   │   ├── __init__.py
│   │   ├── config.py                       # Celery configuration
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   ├── profile_tasks.py            # Profile analysis async tasks
│   │   │   ├── recommendation_tasks.py     # Recommendation async tasks
│   │   │   ├── issue_tasks.py              # Issue analysis async tasks
│   │   │   └── roadmap_tasks.py            # Roadmap generation async tasks
│   │   │
│   │   └── worker.py                       # Celery worker setup
│   │
│   └── docker/
│       ├── api.dockerfile                  # FastAPI container
│       ├── worker.dockerfile               # Celery worker container
│       ├── postgres.dockerfile             # PostgreSQL container
│       ├── redis.dockerfile                # Redis container
│       └── nginx.dockerfile                # Nginx reverse proxy
│
├── docs/
│   ├── architecture/
│   │   ├── ARCHITECTURE.md                 # This document
│   │   ├── DECISIONS.md                    # Architecture Decision Records
│   │   ├── MODULE_DESIGN.md                # Module interaction diagrams
│   │   ├── DATA_FLOW.md                    # Data flow diagrams
│   │   └── SCALABILITY.md                  # Scalability strategies
│   │
│   ├── api/
│   │   ├── ENDPOINTS.md                    # API endpoint documentation
│   │   ├── SCHEMAS.md                      # Request/response schemas
│   │   ├── ERRORS.md                       # Error codes and handling
│   │   └── EXAMPLES.md                     # API usage examples
│   │
│   ├── development/
│   │   ├── SETUP.md                        # Development environment setup
│   │   ├── CONTRIBUTING.md                 # Contribution guidelines
│   │   ├── TESTING.md                      # Testing strategy
│   │   └── DEPLOYMENT.md                   # Deployment guide
│   │
│   ├── guides/
│   │   ├── ONBOARDING.md                   # New developer onboarding
│   │   ├── ADDING_FEATURES.md              # How to add new features
│   │   └── DEBUGGING.md                    # Debugging guide
│   │
│   └── roadmap/
│       └── IMPLEMENTATION_ROADMAP.md       # Implementation phases
│
├── scripts/
│   ├── setup.sh                            # Development environment setup
│   ├── setup_db.py                         # Database initialization
│   ├── seed.py                             # Seed test data
│   ├── lint.sh                             # Run linters
│   ├── format.sh                           # Format code
│   ├── test.sh                             # Run all tests
│   ├── coverage.sh                         # Run coverage analysis
│   ├── docker_build.sh                     # Build Docker images
│   └── docker_compose_up.sh                # Start Docker containers
│
├── tests/
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_profile_workflow.py
│   │   ├── test_recommendation_workflow.py
│   │   ├── test_issue_analysis_workflow.py
│   │   └── test_roadmap_workflow.py
│   │
│   ├── e2e/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_complete_user_journey.py
│   │   └── test_api_flows.py
│   │
│   └── fixtures/
│       ├── __init__.py
│       ├── users.py
│       ├── repositories.py
│       ├── issues.py
│       └── skills.py
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                          # Unit test CI
│   │   ├── integration_tests.yml           # Integration tests CI
│   │   ├── code_quality.yml                # Lint, format checks
│   │   ├── security.yml                    # Security scanning
│   │   └── deployment.yml                  # Deployment CI/CD
│   │
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── architecture_decision.md
│   │
│   └── PULL_REQUEST_TEMPLATE.md
│
├── .env.example                            # Example environment variables
├── .gitignore
├── docker-compose.yml                      # Local development docker setup
├── pyproject.toml                          # Root project configuration
├── poetry.lock                             # Dependency lock file
├── pytest.ini                              # Pytest configuration
├── .pre-commit-config.yaml                 # Pre-commit hooks
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

---

## 2. Folder Responsibilities

### Root Level

| Folder | Responsibility | What Belongs | What Never Belongs |
|--------|---|---|---|
| `apps/` | **Application entry points** | API, CLI, Extensions | Domain logic, infrastructure drivers |
| `packages/` | **Reusable domain & service libraries** | Domain logic, services, shared utilities | Application routes, CLI commands |
| `infrastructure/` | **Database, cache, job queue** | DB models, migrations, connections | Business logic, API handlers |
| `docs/` | **Project documentation** | Architecture, guides, API docs | Code (except examples) |
| `scripts/` | **Development & deployment scripts** | Setup, database init, CI/CD helpers | Production application code |
| `tests/` | **Cross-module integration & E2E tests** | Workflow tests, journey tests | Unit tests (go in each package) |
| `.github/` | **GitHub-specific configuration** | Workflows, templates, automation | Source code, assets |

---

### `apps/api/` - FastAPI Application

**Responsibility:** HTTP API entry point. Request routing and response formatting only.

**What Belongs:**
- Route handlers (receive requests, call services, return responses)
- Middleware (auth, logging, rate limiting)
- Dependency injection
- Request/response schemas (Pydantic models)
- Global exception handlers

**What Never Belongs:**
- Business logic (should be in `packages/integration/services/`)
- Database queries (should be in repositories)
- Direct GitHub API calls (should be in `github-client` package)
- AI model calls (should be through `ai-core` package)

**Key Principle:** Each route should be < 20 lines. If longer, extract to service layer.

---

### `apps/cli/` - Command Line Interface

**Responsibility:** CLI entry point using Typer. Interactive terminal interface for CodeTrail.

**What Belongs:**
- Commands (codetrail login, recommend, analyze, etc.)
- Input prompts and validation
- Output formatting (tables, markdown, JSON)
- Local token/config storage
- CLI-specific error handling

**What Never Belongs:**
- Core business logic
- API client implementation (should wrap service layer)
- Database access

**Key Principle:** CLI delegates to same service layer as API. Both are thin clients.

---

### `apps/vscode-extension/` - VS Code Extension

**Responsibility:** IDE integration for CodeTrail experience.

**What Belongs:**
- VS Code command handlers
- Tree view providers
- WebView panels
- Settings management
- Sidebar displays
- Extension activation/deactivation logic

**What Never Belongs:**
- Python business logic (call API instead)
- Database logic
- Core algorithms

**Key Principle:** VS Code extension communicates with API, not direct package access.

---

### `apps/github-action/` - GitHub Action

**Responsibility:** GitHub Actions workflow automation.

**What Belongs:**
- Webhook handlers
- Issue/PR event processing
- Comments on issues/PRs
- GitHub API interactions specific to Actions
- Workflow orchestration

**What Never Belongs:**
- Analysis logic (call API)
- Local state (should be in CodeTrail backend)

**Key Principle:** Listen to GitHub events, trigger CodeTrail API, post results as comments.

---

### `packages/core-domain/` - Domain Model

**Responsibility:** Core domain entities and value objects. Pure business logic.

**What Belongs:**
- `User`, `Repository`, `Skill`, `Issue`, `Recommendation`, `Roadmap`, `LearningConcept` entities
- Value objects (`SkillLevel`, `Difficulty`, `Language`, `MatchingScore`)
- Domain exceptions
- Domain events

**What Never Belongs:**
- ORM annotations (except as markers for infrastructure)
- Infrastructure dependencies
- API knowledge
- Database-specific code

**Key Principle:** These entities are database/framework agnostic. Pure Python classes.

---

### `packages/github-client/` - GitHub Integration

**Responsibility:** All GitHub API interactions.

**What Belongs:**
- OAuth authentication
- GraphQL queries
- REST API calls
- Issue/PR fetching
- Repository metadata
- Contributor activity

**What Never Belongs:**
- Business logic (analyzing issues)
- Database operations
- AI calls

**Key Principle:** Single responsibility: Get data from GitHub and return Python objects.

---

### `packages/skill-engine/` - Skill Analysis

**Responsibility:** Analyze developer skills from GitHub profile.

**What Belongs:**
- Language detection
- Framework detection
- Repository analysis
- Skill scoring
- Confidence calculation

**What Never Belongs:**
- Storing skills (that's infrastructure)
- Calling GitHub directly (use github-client)
- API routing

**Key Principle:** Input: GitHub data. Output: SkillProfile object.

---

### `packages/issue-engine/` - Issue Analysis

**Responsibility:** Deep analysis of GitHub issues.

**What Belongs:**
- Content parsing
- Requirement extraction
- Difficulty scoring
- Category classification
- Skill requirement extraction
- File relevance identification

**What Never Belongs:**
- Storing analysis (that's infrastructure)
- Matching to users (that's recommendation-engine)
- Fetching issues (that's github-client)

**Key Principle:** Input: GitHub Issue. Output: IssueAnalysis object with structured data.

---

### `packages/recommendation-engine/` - Recommendation Logic

**Responsibility:** Match issues to users.

**What Belongs:**
- Skill matching algorithms
- Similarity scoring
- Ranking strategies
- Recommendation filtering
- Weighting configuration

**What Never Belongs:**
- Storing recommendations (that's infrastructure)
- Analyzing issues (that's issue-engine)
- Analyzing skills (that's skill-engine)

**Key Principle:** Input: User skills + Issue analysis. Output: Ranked recommendation list.

---

### `packages/roadmap-engine/` - Learning Roadmap

**Responsibility:** Generate learning paths for contributors.

**What Belongs:**
- Roadmap generation
- Step sequencing
- File mapping
- Concept extraction
- Format generation (Markdown, JSON, HTML)

**What Never Belongs:**
- Storing roadmaps
- Fetching files from GitHub (use github-client)
- Analyzing code

**Key Principle:** Input: Issue analysis + User context. Output: Structured learning roadmap.

---

### `packages/ai-core/` - AI Provider Abstraction

**Responsibility:** Provider-agnostic AI interaction layer.

**What Belongs:**
- Abstract provider interface
- OpenAI implementation
- Gemini implementation
- Anthropic implementation (future)
- Prompt templates
- LLM call orchestration
- Response caching
- Cost tracking

**What Never Belongs:**
- Business logic (use services)
- Domain entities
- Direct database access

**Key Principle:** Abstract away provider details. Services use without knowing implementation.

---

### `packages/shared/` - Shared Utilities

**Responsibility:** Cross-cutting concerns and constants.

**What Belongs:**
- Constants (supported languages, frameworks)
- Custom exceptions
- Logging setup
- Configuration management
- Utility functions
- Secret management

**What Never Belongs:**
- Business logic specific to one feature
- Domain entities
- API routes

**Key Principle:** If used by multiple packages, it belongs here.

---

### `packages/integration/` - Service Layer & Workflows

**Responsibility:** Orchestrate packages into cohesive services and workflows.

**What Belongs:**
- `ProfileService`: Use skill-engine + github-client to analyze profile
- `RecommendationService`: Use issue-engine + recommendation-engine to match
- `IssueAnalysisService`: Use issue-engine + roadmap-engine for deep analysis
- `RoadmapService`: Use roadmap-engine to generate learning paths
- Workflows that combine multiple services
- Cache strategies for performance

**What Never Belongs:**
- Low-level implementations (those are in specific packages)
- Request/response schemas (those are in API layer)
- Infrastructure setup

**Key Principle:** Services are the orchestration layer. API/CLI call these services.

---

### `infrastructure/database/` - Persistence Layer

**Responsibility:** Database models, migrations, repository pattern.

**What Belongs:**
- SQLAlchemy ORM models
- Alembic migrations
- Repository implementations
- Database connection setup
- Query builders

**What Never Belongs:**
- Business logic
- API schemas
- Domain entities (though there's mapping between domains ↔ ORM)

**Key Principle:** Infrastructure detail. Abstracted through repositories.

---

### `infrastructure/redis/` - Caching

**Responsibility:** Cache management.

**What Belongs:**
- Redis client setup
- Cache operations (get, set, delete)
- Pub/Sub messaging
- Session storage

**What Never Belongs:**
- Cache logic (services decide what to cache)
- Domain entities

**Key Principle:** Thin wrapper around Redis operations.

---

### `infrastructure/celery/` - Async Jobs

**Responsibility:** Background job processing.

**What Belongs:**
- Celery configuration
- Async task definitions
- Task scheduling
- Result backends

**What Never Belongs:**
- Business logic of tasks (call services instead)

**Key Principle:** Tasks are thin wrappers that call services.

---

### `docs/` - Documentation

**Responsibility:** Project documentation.

**What Belongs:**
- Architecture decisions (ADRs)
- API documentation
- Development guides
- Deployment guides
- Design diagrams

**What Never Belongs:**
- Inline code comments (those are in code)
- Auto-generated API docs (build those)

---

---

## 3. Domain Model Design

### Core Entities

#### User
```python
class User:
    id: UUID
    github_username: str
    github_id: int
    email: str
    avatar_url: str
    profile_url: str
    bio: str
    location: str
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    skills: List[Skill]
    repositories: List[Repository]
    recommendations: List[Recommendation]
    roadmaps: List[Roadmap]
```

**Responsibility:** Represents a contributor on CodeTrail.

---

#### Skill
```python
class Skill:
    id: UUID
    user_id: UUID
    technology: str  # "Python", "React", "FastAPI"
    category: SkillCategory  # LANGUAGE, FRAMEWORK, DATABASE
    proficiency: SkillLevel  # BEGINNER, INTERMEDIATE, ADVANCED, EXPERT
    confidence_score: float  # 0-100
    evidence_count: int  # How many projects demonstrate skill
    last_updated: datetime
    
    # Relationships
    user: User
```

**Responsibility:** Represents a skill with proficiency level.

---

#### Repository
```python
class Repository:
    id: UUID
    github_id: int
    owner: str
    name: str
    url: str
    description: str
    language: str
    stars: int
    forks: int
    open_issues_count: int
    last_updated: datetime
    
    # Relationships
    issues: List[Issue]
    skills_required: List[Skill]
```

**Responsibility:** GitHub repository metadata.

---

#### Issue
```python
class Issue:
    id: UUID
    github_id: int
    repository_id: UUID
    title: str
    description: str
    status: IssueStatus  # OPEN, CLOSED
    difficulty: Difficulty  # BEGINNER, INTERMEDIATE, ADVANCED
    category: IssueCategory
    labels: List[str]
    comments_count: int
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    repository: Repository
    analysis: IssueAnalysis
    recommendations: List[Recommendation]
```

**Responsibility:** GitHub issue representation.

---

#### IssueAnalysis
```python
class IssueAnalysis:
    id: UUID
    issue_id: UUID
    required_skills: List[str]  # ["FastAPI", "JWT", "Testing"]
    missing_skills: List[str]   # For user comparison
    relevant_files: List[str]   # ["auth.py", "middleware.py"]
    concepts: List[LearningConcept]
    estimated_hours: float
    created_at: datetime
    
    # Relationships
    issue: Issue
```

**Responsibility:** Enriched analysis of an issue.

---

#### Recommendation
```python
class Recommendation:
    id: UUID
    user_id: UUID
    issue_id: UUID
    matching_score: float  # 0-100
    match_factors: Dict[str, float]  # {skill_match: 85, difficulty: 75}
    missing_skills: List[str]
    created_at: datetime
    
    # Relationships
    user: User
    issue: Issue
```

**Responsibility:** A recommended issue for a user.

---

#### Roadmap
```python
class Roadmap:
    id: UUID
    user_id: UUID
    issue_id: UUID
    steps: List[RoadmapStep]
    total_estimated_hours: float
    generated_at: datetime
    
    # Relationships
    user: User
    issue: Issue
    steps: List[RoadmapStep]
```

**Responsibility:** A learning path for contributing to an issue.

---

#### RoadmapStep
```python
class RoadmapStep:
    id: UUID
    roadmap_id: UUID
    sequence: int
    title: str
    description: str
    resources: List[LearningResource]  # Links to files, docs
    concepts: List[LearningConcept]
    estimated_hours: float
    
    # Relationships
    roadmap: Roadmap
```

**Responsibility:** Individual step in a learning roadmap.

---

#### LearningConcept
```python
class LearningConcept:
    id: UUID
    name: str
    description: str
    category: str  # PATTERN, ALGORITHM, LIBRARY, BEST_PRACTICE
    related_concepts: List[str]
    learning_resources: List[str]  # URLs
```

**Responsibility:** A concept developers need to learn.

---

### Value Objects

#### SkillLevel
```python
class SkillLevel(Enum):
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
```

---

#### Difficulty
```python
class Difficulty(Enum):
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4
```

---

#### MatchingScore
```python
class MatchingScore:
    total: float  # 0-100
    skill_match: float
    difficulty_match: float
    interest_match: float  # Based on repos
```

---

### Entity Relationships Diagram

```
User (1) ─── (N) Skill
   │
   ├─ (1) ─── (N) Recommendation
   │              │
   │              └─ (N) ─── (1) Issue
   │                            │
   │                            ├─ (1) Repository
   │                            └─ (1) IssueAnalysis
   │
   └─ (1) ─── (N) Roadmap
                   │
                   ├─ (N) ─── (1) Issue
                   └─ (1) ─── (N) RoadmapStep
                                   │
                                   └─ (N) ─── (M) LearningConcept
```

---

## 4. Service Layer Architecture

### ProfileService
**Location:** `packages/integration/services/profile_service.py`

**Responsibility:** Analyze user's GitHub profile and generate skill profile.

**Workflow:**
1. Fetch user's GitHub profile (github-client)
2. Fetch user's repositories (github-client)
3. Analyze repositories for languages, frameworks (skill-engine)
4. Calculate skill proficiency scores (skill-engine)
5. Store in database (repository layer)
6. Cache result in Redis
7. Return SkillProfile

**Dependencies:**
- `GitHubClient`
- `SkillEngine`
- `UserRepository`
- `SkillRepository`
- `CacheManager`

**Public Interface:**
```python
async def analyze_user_profile(github_token: str) -> SkillProfile:
    """Analyze user and return skill profile."""
    
async def refresh_user_profile(user_id: UUID) -> SkillProfile:
    """Refresh existing user profile."""
    
async def get_skill_profile(user_id: UUID) -> Optional[SkillProfile]:
    """Get cached skill profile."""
```

---

### RecommendationService
**Location:** `packages/integration/services/recommendation_service.py`

**Responsibility:** Recommend issues matching user skills.

**Workflow:**
1. Get user's skill profile (ProfileService)
2. Fetch issues from repositories user follows
3. Analyze each issue (IssueService)
4. Match issues to user skills (recommendation-engine)
5. Rank recommendations (recommendation-engine)
6. Filter and limit results
7. Store recommendations in database
8. Return ranked list

**Dependencies:**
- `ProfileService`
- `IssueAnalysisService`
- `RecommendationEngine`
- `RecommendationRepository`
- `CacheManager`

**Public Interface:**
```python
async def get_recommendations(
    user_id: UUID, 
    limit: int = 10,
    difficulty: Optional[Difficulty] = None
) -> List[Recommendation]:
    """Get personalized issue recommendations."""
    
async def recommend_for_repository(
    user_id: UUID,
    repo_name: str,
    limit: int = 5
) -> List[Recommendation]:
    """Get recommendations for specific repository."""
```

---

### IssueAnalysisService
**Location:** `packages/integration/services/issue_analysis_service.py`

**Responsibility:** Deep analysis of individual issues.

**Workflow:**
1. Fetch issue from GitHub (github-client)
2. Parse issue content (issue-engine)
3. Extract required skills (issue-engine)
4. Identify relevant files (issue-engine)
5. Classify difficulty (issue-engine)
6. Extract learning concepts (issue-engine)
7. Store analysis in database
8. Cache result
9. Return IssueAnalysis

**Dependencies:**
- `GitHubClient`
- `IssueEngine`
- `IssueRepository`
- `LearningConceptRepository`
- `CacheManager`

**Public Interface:**
```python
async def analyze_issue(
    repo_name: str,
    issue_number: int
) -> IssueAnalysis:
    """Analyze GitHub issue."""
    
async def get_issue_analysis(issue_id: UUID) -> Optional[IssueAnalysis]:
    """Get cached issue analysis."""
```

---

### RoadmapService
**Location:** `packages/integration/services/roadmap_service.py`

**Responsibility:** Generate learning roadmaps for issues.

**Workflow:**
1. Get issue analysis (IssueAnalysisService)
2. Get user's skill profile (ProfileService)
3. Identify missing skills
4. Generate learning path (roadmap-engine)
5. Map relevant files (roadmap-engine)
6. Create learning resources
7. Store roadmap in database
8. Generate markdown/JSON output
9. Cache result
10. Return Roadmap

**Dependencies:**
- `IssueAnalysisService`
- `ProfileService`
- `RoadmapEngine`
- `RoadmapRepository`
- `CacheManager`

**Public Interface:**
```python
async def generate_roadmap(
    user_id: UUID,
    issue_id: UUID
) -> Roadmap:
    """Generate learning roadmap for user to solve issue."""
    
async def export_roadmap(
    roadmap_id: UUID,
    format: str = "markdown"  # markdown, json, html
) -> str:
    """Export roadmap in specified format."""
```

---

### Service Interaction Diagram

```
┌─────────────────┐
│  API Routes     │
└────────┬────────┘
         │
         ├──► ProfileService
         │       │
         │       ├──► GitHubClient
         │       └──► SkillEngine
         │
         ├──► RecommendationService
         │       │
         │       ├──► ProfileService
         │       ├──► IssueAnalysisService
         │       └──► RecommendationEngine
         │
         ├──► IssueAnalysisService
         │       │
         │       ├──► GitHubClient
         │       └──► IssueEngine
         │
         └──► RoadmapService
                 │
                 ├──► IssueAnalysisService
                 ├──► ProfileService
                 └──► RoadmapEngine
```

---

## 5. Database Schema

### Tables

#### users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    github_id INT UNIQUE NOT NULL,
    github_username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    avatar_url TEXT,
    profile_url TEXT,
    bio TEXT,
    location VARCHAR(255),
    github_token_encrypted TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_profile_analysis TIMESTAMP
);

CREATE INDEX idx_github_username ON users(github_username);
CREATE INDEX idx_github_id ON users(github_id);
```

---

#### skills
```sql
CREATE TABLE skills (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    technology VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,  -- LANGUAGE, FRAMEWORK, DATABASE
    proficiency INT NOT NULL,        -- 1-4: BEGINNER to EXPERT
    confidence_score FLOAT NOT NULL,
    evidence_count INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, technology)
);

CREATE INDEX idx_user_skills ON skills(user_id);
CREATE INDEX idx_technology ON skills(technology);
```

---

#### repositories
```sql
CREATE TABLE repositories (
    id UUID PRIMARY KEY,
    github_id INT UNIQUE NOT NULL,
    owner VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    description TEXT,
    language VARCHAR(50),
    stars INT DEFAULT 0,
    forks INT DEFAULT 0,
    open_issues_count INT DEFAULT 0,
    last_github_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_github_id_repo ON repositories(github_id);
CREATE INDEX idx_owner_name ON repositories(owner, name);
```

---

#### issues
```sql
CREATE TABLE issues (
    id UUID PRIMARY KEY,
    github_id INT NOT NULL,
    repository_id UUID NOT NULL REFERENCES repositories(id),
    title VARCHAR(512) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL,
    difficulty INT,                  -- 1-4: BEGINNER to EXPERT
    category VARCHAR(100),
    labels JSONB,
    comments_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(github_id, repository_id)
);

CREATE INDEX idx_repo_issues ON issues(repository_id);
CREATE INDEX idx_difficulty ON issues(difficulty);
CREATE INDEX idx_status ON issues(status);
```

---

#### issue_analyses
```sql
CREATE TABLE issue_analyses (
    id UUID PRIMARY KEY,
    issue_id UUID NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    required_skills JSONB NOT NULL,  -- ["FastAPI", "JWT"]
    relevant_files JSONB NOT NULL,   -- ["auth.py", "models.py"]
    concepts JSONB NOT NULL,         -- ["JWT", "OAuth", "Middleware"]
    estimated_hours FLOAT,
    analysis_version INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(issue_id)
);

CREATE INDEX idx_issue_analysis ON issue_analyses(issue_id);
```

---

#### recommendations
```sql
CREATE TABLE recommendations (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    issue_id UUID NOT NULL REFERENCES issues(id) ON DELETE CASCADE,
    matching_score FLOAT NOT NULL,
    match_factors JSONB NOT NULL,   -- {skill_match: 85, difficulty: 75}
    missing_skills JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    viewed_at TIMESTAMP,
    
    UNIQUE(user_id, issue_id)
);

CREATE INDEX idx_user_recommendations ON recommendations(user_id, created_at DESC);
CREATE INDEX idx_issue_recommendations ON recommendations(issue_id);
```

---

#### roadmaps
```sql
CREATE TABLE roadmaps (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    issue_id UUID NOT NULL REFERENCES issues(id),
    total_estimated_hours FLOAT,
    status VARCHAR(50) DEFAULT 'active',  -- active, completed, abandoned
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    generated_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, issue_id)
);

CREATE INDEX idx_user_roadmaps ON roadmaps(user_id);
CREATE INDEX idx_issue_roadmaps ON roadmaps(issue_id);
```

---

#### roadmap_steps
```sql
CREATE TABLE roadmap_steps (
    id UUID PRIMARY KEY,
    roadmap_id UUID NOT NULL REFERENCES roadmaps(id) ON DELETE CASCADE,
    sequence INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    resources JSONB,                 -- [{name, url, type}]
    concepts JSONB,                  -- [{name, description}]
    estimated_hours FLOAT,
    completed_at TIMESTAMP,
    
    UNIQUE(roadmap_id, sequence)
);

CREATE INDEX idx_roadmap_steps ON roadmap_steps(roadmap_id, sequence);
```

---

#### learning_concepts
```sql
CREATE TABLE learning_concepts (
    id UUID PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    category VARCHAR(100),           -- PATTERN, ALGORITHM, LIBRARY
    related_concepts JSONB,          -- ["JWT", "OAuth"]
    learning_resources JSONB,        -- [URLs]
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_concept_name ON learning_concepts(name);
CREATE INDEX idx_concept_category ON learning_concepts(category);
```

---

#### audit_logs
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    changes JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_logs ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_entity_logs ON audit_logs(entity_type, entity_id);
```

---

### Indexing Strategy

**Hot Path Indexes:**
- `users.github_username` - Profile lookup
- `recommendations.user_id` - User's recommendations
- `issues.repository_id` - Repo issues
- `skills.user_id` - User's skills
- `roadmaps.user_id` - User's roadmaps

**Query Performance Considerations:**
- Recommendations query: Use composite index `(user_id, created_at DESC)`
- Skill lookup: Single index on `user_id` + `technology`
- Roadmap generation: Join roadmaps → steps → concepts (use tree structure in JSONB)

---

## 6. API Design

### Base URL
```
https://api.codetrail.dev/v1
```

### Authentication
All endpoints except `/auth/github/callback` require `Authorization: Bearer {token}`

---

### Endpoints

#### Authentication

##### `POST /auth/github`
Initiate GitHub OAuth flow.

**Request:**
```json
{
  "redirect_uri": "http://localhost:3000/callback"
}
```

**Response:**
```json
{
  "auth_url": "https://github.com/login/oauth/authorize?...",
  "state": "random_state_value"
}
```

---

##### `POST /auth/github/callback`
Handle OAuth callback.

**Request:**
```json
{
  "code": "github_auth_code",
  "state": "state_value"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "token_type": "Bearer",
  "expires_in": 86400,
  "user": {
    "id": "user_uuid",
    "github_username": "octocat",
    "email": "octocat@github.com"
  }
}
```

---

##### `POST /auth/logout`
Logout user.

**Request:** (empty body)

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

---

#### Profile

##### `GET /profile`
Get authenticated user's profile.

**Response:**
```json
{
  "id": "user_uuid",
  "github_username": "octocat",
  "email": "octocat@github.com",
  "avatar_url": "https://...",
  "skills": [
    {
      "id": "skill_uuid",
      "technology": "Python",
      "category": "LANGUAGE",
      "proficiency": "ADVANCED",
      "confidence_score": 92,
      "evidence_count": 25
    }
  ],
  "total_repositories": 42,
  "followers": 1234,
  "last_analysis": "2026-05-30T10:00:00Z"
}
```

---

##### `POST /profile/analyze`
Trigger profile analysis (async).

**Request:** (empty body)

**Response:**
```json
{
  "task_id": "celery_task_uuid",
  "status": "PROCESSING",
  "message": "Profile analysis started"
}
```

---

##### `GET /profile/analysis-status/{task_id}`
Get analysis status.

**Response:**
```json
{
  "task_id": "celery_task_uuid",
  "status": "COMPLETED",
  "progress": 100,
  "result": {
    "skills_analyzed": 15,
    "confidence_improved": 5,
    "new_technologies": 2
  }
}
```

---

#### Recommendations

##### `GET /recommendations`
Get issue recommendations.

**Query Parameters:**
- `limit` (default 10)
- `difficulty` (BEGINNER, INTERMEDIATE, ADVANCED)
- `offset` (default 0)

**Response:**
```json
{
  "total": 247,
  "limit": 10,
  "offset": 0,
  "recommendations": [
    {
      "id": "rec_uuid",
      "issue": {
        "id": "issue_uuid",
        "title": "Add JWT authentication",
        "repository": "fastapi/fastapi",
        "url": "https://github.com/fastapi/fastapi/issues/123",
        "difficulty": "INTERMEDIATE"
      },
      "matching_score": 92,
      "match_factors": {
        "skill_match": 95,
        "difficulty_match": 90,
        "interest_match": 85
      },
      "missing_skills": ["Pytest"],
      "estimated_hours": 4
    }
  ]
}
```

---

##### `GET /recommendations/{repo_owner}/{repo_name}`
Get recommendations for specific repository.

**Response:** Same as above, filtered for repository.

---

#### Issues

##### `POST /issues/analyze`
Analyze a GitHub issue.

**Request:**
```json
{
  "repository": "owner/repo",
  "issue_number": 123
}
```

**Response:**
```json
{
  "id": "analysis_uuid",
  "issue": {
    "id": "issue_uuid",
    "title": "Add JWT authentication",
    "repository": "fastapi/fastapi"
  },
  "difficulty": "INTERMEDIATE",
  "required_skills": ["FastAPI", "JWT", "Cryptography"],
  "missing_skills": [],
  "relevant_files": [
    {
      "path": "fastapi/security/oauth2.py",
      "relevance": 95,
      "snippet": "def get_current_user(...):"
    }
  ],
  "learning_concepts": [
    {
      "name": "JWT Authentication",
      "description": "Stateless authentication using JSON Web Tokens",
      "related_concepts": ["OAuth2", "Security"]
    }
  ],
  "estimated_hours": 4,
  "discussion_summary": "Issue is about adding JWT support..."
}
```

---

#### Roadmaps

##### `POST /roadmaps`
Generate learning roadmap.

**Request:**
```json
{
  "issue_id": "issue_uuid"
}
```

**Response:**
```json
{
  "id": "roadmap_uuid",
  "issue": {
    "id": "issue_uuid",
    "title": "Add JWT authentication"
  },
  "total_estimated_hours": 12,
  "steps": [
    {
      "sequence": 1,
      "title": "Understand JWT",
      "description": "Learn JWT structure and purpose",
      "resources": [
        {
          "title": "JWT.io",
          "url": "https://jwt.io",
          "type": "DOCUMENTATION"
        }
      ],
      "concepts": ["JWT", "Tokens", "Claims"],
      "estimated_hours": 2
    },
    {
      "sequence": 2,
      "title": "Explore fastapi/security",
      "description": "Read FastAPI's security module",
      "resources": [
        {
          "title": "fastapi/security/oauth2.py",
          "path": "fastapi/security/oauth2.py",
          "type": "SOURCE_FILE"
        }
      ],
      "concepts": ["FastAPI", "Security", "Middleware"],
      "estimated_hours": 3
    }
  ],
  "generated_at": "2026-05-30T10:00:00Z"
}
```

---

##### `GET /roadmaps/{roadmap_id}`
Get roadmap by ID.

**Response:** Same as above.

---

##### `GET /roadmaps`
Get user's roadmaps.

**Query Parameters:**
- `status` (active, completed, abandoned)
- `limit` (default 10)

**Response:**
```json
{
  "total": 5,
  "limit": 10,
  "roadmaps": [
    {
      "id": "roadmap_uuid",
      "issue": {...},
      "total_estimated_hours": 12,
      "status": "active",
      "progress": 25,
      "started_at": "2026-05-25T10:00:00Z"
    }
  ]
}
```

---

##### `PATCH /roadmaps/{roadmap_id}`
Update roadmap status.

**Request:**
```json
{
  "status": "completed"
}
```

**Response:**
```json
{
  "id": "roadmap_uuid",
  "status": "completed",
  "completed_at": "2026-05-30T15:00:00Z"
}
```

---

##### `GET /roadmaps/{roadmap_id}/export`
Export roadmap in format.

**Query Parameters:**
- `format` (markdown, json, html)

**Response:** Raw file content

---

### Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid query parameter",
    "details": {
      "field": "difficulty",
      "reason": "Must be one of: BEGINNER, INTERMEDIATE, ADVANCED"
    }
  }
}
```

### Error Codes

| Code | HTTP | Meaning |
|------|------|---------|
| `UNAUTHORIZED` | 401 | Missing/invalid token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `INVALID_REQUEST` | 400 | Invalid parameters |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `GITHUB_ERROR` | 502 | GitHub API error |

---

## 7. CLI Design

### Command Structure

```bash
codetrail [COMMAND] [OPTIONS]
```

---

### Commands

#### `codetrail auth login`
Authenticate with GitHub.

```bash
codetrail auth login

# Output:
# 🔐 Opening GitHub authentication...
# ✅ Logged in as @octocat
# 📦 Token saved to ~/.codetrail/config
```

---

#### `codetrail auth logout`
Logout.

```bash
codetrail auth logout

# Output:
# ✅ Logged out successfully
```

---

#### `codetrail profile`
Show user's skill profile.

```bash
codetrail profile

# Output (table):
# ┌─────────────────┬────────────┬──────────┐
# │ Technology      │ Proficiency│ Confidence
# ├─────────────────┼────────────┼──────────┤
# │ Python          │ ADVANCED   │ 92%
# │ FastAPI         │ ADVANCED   │ 80%
# │ React           │ INTERMEDIATE│ 74%
# │ Docker          │ BEGINNER   │ 25%
# └─────────────────┴────────────┴──────────┘
```

---

#### `codetrail profile update`
Refresh profile analysis (async).

```bash
codetrail profile update --wait

# Output:
# 🔄 Updating profile analysis...
# ⏳ Processing repositories... [████████░░] 80%
# ✅ Analysis complete!
# 📊 Found 2 new technologies
# 📈 Improved confidence in Python to 94%
```

---

#### `codetrail recommend`
Get issue recommendations.

```bash
codetrail recommend --limit 5 --difficulty INTERMEDIATE

# Output (table):
# ┌─────────────────────────────┬────────┬──────────────────┐
# │ Repository                  │ Score  │ Missing Skills
# ├─────────────────────────────┼────────┼──────────────────┤
# │ fastapi/fastapi #1234       │ 92%    │ Pytest
# │ django/django #5678         │ 85%    │ —
# │ pallets/flask #2345         │ 81%    │ Celery, Redis
# └─────────────────────────────┴────────┴──────────────────┘

# 💡 Run `codetrail analyze owner/repo #1234` for details
```

---

#### `codetrail recommend --repository owner/repo`
Get recommendations for specific repository.

```bash
codetrail recommend --repository fastapi/fastapi

# Output: Same as above, filtered for fastapi/fastapi
```

---

#### `codetrail analyze owner/repo #123`
Deep dive into an issue.

```bash
codetrail analyze fastapi/fastapi #1234

# Output (formatted markdown):
# 
# # Issue: Add JWT authentication
# 
# **Difficulty:** Intermediate (74%)
# **Estimated Time:** 4 hours
# 
# ## Required Skills
# - FastAPI ✅
# - JWT ⚠️  (Limited experience)
# - Cryptography ❌ (Missing)
# 
# ## Relevant Files
# 1. fastapi/security/oauth2.py (95% relevant)
# 2. fastapi/security/utils.py (87% relevant)
# 
# ## Key Concepts
# - JWT Authentication (Stateless, secure)
# - OAuth2 (OpenID standard)
# - Password Hashing (bcrypt)
```

---

#### `codetrail roadmap owner/repo #123 [--format markdown|json|html]`
Generate and display roadmap.

```bash
codetrail roadmap fastapi/fastapi #1234

# Output:
# 
# # Learning Roadmap: Add JWT authentication
# ⏱️  Total time: 12 hours
# 
# ## Step 1: Understand JWT (2 hours)
# - 📖 Read: https://jwt.io
# - 📖 Watch: JWT Basics video
# - Concepts: JWT, Claims, Signatures
# 
# ## Step 2: Explore FastAPI Security (3 hours)
# - 📄 Read: fastapi/security/oauth2.py
# - 🧪 Run: `pytest tests/security/`
# - Concepts: FastAPI, Security, Decorators
#
# ... (more steps)
# 
# 💾 Save: `codetrail roadmap owner/repo #1234 --export roadmap.md`
```

---

#### `codetrail roadmap --list`
List user's saved roadmaps.

```bash
codetrail roadmap --list

# Output:
# ┌──────────────────────────────┬────────┬──────────┐
# │ Issue                        │ Status │ Progress
# ├──────────────────────────────┼────────┼──────────┤
# │ fastapi/fastapi #1234        │ Active │ 25%
# │ django/django #5678          │ Done   │ 100%
# │ pallets/flask #2345          │ Active │ 60%
# └──────────────────────────────┴────────┴──────────┘
```

---

#### `codetrail roadmap --export roadmap_id --format markdown`
Export roadmap.

```bash
codetrail roadmap --export abc123 --format markdown > roadmap.md

# Output:
# ✅ Roadmap exported to roadmap.md
```

---

### CLI Architecture

**Command Structure:**
```
codetrail/
├── commands/
│   ├── base.py              # Base command with shared logic
│   ├── auth.py              # login, logout
│   ├── profile.py           # show, update
│   ├── recommend.py         # recommendations
│   ├── analyze.py           # issue analysis
│   └── roadmap.py           # roadmap generation
│
├── formatters/
│   ├── table.py             # Rich tables
│   ├── json.py              # JSON output
│   ├── markdown.py          # Markdown formatting
│   └── spinner.py           # Progress indicators
│
└── utils/
    ├── api_client.py        # HTTP client wrapping services
    ├── storage.py           # ~/.codetrail/ config
    └── logger.py            # CLI logging
```

**Design Principles:**
- Each command is < 100 lines
- Delegates to service layer (not direct packages)
- Commands are stateless (config in ~/.codetrail/)
- All async operations show progress

---

## 8. VS Code Extension Architecture

### Features & Components

#### Sidebar Views

**1. Skill Dashboard Panel**
- Display user's skills with confidence scores
- Show recently analyzed repositories
- Link to profile update
- Display GitHub status

**2. Issue Explorer Tree View**
- Tree of repositories
- Issues grouped by difficulty
- Issue recommendations
- Open issue in GitHub

**3. Roadmap Panel**
- Current/active roadmaps
- Progress visualization
- Interactive step checklist
- Link to issue

**4. Details Panel**
- Issue details when selected
- Skill requirements
- Estimated time
- Relevant files list with links

---

### Architecture Design

```
extension.ts
├── commands/
│   ├── auth.ts              # Authenticate with CodeTrail
│   ├── refresh.ts           # Refresh recommendations
│   ├── openRoadmap.ts       # Open roadmap panel
│   └── copyFileLink.ts      # Copy file from roadmap
│
├── views/
│   ├── skillDashboard.ts    # Skill display webview
│   ├── issueExplorer.ts     # Tree view provider
│   ├── roadmapView.ts       # Roadmap webview
│   └── detailsPanel.ts      # Details sidebar
│
├── providers/
│   ├── issueExplorerProvider.ts  # TreeDataProvider impl
│   └── symbolProvider.ts         # Document symbol provider
│
├── webview/
│   ├── skillDashboard/
│   │   ├── component.tsx
│   │   ├── styles.css
│   │   └── data.ts
│   ├── roadmapView/
│   │   ├── component.tsx
│   │   ├── styles.css
│   │   └── interactive.ts
│   └── detailsPanel/
│       ├── component.tsx
│       ├── styles.css
│       └── utils.ts
│
└── utils/
    ├── api.ts               # API client (HTTP to backend)
    ├── storage.ts           # VS Code SecretStorage
    └── logger.ts            # Output channels
```

---

### Activation & Commands

**Activation Event:**
```json
{
  "activationEvents": [
    "onCommand:codetrail.login",
    "onView:codetrail-skills",
    "onView:codetrail-issues"
  ]
}
```

**Commands:**
```
codetrail.login              → Authenticate
codetrail.logout             → Logout
codetrail.refresh            → Refresh data
codetrail.analyze            → Analyze current issue
codetrail.openRoadmap        → Open roadmap view
codetrail.copyFileFromStep   → Copy file path
```

---

### Data Flow

```
Extension (TS)
    ↓
API Client (HTTP)
    ↓
FastAPI Backend
    ↓
Services
    ↓
Packages
    ↓
Database / GitHub / AI
```

**Key Principle:** Never run Python directly. Always call API.

---

### Storage

**User Data:**
- Token: VS Code SecretStorage (encrypted)
- Config: VS Code GlobalState
- Cache: VS Code ExtensionContext storage path

**No** local Python execution.

---

## 9. Scalability Considerations

### Scale: 10 Users → 1,000 Users → 100,000 Users

#### Phase 1: 10 Users

**Database:**
- Single PostgreSQL instance
- No replication needed

**Cache:**
- Single Redis instance
- Simple LRU eviction

**AI:**
- Direct OpenAI API calls
- Basic retry logic

**Jobs:**
- Single Celery worker
- In-memory queue acceptable

**Deployment:**
- Single API server
- Monolithic architecture fine
- Docker Compose locally

---

#### Phase 2: 1,000 Users

**Database:**
- PostgreSQL with read replicas
- Horizontal scaling with connection pooling
- Query optimization needed
  - Index all foreign keys
  - Denormalize for common queries
  - Archive old analyses

**Cache:**
- Redis cluster for high availability
- Cache warming for hot data:
  - Trending issues
  - Common recommendations
  - Popular skills

**AI:**
- Provider abstraction critical now
- Fallback between OpenAI/Gemini
- Batch requests when possible
- Aggressive response caching

**Jobs:**
- Multiple Celery workers
- Task prioritization:
  - Priority 1: Real-time user requests
  - Priority 2: Profile analysis
  - Priority 3: Batch jobs

**Deployment:**
- Load balancer (nginx/HAProxy)
- Multiple API servers
- Managed Celery queue (e.g., RabbitMQ)

---

#### Phase 3: 100,000 Users

**Database:**
- PostgreSQL sharding (hash-based on user_id)
- Each shard handles ~1000 users
- Cross-shard queries minimized
- Archive/cold storage for old data

**Cache:**
- Redis cluster with sentinel
- Multi-tier cache:
  - L1: In-process cache (API servers)
  - L2: Redis cluster
  - L3: Database query cache

**AI:**
- Batch inference pipelines
- Local embedding caches
- Prompt engineering optimization
- Rate limiting across providers

**Jobs:**
- Distributed job queue
- Task routing by priority/SLA
- Dead-letter queues for failures
- Time-based job scheduling

**API:**
- Auto-scaling API servers (Kubernetes)
- Request batching
- GraphQL layer for flexible queries
- API versioning strategy

**Monitoring:**
- Prometheus metrics
- DataDog/New Relic observability
- Error budgets per service
- SLA monitoring

**Data Pipeline:**
- Real-time: Kafka/Event Streaming
- Batch: Apache Airflow
- Analytics: Data warehouse (BigQuery/Snowflake)

**Deployment:**
- Kubernetes cluster
- Multi-region setup for resilience
- Blue-green deployments
- Canary releases

---

### Database Scaling Strategy

#### Sharding Key
```
shard_id = hash(user_id) % num_shards
```

**Shard Placement:**
- Shard 1: Users 0-999
- Shard 2: Users 1000-1999
- ...

**Global Tables** (not sharded):
- `learning_concepts` (small, reference data)
- `repositories` (could be replicated)

**Hot Data:**
- Cache recommendations in Redis
- Cache skill profiles in Redis
- Pre-compute trending issues

---

### Query Optimization

**For 100K users:**

1. **Recommendation Queries**
   - Index: `(user_id, created_at DESC)`
   - Pagination required (limit 10-50)
   - Cache per user for 1 hour

2. **Skill Queries**
   - Index: `(user_id, technology)`
   - Cache skill profiles for 24 hours
   - Batch updates (not per-skill)

3. **Issue Analysis**
   - Index: `(repository_id, difficulty)`
   - Cache analyses for 7 days
   - JSONB columns: use `GIN` indexes

---

### Rate Limiting Strategy

**Per User:**
- 100 requests/minute (API)
- 10 profile analyses/day
- 5 roadmap generations/hour

**Per IP:**
- 1000 requests/minute

**Per Provider:**
- OpenAI: Batching to stay within tier
- Gemini: Distribute across keys

---

### Cost Optimization

**AI Costs:**
- Cache responses (avoid re-analysis)
- Batch requests when possible
- Cheaper models for non-critical tasks
- Local vector embeddings (not API)

**Database Costs:**
- Compress old data
- Archive to S3 after 6 months
- Use serverless for analytics

**Infrastructure:**
- Auto-scale down during off-hours
- Reserved capacity for baseline
- Spot instances for batch jobs

---

## 10. Development Roadmap

### Phase 1: Authentication & Infrastructure (Weeks 1-2)

**Goals:**
- Establish project structure
- GitHub OAuth working
- Database running
- API health check

**Tasks:**
1. Set up monorepo with Poetry
2. Create folder structure
3. Implement GitHub OAuth flow
4. Create User entity + table
5. Create basic API health endpoint
6. Docker Compose setup
7. CI/CD pipeline (GitHub Actions)

**Deliverables:**
- GitHub OAuth login working
- `/health` endpoint
- Docker development environment
- Unit test setup (pytest)

---

### Phase 2: Profile Analysis (Weeks 3-4)

**Goals:**
- Analyze user skills
- Store skill profiles
- Provide profile API

**Tasks:**
1. Implement `GitHubClient` (fetch repos, languages)
2. Implement `SkillEngine` (language/framework detection)
3. Implement `SkillAnalysisService`
4. Create `Skill` entity + table
5. Create `/profile` API endpoints
6. Create async job: `analyze_profile`
7. Implement Redis caching
8. CLI: `codetrail profile`

**Deliverables:**
- User skill profile in database
- `/profile` API endpoint
- `codetrail profile` command
- Skill analysis working async

---

### Phase 3: Issue Analysis (Weeks 5-6)

**Goals:**
- Analyze GitHub issues
- Extract requirements
- Store analysis data

**Tasks:**
1. Implement `IssueEngine` components:
   - Content analyzer
   - Requirement extractor
   - Difficulty scorer
   - File extractor
2. Implement `IssueAnalysisService`
3. Create `Issue` + `IssueAnalysis` entities/tables
4. Create `/issues/analyze` endpoint
5. Async job: `analyze_issue`
6. AI integration for analysis
7. CLI: `codetrail analyze`

**Deliverables:**
- Issue analysis stored
- `/issues/analyze` endpoint
- `codetrail analyze` command
- AI integration working

---

### Phase 4: Recommendation Engine (Weeks 7-8)

**Goals:**
- Match issues to user skills
- Rank recommendations
- Provide recommendation API

**Tasks:**
1. Implement `RecommendationEngine`:
   - Skill matching
   - Similarity scoring
   - Ranking algorithm
2. Implement `RecommendationService`
3. Create `Recommendation` entity + table
4. Create `/recommendations` endpoint
5. Caching strategies
6. CLI: `codetrail recommend`
7. Write unit + integration tests

**Deliverables:**
- Personalized recommendations
- `/recommendations` endpoint
- `codetrail recommend` command
- Tests for matching algorithm

---

### Phase 5: Learning Roadmap (Weeks 9-10)

**Goals:**
- Generate learning paths
- Create interactive roadmaps
- Export roadmaps

**Tasks:**
1. Implement `RoadmapEngine`:
   - Roadmap planner
   - File mapper
   - Concept mapper
   - Formatters (MD, JSON, HTML)
2. Implement `RoadmapService`
3. Create `Roadmap` + `RoadmapStep` entities/tables
4. Create `/roadmaps` endpoints
5. Format exporters
6. CLI: `codetrail roadmap`
7. Comprehensive tests

**Deliverables:**
- Roadmap generation working
- `/roadmaps` endpoint
- `codetrail roadmap` command
- Export in multiple formats
- Full test coverage

---

### Phase 6: Polish & Optimization (Weeks 11-12)

**Goals:**
- Performance optimization
- Error handling
- Documentation
- Release preparation

**Tasks:**
1. Performance profiling
2. Database query optimization
3. Redis cache tuning
4. API response time optimization
5. Comprehensive API documentation
6. Architecture decision records
7. Development guide
8. Deployment documentation
9. Security review
10. Load testing

**Deliverables:**
- Production-ready API
- Complete documentation
- Security hardened
- Performance benchmarks
- Ready for MVP launch

---

### Implementation Order (Detailed)

#### Week 1: Foundation
```
Day 1-2:
  ✓ Initialize monorepo
  ✓ Create all directories
  ✓ Set up pyproject.toml structure
  ✓ Configure Poetry
  ✓ Set up pre-commit hooks

Day 3-4:
  ✓ Implement core-domain package
    - User, Skill entities
    - Base exceptions
    - Interfaces
  ✓ Create database setup
    - Base SQLAlchemy model
    - User table
    - Connection factory

Day 5:
  ✓ Create API app structure
  ✓ Health check endpoint
  ✓ Basic middleware
  ✓ Error handling
  ✓ Docker Compose (PostgreSQL + Redis)
  ✓ GitHub Actions CI setup
```

---

#### Week 2: Authentication
```
Day 1-2:
  ✓ Implement GitHubClient
    - OAuth module
    - Token management
    - Basic REST client

Day 3-4:
  ✓ API authentication routes
    - GET /auth/github
    - POST /auth/github/callback
    - JWT token generation
  ✓ Auth middleware
    - Token validation
    - User extraction from token

Day 5:
  ✓ CLI auth commands
    - login
    - logout
  ✓ Local token storage
  ✓ Tests for auth flow
```

---

#### Week 3: Profile Setup
```
Day 1-2:
  ✓ Implement skill-engine package
    - Language analyzer
    - Framework detector
    - Skill scorer
  ✓ Add Skill entity + table
  ✓ SkillRepository

Day 3-4:
  ✓ ProfileService implementation
    - Use GitHubClient
    - Use SkillEngine
    - Store in database
  ✓ /profile endpoint
  ✓ Async task: analyze_profile

Day 5:
  ✓ CLI: codetrail profile
  ✓ Caching strategy
  ✓ Tests
```

---

#### Week 4: Profile Completion
```
Day 1-2:
  ✓ Redis cache integration
  ✓ Cache warming for hot profiles
  ✓ Celery worker setup

Day 3-4:
  ✓ Performance optimization
    - Query optimization
    - Batch analysis
  ✓ Error handling
  ✓ Logging improvements

Day 5:
  ✓ Integration tests
  ✓ Documentation
  ✓ Release candidate
```

---

#### Weeks 5-12
Continue with same detailed breakdown for each remaining phase.

---

## Architectural Principles & Patterns

### 1. Clean Architecture Layers

```
     API Routes
        ↓
    Middleware
        ↓
    Services (Orchestration)
        ↓
    Domain/Business Logic
        ↓
    Repositories (Data Access)
        ↓
    Infrastructure
```

**Dependency Rule:** Inner layers cannot depend on outer layers.

---

### 2. Dependency Injection

**Factory Pattern for Services:**
```python
# API routes receive dependencies via FastAPI's Depends
@router.get("/profile")
async def get_profile(
    user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
) -> ProfileResponse:
    return profile_service.get_profile(user.id)
```

---

### 3. Repository Pattern

**All data access goes through repositories:**
```python
# Never do direct queries in services
user_repo.get_by_id(user_id)
skill_repo.find_by_user(user_id)
recommendation_repo.save(recommendation)
```

---

### 4. Service Layer as Orchestration

**Services coordinate multiple packages:**
```python
class RecommendationService:
    async def get_recommendations(self, user_id):
        # 1. Get user's skills (ProfileService)
        # 2. Fetch issues (GitHubClient)
        # 3. Analyze each (IssueEngine)
        # 4. Match & rank (RecommendationEngine)
        # 5. Store & cache results
```

---

### 5. Provider Abstraction for AI

**Never hardcode OpenAI/Gemini:**
```python
class AIProvider(ABC):
    async def chat(self, prompt: str) -> str: ...

class OpenAIProvider(AIProvider): ...
class GeminiProvider(AIProvider): ...

# Router decides which provider based on config
orchestrator.chat(prompt, provider="gemini")
```

---

### 6. Caching Strategy

**Multi-level:**
1. Database query results → Redis (1 hour)
2. API responses → Redis (30 min)
3. AI responses → Redis (24 hours)
4. Skill profiles → Redis (24 hours)

**Cache Invalidation:**
- Profile updated → invalidate profile cache + recommendations
- Issue analyzed → invalidate issue cache
- Manual: `redis.delete(key)`

---

### 7. Async Processing

**For Long-Running Tasks:**
- Profile analysis → Celery task
- Issue analysis → Celery task
- Roadmap generation → Celery task

**Polling Pattern:**
1. POST `/profile/analyze` → returns task_id
2. GET `/profile/analysis-status/{task_id}` → returns progress
3. Client polls until complete

---

### 8. Error Handling

**Domain Exceptions:**
```python
class CodeTrailException(Exception): ...
class ProfileNotFound(CodeTrailException): ...
class GitHubError(CodeTrailException): ...
```

**API Maps Exceptions:**
```python
@app.exception_handler(ProfileNotFound)
async def handle_not_found(request, exc):
    return JSONResponse({
        "error": {
            "code": "NOT_FOUND",
            "message": str(exc)
        }
    }, status_code=404)
```

---

### 9. Logging Strategy

**Structured Logging:**
```python
logger.info("recommendation_generated", extra={
    "user_id": user_id,
    "issue_id": issue_id,
    "score": matching_score,
    "duration_ms": elapsed_ms
})
```

**Log Levels:**
- ERROR: System failures
- WARNING: Degraded functionality
- INFO: Business events
- DEBUG: Detailed execution

---

### 10. Testing Strategy

**Pyramid:**
```
        /\
       /  \  E2E Tests (5%)
      /────\
     /      \
    /────────\ Integration Tests (25%)
   /          \
  /────────────\ Unit Tests (70%)
```

**Test Organization:**
- Unit tests: In each package under `tests/`
- Integration: `tests/integration/`
- E2E: `tests/e2e/`
- Fixtures: `tests/fixtures/`

---

## Conclusion

This architecture is designed to:

✅ **Scale horizontally** - Stateless services, sharded database  
✅ **Be maintainable** - Clear boundaries, DI, clean layers  
✅ **Support growth** - Future extensions, provider flexibility  
✅ **Enable testing** - Mockable dependencies, isolated units  
✅ **Remain agile** - Monorepo for development, microservice-ready  

**Next Steps:**
1. Validate architecture with stakeholders
2. Begin Phase 1 implementation
3. Adjust as learnings emerge
4. Document decisions in ADRs
