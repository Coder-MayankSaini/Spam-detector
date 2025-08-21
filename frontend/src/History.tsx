import React, { useState, useEffect, useMemo } from 'react';
import { HistoryItem } from './types';
import { apiService } from './apiService';
import { useTheme } from './ThemeContext';

interface HistoryProps {
  refreshTrigger: number;
}

const ITEMS_PER_PAGE = 10;

export const History: React.FC<HistoryProps> = ({ refreshTrigger }) => {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'spam' | 'ham'>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [cache, setCache] = useState<Map<string, HistoryItem[]>>(new Map());
  const { theme } = useTheme();

  const cacheKey = `${filterType}-${searchQuery}`;

  const filteredItems = useMemo(() => {
    if (cache.has(cacheKey)) {
      return cache.get(cacheKey)!;
    }

    let filtered = items;

    // Apply filter
    if (filterType !== 'all') {
      filtered = filtered.filter(item => 
        filterType === 'spam' ? item.is_spam : !item.is_spam
      );
    }

    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(item =>
        item.text.toLowerCase().includes(query)
      );
    }

    // Cache the result
    const newCache = new Map(cache);
    newCache.set(cacheKey, filtered);
    setCache(newCache);

    return filtered;
  }, [items, filterType, searchQuery, cache, cacheKey]);

  const paginatedItems = useMemo(() => {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredItems.slice(startIndex, startIndex + ITEMS_PER_PAGE);
  }, [filteredItems, currentPage]);

  const totalPages = Math.ceil(filteredItems.length / ITEMS_PER_PAGE);

  useEffect(() => {
    const loadHistory = async () => {
      setLoading(true);
      setError(null);
      try {
        const history = await apiService.getHistory();
        setItems(history);
        setCache(new Map()); // Clear cache when new data arrives
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load history');
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, [refreshTrigger]);

  useEffect(() => {
    setCurrentPage(1); // Reset to first page when filters change
  }, [searchQuery, filterType]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFilterType(e.target.value as 'all' | 'spam' | 'ham');
  };

  const formatDate = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return 'Unknown time';
    }
  };

  if (loading) return <div className="loading">Loading history...</div>;
  if (error) return <div className="error-message">Error: {error}</div>;

  return (
    <div className="history-card">
      <div className="history-header">
        <h2>Analysis History</h2>
        <div className="history-controls">
          <input
            type="text"
            placeholder="Search emails..."
            value={searchQuery}
            onChange={handleSearchChange}
            className={`search-input ${theme}`}
          />
          <select
            value={filterType}
            onChange={handleFilterChange}
            className={`filter-select ${theme}`}
          >
            <option value="all">All ({items.length})</option>
            <option value="spam">Spam ({items.filter(i => i.is_spam).length})</option>
            <option value="ham">Ham ({items.filter(i => !i.is_spam).length})</option>
          </select>
        </div>
      </div>

      {filteredItems.length === 0 ? (
        <div className="no-results">
          {searchQuery || filterType !== 'all' 
            ? 'No emails match your criteria' 
            : 'No history yet'}
        </div>
      ) : (
        <>
          <ul className="history-list">
            {paginatedItems.map((item, index) => (
              <li key={`${item.timestamp}-${index}`} className="history-item">
                <div className="item-header">
                  <span className={`badge ${item.is_spam ? 'spam' : 'ham'}`}>
                    {item.is_spam ? 'Spam' : 'Ham'}
                  </span>
                  <small className="timestamp">{formatDate(item.timestamp)}</small>
                </div>
                <div className="item-content">
                  {item.text.length > 150 
                    ? `${item.text.slice(0, 150)}...` 
                    : item.text}
                </div>
              </li>
            ))}
          </ul>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="pagination-btn"
              >
                Previous
              </button>
              <span className="pagination-info">
                Page {currentPage} of {totalPages} ({filteredItems.length} total)
              </span>
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="pagination-btn"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};
