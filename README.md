# gunslol

Simple URL shortener built with Next.js 14, Prisma and NextAuth.

## Development

```bash
cd web
npm install
npm run dev
```

Configure environment variables by copying `.env.example` to `.env` and setting the values for your database connection string, `NEXTAUTH_SECRET` and OAuth provider keys.

Run Prisma migrations:

```bash
cd web
npx prisma migrate dev --name init
```

## Seed

Run optional seed script:

```bash
cd web
node prisma/seed.ts
```

## Deployment

The app is ready to deploy on Vercel. Set the environment variables from `.env` in your project settings and run `vercel --prod`.
