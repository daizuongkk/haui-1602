import Link from "next/link";
import { ShieldAlert, Users, LayoutDashboard, ArrowRight } from "lucide-react";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 text-white">
      <div className="mx-auto flex min-h-screen max-w-5xl flex-col items-center justify-center gap-10 px-4 py-16 text-center">
        <div className="space-y-4">
          <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-1.5 text-sm font-medium">
            <ShieldAlert className="h-4 w-4 text-red-400" />
            Hệ thống AI cảnh báo thiên tai
          </div>
          <h1 className="text-4xl font-extrabold leading-tight sm:text-5xl">
            Cảnh báo thời tiết cực đoan
            <span className="block text-red-400">Tỉnh Điện Biên</span>
          </h1>
          <p className="mx-auto max-w-xl text-slate-300">
            Phát hiện sớm mưa lớn, lũ quét, sạt lở và rét hại theo từng huyện. Bản tin đa ngôn ngữ
            Việt – Thái – H&apos;Mông kèm audio phát thanh.
          </p>
        </div>

        <div className="grid w-full max-w-3xl gap-5 sm:grid-cols-2">
          <PortalCard
            href="/citizen"
            icon={Users}
            title="Người dân"
            desc="Xem cảnh báo, hướng dẫn cần làm và dự báo nhiều ngày cho khu vực của bạn."
            accent="bg-red-500"
          />
          <PortalCard
            href="/dashboard"
            icon={LayoutDashboard}
            title="Trung tâm điều hành"
            desc="Theo dõi toàn tỉnh, duyệt cảnh báo AI và phát thông báo đa kênh."
            accent="bg-indigo-500"
          />
        </div>
      </div>
    </main>
  );
}

function PortalCard({
  href,
  icon: Icon,
  title,
  desc,
  accent,
}: {
  href: string;
  icon: typeof Users;
  title: string;
  desc: string;
  accent: string;
}) {
  return (
    <Link
      href={href}
      className="group flex flex-col gap-3 rounded-2xl bg-white/5 p-6 text-left ring-1 ring-white/10 transition-all hover:bg-white/10 hover:ring-white/30"
    >
      <span className={`flex h-12 w-12 items-center justify-center rounded-xl ${accent}`}>
        <Icon className="h-6 w-6 text-white" />
      </span>
      <h2 className="text-xl font-bold">{title}</h2>
      <p className="text-sm text-slate-300">{desc}</p>
      <span className="mt-auto inline-flex items-center gap-1 pt-2 font-semibold text-red-300 group-hover:gap-2">
        Truy cập <ArrowRight className="h-4 w-4 transition-all" />
      </span>
    </Link>
  );
}
