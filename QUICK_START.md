# ZYRA — Quick Start Guide

## 📁 Estrutura de Pastas (Completa)

```
zyra/
├── backend/
│   ├── app.py                           # FastAPI app principal
│   ├── config.py                        # Env vars (Pydantic Settings)
│   ├── middleware_auth.py               # JWT validation
│   ├── middleware_rate_limit.py         # Redis rate limiter (TODO)
│   │
│   ├── routes/
│   │   ├── auth.py                      # POST /login, /register (TODO)
│   │   ├── social.py                    # Posts, friendships (TODO)
│   │   ├── health.py                    # Metrics, workouts (TODO)
│   │   └── ai.py                        # Gemini integration (TODO)
│   │
│   ├── services/
│   │   ├── auth_service.py              # Login logic (TODO)
│   │   ├── social_service.py            # Posts, feed (TODO)
│   │   ├── health_service.py            # IMC, TMB, streak (TODO)
│   │   ├── ai_service.py                # Gemini calls (TODO)
│   │   └── media_service.py             # R2 uploads (TODO)
│   │
│   ├── models/
│   │   └── schemas.py                   # Pydantic models (TODO)
│   │
│   ├── requirements.txt                 # Python dependencies
│   ├── .env.example                     # Env template
│   └── tests/
│       ├── test_auth.py                 # Auth tests (TODO)
│       ├── test_health.py               # Health tests (TODO)
│       └── test_social.py               # Social tests (TODO)
│
├── mobile/
│   ├── app/
│   │   ├── _layout.tsx                  # Root layout (Expo Router)
│   │   ├── (auth)/
│   │   │   ├── _layout.tsx
│   │   │   ├── login.tsx                # Login screen (TODO)
│   │   │   └── register.tsx             # Register screen (TODO)
│   │   ├── (app)/
│   │   │   ├── _layout.tsx              # Main layout
│   │   │   ├── index.tsx                # Feed screen (TODO)
│   │   │   ├── profile.tsx              # Profile screen (TODO)
│   │   │   ├── create-post.tsx          # Post creation (TODO)
│   │   │   └── health/
│   │   │       ├── tracker.tsx          # Health tracker (TODO)
│   │   │       └── history.tsx          # Workout history (TODO)
│   ├── package.json
│   ├── app.json                         # Expo config
│   ├── eas.json                         # EAS Build config
│   └── tsconfig.json
│
├── IMPLEMENTATION_PLAN.md               # 6-week plan (this file)
├── ARCHITECTURE.md                      # Architecture overview (TODO)
└── README.md                            # Project info

```

---

## 🚀 Setup Local (5 min)

### 1. Backend Setup

```bash
cd backend

# Criar env virtual
python -m venv venv
source venv/bin/activate    # Windows: .\venv\Scripts\activate

# Instalar dependências
pip install fastapi uvicorn pydantic pydantic-settings pyjwt supabase redis pytest

# Copiar .env.example → .env
cp .env.example .env

# Editar .env com suas credenciais
# SUPABASE_URL, SUPABASE_ANON_KEY, REDIS_URL, GEMINI_API_KEY, R2_BUCKET_URL
```

### 2. Run Backend

```bash
# Dev mode (hot reload)
python app.py

# Ou com uvicorn
uvicorn app:app --reload --port 8000

# Verificar:
# - Health: http://localhost:8000/health
# - Docs (Swagger): http://localhost:8000/docs
```

### 3. Mobile Setup

```bash
cd mobile

# Instalar dependências
npm install
# ou
yarn install

# Rodar no Expo
npx expo start

# Escanear QR code com Expo Go app (iOS/Android)
```

---

## 📊 Stack Resumido

| Layer | Tech | Custo | Cert |
|-------|------|-------|------|
| Frontend | React Native + Expo | $0 | deploy@eas |
| Backend | FastAPI (Python) | $0 | railway.app |
| Database | Supabase Postgres | $0–25/mês | supabase.co |
| Cache | Upstash Redis | $0–10/mês | upstash.com |
| Storage | Cloudflare R2 | $0–5/mês | cloudflare.com |
| IA | Google Gemini | $0/mês | ai.google.dev |
| Auth | Supabase Auth | included | supabase |
| **Total** | | **~$10/mês** | FREE tier! |

---

## 🔑 Credenciais Necessárias

| Serviço | Onde Conseguir | Quanto Tempo |
|---------|---------------|-------------|
| **Supabase** | https://app.supabase.com | 2 min (sign up + create project) |
| **Upstash** | https://console.upstash.com | 1 min (create database) |
| **Cloudflare R2** | https://dash.cloudflare.com | 2 min (create bucket) |
| **Google Gemini** | https://ai.google.dev | 5 min (get API key) |
| **Railway** | https://railway.app | 3 min (connect GitHub) |

**Total: 15 minutos para estar 100% setup**

---

## 📋 Checklist Fase 1 — Semana 1

- [ ] Backend setup + FastAPI running
- [ ] Auth middleware validando JWT
- [ ] Supabase: criar tabela `profiles`
- [ ] POST /api/v1/auth/register funcionando
- [ ] POST /api/v1/auth/login funcionando
- [ ] Mobile: login screen com Zustand store
- [ ] Tests: 80%+ coverage em auth_service.py

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
pip install -r requirements.txt
```

### "Connection refused" (Supabase/Redis)
```bash
1. Verificar .env (URL e keys corretas?)
2. Supabase: https://app.supabase.com → verificar se projeto está ativo
3. Redis: Usar `redis://localhost:6379` para local dev (sem Upstash)
```

### "Invalid token" (Auth error)
```bash
1. Token expirado? → Usar refresh token
2. Token malformado? → Verificar header "Authorization: Bearer <token>"
3. Key incorreta? → Confirmar SUPABASE_ANON_KEY no .env
```

---

## 📞 Próximos Passos

**Imediato:**
1. ✅ Setup backend + mobile (15 min)
2. ✅ Configurar .env com credenciais
3. ✅ Rodar `python app.py` ← você está aqui

**Semana 1:**
1. Implementar auth_service.py (login + register)
2. Criar roteadores completos em routes/
3. Setup Supabase tables + RLS
4. Mobile screens de auth
5. Testes passando em 80%

**Quando pronto, avance para Semana 2**

---

**Status: ✅ READY FOR DEVELOPMENT**

Comandos rápidos:
```bash
# Backend
cd backend && python app.py

# Mobile
cd mobile && npx expo start

# Tests
cd backend && pytest -v
```
