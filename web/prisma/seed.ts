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
  const link1 = await prisma.link.create({
    data: { slug: 'hello', url: 'https://example.com', userId: user.id },
  });
  const link2 = await prisma.link.create({
    data: { slug: 'docs', url: 'https://example.com/docs', userId: user.id },
  });
  await prisma.click.createMany({
    data: [
      { linkId: link1.id, ip: '127.0.0.1', userAgent: 'seed' },
      { linkId: link1.id, ip: '127.0.0.1', userAgent: 'seed' },
      { linkId: link2.id, ip: '127.0.0.1', userAgent: 'seed' },
    ],
  });
  await prisma.link.create({
    data: { slug: 'hello', url: 'https://example.com', userId: user.id },
  });
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
