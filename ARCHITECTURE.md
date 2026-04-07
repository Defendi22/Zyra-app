# ZYRA — Arquitetura & Design

## 4 Camadas — Clean Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               LAYER 1: PRESENTATION                         │
│        (React Native + Expo + Zustand + React Query)        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • Login/Register (auth)                             │   │
│  │ • Feed (social)                                     │   │
│  │ • Profile + Metrics (health)                        │   │
│  │ • Meal Scanner + Coach (ai)                         │   │
│  │ Componentes: posts, streaks, treinos, amizades      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP + WebSocket
┌─────────────────────▼───────────────────────────────────────┐
│           LAYER 2: API GATEWAY (FastAPI)                    │
│  /api/v1/auth    /api/v1/social    /api/v1/health         │
│  /api/v1/ai                                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Middleware:                                         │   │
│  │ • Auth: JWT validation (Supabase tokens)            │   │
│  │ • Rate Limit: 60 req/min (Redis)                    │   │
│  │ • Logging: request_id tracking                      │   │
│  └─────────────────────────────────────────────────────┘   │
│  Roteadores por domínio (separação clara)                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│      LAYER 3: SERVICE LAYER (Business Logic)                │
│  ┌──────────────┬──────────────┬───────────────────────┐   │
│  │ AuthService  │ SocialService│ HealthService        │   │
│  │ • Login      │ • Posts      │ • IMC/TMB calc       │   │
│  │ • Register   │ • Feed       │ • Streak             │   │
│  │ • Tokens     │ • Friendships│ • Workouts           │   │
│  │              │ • Compare    │ • Checkins           │   │
│  └──────────────┴──────────────┴───────────────────────┘   │
│  ┌──────────────────┬──────────────────────────────────┐   │
│  │ AIService        │ MediaService                     │   │
│  │ • Meal analysis  │ • Upload R2                      │   │
│  │ • Diet gen       │ • Delete files                   │   │
│  │ • Workout gen    │ • Image optimization             │   │
│  │ • Coach chat     │                                  │   │
│  └──────────────────┴──────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│           LAYER 4: DATA + EXTERNAL SERVICES                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐   │
│  │ Supabase DB  │  │ Upstash Redis│  │ Cloudflare R2  │   │
│  │ • Profiles   │  │ • Feed cache │  │ • Avatars      │   │
│  │ • Posts      │  │ • Sessions   │  │ • Post images  │   │
│  │ • Friendships│  │ • Rate limit │  │ • Meal photos  │   │
│  │ • Workouts   │  │ • Rate limit │  │                │   │
│  │ • Health     │  │               │  │                │   │
│  │ • RLS Rules  │  │               │  │                │   │
│  └──────────────┘  └──────────────┘  └────────────────┘   │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Google Gemini API                                  │   │
│  │ • Vision: analyze meal photos                      │   │
│  │ • Text: generate diet + workout plans              │   │
│  │ • Chat: coach dialogue                             │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

---

## Data Flow — Exemplo: Postar Conquista

```
Mobile App
│
├─ User tira foto + escreve caption
└─> POST /api/v1/social/posts
    {
      "image": "base64...",
      "caption": "200kg no supino! 💪",
      "visibility": "public"
    }

    ▼

    Middleware: AuthMiddleware
    ├─ Valida JWT
    └─ Injeta user_id no request.state

    ▼

    Router: @app.post("/posts")
    ├─ Valida Pydantic schema
    └─ Chama social_service.create_post()

    ▼

    Service Layer: SocialService.create_post()
    ├─ 1. Valida visibilidade (public/friends/private)
    ├─ 2. Chama media_service.upload_image() → R2
    ├─ 3. Salva post no Supabase
    ├─ 4. Invalida cache de feed (Redis)
    └─ 5. Dispara Realtime event (Supabase)

    ▼

    Database Layer
    ├─ R2: armazena imagem
    └─ Supabase: insert em posts table
       (RLS: user_id = current_user_id)

    ▼

    Response
    {
      "id": "uuid",
      "user_id": "uuid",
      "image_url": "https://zyra.cdn.../image.jpg",
      "created_at": "2024-01-15T10:30:00Z"
    }

    ▼

    Mobile: React Query invalidates feed
    └─> Users see new post in real-time (Realtime subscription)
```

---

