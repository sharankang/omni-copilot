"use client";

import React, { useState } from 'react';
import ChatLayout from '@/components/ChatLayout';
import ChatInterface from '@/components/ChatInterface';

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);

  return (
    <ChatLayout onSelectSession={setSessionId} currentSessionId={sessionId}>
      <ChatInterface sessionId={sessionId} />
    </ChatLayout>
  );
}
