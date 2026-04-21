import React, { useState } from 'react';
import { User, Copy, ThumbsUp, RefreshCw, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { cn } from '@/utils/cn';

interface ChatMessageProps {
  content: string;
  isUser: boolean;
}

export default function ChatMessage({ content, isUser }: ChatMessageProps) {
  const [hasCopied, setHasCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setHasCopied(true);
    setTimeout(() => setHasCopied(false), 2000);
  };

  return (
    <div className={cn(
      "flex w-full mb-8",
      isUser ? "justify-end" : "justify-start"
    )}>
      <div className={cn(
        "flex max-w-[85%] md:max-w-[75%] gap-4 selection:bg-indigo-500/30",
        isUser ? "flex-row-reverse" : "flex-row"
      )}>
        <div className={cn(
          "w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-lg border relative overflow-hidden",
          isUser 
            ? "bg-gradient-to-br from-indigo-500 to-purple-600 border-white/20 text-white" 
            : "bg-foreground/5 border-foreground/10 text-foreground backdrop-blur-md"
        )}>
          {isUser ? <User className="w-4 h-4" /> : <span className="font-semibold text-[10px]">AI</span>}
        </div>
        
        <div className={cn(
          "px-5 py-4 text-[15px] leading-relaxed shadow-xl min-w-0 glass-panel",
          isUser 
            ? "bg-gradient-to-tr from-indigo-600/90 to-purple-600/90 text-white border-white/10 rounded-3xl rounded-tr-sm" 
            : "bg-foreground/5 text-foreground border-foreground/10 rounded-3xl rounded-tl-sm backdrop-blur-2xl shadow-sm"
        )}>
          {isUser ? (
            <p 
              className="whitespace-pre-wrap font-medium"
              style={{ overflowWrap: 'anywhere', wordBreak: 'break-word' }}
            >
              {content}
            </p>
          ) : (
            <div 
              className="prose prose-sm dark:prose-invert max-w-none prose-p:leading-relaxed prose-pre:bg-foreground/5 prose-pre:border-foreground/10 prose-headings:font-medium prose-a:text-indigo-500 dark:prose-a:text-indigo-400"
              style={{ overflowWrap: 'anywhere', wordBreak: 'break-word' }}
            >
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>
          )}
          
          {!isUser && (
            <div className="flex items-center gap-3 mt-4 pt-3 border-t border-foreground/10 text-muted-foreground/60">
              <button 
                onClick={handleCopy}
                className="hover:text-foreground hover:bg-foreground/5 p-1 rounded transition-colors" 
                title="Copy response"
              >
                 {hasCopied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
              <button className="hover:text-foreground hover:bg-foreground/5 p-1 rounded transition-colors" title="Helpful">
                 <ThumbsUp className="w-3.5 h-3.5" />
              </button>
              <button className="hover:text-foreground hover:bg-foreground/5 p-1 rounded transition-colors" title="Regenerate">
                 <RefreshCw className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
