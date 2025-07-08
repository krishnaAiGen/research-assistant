'use client';

import { useState } from 'react';
import { Search } from 'lucide-react';

interface SearchFormProps {
  onSearch: (query: string) => void;
  disabled?: boolean;
}

export default function SearchForm({ onSearch, disabled }: SearchFormProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card">
      <div className="flex gap-4">
        <div className="flex-1">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question about research papers..."
            className="w-full input-field text-lg"
            disabled={disabled}
          />
        </div>
        <button
          type="submit"
          disabled={disabled || !query.trim()}
          className="btn-primary flex items-center gap-2"
        >
          <Search size={20} />
          Search
        </button>
      </div>
      
      <div className="mt-4 text-sm text-gray-600">
        <p className="mb-2">Example questions:</p>
        <ul className="list-disc list-inside space-y-1">
          <li>What is velvet bean and what are its benefits?</li>
          <li>How does the attention mechanism work in transformers?</li>
          <li>What are the applications of neural networks in agriculture?</li>
        </ul>
      </div>
    </form>
  );
} 