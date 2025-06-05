import Link from 'next/link';
import CreateLinkForm from './components/CreateLinkForm';
=======
import { revalidatePath } from 'next/cache';

export default function Home() {
  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold mb-4">gunslol URL Shortener</h1>
      <CreateLinkForm />
      <form action="/api/links" method="post" className="flex flex-col gap-2">
        <input className="border p-2" type="url" name="url" placeholder="https://" required />
        <input className="border p-2" type="text" name="slug" placeholder="custom slug" />
        <button className="bg-blue-500 text-white px-4 py-2">Create</button>
      </form>
      <p className="mt-4 text-sm text-gray-500">Login to manage your links.</p>
    </main>
  );
}
