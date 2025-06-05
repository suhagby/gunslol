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
  await prisma.link.create({
    data: { slug: 'hello', url: 'https://example.com', userId: user.id },
  });
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
