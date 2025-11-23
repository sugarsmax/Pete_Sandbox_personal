# Git ADSK Repositories

**Built by**: AI Assistant  
**Date**: October 22, 2025  
**Agent Model**: claude-4.5-haiku-thinking

---

## Repository Index

This document provides a comprehensive listing of all repositories in `/Users/maxfiep/git_adsk/`.

---

## Analytics & BI Repositories

### [ADPBI_Fusion](https://git.autodesk.com/Business-Intelligence-Solutions/ADPBI_Fusion)
- **Type**: Looker project
- **Purpose**: Fusion product analytics dashboard
- **Components**: Views, Models, Dashboards, Explores
- **Key Subdirectories**: 
  - `Dashboards/` - Looker dashboards
  - `Models/` - Looker models
  - `Snowflake/` - Snowflake-specific views
  - `Presto/` - Presto-specific views

### [ADPBI_Fusion_Gd_Sim](https://git.autodesk.com/Business-Intelligence-Solutions/ADPBI_Fusion_Gd_Sim)
- **Type**: Looker project
- **Purpose**: Fusion geometry/simulation analytics
- **Components**: Views, Models, LookML manifests
- **Status**: Appears to be a specialty analytics instance

### [ADPBI_Fusion_Product_Analytics](https://git.autodesk.com/Business-Intelligence-Solutions/ADPBI_Fusion_Product_Analytics)
- **Type**: Looker project
- **Purpose**: Product analytics for Fusion platform
- **Components**: Views, Models, Dashboards
- **Key Subdirectories**:
  - `views/` - Data views
  - `models/` - Looker models
  - `Presto/` - Presto queries

### [ADPBI_Fusion_Team](https://git.autodesk.com/Business-Intelligence-Solutions/ADPBI_Fusion_Team)
- **Type**: Looker project
- **Purpose**: Team-level Fusion analytics
- **Components**: Dashboards, Models, Views
- **Key Files**: `README.md`

### [PDMS_Product_Analytics](https://git.autodesk.com/maxfiep/PDMS_Product_Analytics)
- **Type**: Product analytics repository
- **Purpose**: PDMS-specific product analytics

---

## MCP (Model Context Protocol) Repositories

### [adsk_help_mcp](https://git.autodesk.com/gangula/adsk_help_mcp)
- **Type**: MCP Server
- **Purpose**: Autodesk Help system MCP integration
- **Components**: 
  - Flask/Python app (`app/`)
  - AWS infrastructure (`aws/`)
  - Docker deployment
- **Key Files**: 
  - `README.md`
  - `CLAUDE_DESKTOP_MCP_SETUP.md`
  - `CURSOR_MCP_SETUP.md`
  - `requirements.txt`

### [help-mcp](https://git.autodesk.com/dpe/help-mcp)
- **Type**: MCP Server
- **Purpose**: Help system MCP with enhanced features
- **Components**:
  - Flask/Python app (`app/`)
  - Documentation (`docs/`)
  - Docker support
- **Build Tools**: `uv` (Python package manager)
- **Key Files**: 
  - `README.md`
  - `CURSOR_MCP_SETUP.md`
  - `requirements.txt`
  - `uv.lock`

### [mcp_fusion_360_api](https://git.autodesk.com/adamb1/mcp_fusion_360_api)
- **Type**: MCP Server
- **Purpose**: Fusion API documentation server as MCP
- **Components**:
  - Python Flask servers (web + docs)
  - MCP integration
  - Railway/Render deployment configs
- **Key Files**: 
  - `README.md`
  - `DEPLOYMENT.md`
  - `PROJECT_SUMMARY.md`
  - `requirements.txt`

### [mcp-atlassian](https://github.com/sooperset/mcp-atlassian)
- **Type**: MCP Server
- **Purpose**: Atlassian (Jira/Confluence) MCP integration
- **Components**:
  - Source code (`src/`)
  - Tests (`tests/`)
  - Docker support
- **Build Tools**: `uv` + `pyproject.toml`
- **Key Files**: 
  - `README.md`
  - `CONTRIBUTING.md`
  - `SECURITY.md`
  - `AGENTS.md`

### [mcp-commons](https://git.autodesk.com/openatadsk/mcp-commons)
- **Type**: Shared MCP utilities
- **Purpose**: Common libraries and utilities for MCP servers
- **Components**:
  - Shared libraries (`shared-libraries/`)
  - Documentation (`docs/`)
  - Examples (`examples/`)
  - Test harnesses
- **Documentation**: `mkdocs.yml`
- **Key Files**: 
  - `README.md`
  - `CONTRIBUTING.md`
  - `PUBLISHING.md`

### [mcp-proxy](https://github.com/TBXark/mcp-proxy)
- **Type**: MCP Proxy Server (Go)
- **Purpose**: HTTP proxy for MCP communications
- **Language**: Go
- **Components**:
  - Core proxy logic
  - HTTP handler
  - File proxy
  - Docker deployment
- **Key Files**: 
  - `README.md`
  - `Dockerfile`
  - `Makefile`

### [mcp-servers](https://git.autodesk.com/fusion/mcp-servers)
- **Type**: MCP servers collection
- **Purpose**: Multiple MCP server implementations
- **Subdirectories**: `design/`

### [mcp-trino-viz](https://git.autodesk.com/chewd1/mcp-trino-viz)
- **Type**: MCP Server
- **Purpose**: Trino/Presto visualization MCP

