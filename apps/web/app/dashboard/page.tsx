import { getServerSession } from 'next-auth';
import { authOptions } from '../../lib/auth';
import { redirect } from 'next/navigation';


export default async function Dashboard() {
  const session = await getServerSession(authOptions);
  if (!session?.user) {
    return redirect('/login');
  }
  const res = await fetch('http://localhost:3001/links', { cache: 'no-store' });
  const links = await res.json();
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Your Links</h1>
      <ul className="space-y-2">
        {links.map((link: { id: string; slug: string; url: string; createdAt: Date; clickCount: number }) => (
          <li key={link.id} className="border p-2 flex flex-col">
            <div>
              <a
                href={`/${link.slug}`}
                className="text-blue-600"
                target="_blank"
                rel="noopener noreferrer"
              >
                {link.slug}
              </a>
              <span className="ml-2 text-sm text-gray-500">{link.url}</span>
            </div>
            <span className="text-xs text-gray-500">
              {link.clickCount} clicks •{' '}
              {new Date(link.createdAt).toLocaleDateString()}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
