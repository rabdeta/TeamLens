# TeamLens

> Work in progress

A privacy-focused full-stack employee intelligence platform that generates workplace insights from metadata without reading message content.

## Current features

- Searchable employee profiles and detail views
- Response-time, attendance, task, and collaboration metrics
- Measurement-period and data-coverage context
- PostgreSQL persistence and database migrations
- Data-source connection status dashboard
- Linear OAuth integration
- Encrypted OAuth token storage and automatic token refresh
- Privacy-safe Linear member and completed-task synchronization
- Automated backend tests

## Privacy approach

TeamLens requests only the metadata needed to generate workplace metrics.

The Linear integration currently retrieves:

- Workspace member ID
- Display name
- Active status
- Assignee ID
- Issue completion timestamp

It does not request issue titles, descriptions, comments, or message content.

## Technology stack

- React
- TypeScript
- Vite
- Python
- Flask
- PostgreSQL
- SQLAlchemy
- Flask-Migrate
- pytest

## Architecture

```text
React frontend
      ↓
Flask REST API
      ↓
PostgreSQL

Flask API ← OAuth/GraphQL → Linear
```

OAuth tokens are encrypted before being stored in PostgreSQL.

## Local setup

### Requirements

- Node.js and npm
- Python
- PostgreSQL
- A Linear OAuth application

### Backend

Create and activate the virtual environment, then install dependencies:

```powershell
py -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

Copy `.env.example` to `.env` and provide your local database and Linear OAuth values.

Apply migrations and seed development data:

```powershell
python -m flask --app backend.app db upgrade
python -m flask --app backend.app seed-db
```

Start Flask:

```powershell
python -m flask --app backend.app run --debug
```

### Frontend

Install dependencies:

```powershell
npm install --prefix frontend
```

Start Vite:

```powershell
npm run dev --prefix frontend
```

Open the local address displayed by Vite.

## Linear OAuth setup

Configure this development redirect URI in the Linear OAuth application:

```text
http://127.0.0.1:5000/api/integrations/linear/callback
```

The application uses read-only Linear access.

Never commit `.env`, OAuth credentials, encryption keys, or access tokens.

## Verification

```powershell
npm run lint --prefix frontend
npm run build --prefix frontend
python -m pytest backend
```

## Planned work

- Persist synchronized Linear metrics to employee profiles
- Google Workspace integration
- Microsoft Graph integration
- Jira integration
- Authentication and organization-level access control
- AI-generated summaries based only on approved aggregated metadata
- Deployment and production configuration