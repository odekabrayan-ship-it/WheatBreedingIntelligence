import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "WheatBreeding Intelligence",
  description:
    "A scientific decision-support platform for wheat breeding, genomic data, phenotypic data, environmental data, prediction, and explainable machine learning.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full">{children}</body>
    </html>
  );
}
