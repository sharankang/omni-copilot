import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/ThemeProvider";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Omni Copilot - Your Premium AI",
  description: "Advanced AI assistance with a gorgeous dynamic UI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${outfit.variable} h-full antialiased font-sans bg-background text-foreground transition-colors duration-300 overflow-hidden`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <div className="bg-mesh-container">
            <div className="blob blob-1"></div>
            <div className="blob blob-2"></div>
            <div className="blob blob-3"></div>
          </div>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
