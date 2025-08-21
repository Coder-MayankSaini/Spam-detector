import React from 'react';
import TestComponent from './TestComponent';

const App: React.FC = () => {
  console.log('App component rendering');
  console.log('Environment variables:', {
    REACT_APP_API_URL: process.env.REACT_APP_API_URL,
    NODE_ENV: process.env.NODE_ENV
  });

  return (
    <div>
      <TestComponent />
    </div>
  );
};

export default App;
