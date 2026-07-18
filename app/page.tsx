import type { Metadata } from "next";
import { redirect } from "next/navigation";

export const metadata: Metadata = {
  title: "Your site is taking shape",
  description:
    "Your first version will appear here automatically when it’s ready.",
  other: {
    "codex-preview": "development",
  },
};

export default function Home() {
  redirect("/dashboard");
}
