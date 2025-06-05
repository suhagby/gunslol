"use client";
import { signIn } from 'next-auth/react';

export default function Login() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen gap-2">
      <h1 className="text-xl font-bold">Login</h1>
      <button
        onClick={() => signIn('github')}
        className="bg-gray-800 text-white px-4 py-2"
      >
        Sign in with GitHub
      </button>
      <button
        onClick={() => signIn('google')}
        className="bg-red-500 text-white px-4 py-2"
      >
        Sign in with Google
      </button>
    </div>
  );
}
