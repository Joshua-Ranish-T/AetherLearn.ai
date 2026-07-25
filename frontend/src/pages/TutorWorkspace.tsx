import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useCreateProject, useCreateProjectWithFile, useStartGeneration, useJobStatus } from '@/hooks/useProjects';
import { videoService } from '@/services/generationService';
import { projectsService } from '@/services/projectsService';
import { resolveStorageUrl } from '@/services/api';
import BackgroundShader from '@/components/BackgroundShader';
import ThreeJSWidget from '@/components/ThreeJSWidget';

export function TutorWorkspace() {
  const [input, setInput] = useState('');
  const [chatHistory, setChatHistory] = useState<{ role: 'user' | 'ai', content: string | React.ReactNode }[]>([]);
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  
  const [currentProjectId, setCurrentProjectId] = useState<string | null>(null);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  
  const createProject = useCreateProject();
  const createWithFile = useCreateProjectWithFile();
  const startGeneration = useStartGeneration();
  
  const { data: job } = useJobStatus(currentJobId);
  const { data: videos } = useQuery({
    queryKey: ['videos', currentProjectId],
    queryFn: () => videoService.getByProject(currentProjectId!),
    enabled: !!currentProjectId,
  });

  const latestVideo = videos?.[0];
  const isGenerating = job?.status === 'running' || job?.status === 'pending';
  
  const logsEndRef = useRef<HTMLDivElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [job?.logs]);
  
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  // Sync completion message
  useEffect(() => {
    if (job?.status === 'completed' && latestVideo && chatHistory.length > 0) {
      const lastMsg = chatHistory[chatHistory.length - 1];
      if (lastMsg.role === 'ai' && typeof lastMsg.content === 'string' && lastMsg.content.includes("3D")) {
        setChatHistory(prev => [
          ...prev,
          { 
            role: 'ai', 
            content: `✨ Your 3D animated video lesson for "${latestVideo.title}" is ready! You can watch and download it in the player on the right.`
          }
        ]);
      }
    }
  }, [job?.status, latestVideo]);

  const handleReset = () => {
    setChatHistory([]);
    setCurrentProjectId(null);
    setCurrentJobId(null);
    setInput('');
    setAttachedFile(null);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setAttachedFile(e.target.files[0]);
    }
  };

  const handleGenerate = async () => {
    if ((!input.trim() && !attachedFile) || isGenerating) return;
    
    const userQuery = input.trim() || `Analyze attached file: ${attachedFile?.name}`;
    setInput('');
    setChatHistory(prev => [...prev, { role: 'user', content: userQuery }]);
    
    // Immediate chatbot tutor explanation
    let explanationText = `Sure! Let's explore **${userQuery}**. This is a key concept that helps us understand dynamic scientific and mathematical relationships.\n\n*I am constructing your custom 3D animated video lesson now! Watch the terminal logs below as the scenes are rendered step-by-step.*`;
    
    try {
      const res = await projectsService.explain(userQuery);
      if (res && res.explanation) {
        explanationText = res.explanation;
      }
    } catch (err) {
      // Fallback explanation already set
    }

    setChatHistory(prev => [
      ...prev, 
      { 
        role: 'ai', 
        content: explanationText
      }
    ]);

    try {
      let projectId: string;
      if (attachedFile) {
        const formData = new FormData();
        formData.append('title', userQuery.substring(0, 40) + (userQuery.length > 40 ? '...' : ''));
        formData.append('description', userQuery);
        formData.append('input_type', attachedFile.type === 'application/pdf' ? 'pdf' : 'image');
        formData.append('file', attachedFile);
        const project = await createWithFile.mutateAsync(formData);
        projectId = project.id;
        setAttachedFile(null);
      } else {
        const project = await createProject.mutateAsync({
          title: userQuery.substring(0, 40) + (userQuery.length > 40 ? '...' : ''),
          input_type: 'topic',
          input_text: userQuery
        });
        projectId = project.id;
      }
      
      setCurrentProjectId(projectId);
      
      const newJob = await startGeneration.mutateAsync({ project_id: projectId });
      setCurrentJobId(newJob.id);
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'ai', content: `Sorry, there was an error starting the video generation.` }]);
    }
  };

  return (
    <div className="font-body-base text-on-surface antialiased h-screen w-screen overflow-hidden relative bg-surface-container-low transition-colors duration-500">
      {/* Background Shader Level 0 */}
      <div className="absolute inset-0 z-0 pointer-events-none mix-blend-multiply opacity-50">
        <BackgroundShader />
      </div>

      {/* Decorative 3D Widget (Level 2) */}
      <div className="absolute top-20 right-10 z-10 w-64 h-64 pointer-events-none drop-shadow-xl opacity-80">
        <ThreeJSWidget />
      </div>

      <div className="relative z-20 flex flex-col h-full w-full">
        {/* TopNavBar */}
        <nav className="flex justify-between items-center w-full px-md py-sm sticky top-0 z-50 glass-header shadow-sm transition-all duration-300">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-gradient-to-br from-primary to-green-600 rounded-md flex items-center justify-center shadow-lg">
              <span className="material-symbols-outlined text-white text-[24px]">school</span>
            </div>
            <span className="text-headline-md font-headline-md text-primary tracking-tighter drop-shadow-sm">EduVideo AI</span>
          </div>
          
          <div className="hidden md:flex gap-6 items-center">
            <Link className="text-primary border-b-2 border-primary pb-1 font-body-base text-body-base transition-all duration-300 font-bold" to="/">Workspace</Link>
            <Link className="text-gray-600 hover:text-gray-900 font-body-base text-body-base transition-all duration-300 active:scale-95" to="/dashboard">Dashboard</Link>
            <Link className="text-gray-600 hover:text-gray-900 font-body-base text-body-base transition-all duration-300 active:scale-95" to="/history">Library</Link>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center glass-panel rounded-full px-4 py-2 !border-gray-200">
              <span className="material-symbols-outlined text-gray-500 mr-2 text-[20px]">search</span>
              <input className="bg-transparent border-none focus:ring-0 outline-none text-body-base text-gray-800 placeholder:text-gray-400 w-48" placeholder="Search topics..." type="text" />
            </div>
            <button 
              onClick={handleGenerate}
              disabled={isGenerating || (!input.trim() && !attachedFile)}
              className="bg-primary text-white rounded-full px-6 py-2 font-body-base font-semibold interactive-glow hover:scale-105 transition-transform duration-200 disabled:opacity-50 disabled:hover:scale-100 shadow-md"
            >
              Generate
            </button>
            <div className="flex gap-2">
              <button onClick={handleReset} title="Clear Session" className="p-2 rounded-full hover:bg-white/50 transition-colors text-gray-500 hover:text-red-500">
                <span className="material-symbols-outlined">delete_sweep</span>
              </button>
              <button className="p-2 rounded-full hover:bg-white/50 transition-colors text-gray-500">
                <span className="material-symbols-outlined">notifications</span>
              </button>
            </div>
          </div>
        </nav>

        {/* Main Workspace Grid */}
        <main className="flex-1 flex flex-col md:flex-row gap-gutter p-md overflow-hidden relative z-20">
          
          {/* Left Panel: Chat Workspace */}
          <section className="flex-[1.2] flex flex-col glass-panel floating-element h-full overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-gray-200/50 flex justify-between items-center bg-white/30 backdrop-blur-md rounded-t-3xl">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-primary">forum</span>
                <h2 className="font-headline-md text-headline-md text-gray-800">Creative Session</h2>
              </div>
              <div className="flex items-center gap-2">
                {isGenerating && (
                  <span className="bg-amber-100 border border-amber-300 px-3 py-1 rounded-full font-label-caps text-label-caps text-amber-800 shadow-sm flex items-center gap-1.5 animate-pulse">
                    <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                    {job?.current_stage ? job.current_stage.replace(/_/g, ' ').toUpperCase() : 'GENERATING...'}
                  </span>
                )}
                <span className="bg-green-100 border border-green-200 px-3 py-1 rounded-full font-label-caps text-label-caps text-green-700 shadow-sm">AI Tutor Active</span>
              </div>
            </div>
            
            {/* Message History */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              
              {/* Initial Welcome */}
              {chatHistory.length === 0 && (
                <div className="flex justify-center items-center h-full text-center">
                  <div className="max-w-xs space-y-4 animate-slide-up">
                    <div className="w-24 h-24 rounded-full mx-auto green-globe animate-pulse-slow"></div>
                    <h3 className="text-headline-md font-headline-md text-gray-800 mt-6 drop-shadow-sm">What do you want to learn?</h3>
                    <p className="text-gray-500 text-sm">Describe a concept or attach a PDF/screenshot, and I will explain the theory and generate a 3D animated lesson.</p>
                  </div>
                </div>
              )}

              {chatHistory.map((msg, idx) => (
                <div key={idx} className={`flex animate-slide-up ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`} style={{ animationDelay: `${idx * 0.1}s` }}>
                  <div className={`p-4 max-w-[85%] transition-transform hover:-translate-y-0.5 ${
                    msg.role === 'user' 
                      ? 'chat-bubble-user' 
                      : 'chat-bubble-ai interactive-glow'
                  }`}>
                    {msg.role === 'ai' && (
                      <div className="flex items-center gap-2 mb-3 border-b border-gray-200/50 pb-2">
                        <span className={`material-symbols-outlined text-primary ${isGenerating && idx === chatHistory.length - 1 ? 'animate-spin' : ''}`}>
                          {isGenerating && idx === chatHistory.length - 1 ? 'autorenew' : 'auto_awesome'}
                        </span>
                        <span className="font-bold text-primary">EduVideo AI Tutor</span>
                      </div>
                    )}
                    <div className={msg.role === 'user' ? 'text-gray-800 font-medium' : 'text-gray-800 leading-relaxed whitespace-pre-wrap'}>
                      {msg.content}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={chatEndRef} />
            </div>
            
            {/* Input Area */}
            <div className="p-4 bg-white/40 border-t border-gray-200/50 rounded-b-3xl">
              {attachedFile && (
                <div className="flex items-center gap-2 bg-green-50 text-green-700 px-3 py-1.5 rounded-full text-xs font-medium w-fit mb-2 border border-green-200 shadow-sm animate-fade-in">
                  <span className="material-symbols-outlined text-[16px]">description</span>
                  <span className="truncate max-w-[200px]">{attachedFile.name}</span>
                  <button onClick={() => setAttachedFile(null)} className="hover:text-red-500 ml-1 font-bold">×</button>
                </div>
              )}
              <div className="relative flex items-end bg-white/60 backdrop-blur-md rounded-2xl p-2 border border-gray-200 neon-border transition-all duration-300 shadow-sm">
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={handleFileSelect} 
                  accept=".pdf,image/*" 
                  className="hidden" 
                  style={{ display: 'none' }} 
                />
                <button 
                  onClick={() => fileInputRef.current?.click()} 
                  title="Attach PDF or Image"
                  className={`p-2 transition-colors rounded-full ${attachedFile ? 'text-green-600 bg-green-100/50 font-bold' : 'text-gray-400 hover:text-primary'}`}
                >
                  <span className="material-symbols-outlined">attach_file</span>
                </button>
                <textarea 
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleGenerate();
                    }
                  }}
                  className="w-full bg-transparent outline-none border-none focus:ring-0 text-gray-800 font-body-base resize-none max-h-32 min-h-[44px] py-3 px-2 placeholder:text-gray-400" 
                  placeholder="Ask me anything or attach content... (e.g. 'Explain Derivatives')"
                />
                <button 
                  onClick={handleGenerate}
                  disabled={(!input.trim() && !attachedFile) || isGenerating}
                  className="p-2 text-primary hover:text-tertiary transition-colors interactive-glow rounded-full disabled:opacity-30 disabled:hover:text-primary"
                >
                  <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>send</span>
                </button>
              </div>
            </div>
          </section>

          {/* Right Panel: Split (Video & Terminal) */}
          <section className="flex-1 flex flex-col gap-gutter h-full">
            {/* Top: Video Player Window */}
            <div className="flex-[1.5] glass-panel floating-element overflow-hidden relative flex flex-col">
              
              {/* Player Header */}
              <div className="absolute top-0 w-full p-4 flex justify-between items-center z-30 bg-gradient-to-b from-black/20 to-transparent">
                <span className={`px-3 py-1 rounded-full text-xs font-bold text-white flex items-center gap-2 border shadow-sm ${
                  isGenerating ? 'bg-amber-500/80 border-amber-300/50' 
                  : latestVideo ? 'bg-primary/80 border-primary/50' 
                  : 'bg-surface-variant/80 border-outline/30 text-on-surface'
                } backdrop-blur-md`}>
                  {isGenerating && <span className="w-2 h-2 rounded-full bg-white animate-pulse"></span>}
                  {!isGenerating && latestVideo && <span className="w-2 h-2 rounded-full bg-white"></span>}
                  {isGenerating ? `Generating: ${job?.current_stage?.replace(/_/g, ' ') || 'Processing...'}` : latestVideo ? 'Video Ready' : 'Standby'}
                </span>
              </div>
              
              {/* Viewport */}
              <div className="flex-1 relative bg-surface-dim flex items-center justify-center overflow-hidden">
                {latestVideo && latestVideo.file_url ? (
                  <video 
                    src={resolveStorageUrl(latestVideo.file_url)} 
                    controls 
                    className="w-full h-full object-contain"
                    autoPlay
                  />
                ) : (
                  <div className="flex flex-col items-center text-on-surface-variant/50">
                    <span className="material-symbols-outlined text-[64px] mb-4 opacity-50">smart_display</span>
                    <p className="font-medium">Video Player</p>
                  </div>
                )}
              </div>
            </div>

            {/* Bottom: Terminal/Log Window */}
            <div className="flex-1 terminal-panel rounded-3xl floating-element overflow-hidden flex flex-col shadow-2xl">
              <div className="flex border-b border-slate-700/50 bg-slate-800/50 px-4 py-3 items-center justify-between">
                <div className="flex gap-4">
                  <button className="font-label-caps text-label-caps text-primary border-b-2 border-primary pb-1 font-bold">Live Logs</button>
                  <button className="font-label-caps text-label-caps text-slate-400 hover:text-slate-200 transition-colors pb-1">Pipeline Nodes</button>
                </div>
                <div className="flex items-center gap-3">
                  {isGenerating && (
                    <span className="bg-amber-500/20 text-amber-300 border border-amber-500/30 font-code-sm text-[10px] px-2.5 py-0.5 rounded-full">
                      Stage: {job?.current_stage || 'init'}
                    </span>
                  )}
                  <span className={`font-code-sm text-[10px] flex items-center gap-1 ${
                    isGenerating ? 'text-amber-400 font-bold' : 'text-primary'
                  }`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${isGenerating ? 'bg-amber-400 animate-pulse' : 'bg-primary'}`}></span>
                    {isGenerating ? 'Active Engine...' : 'System Idle'}
                  </span>
                </div>
              </div>
              
              <div className="flex-1 p-4 font-code-sm text-code-sm overflow-y-auto bg-transparent">
                {job ? (
                  <div className="space-y-2">
                    {job.logs?.map((log, i) => (
                      <p key={i} className="text-slate-300">
                        <span className="text-primary font-medium">{new Date(log.timestamp).toLocaleTimeString([], {hour12: false})}</span> 
                        <span className="text-slate-400 font-bold mx-2">[{log.stage}]</span> 
                        <span className={
                          log.status === 'error' ? 'text-red-400 font-bold' 
                          : log.status === 'completed' || log.status === 'success' ? 'text-emerald-400 font-bold' 
                          : 'text-slate-200'
                        }>
                          {log.message}
                        </span>
                      </p>
                    ))}
                    {isGenerating && (
                      <p className="text-slate-400 animate-pulse mt-2">
                        <span className="text-primary font-medium">{new Date().toLocaleTimeString([], {hour12: false})}</span> 
                        <span className="mx-2">...</span>
                        <span className="inline-block w-2 h-4 bg-emerald-400 ml-1 animate-ping"></span>
                      </p>
                    )}
                    <div ref={logsEndRef} />
                  </div>
                ) : (
                  <div className="flex h-full items-center justify-center text-slate-500">
                    <p className="flex items-center gap-2"><span className="material-symbols-outlined text-lg">terminal</span> Awaiting generation task...</p>
                  </div>
                )}
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

