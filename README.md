# Employee Intelligence Platform

> Work in progress

A privacy-focused full-stack application that generates employee insight profiles from workplace metadata without reading message content.

## Current features

- Searchable employee profiles
- Response-time, attendance, task, and collaboration metrics
- Measurement periods and data-coverage context
- Employee detail views
- Data-source connection statuses
- Flask REST API
- PostgreSQL database with migrations
- Automated backend tests

## Planned integrations

- Google Workspace
- Microsoft Graph
- Jira
- Linear

## Technology stack

- React
- TypeScript
- Vite
- Python
- Flask
- PostgreSQL
- SQLAlchemy
- pytest

## Architecture

The React frontend requests employee and integration data from the Flask API. Flask queries PostgreSQL and returns JSON responses to the frontend.

```text
React frontend → Flask API → PostgreSQL