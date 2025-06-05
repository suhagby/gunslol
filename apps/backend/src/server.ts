import Fastify from 'fastify';
import cors from '@fastify/cors';
import { PrismaClient } from '@prisma/client';
import { CreateLinkInput, ShortLink } from 'shared';
import { nanoid } from 'nanoid';
import { z } from 'zod';

const prisma = new PrismaClient();
const server = Fastify();

server.register(cors);

const createSchema = z.object({
  url: z.string().url(),
  slug: z
    .string()
    .min(3)
    .max(32)
    .regex(/^[a-zA-Z0-9_-]+$/)
    .optional(),
});

const shortenSchema = z.object({
  originalUrl: z.string().url(),
  customSlug: z
    .string()
    .min(3)
    .max(32)
    .regex(/^[a-zA-Z0-9_-]+$/)
    .optional(),
});

server.post<{ Body: CreateLinkInput }>('/links', async (req, reply) => {
  const parsed = createSchema.safeParse(req.body);
  if (!parsed.success) {
    reply.code(400).send({ error: 'Invalid input' });
    return;
  }
  let slug = parsed.data.slug || nanoid(6);
  if (parsed.data.slug) {
    const exists = await prisma.shortLink.findUnique({ where: { slug } });
    if (exists) {
      reply.code(400).send({ error: 'Slug already in use' });
      return;
    }
  }
  const link = await prisma.shortLink.create({
    data: { slug, url: parsed.data.url },
  });
  reply.send(link as ShortLink);
});

server.post('/api/shorten', async (req, reply) => {
  const parsed = shortenSchema.safeParse(req.body);
  if (!parsed.success) {
    reply.code(400).send({ error: 'Invalid input' });
    return;
  }
  let slug = parsed.data.customSlug || nanoid(6);
  if (parsed.data.customSlug) {
    const exists = await prisma.shortLink.findUnique({ where: { slug } });
    if (exists) {
      reply.code(400).send({ error: 'Slug already in use' });
      return;
    }
  }
  await prisma.shortLink.create({
    data: { slug, url: parsed.data.originalUrl },
  });
  const base = process.env.BASE_URL || 'http://localhost:3001';
  reply.send({ shortUrl: `${base}/r/${slug}` });
});

server.get('/r/:slug', async (req, reply) => {
  const { slug } = req.params as { slug: string };
  const link = await prisma.shortLink.findUnique({ where: { slug } });
  if (!link) {
    reply.code(404).send({ error: 'Not found' });
    return;
  }
  await prisma.click.create({
    data: { shortLinkId: link.id },
  });
  reply.redirect(link.url);
});

export async function start() {
  try {
    await server.listen({ port: 3001, host: '0.0.0.0' });
    console.log('Backend running on http://localhost:3001');
  } catch (err) {
    server.log.error(err);
    process.exit(1);
  }
}

if (require.main === module) {
  start();
}
