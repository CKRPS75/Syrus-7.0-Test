This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

## Authentication service configuration

The FastAPI backend provides `/auth/register`, `/auth/login`, `/auth/me`, and `/auth/logout`. Set a PostgreSQL connection string in the backend environment as `DATABASE_URL`; it is a server-only secret and must never use a `NEXT_PUBLIC_` name. `TRUSTROUTE_CORS_ORIGINS` should contain the exact frontend origins as a comma-separated list. The default allows local development at `http://localhost:3000` and `http://127.0.0.1:3000`.

Passwords are stored as PBKDF2-SHA256 hashes, and sessions use random HttpOnly cookies whose hashes are stored in PostgreSQL. The frontend sends requests to the existing `NEXT_PUBLIC_API_URL` (default `http://127.0.0.1:8000`) with credentials enabled; it does not store passwords or session tokens. Use HTTPS in production and set `ENVIRONMENT=production` so session cookies are marked Secure.

Password-reset email delivery is not configured. `/auth/reset` returns an explicit unavailable response, and the frontend displays a configuration message instead of reporting a successful reset. Add an email provider before enabling reset links.

Start PostgreSQL, set `DATABASE_URL`, then run the backend with `python -m backend.main` from the project root. The authentication tables are created automatically on the first request. Registration creates an account but does not sign the user in; sign in separately after successful registration.

The sidebar profile editor currently changes only the display name shown for the active dashboard session. Persistent profile updates require a profile-update endpoint from the authentication service.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
