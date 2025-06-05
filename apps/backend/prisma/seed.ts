import { PrismaClient } from '@prisma/client';
import { hash } from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  const password = await hash('password', 10);
  const user = await prisma.user.upsert({
    where: { email: 'test@example.com' },
    update: {},
    create: { email: 'test@example.com', password },
  });
  const link1 = await prisma.shortLink.create({
    data: { slug: 'hello', url: 'https://example.com', userId: user.id, clickCount: 2 },
  });
  const link2 = await prisma.shortLink.create({
    data: { slug: 'docs', url: 'https://example.com/docs', userId: user.id, clickCount: 1 },
  });
  await prisma.click.createMany({
    data: [
      { shortLinkId: link1.id, ip: '127.0.0.1', userAgent: 'seed' },
      { shortLinkId: link1.id, ip: '127.0.0.1', userAgent: 'seed' },
      { shortLinkId: link2.id, ip: '127.0.0.1', userAgent: 'seed' },
    ],
  });
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
