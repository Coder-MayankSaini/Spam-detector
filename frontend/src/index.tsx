import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import AppTest from './AppTest';
import { ErrorBoundary } from './ErrorBoundary';

console.log('Index.tsx loading');

const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  
  // Use test component temporarily to debug white screen
  const isDebugMode = window.location.search.includes('debug=true');
  console.log('Debug mode:', isDebugMode);
  
  root.render(
    <ErrorBoundary>
      {isDebugMode ? <AppTest /> : <App />}
    </ErrorBoundary>
  );
} else {
  console.error('Root container not found');
}
