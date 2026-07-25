import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

interface ChatMarkdownProps {
  content: string;
}

export const ChatMarkdown: React.FC<ChatMarkdownProps> = ({ content }) => {
  return (
    <div className="prose prose-sm md:prose-base max-w-none text-gray-800 leading-relaxed font-sans">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          h1: ({ node, ...props }) => <h1 className="text-xl font-bold text-gray-950 mt-4 mb-2 border-b border-[#6ED987]/40 pb-1" {...props} />,
          h2: ({ node, ...props }) => <h2 className="text-lg font-bold text-gray-950 mt-4 mb-2 border-b border-[#6ED987]/40 pb-1" {...props} />,
          h3: ({ node, ...props }) => <h3 className="text-base font-bold text-[#1BC237] mt-3 mb-1.5" {...props} />,
          strong: ({ node, ...props }) => <strong className="font-semibold text-gray-950 bg-[#d1f4d9]/70 px-1.5 py-0.5 rounded border border-[#6ED987]/60 shadow-2xs" {...props} />,
          p: ({ node, ...props }) => <p className="mb-3 last:mb-0 leading-relaxed text-gray-800" {...props} />,
          ul: ({ node, ...props }) => <ul className="list-disc list-outside ml-5 mb-3 space-y-1.5 text-gray-800" {...props} />,
          ol: ({ node, ...props }) => <ol className="list-decimal list-outside ml-5 mb-3 space-y-1.5 text-gray-800" {...props} />,
          li: ({ node, ...props }) => <li className="leading-relaxed pl-1" {...props} />,
          blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-[#1BC237] bg-[#d1f4d9]/40 px-4 py-2.5 italic text-gray-800 my-3 rounded-r-lg shadow-2xs" {...props} />,
          code: ({ inline, className, children, ...props }: any) => {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <div className="my-3 rounded-xl overflow-hidden border border-gray-700 shadow-md">
                <div className="bg-gray-800 text-gray-300 px-3 py-1.5 text-xs font-mono flex justify-between items-center border-b border-gray-700">
                  <span className="font-semibold text-[#6ED987]">{match[1]}</span>
                  <span className="text-[10px] text-gray-400">code</span>
                </div>
                <pre className="bg-gray-900 text-gray-100 p-3.5 overflow-x-auto text-xs md:text-sm font-mono leading-relaxed">
                  <code className={className} {...props}>
                    {children}
                  </code>
                </pre>
              </div>
            ) : (
              <code className="bg-[#d1f4d9]/70 text-[#1BC237] px-1.5 py-0.5 rounded text-xs font-mono border border-[#6ED987]/50 font-bold" {...props}>
                {children}
              </code>
            );
          },
          table: ({ node, ...props }) => (
            <div className="my-4 overflow-x-auto rounded-xl border border-[#6ED987]/50 shadow-sm bg-white/90">
              <table className="w-full text-left border-collapse text-sm" {...props} />
            </div>
          ),
          thead: ({ node, ...props }) => <thead className="bg-[#d1f4d9]/60 border-b border-[#6ED987]/50 text-gray-950 font-bold" {...props} />,
          tbody: ({ node, ...props }) => <tbody className="divide-y divide-[#6ED987]/20 bg-white/80" {...props} />,
          tr: ({ node, ...props }) => <tr className="hover:bg-[#d1f4d9]/30 transition-colors" {...props} />,
          th: ({ node, ...props }) => <th className="px-4 py-3 font-bold text-gray-950 border-r last:border-r-0 border-[#6ED987]/30 bg-[#d1f4d9]/40" {...props} />,
          td: ({ node, ...props }) => <td className="px-4 py-2.5 text-gray-800 border-r last:border-r-0 border-[#6ED987]/20" {...props} />,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};
