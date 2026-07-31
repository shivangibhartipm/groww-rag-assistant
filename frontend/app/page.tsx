"use client";

import dynamic from "next/dynamic";

/**
 * Chat history lives in localStorage, so the shell is restored synchronously on
 * the client rather than server-rendered and then reconciled.
 */
const AssistantApp = dynamic(
  () => import("@/components/AssistantApp").then((mod) => mod.AssistantApp),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full">
        <div className="w-[272px] shrink-0 border-r border-line bg-mint-50" />
        <div className="flex-1" />
      </div>
    ),
  },
);

export default function Home() {
  return <AssistantApp />;
}
