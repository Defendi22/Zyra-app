# ZYRA — Rede Social Fitness

**Um app mobile estilo LinkedIn para comunidade fitness. Combine tracking pessoal de saúde com funcionalidades sociais.**

---

## 🎯 MVP (6 semanas)

```
Semana 1 → Auth + Perfil
Semana 2 → Métricas (IMC, TMB, Streak)
Semana 3 → Feed + Posts
Semana 4 → Treinos (séries/reps/carga)
Semana 5 → Sistema de Amizades
Semana 6 → Polish + Deploy
```

**Status:** ✅ Arquitetura pronta, pronto para começar Semana 1

---

## ⚡ Stack (Sem Custo Fixo)

| Layer | Tech | Deploy |
|-------|------|--------|
| Frontend | React Native + Expo Router | TestFlight + Play Store |
| Backend | FastAPI (Python) | Railway (gratuito) |
| Database | Supabase (Postgres + Auth) | Supabase Cloud |
| Cache | Upstash Redis | pay-per-request |
| Storage | Cloudflare R2 | $0.015/GB (no egress fee) |
| IA | Google Gemini API | Free tier |

**Total MVP: ~$10/mês**

---

## 📁 Estrutura

```
zyra/
├── backend/              ✅ FastAPI setup pronto
│   ├── app.py           ✅ FastAPI app + middleware
│   ├── config.py        ✅ Env vars
│   ├── middleware_auth.py ✅ JWT validation
│   ├── routes/          → Login, Posts, Metrics, AI
│   ├── services/        → Business logic
│   └── requirements.txt  ✅ Python deps
│
├── mobile/              → React Native + Expo
│   ├── app/
│   │   ├── (auth)/      → Login/Register screens
│   │   └── (app)/       → Feed, Profile, Metrics
│   ├── package.json
│   └── eas.json
│
├── QUICK_START.md       ✅ Setup em 5 min
├── IMPLEMENTATION_PLAN.md ✅ Plano 6 semanas
├── ARCHITECTURE.md      ✅ Diagramas + flows
└── README.md           ✅ Este arquivo
```

---

## 🚀 Começar (5 min)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Editar .env com credenciais do Supabase, Upstash, Gemini

python app.py
# Verificar: http://localhost:8000/docs
```

### Mobile

```bash
cd mobile
npm install
npx expo start
# Escanear QR code num Expo Go app (iOS/Android)
```

---

## 📊 Arquitetura (4 Camadas)

```
1. PRESENTATION
   React Native + Expo Router + Zustand

2. API GATEWAY
   FastAPI + Middleware (Auth, Rate Limit, Logging)

3. SERVICES
   AuthService, SocialService, HealthService, AIService

4. DATA
   Supabase, Upstash Redis, Cloudflare R2, Gemini API
```

**Ver completo em:** `ARCHITECTURE.md`

---

## 📋 Fase 1 Completa (MVP)

| Semana | Entregável | Status |
|--------|-----------|--------|
| 1 | Auth + Perfil | → Começar aqui |
| 2 | Health Metrics | TODO |
| 3 | Feed + Posts | TODO |
| 4 | Workouts | TODO |
| 5 | Friendships | TODO |
| 6 | Deploy | TODO |

---

## ✅ Checklist Fase 1 — Semana 1

- [ ] Backend setup ✅ (você está aqui)
- [ ] FastAPI running na porta 8000 ✅
- [ ] Auth middleware validando JWT ✅
- [ ] Supabase: create table `profiles`
- [ ] POST /api/v1/auth/register
- [ ] POST /api/v1/auth/login
- [ ] Mobile: login & register screens
- [ ] Tests: 80%+ em auth_service.py

---

## 💰 Custo Estimado

| Fase | Usuários | Custo/mês |
|------|----------|-----------|
| MVP | 0–10 | $0–5 |
| Social | 10–100 | $25–50 |
| IA | 100–1k | $50–100 |
| Scale | 1k+ | $100–500 |

**Nenhum custo fixo até ter usuários pagos**

---

## 🔒 Segurança Implementada

- ✅ JWT validation (Supabase tokens)
- ✅ Rate limiting (60 req/min per user)
- ✅ RLS policies (Postgres + Supabase)
- ✅ HTTPS on production
- ✅ Secrets in .env (never commit)

---

## 📚 Documentação

1. **QUICK_START.md** → Setup local + troubleshooting
2. **IMPLEMENTATION_PLAN.md** → Plano 6 semanas + 2 phases extras
3. **ARCHITECTURE.md** → Diagramas, data flows, RLS policies

---

## 🎯 Próximo Passo

1. Setup local (5 min) → QUICK_START.md
2. Começar Fase 1 — Semana 1 → Implementar auth_service.py
3. Quando pronto → avançar para Semana 2

---

## 📞 Stack Features

| Feature | Tech | Status |
|---------|----|--------|
| Cross-platform mobile | React Native + Expo | ✅ |
| Real-time feed | Supabase Realtime | ✅ |
| Image storage | Cloudflare R2 | ✅ |
| AI diet/workout | Google Gemini | ✅ |
| Authentication | Supabase Auth | ✅ |
| Caching | Upstash Redis | ✅ |
| Logging | Python logging | ✅ |
| Testing | Pytest | ✅ |

---

## 🚨 Importante

- Nunca commit `.env` (use `.env.example`)
- Todas as queries devem usar ORM (previne SQL injection)
- RLS policies obrigatórias em todas as tabelas
- Testes unitários: >= 80% coverage
- Rate limiting: sempre ativo

---

**Status: ✅ PRONTO PARA COMEÇAR**

```bash
# Start here:
cd backend && python app.py
# Verify: http://localhost:8000/docs
```

Quando estiver pronto para Phase 1 Week 1, consulte: `IMPLEMENTATION_PLAN.md`
