"use client";

import { useState } from "react";

export default function CreateLinkForm() {
  const [url, setUrl] = useState("");
  const [slug, setSlug] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    const res = await fetch("http://localhost:3001/api/shorten", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, slug: slug || undefined }),
    });
    const data = await res.json();
    setLoading(false);
    if (!res.ok) {
      setError(data.error || "Failed to create link");
    } else {
      setResult(data.shortUrl);
      setUrl("");
      setSlug("");
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2">
      <input
        className="border p-2"
        type="url"
        placeholder="https://"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        required
      />
      <input
        className="border p-2"
        type="text"
        placeholder="custom slug"
        value={slug}
        onChange={(e) => setSlug(e.target.value)}
      />
      <button
        type="submit"
        className="bg-blue-500 text-white px-4 py-2"
        disabled={loading}
      >
        {loading ? "Creating..." : "Create"}
      </button>
      {error && <p className="text-red-600 text-sm">{error}</p>}
      {result && (
        <p className="text-sm">
          Short link: <a className="text-blue-600" href={result}>{result}</a>
        </p>
      )}
    </form>
  );
}
