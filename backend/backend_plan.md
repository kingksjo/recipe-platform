### Backend Development Plan for Recipe Sharing Platform

This document outlines a **complete, step-by-step plan** for building the backend of your Recipe Sharing Platform using the FARM stack (FastAPI, React/Next.js, MongoDB). It is based exactly on the 6 components we've agreed upon, ensuring we deliver a simple, fast, reliable MVP that aligns with your product vision: a public platform for home cooks to store, share, and discover recipes with features like creation, viewing/editing, browsing, basic search, and filtering.

The plan is broken down into **phases**, with each phase including:
- **Objectives**: What we achieve.
- **Steps**: Numbered actions (brief, but detailed enough to guide implementation without overwhelming).
- **Best Practices**: Key industry standards we'll follow.
- **Testing Milestones**: How to verify it's working.
- **Dependencies**: Files/tools from previous phases.

We'll implement one phase at a time in our tutoring sessions, with you confirming completion before moving on. No auth is included (as agreed), but the design allows seamless addition later.

#### Key Assumptions & Guidelines
- **Tech Stack**: FastAPI (API), Motor (async MongoDB driver), Pydantic (validation/schemas), Uvicorn (server), Docker Compose (dev/prod environment).
- **MVP Scope**: Public CRUD + search/filtering. No user auth, images are URL-only (uploads in future).
- **Best Practices Throughout**:
  - Dependency injection for DB.
  - Async code for scalability.
  - Pydantic for type-safety and auto-docs.
  - Error handling: User-friendly JSON responses (e.g., 404 with {"detail": "Recipe not found"}).
  - Logging: Basic startup/shutdown prints; expand to structlog later.
  - Security: No auth yet, but CORS for frontend + env vars for secrets.
  - Performance: Indexes for search; pagination to avoid loading everything.
- **Deployment Goal**: Runnable locally via Docker; ready for Railway/Render/Heroku with one command.
- **Total Estimated Time**: 2-4 hours (spread over sessions), assuming your Python/Docker comfort.
- **Version Control**: Use Git commits per phase.

---

#### Phase 1: Setup & Configuration (Component 1 & 2 Prep)
**Objectives**: Establish project structure, config, and DB connection. Lock in the core recipe document schema.
**Steps**:
1. Ensure project root has `backend/` with `app/` subdir (as we set up earlier).
2. Implement `app/core/config.py`: Pydantic Settings class loading `.env.local` (MONGODB_URL, ENV, DEBUG, DATABASE_NAME="recipe_db").
3. Implement `app/core/database.py`: Async Motor client + `get_db` dependency + `close_db` function.
4. Update `app/main.py`: Add lifespan hook for startup/shutdown.
5. Update `docker-compose.yml` and `Dockerfile` if needed for hot-reload.
**Best Practices**: Env vars for all secrets; singleton client for efficiency.
**Testing Milestones**: Run `docker compose up -d`; hit `/` endpoint → see {"env": "development", "db_collections": []}; check logs for "Backend starting...".
**Dependencies**: Existing `.env.local`, `requirements.txt`.

---

#### Phase 2: Schemas & Data Model (Components 1 & 2)
**Objectives**: Define the exact recipe document and validation logic.
**Steps**:
1. Create `app/schemas/recipe.py`: Implement `Ingredient`, `RecipeCreate`, `RecipeInDB` with agreed fields + PyObjectId helper.
2. Add examples and Field constraints (e.g., min_items=1 for ingredients/steps).
**Best Practices**: Separate input/output schemas; forbid extra fields; use aliases for _id → id.
**Testing Milestones**: Restart containers; open /docs → see schema examples in the UI (no endpoints yet).
**Dependencies**: Phase 1 complete.

---

#### Phase 3: CRUD Logic Layer (Component 3)
**Objectives**: Build the isolated data-access layer with all agreed methods.
**Steps**:
1. Create `app/models/recipe.py`: Implement `RecipeCRUD` class with create, get_by_id, get_all (paginated, sorted by created_at desc), update (full replace + bump updated_at), delete.
2. Add basic error handling (e.g., return None on invalid ID).
**Best Practices**: All MongoDB ops async; use model_dump() for clean dicts; no business logic here (keep in routers).
**Testing Milestones**: Manually test in Python shell (import and call methods) → insert a recipe, fetch it, update, delete.
**Dependencies**: Phases 1-2.

