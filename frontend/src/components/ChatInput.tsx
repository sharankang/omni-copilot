import React, { KeyboardEvent, useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Mic } from 'lucide-react';
import { cn } from '@/utils/cn';

interface ChatInputProps {
  input: string;
  setInput: React.Dispatch<React.SetStateAction<string>>;
  handleSubmit: (e?: React.FormEvent) => void;
  isLoading: boolean;
}

export default function ChatInput({ input, setInput, handleSubmit, isLoading }: ChatInputProps) {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = false;
        
        recognitionRef.current.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          setInput(prev => prev ? prev + ' ' + transcript : transcript);
        };

        recognitionRef.current.onend = () => {
          setIsListening(false);
        };
      }
    }
  }, [setInput]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert("Voice input is not supported in this browser.");
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Use a temporary loading text or just block UI
    const prevInput = input;
    setInput(prev => prev + `\n[Uploading ${file.name}...]`);

    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/chat/upload`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setInput(prevInput + `\n[Attached File: ${data.file_path}] (OriginalName: ${file.name})\n`);
      } else {
        alert("File upload failed.");
        setInput(prevInput);
      }
    } catch (err) {
      console.error(err);
      alert("Error uploading file.");
      setInput(prevInput);
    }

    e.target.value = '';
  };

  return (
    <div className="absolute bottom-6 left-0 right-0 px-4 pointer-events-none z-20">
      <div className="max-w-3xl mx-auto pointer-events-auto">
        <form id="chat-form" onSubmit={(e) => handleSubmit(e)} className="relative group">
          <div className="absolute inset-2 bg-gradient-to-r from-indigo-500/20 via-purple-500/20 to-cyan-500/20 rounded-full blur-xl group-focus-within:blur-2xl group-focus-within:opacity-100 transition-all duration-700 -z-10 opacity-40"></div>
          
          <div className="relative flex items-center gap-2 glass-panel border border-foreground/10 focus-within:border-indigo-500/50 focus-within:ring-4 focus-within:ring-indigo-500/20 rounded-full p-2 pl-4 transition-all duration-300 shadow-2xl bg-background/80 hover:bg-background/95">
            
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              className="hidden" 
              accept=".txt,.md,.csv,.json,.ts,.js,.py,.pdf,image/*"
            />

            <button 
              type="button" 
              onClick={triggerFileInput}
              className="p-2.5 text-muted-foreground hover:bg-foreground/5 hover:text-foreground rounded-full transition-colors shrink-0"
              title="Attach text file"
            >
              <Paperclip className="w-5 h-5" />
            </button>
            
            <textarea
              className="flex-1 max-h-32 min-h-[44px] bg-transparent border-0 focus:ring-0 resize-none py-2.5 text-[15px] custom-scrollbar placeholder:text-muted-foreground/60 text-foreground font-medium self-center"
              placeholder="Message Omni to orchestrate your workspace..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
            />
            
            <div className="flex items-center gap-1.5 shrink-0 pr-1">
              <button 
                type="button" 
                onClick={toggleListening}
                className={cn(
                  "p-2.5 rounded-full transition-colors relative",
                  isListening ? "text-red-400 bg-red-400/10" : "text-muted-foreground hover:bg-foreground/5 hover:text-foreground"
                )}
                title="Voice input"
              >
                <Mic className="w-5 h-5 relative z-10" />
                {isListening && (
                  <span className="absolute inset-0 rounded-full bg-red-400/20 animate-ping"></span>
                )}
              </button>
              
              <button 
                type="submit" 
                disabled={!input.trim() || isLoading}
                className="w-[44px] h-[44px] flex items-center justify-center bg-gradient-to-tr from-indigo-500 to-purple-500 hover:from-indigo-400 hover:to-purple-400 text-white disabled:opacity-50 disabled:grayscale rounded-full transition-all shadow-md hover:shadow-indigo-500/25 ml-1"
              >
                <Send className="w-4 h-4 ml-0.5" />
              </button>
            </div>
          </div>
        </form>
        <div className="text-center mt-4">
          <p className="text-[11px] text-muted-foreground/60 font-medium tracking-wide pointer-events-auto">
            Omni Copilot seamlessly interfaces directly with your authentic API vectors.
          </p>
        </div>
      </div>
    </div>
  );
}
