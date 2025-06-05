import { redirect } from 'next/navigation';

export default function RedirectPage({ params }: { params: { slug: string } }) {
  redirect(`http://localhost:3001/r/${params.slug}`);
}
