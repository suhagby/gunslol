import { PrismaClient } from '@prisma/client';
import { redirect } from 'next/navigation';

const prisma = new PrismaClient();

export default async function RedirectPage({ params }: { params: { slug: string } }) {
  const link = await prisma.shortLink.findUnique({ where: { slug: params.slug } });
  if (link) {
    await prisma.click.create({ data: { shortLinkId: link.id } });
    redirect(link.url);
  }
  return <p>Link not found</p>;
}
