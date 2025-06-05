import Link from 'next/link';
import CreateLinkForm from './components/CreateLinkForm';

export default function Home() {
  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold mb-4">gunslol URL Shortener</h1>
      <CreateLinkForm />
      <p className="mt-4 text-sm text-gray-500">Login to manage your links.</p>
    </main>
  );
}
