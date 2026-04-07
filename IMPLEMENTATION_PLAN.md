# ZYRA — Plano de Implementação (3 Fases, 20 Semanas)

## FASE 1: MVP (6 semanas)

### Semana 1: Auth + Perfil ⭐
- [x] Setup FastAPI + middleware
- [ ] Supabase: criar tabelas (profiles)
- [ ] POST /api/v1/auth/register (email + password)
- [ ] POST /api/v1/auth/login
- [ ] GET /api/v1/profile/{id}
- [ ] PUT /api/v1/profile (atualizar foto + bio)
- [ ] Mobile: screens de auth (login/register)

**Entregáveis:** Login funcionando + perfil básico

---

### Semana 2: Métricas (IMC, TMB, Streak) ⭐
- [ ] POST /api/v1/health/metrics (weight, body_fat, height)
- [ ] Cálcular IMC e TMB (Harris-Benedict)
- [ ] GET /api/v1/health/streak (dias consecutivos)
- [ ] POST /api/v1/health/checkin (academia, localização)
- [ ] Mobile: health tracker screen
- [ ] Testes unitários de cálculos

**Entregáveis:** Dashboard de saúde com streak

---

### Semana 3: Feed + Posts ⭐
- [ ] POST /api/v1/social/posts (foto + texto)
- [ ] GET /api/v1/social/feed (público, cronológico, paginação)
- [ ] Media service: upload para Cloudflare R2
- [ ] Cache de feed em Redis
- [ ] Mobile: feed screen + create post
- [ ] Lazy loading de imagens

**Entregáveis:** Successfully posting conquistas + feed público

---

### Semana 4: Treinos
- [ ] POST /api/v1/health/workouts (date, duration)
- [ ] POST /api/v1/health/workout_sets (exercise, sets, reps, weight)
- [ ] GET /api/v1/health/workouts (histórico)
- [ ] Mobile: workout logging screen
- [ ] Visual de histórico (tabela de treinos)

**Entregáveis:** Registro completo de treinos

---

### Semana 5: Sistema de Amizades
- [ ] POST /api/v1/social/friendships/request (enviar convite)
- [ ] POST /api/v1/social/friendships/accept (aceitar convite)
- [ ] GET /api/v1/social/friends (listar amigos)
- [ ] GET /api/v1/social/compare/{friend_id} (comparar métricas)
- [ ] Mobile: friends screen

**Entregáveis:** Sistema social básico

---

### Semana 6: Polish + Deploy
- [ ] Todos os testes passando (pytest)
- [ ] Configurar Railway para deploy automático
- [ ] EAS Build: configurar iOS + Android
- [ ] Documentação de API completa (Swagger)
- [ ] Security: RLS rules no Supabase
- [ ] Performance: optimize queries + cache

**Entregáveis:** MVP em produção no Railway + TestFlight/Google Play

---

## FASE 2: Social (Semanas 7–12)

- [ ] Feed personalizado (amigos em destaque)
- [ ] Notificações push (Expo Push)
- [ ] Compartilhamento com visibilidade (público/amigos/privado)
- [ ] Sistema de comentários em posts
- [ ] Like/unlike posts
- [ ] Follow/unfollow usuários

---

## FASE 3: IA + Avançado (Semanas 13–20)

- [ ] POST /api/v1/ai/analyze-meal (Gemini Vision)
- [ ] POST /api/v1/ai/generate-diet (dieta personalizada)
- [ ] POST /api/v1/ai/generate-workout (plano de treino)
- [ ] POST /api/v1/ai/coach (coach virtual com chat)
- [ ] Integração Google Fit / Apple Health
- [ ] Dashboards com gráficos interativos

---

## Timeline Crítica

```
Semana → 1  2  3  4  5  6 | 7  8  9 10 11 12 | 13 14 15 16 17 18 19 20
Status  → ████████████████ | ████████████████ | ████████████████████
Fase    → ← MVP em Prod ←   | ← Social Features | ← IA + Avançado ←
Users   → 0 → 10 → 50 → 200 | 100 → 500 → 1000 | 1k → 5k → 10k
```

---

## Stack Mantém-se:

| Camada | Tech | Deploy |
|--------|------|--------|
| Frontend | React Native + Expo Router | EAS Build + TestFlight/Play Store |
| Backend | FastAPI (Python) | Railway (push automático) |
| Database | Supabase (Postgres + Auth + Realtime) | Supabase Cloud |
| Cache | Upstash Redis | Upstash (pay-per-request) |
| Storage | Cloudflare R2 | CDN automático |
| IA | Google Gemini API | Gemini Cloud |

---

## Métrica de Sucesso (MVP)

- ✅ 0 bugs críticos
- ✅ < 2s load time em feed
- ✅ 90%+ uptime
- ✅ < 1% auth error rate
