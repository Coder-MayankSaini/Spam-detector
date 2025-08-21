import React from 'react';

const TestComponent: React.FC = () => {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>🎉 Spam Wall is Loading!</h1>
      <p>Frontend is working correctly</p>
      <p>API URL: {process.env.REACT_APP_API_URL || 'Not set'}</p>
      <p>Environment: {process.env.NODE_ENV}</p>
      <p>Time: {new Date().toLocaleString()}</p>
    </div>
  );
};

export default TestComponent;
