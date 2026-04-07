# ZYRA — Arquitetura Validada & Pronta

## 1️⃣ Arquitetura em 4 Camadas

```
┌─────────────────────────────────────────────────────────────┐
│                   LAYER 1: PRESENTATION                     │
│         (React Native + Expo Router + Zustand)              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ (auth) auth flow    (app) main app                  │   │
│  │  │                    │                              │   │
│  │  ├─ login.tsx         ├─ index.tsx (feed)           │   │
│  │  ├─ register.tsx      ├─ profile.tsx                │   │
│  │  └─ forgot-pwd.tsx    └─ create-post.tsx            │   │
│  │                       ├─ health/ (tracker, history) │   │
│  │                       ├─ social/ (friends, compare) │   │
│  │                       └─ ai/ (meal scan, coach)     │   │
│  └──────────────────────────────────────────────────────┘   │
│                            ▼                                 │
│  Zustand Store + React Query + NativeWind (Tailwind)       │
└────────────────┬──────────────────────────────────────────┘
                 │ HTTP + WebSocket (Realtime)
┌────────────────▼──────────────────────────────────────────┐
│              LAYER 2: API GATEWAY (FastAPI)                │
│  /api/v1/auth    /api/v1/social    /api/v1/health        │
│  /api/v1/ai                                               │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ Middleware Stack:                                   │  │
│  │ 1. CORS (allow mobile origins)                      │  │
│  │ 2. Auth (JWT + Supabase validation)                 │  │
│  │ 3. Rate Limit (Redis sliding window)                │  │
│  │ 4. Logging (request_id + timing)                    │  │
│  └─────────────────────────────────────────────────────┘  │
└────────────────┬──────────────────────────────────────────┘
                 │
┌────────────────▼──────────────────────────────────────────┐
│       LAYER 3: SERVICE LAYER (Business Logic)              │
│                                                            │
│  AuthService       SocialService      HealthService      │
│  • Login/Register  • Posts            • IMC/TMB           │
│  • Token mgmt      • Friendships      • Streaks           │
│  • Permissions    • Feed              • Workouts         │
│                    • Metrics compare   • Checkins         │
│                                                            │
│  AIService               MediaService                      │
│  • Meal analysis         • R2 upload/delete                │
│  • Diet generation       • Image optimization              │
│  • Workout generation    • URL generation                  │
│  • Coach chat            • Cleanup tasks                   │
└────────────────┬──────────────────────────────────────────┘
                 │
┌────────────────▼──────────────────────────────────────────┐
│           LAYER 4: DATA + EXTERNAL SERVICES                │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Supabase PostgreSQL (RLS enabled)                    │ │
│  │ • profiles, posts, friendships                       │ │
│  │ • workouts, workout_sets, health_metrics            │ │
│  │ • checkins, diet_plans                              │ │
│  │ • Realtime subscriptions (feed updates)             │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌───────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │ Upstash Redis │  │  Cloudflare R2   │  │ Gemini API │ │
│  │ (Cache)       │  │  (Images)        │  │ (AI)       │ │
│  │ • Feed cache  │  │  • Avatars       │  │ • Vision   │ │
│  │ • Sessions    │  │  • Post images   │  │ • Text     │ │
│  │ • Rate limit  │  │  • Meals photos  │  │ • Patterns │ │
│  └───────────────┘  └──────────────────┘  └────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## 2️⃣ Data Flow — Exemplo: Postar Conquista

```
Mobile App                          Backend                     Database
┌─────────┐
│ User    │
│ fills   │
│ post    │
└────┬────┘
     │ POST /api/v1/social/posts
     │ { image, caption, visibility }
     ▼
  ┌────────────────────────────────────────┐
  │ Middleware Stack                       │
  │ - Auth: validate JWT                   │
  │ - Rate Limit: check 60 req/min         │
  │ - Logging: generate request_id         │
  └────────────────────────────────────────┘
     │
     ▼
  ┌────────────────────────────────────────┐
  │ Router: create_post()                  │
  │ - Parse body (Pydantic validation)     │
  └────────────────────────────────────────┘
     │
     ▼
  ┌────────────────────────────────────────┐
  │ Service Layer                          │
  │ social_service.create_post()           │
  │  ├─ 1. Validate visibility             │
  │  ├─ 2. Upload image to R2 (if present) │
  │  ├─ 3. Insert post to Supabase         │
  │  ├─ 4. Invalidate feed cache in Redis  │
  │  └─ 5. Trigger Realtime event          │
  └────────────────────────────────────────┘
     │
     ├─ Upload Image ────────────────────────── Cloudflare R2
     │                                          (store image)
     │
     ├─ Insert Post ────┬──────────────────── Supabase
     │                  │                     (profiles, posts)
     │                  │ RLS: user_id check
     │                  │ (user can only create their own posts)
     │                  ▼
     │              ┌──────────────┐
     │              │ posts table  │
     │              └──────────────┘
     │
     └─ Invalidate Cache ──────────────────── Upstash Redis
                                              (delete feed cache)

