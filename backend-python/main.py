import os
import ipaddress
from pathlib import Path
from dotenv import load_dotenv

# 1. LOAD ENV BEFORE ANYTHING THAT READS IT
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)

# 2. NOW import routers
from routers import auth, grading, progress, billing, account_lifecycle, webhooks, community, grader, admin, organisations, organisation_members, courses, course_access, course_content, internal_auth, internal_staff, internal_teams, commercial, creator, lifecycle, learning_structure, media, access, organisation_teams, ai, creator_finance, evidence, internal_operations, internal_content, ai_profiles, public_directory, internal_tracks, internal_assessments, learner_onboarding, learning_plans, cohort_learners, cohort_learning, notifications as notifications_router, credentials, internal_projects
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Supabase is managed externally via SQL, no local init_db needed
    print("Backend startup: Connected to Supabase PostgreSQL")
    yield

app = FastAPI(
    title="Learnora - Python Backend",
    version="2.0.0-secure",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("APP_ENV", "production").strip().lower() != "production" else None,
    redoc_url="/redoc" if os.getenv("APP_ENV", "production").strip().lower() != "production" else None,
    openapi_url="/openapi.json" if os.getenv("APP_ENV", "production").strip().lower() != "production" else None,
)

def _trusted_rate_limit_ip(request: Request) -> str:
    """Use Vercel's normalised client IP only on Vercel; otherwise use the peer address."""
    if os.getenv("VERCEL", "").strip() == "1":
        candidate = (request.headers.get("x-real-ip") or "").strip()
        if candidate:
            try:
                return str(ipaddress.ip_address(candidate))
            except ValueError:
                pass
    if request.client and request.client.host:
        try:
            return str(ipaddress.ip_address(request.client.host))
        except ValueError:
            pass
    return "unknown"

# Shared PostgreSQL rate limiting is used in production so counters survive
# serverless instance churn. Local development remains deterministic.
API_RATE_LIMIT_REQUESTS = max(1, int(os.getenv("API_RATE_LIMIT_REQUESTS", "60")))
API_RATE_LIMIT_WINDOW_SECONDS = max(1, int(os.getenv("API_RATE_LIMIT_WINDOW_SECONDS", "60")))
_RATE_LIMIT_EXEMPT_PATHS = {"/", "/api/health"}


# CORS Middleware (Correctly placed to handle preflight OPTIONS requests)
origins = [
    "https://thepheonixanalytics.com",
    "https://www.thepheonixanalytics.com",
    "https://teamslearnora.vercel.app",
    "https://learnora-me-v02.vercel.app",
    "https://learnorame.vercel.app",
]

if os.getenv("APP_ENV", "production").strip().lower() != "production":
    origins.extend(["http://localhost:3000", "http://localhost:3001"])

internal_frontend = os.getenv("INTERNAL_FRONTEND_URL", "").rstrip("/")
if internal_frontend and internal_frontend not in origins:
    origins.append(internal_frontend)

frontend = os.getenv("FRONTEND_URL", "").rstrip("/")
if frontend and frontend not in origins:
    origins.append(frontend)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # Preview origins must be explicitly allow-listed; do not trust every deployment
    # that happens to match a Vercel team naming convention.
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
    "Content-Type",
    "Authorization",
    "X-Requested-With",
    "X-Organisation-ID",
    ],
)

def _rate_limit_cors_headers(request: Request, retry_after: str) -> dict[str, str]:
    headers = {"Retry-After": retry_after, "Vary": "Origin"}
    origin = request.headers.get("origin", "")
    if origin in origins:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return headers


