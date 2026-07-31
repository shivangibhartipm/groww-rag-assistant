import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Groww AI - Mutual Fund Assistant",
  description:
    "Factual answers about mutual fund schemes, sourced from official documents.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full overflow-hidden">{children}</body>
    </html>
  );
}
