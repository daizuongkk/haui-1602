import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Cảnh Báo Thời Tiết – Tỉnh Điện Biên",
  description:
    "Hệ thống cảnh báo thời tiết và phát thanh tự động tỉnh Điện Biên.",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
