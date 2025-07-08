# 🚀 NutriAI Backend - Sistema Real

Backend Flask para o sistema NutriAI com IA Gemini e banco Neon.

## ⚡ Deploy Direto no Vercel

### 1. Subir no GitHub
```bash
git init
git add .
git commit -m "NutriAI Backend completo"
git remote add origin https://github.com/SEU-USUARIO/nutriai-backend.git
git push -u origin main
```

### 2. Deploy no Vercel
1. Conecte seu GitHub no Vercel
2. Importe o repositório
3. Configure as variáveis de ambiente:

```
GEMINI_API_KEY=sua_chave_gemini
NEON_DATABASE_URL=sua_url_neon
JWT_SECRET_KEY=sua_chave_jwt_secreta
SECRET_KEY=sua_chave_flask_secreta
CORS_ORIGINS=https://seu-frontend.vercel.app
```

### 3. APIs Necessárias

#### 🤖 Gemini AI
- Acesse: https://makersuite.google.com/app/apikey
- Crie uma API key
- Cole em `GEMINI_API_KEY`

#### 💾 Neon Database
- Acesse: https://neon.tech
- Crie um banco PostgreSQL
- Cole a connection string em `NEON_DATABASE_URL`

## 🔐 Usuários de Teste (apenas desenvolvimento)

- **Usuário:** ana@email.com / 123456
- **Nutricionista:** maria@nutricionista.com / 123456

## 🌐 Endpoints da API

### Autenticação
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Registro
- `GET /api/auth/me` - Perfil atual

### Planos Alimentares
- `POST /api/diet-plans/generate` - Gerar plano
- `GET /api/diet-plans/my-plans` - Meus planos
- `POST /api/diet-plans/{id}/validate` - Validar plano

### Status
- `GET /api/status` - Status da API

## ✅ Funcionalidades

- ✅ **Autenticação JWT** real
- ✅ **IA Gemini** integrada
- ✅ **Banco Neon** configurado
- ✅ **CORS** para frontend
- ✅ **Deploy** automático Vercel
- ✅ **Variáveis** de ambiente
- ✅ **Pronto** para produção

## 🎯 Resultado

Sistema backend completo pronto para produção com todas as integrações reais funcionando.