@app.middleware("http")
async def distributed_api_rate_limit(request: Request, call_next):
    if (
        os.getenv("APP_ENV", "production").strip().lower() != "production"
        or request.method == "OPTIONS"
        or request.url.path in _RATE_LIMIT_EXEMPT_PATHS
    ):
        return await call_next(request)

    client_ip = _trusted_rate_limit_ip(request)
    bucket_key = auth._rate_limit_digest(f"api:{client_ip}")
    try:
        # The shared Supabase client is synchronous. Keep its network wait off
        # the ASGI event loop so one slow rate-limit RPC cannot stall unrelated
        # requests handled by the same function instance.
        result = await run_in_threadpool(lambda: auth.supabase.rpc("consume_api_rate_limit", {
            "p_bucket_key": bucket_key,
            "p_max_requests": API_RATE_LIMIT_REQUESTS,
            "p_window_seconds": API_RATE_LIMIT_WINDOW_SECONDS,
        }).execute())
        limited = getattr(result, "data", None)
        if not isinstance(limited, bool):
            if isinstance(limited, list) and limited and isinstance(limited[0], dict):
                limited = limited[0].get("consume_api_rate_limit", limited[0].get("limited"))
            elif isinstance(limited, dict):
                limited = limited.get("consume_api_rate_limit", limited.get("limited"))
        if not isinstance(limited, bool):
            raise RuntimeError("Unexpected response from shared API rate limiter")
    except Exception as exc:
        print(f"Shared API rate-limit check failed: {type(exc).__name__}")
        return JSONResponse(
            status_code=503,
            content={"error": "Request protection is temporarily unavailable. Please retry shortly."},
            headers=_rate_limit_cors_headers(request, "5"),
        )

    if limited:
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded. Please retry after the rate-limit window."},
            headers=_rate_limit_cors_headers(request, str(API_RATE_LIMIT_WINDOW_SECONDS)),
        )
    return await call_next(request)



@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    # API responses can contain account, learning, and payment information.
    # Never allow browsers or intermediary caches to retain them.
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    # The production API does not serve interactive docs; constrain any
    # accidental HTML/error response without breaking local Swagger tooling.
    if os.getenv("APP_ENV", "production").strip().lower() == "production":
        response.headers["Content-Security-Policy"] = "default-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(account_lifecycle.router)
app.include_router(grading.router, prefix="/api/grading", tags=["grading"])
# The progress router already declares its /api/progress prefix.
# Do not add it a second time here.
app.include_router(progress.router)
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(community.router, prefix="/api/community", tags=["community"])
app.include_router(grader.router, prefix="/api/grader", tags=["grader"])


# Learnora V1 organisation architecture
app.include_router(organisations.router)
app.include_router(cohort_learners.router)
app.include_router(cohort_learning.router)
app.include_router(organisation_members.router)
app.include_router(courses.router)
app.include_router(course_access.router)
app.include_router(course_content.router)

# Internal Learnora staff platform. Security is enforced by backend authentication + staff membership + granular permissions.
app.include_router(internal_auth.router)
app.include_router(internal_staff.router)
app.include_router(internal_teams.router)
app.include_router(internal_operations.router)
app.include_router(internal_content.router)
app.include_router(internal_tracks.router)
app.include_router(internal_assessments.router)
app.include_router(commercial.router)
app.include_router(creator.router)
app.include_router(lifecycle.router)
app.include_router(learning_structure.router)
app.include_router(media.router)
app.include_router(access.router)
app.include_router(organisation_teams.router)
app.include_router(ai.router)
app.include_router(ai_profiles.router)
app.include_router(creator_finance.router)
app.include_router(evidence.router)
app.include_router(credentials.router)
app.include_router(internal_projects.router)
app.include_router(public_directory.router)
app.include_router(learner_onboarding.router)
app.include_router(learning_plans.router)
app.include_router(notifications_router.router)
@app.get("/")
def health():
    return {"status": "ok", "service": "learnora-backend", "version": "2.0.0-secure"}

@app.get("/api/health")
def api_health():
    # Liveness only: confirms that the FastAPI process is serving requests.
    return {"status": "ok", "service": "learnora-backend", "version": "2.0.0"}


@app.get("/api/ready")
def api_ready():
    """Readiness probe for deployment checks; never returns credentials or raw DB errors."""
    configured = bool(
        getattr(auth, "SUPABASE_URL", "")
        and getattr(auth, "SUPABASE_KEY", "")
        and getattr(auth, "JWT_SECRET", "")
    )
    if not configured:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready"},
        )

    try:
        # auth.py owns the shared service-role client and uses public.users
        # as the canonical learner account table.
        auth.supabase.table("users").select("id").limit(1).execute()
    except Exception as exc:
        # Keep the response safe; detailed provider errors can contain internals.
        print(f"Readiness database probe failed: {type(exc).__name__}")
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready"},
        )

    return {"status": "ready"}
