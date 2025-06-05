import { z } from 'zod';
import { PrismaClient } from '@prisma/client';
import { nanoid } from 'nanoid';
import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '../auth/[...nextauth]/route';

const prisma = new PrismaClient();

const createSchema = z.object({
  url: z.string().url(),
  slug: z
    .string()
    .min(3)
    .max(32)
    .regex(/^[a-zA-Z0-9_-]+$/)
    .optional(),
});

export async function POST(req: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  const user = await prisma.user.findUnique({ where: { email: session.user.email! } });
  if (!user) {
    return NextResponse.json({ error: 'User not found' }, { status: 400 });
  }
  const data = await req.json();
  const parsed = createSchema.safeParse(data);
  if (!parsed.success) {
    return NextResponse.json({ error: 'Invalid data' }, { status: 400 });
  }
  let slug = parsed.data.slug || nanoid(6);
  if (parsed.data.slug) {
    const exists = await prisma.shortLink.findUnique({ where: { slug } });
    if (exists) {
      return NextResponse.json(
        { error: 'Slug already in use' },
        { status: 400 }
      );
    }
  }
  const link = await prisma.shortLink.create({
    data: {
      slug,
      url: parsed.data.url,
      userId: user.id,
    },
  });
  return NextResponse.json(link);
}

export async function GET() {
  const links = await prisma.shortLink.findMany({});
  return NextResponse.json(links);
}
