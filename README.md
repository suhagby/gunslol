# gunslol

Simple URL shortener built with Next.js 14, Prisma and NextAuth.

## Development

```bash
npm install
npm run dev
```

Configure environment variables by copying `.env.example` to `.env` and providing your database connection string and `NEXTAUTH_SECRET`.

Run Prisma migrations:

```bash
npx prisma migrate dev --name init
```

## Seed

Run optional seed script:

```bash
node web/prisma/seed.ts
```
