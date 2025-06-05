import { getServerSession } from 'next-auth';
import { authOptions } from '../api/auth/[...nextauth]/route';
import { redirect } from 'next/navigation';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export default async function Dashboard() {
  const session = await getServerSession(authOptions);
  if (!session?.user) {
    return redirect('/login');
  }
  const user = await prisma.user.findUnique({ where: { email: session.user.email! } });
  if (!user) {
    return <p>User not found</p>;
  }
  const links = await prisma.link.findMany({ where: { userId: user.id } });
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Your Links</h1>
      <ul className="space-y-2">
        {links.map((link: { id: string; slug: string; url: string }) => (
          <li key={link.id} className="border p-2">
            <a href={`/${link.slug}`} className="text-blue-600" target="_blank" rel="noopener noreferrer">
              {link.slug}
            </a>
            <span className="ml-2 text-sm text-gray-500">{link.url}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