### [nucleus-mcp](https://git.autodesk.com/LocalizationServices/nucleus-mcp)
- **Type**: MCP Server
- **Purpose**: Nucleus integration MCP

### [playwright-mcp](https://github.com/microsoft/playwright-mcp)
- **Type**: MCP Server
- **Purpose**: Playwright automation MCP

### [snowflake-mcp-server](https://git.autodesk.com/fraza/snowflake-mcp-server)
- **Type**: MCP Server
- **Purpose**: Snowflake integration MCP

---

## Fusion & Product Development Repositories

### [adp-astro-fusion](https://git.autodesk.com/ADP/adp-astro-fusion)
- **Type**: Airflow DAG repository
- **Purpose**: Data pipeline orchestration for Fusion
- **Components**:
  - Airflow DAGs (`dags/`)
  - Docker support
  - Jenkins CI/CD (`Jenkinsfile*`)
  - Python plugins and scripts
- **Key Files**: 
  - `README.md`
  - `requirements.txt`
  - `Dockerfile`
  - `Makefile`

### [Fusion_MCP](https://git.autodesk.com/maxfiep/Fusion_MCP)
- **Type**: Fusion plugin + MCP
- **Purpose**: MCP integration for Fusion 360
- **Components**: `fusion360_cylinder_app/`

### [fusion-mcp-server](https://git.autodesk.com/stankod/fusion-mcp-server)
- **Type**: Fusion MCP Server
- **Purpose**: Server for Fusion 360 MCP integration
- **Components**:
  - Fusion MCP Addin
  - Server implementation

### [fusion-plugin-feature-flag-explorer](https://git.autodesk.com/legooa/fusion-plugin-feature-flag-explorer)
- **Type**: Fusion 360 plugin
- **Purpose**: Feature flag exploration tool
- **Components**:
  - Commands (`commands/`)
  - Libraries (`lib/`)
- **Key Files**: 
  - `Feature Flag Explorer.manifest`
  - `Feature Flag Explorer.py`
  - `config.py`

### [Fusion360DevTools](https://github.com/AutodeskFusion360/Fusion360DevTools)
- **Type**: Fusion 360 plugin
- **Purpose**: Development tools for Fusion
- **Components**:
  - Commands (`commands/`)
  - Resources (`resources/`)
  - Libraries (`lib/`)
- **Key Files**: 
  - `README.md`
  - `LICENSE`
  - `Fusion360DevTools.manifest`

### [Marlin-FusionAdoptabot](https://github.com/sugarsmax/Marlin-FusionAdoptabot)
- **Type**: Hardware firmware + Fusion integration
- **Purpose**: Fusion-based robotics project
- **Components**:
  - Marlin firmware (`Marlin/`)
  - Build configuration (`buildroot/`)
  - PlatformIO configuration
- **Key Files**: 
  - `README.md`
  - `LICENSE`

---

## Utility & Support Repositories

### [cerv2-easy-oauth](https://git.autodesk.com/chens/cerv2-easy-oauth)
- **Type**: OAuth utility (Go)
- **Purpose**: Simplified OAuth for CERv2
- **Language**: Go
- **Key Files**: 
  - `README.md`
  - `run.sh`
  - `run_for_dev.sh`

### [cursor-notes](https://git.autodesk.com/patela2/cursor-notes)
- **Type**: Documentation
- **Purpose**: Cursor IDE productivity notes
- **Key Files**: 
  - `cursor-productivity-guide.md`
  - `README.md`

### [pd-ai-rules](https://git.autodesk.com/forge/pd-ai-rules)
- **Type**: Configuration
- **Purpose**: AI rules for product development
- **Components**: `config/`, `cursor/`
- **CI/CD**: `Jenkinsfile`

---

## Personal/Sandbox Repositories

### [Maxfield_Sandbox](https://git.autodesk.com/maxfiep/Maxfield_Sandbox)
- **Type**: Personal sandbox
- **Purpose**: Development experimentation
- **Components**:
  - Python scripts (`Python/`)
  - Jupyter notebooks (`notebooks/`)
  - Documentation (`docs/`)
  - Wiki (`Wiki/`)
  - Zoom chat analysis (`zoom_chat_analysis/`)
- **Key Files**: 
  - `README.md`

### [Repo_w_Pete](https://git.autodesk.com/tavallm/Repo_w_Pete)
- **Type**: Collaborative repository
- **Purpose**: Joint development project

### [empty](https://git.autodesk.com/maxfiep/empty)
- **Type**: Archive/template
- **Purpose**: Contains `Autodesk_Assistant_Evaluation.md`

### ____ git personal
- **Type**: Personal notes/configuration

---

## Current Working Repository

### [OSplan_Distribution_Package](https://git.autodesk.com/maxfiep/OSplan_Distribution_Package)
- **Type**: Data distribution and analysis package
- **Purpose**: OSplan data packaging and distribution
- **Components**:
  - Data (`data/`)
  - Insights (`insights/`)
  - Reports (`reports/`)
  - System configuration (`system/`)
  - Workflows (`workflows/`)
- **Key Files**: 
  - `README.md`
  - `requirements.txt`
  - `SETUP_INSTRUCTIONS.md`
  - `PACKAGE_MANIFEST.md`

---

## Summary Statistics

- **Total Repositories**: ~35
- **MCP Servers**: 8+
- **Looker Projects**: 4
- **Fusion Plugins**: 2
- **Utility Projects**: 3
- **Personal/Sandbox**: 3

---

*Last Generated: October 22, 2025*  
*Built by: AI Assistant (claude-4.5-haiku-thinking)*