Response:
┌──────────────────────┐
│ {                    │
│  id: uuid,           │
│  user_id: uuid,      │
│  media_url: R2 url,  │
│  created_at: now     │
│ }                    │
└──────────────────────┘
     │
     ▼
Mobile receives post
Feed updates (React Query invalidation)
Realtime subscribers notified (Supabase Realtime)
```

---

## 3️⃣ Fluxo de Autenticação

```
1. REGISTER
┌─────────┐
│ Mobile  │ POST /api/v1/auth/register
│ { email │ { email, password, username }
│  pass } │
└────┬────┘
     │
     ▼
  Supabase Auth Service
  ├─ Create user (with email+password)
  ├─ Return access_token + refresh_token
  │
  └─ Also create profile in Supabase DB
     (via trigger or manual insert)

2. LOGIN
┌─────────┐
│ Mobile  │ POST /api/v1/auth/login
│ { email │ { email, password }
│ pass }  │
└────┬────┘
     │
     ▼
  Supabase Auth
  ├─ Verify credentials
  └─ Return access_token (JWT)
     ├─ user_id (sub claim)
     ├─ email
     └─ exp (1 hour by default)

3. AUTHENTICATED REQUEST
┌──────────┐
│ Mobile   │ GET /api/v1/health/metrics
│ +Header: │ Authorization: Bearer <jwt_token>
│ Bearer   │
└────┬─────┘
     │
     ▼
  Middleware: auth.py
  ├─ Extract token from header
  ├─ Decode JWT (verify with Supabase PK)
  ├─ Extract user_id from 'sub' claim
  └─ Inject into request.state.user_id

  ▼
  Endpoint handler
  ├─ Use dependency: require_auth
  ├─ user_id injected as parameter
  └─ Query Supabase with user_id (RLS handles security)

RLS Policy Example:
  SELECT * FROM health_metrics
  WHERE user_id = current_user_id
  (Supabase enforces this automatically)
```

---

## 4️⃣ Rate Limiting — Step by Step

```
Request arrives
    │
    ▼
Middleware: rate_limit.py
├─ Identify client
│  ├─ If authenticated: use user_id
│  └─ If not: use IP address
│
├─ Check 1-minute window
│  ├─ key = "rate_limit:1m:{client_id}"
│  ├─ INCR key
│  ├─ If count > 60: return 429 Too Many Requests
│  └─ If count == 1: EXPIRE key 60 (set TTL)
│
├─ Check 1-hour window
│  ├─ key = "rate_limit:1h:{client_id}"
│  ├─ INCR key
│  ├─ If count > 1000: return 429
│  └─ If count == 1: EXPIRE key 3600
│
└─ Continue to endpoint

Example:
  User makes 65 requests in 1 minute
  ├─ Request #61: 429 Too Many Requests
  ├─ Retry-After: 60 seconds
  └─ Mobile shows "Rate limited, wait 1 min"
