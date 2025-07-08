'use client';

import { useState } from 'react';
import SearchForm from '@/components/SearchForm';
import SearchResults from '@/components/SearchResults';
import LoadingSpinner from '@/components/LoadingSpinner';
import { ChatResponse } from '@/types';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error('Failed to get answer');
      }

      const data: ChatResponse = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <SearchForm onSearch={handleSearch} disabled={isLoading} />
      
      {isLoading && (
        <div className="mt-8 text-center">
          <LoadingSpinner />
          <p className="mt-4 text-gray-600">
            Searching research papers and generating answer...
          </p>
        </div>
      )}

      {error && (
        <div className="mt-8 card bg-red-50 border-red-200">
          <div className="text-red-800">
            <h3 className="font-semibold mb-2">Error</h3>
            <p>{error}</p>
          </div>
        </div>
      )}

      {result && !isLoading && (
        <SearchResults result={result} />
      )}
    </div>
  );
} 