import type { Metadata } from "next";
import "./globals.css";
import { ToastProvider } from "@/components/ui/toast";
import { LanguageProvider } from "@/lib/i18n";

export const metadata: Metadata = {
  title: "Cảnh báo thiên tai Điện Biên",
  description: "Hệ thống AI cảnh báo thời tiết cực đoan và thiên tai tỉnh Điện Biên",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <body>
        <LanguageProvider>
          <ToastProvider>{children}</ToastProvider>
        </LanguageProvider>
      </body>
    </html>
  );
}
