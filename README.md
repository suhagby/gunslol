# gunslol


Monorepo URL shortener built with TurboRepo. The frontend is Next.js 14 and the
backend uses Fastify with Prisma and PostgreSQL.

## Development

Install dependencies and start both apps in development mode:

```bash
npm install
npm run dev -w apps/web
npm run dev -w apps/backend

Simple URL shortener built with Next.js 14, Prisma and NextAuth.

## Development

```bash
cd web
main
npm install
npm run dev

```

Configure environment variables by copying `.env.example` to `.env` and setting the values for your database connection string, `NEXTAUTH_SECRET` and OAuth provider keys.

Run Prisma migrations to create the `User`, `ShortLink` and `Click` tables:

```bash
cd apps/backend


Configure environment variables by copying `.env.example` to `.env` and providing your database connection string and `NEXTAUTH_SECRET`.

Run Prisma migrations:

```bash

cd web

main

npx prisma migrate dev --name init
```

## Seed

Run optional seed script:

```bash

cd apps/backend
npm run seed


cd apps/backend
npm run seed

cd web
node prisma/seed.ts

```

## Deployment

The app is ready to deploy on Vercel. Set the environment variables from `.env` in your project settings and run `vercel --prod`.




node web/prisma/seed.ts


