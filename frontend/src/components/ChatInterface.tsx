"use client";

import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { motion } from 'framer-motion';
import { Mail, Settings, FolderSync, Calendar, Database, MailOpen } from 'lucide-react';

interface Message {
  id: string;
  content: string;
  isUser: boolean;
}

interface ChatInterfaceProps {
  sessionId: string | null;
}

export default function ChatInterface({ sessionId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [localSessionId, setLocalSessionId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    if (!sessionId) {
      setMessages([]);
      setLocalSessionId(crypto.randomUUID());
    } else {
      setLocalSessionId(sessionId);
      fetchSessionHistory(sessionId);
    }
  }, [sessionId]);

  const fetchSessionHistory = async (id: string) => {
    setIsLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/chat/${id}`);
      if (response.ok) {
        const data = await response.json();
        const formatted = data.messages.map((m: any) => ({
          id: m.id,
          content: m.content,
          isUser: m.role === 'user'
        }));
        setMessages(formatted);
      }
    } catch (e) {
      console.error("Could not load history.");
    } finally {
      setIsLoading(false);
    }
  }

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userText = input.trim();
    setInput('');

    setMessages(prev => [...prev, { id: Date.now().toString(), content: userText, isUser: true }]);
    setIsLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userText, session_id: localSessionId }),
      });

      if (!response.ok) throw new Error("API failed");
      const data = await response.json();

      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        content: data.response,
        isUser: false
      }]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        content: "Sorry, I encountered an error communicating with the backend API.",
        isUser: false
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const startTopic = (topic: string) => {
    setInput(topic);
    setTimeout(() => {
      const form = document.getElementById('chat-form') as HTMLFormElement;
      if (form) form.requestSubmit();
    }, 100);
  }

  const suggestions = [
    { icon: <Mail className="w-5 h-5 text-indigo-400" />, title: "Draft an Email", desc: "Native Gmail integration to compose emails" },
    { icon: <MailOpen className="w-5 h-5 text-fuchsia-400" />, title: "Read my Inbox", desc: "Fetch recent unread messages securely" },
    { icon: <FolderSync className="w-5 h-5 text-cyan-400" />, title: "Search Drive", desc: "Extract text seamlessly from PDF files" },
    { icon: <Calendar className="w-5 h-5 text-emerald-400" />, title: "Check Calendar", desc: "List upcoming events natively" },
  ];

  return (
    <div className="flex-1 flex flex-col h-full relative overflow-hidden bg-transparent">
      <div className="flex-1 overflow-y-auto w-full custom-scrollbar pb-40 relative z-10">
        <div className="max-w-3xl mx-auto p-4 md:p-8 pt-10 min-h-full flex flex-col">
          
          {messages.length === 0 ? (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: "easeOut" }}
              className="flex-1 flex flex-col items-center justify-center py-20 text-center"
            >
              <div className="relative w-20 h-20 rounded-3xl bg-foreground/5 border border-foreground/10 flex items-center justify-center mb-8 shadow-2xl backdrop-blur-xl group">
                <div className="absolute inset-0 bg-gradient-to-tr from-indigo-500/20 to-purple-500/20 rounded-3xl blur-xl group-hover:blur-2xl transition-all duration-300"></div>
                <div className="absolute inset-[1px] bg-gradient-to-tr from-foreground/5 to-transparent rounded-3xl z-0"></div>
                <span className="text-4xl font-light text-primary relative z-10">o</span>
              </div>
              <h2 className="text-3xl font-medium tracking-tight mb-3 text-foreground bg-clip-text text-transparent bg-gradient-to-b from-foreground to-foreground/60">How can I assist you?</h2>
              <p className="text-muted-foreground max-w-md mx-auto mb-12 text-sm leading-relaxed">
                Experience unparalleled productivity. Omni securely coordinates your emails, documentation, and schedule through natural intelligence.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                {suggestions.map((item, idx) => (
                  <motion.button
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * idx, duration: 0.5 }}
                    whileHover={{ y: -4, scale: 1.01 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => startTopic(item.title)}
                    className="flex flex-col items-start p-6 rounded-[2rem] glass-panel group text-left hover:border-indigo-500/30 hover:bg-foreground/5 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 w-full"
                  >
                    <div className="p-3 rounded-2xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-foreground/5 shadow-sm mb-4 group-hover:scale-110 group-hover:shadow-indigo-500/20 transition-all duration-300 text-indigo-500 dark:text-indigo-400">
                      {item.icon}
                    </div>
                    <div>
                      <h3 className="font-semibold text-sm text-foreground mb-1">{item.title}</h3>
                      <p className="text-[13px] text-muted-foreground/80 leading-relaxed">{item.desc}</p>
                    </div>
                  </motion.button>
                ))}
              </div>
            </motion.div>
          ) : (
            <div className="space-y-6">
              {messages.map((msg) => (
                <ChatMessage key={msg.id} content={msg.content} isUser={msg.isUser} />
              ))}

              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex w-full mb-8 justify-start"
                >
                  <div className="flex max-w-2xl gap-4">
                    <div className="w-8 h-8 rounded-full bg-background border border-foreground/10 flex items-center justify-center shrink-0 shadow-lg backdrop-blur-sm">
                      <span className="w-1.5 h-1.5 rounded-full bg-primary animate-ping"></span>
                    </div>
                    <div className="px-6 py-4 glass-panel rounded-2xl rounded-tl-sm flex items-center gap-1.5 h-[56px] shadow-md border-foreground/10">
                      <motion.div animate={{ y: [0, -3, 0], opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1 }} className="w-1.5 h-1.5 bg-primary rounded-full" />
                      <motion.div animate={{ y: [0, -3, 0], opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1, delay: 0.2 }} className="w-1.5 h-1.5 bg-indigo-400 rounded-full" />
                      <motion.div animate={{ y: [0, -3, 0], opacity: [0.3, 1, 0.3] }} transition={{ repeat: Infinity, duration: 1, delay: 0.4 }} className="w-1.5 h-1.5 bg-indigo-400 rounded-full" />
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          )}
          <div ref={messagesEndRef} className="h-4" />
        </div>
      </div>

      <ChatInput
        input={input}
        setInput={setInput}
        handleSubmit={handleSubmit}
        isLoading={isLoading}
      />
    </div>
  );
}
