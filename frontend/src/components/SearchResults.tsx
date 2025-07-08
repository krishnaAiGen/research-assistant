'use client';

import { ChatResponse } from '@/types';
import { ExternalLink, FileText } from 'lucide-react';

interface SearchResultsProps {
  result: ChatResponse;
}

export default function SearchResults({ result }: SearchResultsProps) {
  return (
    <div className="mt-8 space-y-6">
      {/* AI Generated Answer */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4 text-gray-900">
          AI Answer
        </h2>
        <div className="prose max-w-none">
          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
            {result.answer}
          </p>
        </div>
      </div>

      {/* Sources */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4 text-gray-900 flex items-center gap-2">
          <FileText size={20} />
          Sources ({result.sources.length})
        </h3>
        <div className="space-y-4">
          {result.sources.map((source, index) => (
            <div key={source.id} className="border-l-4 border-primary-500 pl-4 py-2">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 mb-1">
                    {source.section_heading}
                  </h4>
                  <p className="text-sm text-gray-600 mb-2">
                    {source.journal} ({source.publish_year}) • Score: {source.score.toFixed(3)}
                  </p>
                  <p className="text-sm text-gray-700 line-clamp-3">
                    {source.text.substring(0, 200)}...
                  </p>
                </div>
                <a
                  href={source.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="ml-4 text-primary-600 hover:text-primary-700 flex items-center gap-1 text-sm"
                >
                  <ExternalLink size={16} />
                  View
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 