```

---

## 5️⃣ Stack de Dependências — Resumo

### Backend (Python)
```
FastAPI              → Framework web
Uvicorn              → ASGI server
Pydantic             → Data validation
PyJWT                → JWT handling
Supabase             → DB + Auth client
Redis                → Cache client
Google Generative AI → Gemini API
Boto3                → S3/R2 client
Pytest               → Testing
```

### Mobile (React Native)
```
Expo                  → React Native framework
Expo Router           → File-based routing
Zustand              → State management
React Query          → Server state cache
NativeWind           → Tailwind for RN
FastImage            → Image loading optimization
Axios                → HTTP client
```

### DevOps
```
Railway              → Backend hosting
Expo EAS Build       → Mobile build service
GitHub Actions       → CI/CD
Sentry              → Error tracking
```

---

## 6️⃣ Segurança — Checklist Implementado ✅

| Aspecto | Status | Detalhe |
|---------|--------|---------|
| Auth | ✅ Implementado | JWT via Supabase, validation no middleware |
| Rate Limit | ✅ Implementado | Redis sliding window, bypass paths configuráveis |
| CORS | ✅ Configurado | Origins configurable por env |
| RLS | ✅ Preparado | Supabase RLS rules (a configurar no banco) |
| HTTPS | ⚠️ Dev | Habilitado em produção (Railway/EAS automático) |
| Secrets | ✅ Implementado | .env files, não commitados |
| JWT | ⚠️ Migição | Atualmente HS256, migrar para RS256 + JWKS em prod |
| Logging | ✅ Implementado | Structured logging com request_id |

---

## 7️⃣ Custo Total — Projeção 12 Meses

```
Fase 1 (MVP): 6 semanas
├─ Supabase: $0 (free tier)
├─ Upstash: $0–10/mês
├─ Cloudflare: $0–5/mês
├─ Gemini: $0 (free tier)
├─ Railway: $0 (free 500h/mês)
└─ TOTAL: ~$10–15/mês

Fase 2-3 (Social + IA): 14 semanas
├─ Supabase: $25–50/mês (scaling)
├─ Upstash: $20–50/mês
├─ Cloudflare: $10–20/mês (bandwidth)
├─ Gemini: $5–20/mês (scaled usage)
├─ Railway: $5–20/mês (dyno scaling)
└─ TOTAL: ~$65–160/mês

Com 1º de usuários pagos:
├─ Stripe fees: 2.9% + $0.30 por transação
├─ Aumenta ROI significantly
└─ Pode sponsorizar custos de infra
```

---

## 8️⃣ Próximo Passo Action Item

**Comando para iniciar Fase 1:**

```bash
# 1. Setup local
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 2. Configurar .env com credenciais reais

# 3. Run backend
uvicorn app.main:app --reload --port 8000

# 4. Verificar health
curl http://localhost:8000/health

# 5. Acessar Swagger Docs
open http://localhost:8000/docs
```

**Próximo commit:**
- ✅ Todos arquivos criados estão em `backend/`
- ✅ Ready para primeira implementação
- 📌 Escrever em memória para próximas sessões

**Quando disser "Implementar Fase 1 — Semana 1":**
→ Vou criar auth_service.py + completar auth.py + criar models.py + mobile screens

---

## 🎯 Arquitetura Validada ✅

| Aspecto | Status | Evidência |
|---------|--------|-----------|
| Setup Inicial | ✅ Complete | Todos arquivos críticos criados |
| Middleware Stack | ✅ Complete | Auth, rate limit, logging implementados |
| DB Connection | ✅ Ready | SupabaseClient wrapper pronto |
| Cache Layer | ✅ Ready | AsyncRedisClient pronto |
| Documentation | ✅ Complete | IMPLEMENTATION_PLAN.md + QUICK_START.md |
| Security | ✅ Foundation | JWT + RLS blueprint + rate limiting |
| Scalability | ✅ Design | Serverless stack (Upstash, R2, Gemini, Railway) |

**Conclusão: Arquitetura VALIDADA e PRONTA PARA DESENVOLVIMENTO** 🚀
