"use client";

import React, { useEffect, useState } from 'react';
import { PanelLeft, Sparkles, Sun, Moon } from 'lucide-react';
import { motion } from 'framer-motion';
import { useTheme } from 'next-themes';

interface HeaderProps {
  toggleSidebar: () => void;
}

export default function Header({ toggleSidebar }: HeaderProps) {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const toggleTheme = () => {
    setTheme(resolvedTheme === "light" ? "dark" : "light");
  };

  return (
    <motion.header 
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="sticky top-0 z-30 flex items-center justify-between p-4 bg-transparent border-b border-border/50 backdrop-blur-md"
    >
      <div className="flex items-center gap-4">
        <button 
          onClick={toggleSidebar} 
          className="p-2 -ml-2 rounded-xl hover:bg-foreground/5 text-muted-foreground hover:text-foreground transition-colors focus:ring-2 focus:ring-indigo-500"
          aria-label="Toggle Sidebar"
        >
          <PanelLeft className="w-5 h-5" />
        </button>
        
        <div className="flex items-center gap-3">
          <div className="relative w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/30 overflow-hidden border border-foreground/10">
             <div className="absolute inset-0 bg-white/20 blur-sm"></div>
             <Sparkles className="w-4 h-4 text-white relative z-10" />
          </div>
          <h1 className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 via-purple-500 to-indigo-600 dark:from-indigo-400 dark:via-purple-400 dark:to-indigo-400">
            Omni <span className="font-light opacity-70">Copilot</span>
          </h1>
        </div>
      </div>
      
      <div className="flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-xs font-medium text-primary backdrop-blur-sm">
          <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
          System Online
        </div>
        
        {mounted && (
          <button 
            onClick={toggleTheme}
            className="w-9 h-9 rounded-full bg-foreground/5 hover:bg-foreground/10 border border-foreground/10 flex items-center justify-center text-muted-foreground hover:text-foreground transition-all cursor-pointer backdrop-blur-sm"
            aria-label="Toggle Theme"
          >
            {resolvedTheme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        )}
      </div>
    </motion.header>
  );
}
