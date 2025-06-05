import { redirect } from 'next/navigation';

export default function RedirectPage({ params }: any) {
  redirect(`http://localhost:3001/r/${params.slug}`);
}
