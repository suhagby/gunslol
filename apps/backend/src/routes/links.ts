import { FastifyInstance } from 'fastify';
import { nanoid } from 'nanoid';
import { z } from 'zod';
import { prisma } from '../utils/prisma';

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

export async function registerLinkRoutes(server: FastifyInstance) {
  server.post<{ Body: { url: string; slug?: string } }>('/links', async (req, reply) => {
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
    const link = await prisma.shortLink.create({ data: { slug, url: parsed.data.url } });
    reply.send(link);
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
    await prisma.shortLink.create({ data: { slug, url: parsed.data.originalUrl } });
    const base = process.env.BASE_URL || 'http://localhost:3001';
    reply.send({ shortUrl: `${base}/r/${slug}` });
  });

  server.get('/links', async (_, reply) => {
    const links = await prisma.shortLink.findMany({ orderBy: { createdAt: 'desc' } });
    reply.send(links);
  });

  server.get('/r/:slug', async (req, reply) => {
    const { slug } = req.params as { slug: string };
    const link = await prisma.shortLink.findUnique({ where: { slug } });
    if (!link) {
      reply.code(404).send({ error: 'Not found' });
      return;
    }
    await prisma.click.create({ data: { shortLinkId: link.id } });
    await prisma.shortLink.update({
      where: { id: link.id },
      data: { clickCount: { increment: 1 } },
    });
    reply.redirect(link.url);
  });
}
