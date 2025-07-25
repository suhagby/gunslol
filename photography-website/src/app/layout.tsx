import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ana Photography - Păstrăm magia momentelor tale",
  description: "Fotografie profesională pentru evenimente speciale: nunți, botezuri, aniversări. Capturăm emoțiile pure și transformăm momentele în amintiri de neuitat.",
  keywords: "fotografie, nuntă, botez, aniversare, evenimente, fotografie profesională, România",
  authors: [{ name: "Ana Photography" }],
  creator: "Ana Photography",
  openGraph: {
    title: "Ana Photography - Păstrăm magia momentelor tale",
    description: "Fotografie profesională pentru evenimente speciale: nunți, botezuri, aniversări.",
    type: "website",
    locale: "ro_RO",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ro">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