## Request Timeline — Performance

```
Total: < 500ms em 99% dos casos

Request arrives
    │
    ├─ Auth middleware: 5ms
    │  └─ JWT decode
    │
    ├─ Rate limit check: 2ms
    │  └─ Redis INCR
    │
    ├─ Route handler: 10ms
    │  └─ Pydantic validation
    │
    ├─ Service layer: 400ms
    │  ├─ Image resize: 100ms (R2)
    │  ├─ DB insert: 50ms (Supabase)
    │  └─ Cache invalidation: 5ms (Redis)
    │
    └─ Response: ~500ms total
```

---

## Segurança — Camadas

### Layer 2 (API Gateway)
- ✅ JWT validation
- ✅ Rate limiting
- ✅ CORS headers
- ✅ Request logging (detect abuse)

### Layer 3 (Services)
- ✅ Input validation (Pydantic)
- ✅ Authorization checks
- ✅ SQL injection prevention (ORM)
- ✅ Sensitive data masking in logs

### Layer 4 (Database)
- ✅ RLS (Row Level Security) — user only sees their own data
- ✅ Encrypted connection (HTTPS/TLS)
- ✅ Secrets in .env (never commit)

---

## RLS Policies — Exemplo

```sql
-- profiles: users só veem seu próprio perfil
CREATE POLICY "users_can_read_own_profile" ON profiles
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "users_can_update_own_profile" ON profiles
  FOR UPDATE
  USING (auth.uid() = user_id);

-- posts: todos veem posts públicos, amigos veem posts privados
CREATE POLICY "see_public_posts" ON posts
  FOR SELECT
  USING (visibility = 'public' OR user_id = auth.uid());

CREATE POLICY "see_friend_posts" ON posts
  FOR SELECT
  USING (
    visibility = 'friends'
    AND user_id IN (
      SELECT friend_id FROM friendships
      WHERE requester_id = auth.uid() AND status = 'accepted'
    )
  );
```

---

## Testing Strategy

### Unit Tests (services/)
```python
# test_health_service.py
def test_imc_calculation():
    imc = HealthService.calculate_imc(weight=70, height=1.75)
    assert imc == 22.86

def test_streak_logic():
    streak = HealthService.calculate_streak([date1, date2, date3])
    assert streak == 3  # 3 dias consecutivos
```

### Integration Tests (routes/)
```python
# test_auth.py
def test_login_success(client):
    response = client.post("/api/v1/auth/login",
                           json={"email": "test@gmail.com", "password": "123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials(client):
    response = client.post("/api/v1/auth/login",
                           json={"email": "test@gmail.com", "password": "wrong"})
    assert response.status_code == 401
```

### E2E Tests (mobile + backend)
```bash
# Full flow: register → login → post → see in feed
pytest -m e2e
```

---

## Deployment Pipeline

```
Git push to main
    │
    ├─ GitHub Actions: run tests
    │  └─ backend/tests/ must pass 100%
    │
    ├─ GitHub Actions: lint + format
    │  └─ black, flake8
    │
    ├─ Railway: auto deploy on main
    │  └─ backend/ → railway.app
    │
    ├─ EAS Build: auto build on git tag
    │  └─ mobile/ → TestFlight + Google Play
    │
    └─ ✅ Live on production
```

---

## Cost Breakdown (Fase 1-3)

| Service | Fase 1 | Fase 2 | Fase 3 |
|---------|--------|--------|--------|
| Supabase | $0 | $25 | $50 |
| Upstash | $0–5 | $10–20 | $20–50 |
| R2 | $0–2 | $5–10 | $10–20 |
| Gemini | $0 | $5–10 | $20–100 |
| Railway | $0 | $5–10 | $20–50 |
| **Total** | **$0–5** | **$50–75** | **$120–270** |

---

## Scalability Checklist

- [x] Serverless (Upstash, R2, Gemini, Railway)
- [x] Auto-scaling (Supabase scales automatically)
- [x] Caching strategy (Redis + React Query)
- [x] CDN for images (Cloudflare R2 + Workers)
- [x] Database optimization (indexes + RLS)
- [x] API rate limiting (prevent abuse)
- [x] Monitoring (Sentry + custom logging)
- [x] Load testing (k6 or similar before launch)

---

**Status: ✅ ARCHITECTURE SOLID & READY**