---

#### Phase 4: API Endpoints (Component 4)
**Objectives**: Expose the full API with validation and errors.
**Steps**:
1. Create `app/routers/recipes.py`: Implement APIRouter with the 5 CRUD endpoints (POST, GET list, GET id, PUT, DELETE).
2. Use Depends(get_db) in every endpoint; raise HTTPException on not found.
3. Update `app/main.py`: Include the router.
**Best Practices**: Response models for type-hinting; status codes per spec; query params for pagination.
**Testing Milestones**: Use /docs to create a recipe → list shows it → get by ID works → update changes it → delete removes it → 404 on bad ID.
**Dependencies**: Phases 1-3.

---

#### Phase 5: Search & Indexing (Components 5 & 6)
**Objectives**: Add text search + filtering; auto-create index on startup.
**Steps**:
1. In `app/models/recipe.py`: Add `search` method using $text + score sorting.
2. In `app/routers/recipes.py`: Add GET /search endpoint with q param.
3. In `app/core/database.py`: Add `create_indexes` function with the agreed text index.
4. Update `app/main.py` lifespan: Call create_indexes on startup (use async for db in get_db() to grab db once).
**Best Practices**: Idempotent index creation (MongoDB skips if exists); combine with created_at sort for relevance + freshness.
**Testing Milestones**: Create 3 recipes (one with "chicken" in title, one in ingredients); search "chicken" → returns both, sorted by score; empty query → 400 error.
**Dependencies**: Phases 1-4.

---

#### Phase 6: Filtering Enhancement (Should-Have Feature)
**Objectives**: Add time-based filtering (e.g., under 30 minutes).
**Steps**:
1. In `app/routers/recipes.py`: Update GET /recipes and /search with optional query param `max_total_time: int = Query(None, ge=1)`.
2. In `app/models/recipe.py`: Update get_all and search to filter where (prep_time_minutes + cook_time_minutes) <= max_total_time if provided (handle None times as 0).
**Best Practices**: Use MongoDB $expr for calculated filter; keep optional to not break existing calls.
**Testing Milestones**: Create recipes with times; filter max_total_time=30 → only quick ones return.
**Dependencies**: Phase 5.

---

#### Phase 7: Error Handling & Polish
**Objectives**: Make the backend robust and user-friendly.
**Steps**:
1. Add global exception handlers in `main.py` for validation errors → return structured {"detail": msg}.
2. Add CORS middleware for frontend (allow localhost:3000).
3. Update all endpoints: Catch Motor exceptions → 500 with {"detail": "Database error — try again"}.
**Best Practices**: Never expose stack traces; use FastAPI's HTTPException for consistency.
**Testing Milestones**: Invalid input → clear error; DB down → graceful 500; frontend can call without CORS issues.
**Dependencies**: All previous.

---

#### Phase 8: Deployment Readiness
**Objectives**: Make it deployable anywhere.
**Steps**:
1. Add `backend/.env.prod` template (same as .local but ENV=production, DEBUG=False).
2. Update Dockerfile: Multi-stage build for prod (no dev deps).
3. Update docker-compose.yml: Add prod service override (no --reload, volumes read-only).
4. Add a simple health check endpoint GET /health → {"status": "ok"}.
**Best Practices**: Separate dev/prod envs; use MongoDB Atlas for cloud (free tier) if desired.
**Testing Milestones**: Run in prod mode locally → no reload, no debug info; deploy to free Railway tier → API live online.
**Dependencies**: All previous.

---

#### Phase 9: Final Review & Handoff to Frontend
**Objectives**: Ensure backend is MVP-complete.
**Steps**:
1. Run full end-to-end tests: Create 10 recipes, search, filter, edit, delete.
2. Document API in README.md (endpoints, examples, curl commands).
3. Commit to Git with "Backend MVP complete".
**Best Practices**: 100% coverage of your features; auto-generated docs via /docs.
**Testing Milestones**: All user stories work; performance under 100ms per request.
**Dependencies**: All previous.

This plan is **self-contained and executable**. It builds directly on our agreed components, with no surprises.

When you're ready to start implementing (starting with Phase 1), just say **“Start Phase 1”**. Or tweak any part of this plan first.