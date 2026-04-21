"use client";

import React, { useState, useEffect } from 'react';
import { Plus, MessageSquare, PanelLeftClose, Link2, Check, X, Trash2 } from 'lucide-react';
import { cn } from '@/utils/cn';
import { motion, AnimatePresence } from 'framer-motion';

interface Session {
  id: string;
  title: string;
  created_at: string;
}

interface SidebarProps {
  isOpen: boolean;
  closeSidebar: () => void;
  onSelectSession: (id: string | null) => void;
  currentSessionId: string | null;
}

export default function Sidebar({ isOpen, closeSidebar, onSelectSession, currentSessionId }: SidebarProps) {
  const [connections, setConnections] = useState<Record<string, boolean>>({});
  const [sessions, setSessions] = useState<Session[]>([]);

  const fetchStatus = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/status`);
      if (response.ok) {
        const data = await response.json();
        const serverConns = data.connections || {};
        const isGoogleConnected = Boolean(serverConns["Google Calendar"]);
        
        setConnections({
          "Gmail": isGoogleConnected,
          "Drive": isGoogleConnected,
          "GMeet": isGoogleConnected,
          "Calendar": isGoogleConnected,
          "Slack": Boolean(serverConns["Slack"])
        });
      }
    } catch (e) {
      console.error("Could not fetch connection status");
    }
  };

  const fetchSessions = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/chat/sessions`);
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions || []);
      }
    } catch (e) {
      console.error("Could not fetch sessions");
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchSessions();
    const interval = setInterval(fetchSessions, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleDeleteSession = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      await fetch(`${apiUrl}/api/chat/${id}`, { method: 'DELETE' });
      setSessions(prev => prev.filter(s => s.id !== id));
      if (currentSessionId === id) {
        onSelectSession(null);
      }
    } catch (e) {
      console.error("Could not delete session");
    }
  };

  return (
    <AnimatePresence>
      <motion.div 
        initial={{ x: -300 }}
        animate={{ x: isOpen ? 0 : -300 }}
        transition={{ type: "spring", stiffness: 260, damping: 20 }}
        className={cn(
          "fixed md:relative z-40 h-full w-[280px] glass-panel border-r flex flex-col shrink-0 overflow-hidden",
          !isOpen && "md:w-0 md:border-none"
        )}
      >
        <div className="p-5 flex items-center justify-between border-b border-foreground/5">
          <motion.div 
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex-1"
          >
            <button 
              onClick={() => onSelectSession(crypto.randomUUID())}
              className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-500 to-purple-500 text-white hover:from-indigo-400 hover:to-purple-400 p-2.5 rounded-xl transition-all shadow-lg shadow-indigo-500/20 font-medium text-sm border border-white/10"
            >
              <Plus className="w-4 h-4" />
              <span>New Conversation</span>
            </button>
          </motion.div>
          <button onClick={closeSidebar} className="p-2 ml-3 hover:bg-foreground/5 rounded-xl md:hidden text-muted-foreground transition-colors">
            <PanelLeftClose className="w-5 h-5" />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto px-4 py-4 custom-scrollbar">
          <div className="flex items-center gap-2 text-[10px] font-bold text-indigo-400/80 mb-3 px-2 uppercase tracking-widest">
            <span>Recent Chats</span>
          </div>
          <div className="space-y-1.5 mb-8">
            {sessions.length === 0 ? (
              <div className="px-2 py-4 text-xs text-muted-foreground/60 text-center italic">No recent chats</div>
            ) : (
              sessions.map((session) => (
                <button 
                  key={session.id}
                  onClick={() => onSelectSession(session.id)}
                  className={cn(
                    "w-full text-left flex items-center gap-3 px-3 py-3 rounded-xl text-sm font-medium transition-all group border",
                    currentSessionId === session.id 
                      ? "bg-foreground/10 border-foreground/10 shadow-sm text-foreground" 
                      : "bg-transparent border-transparent text-muted-foreground hover:bg-foreground/5 hover:text-foreground"
                  )}
                >
                  <MessageSquare className={cn("w-4 h-4 shrink-0 transition-colors", currentSessionId === session.id ? "text-primary" : "text-muted-foreground/50")} />
                  <span className="truncate flex-1">{session.title}</span>
                  <div 
                    onClick={(e) => handleDeleteSession(e, session.id)}
                    className="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-red-500/20 hover:text-red-400 rounded-md transition-all shrink-0"
                    title="Delete Chat"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </div>
                </button>
              ))
            )}
          </div>

          <div className="flex items-center gap-2 text-[10px] font-bold text-purple-400/80 mb-3 px-2 uppercase tracking-widest">
            <Link2 className="w-3.5 h-3.5" />
            <span>Integrations</span>
          </div>
          <div className="space-y-2 px-1">
            {Object.keys(connections).length > 0 ? (
              Object.entries(connections).map(([app, isConnected]) => (
                <div key={app} className="flex items-center justify-between px-2 py-2 text-sm font-medium text-foreground">
                  <span className="text-muted-foreground text-[13px]">{app}</span>
                  <div className={cn(
                    "flex items-center justify-center w-2 h-2 rounded-full shadow-lg relative",
                    isConnected 
                      ? "bg-emerald-400 shadow-emerald-400/50" 
                      : "bg-red-500 shadow-red-500/50"
                  )}>
                     {isConnected && (
                       <span className="absolute w-full h-full rounded-full bg-emerald-400 animate-ping opacity-60"></span>
                     )}
                  </div>
                </div>
              ))
            ) : (
               <div className="px-2 py-1.5 text-xs text-muted-foreground italic">Backend unavailable</div>
            )}
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
