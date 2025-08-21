import React from 'react';

interface Props {
  children: React.ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <h2>Something went wrong.</h2>
          <details style={{ whiteSpace: 'pre-wrap', textAlign: 'left', marginTop: '20px' }}>
            <summary>Error Details</summary>
            <p><strong>Error:</strong> {this.state.error?.message}</p>
            <p><strong>Stack:</strong> {this.state.error?.stack}</p>
            <p><strong>API URL:</strong> {process.env.REACT_APP_API_URL || 'undefined'}</p>
            <p><strong>Environment:</strong> {process.env.NODE_ENV}</p>
          </details>
          <button onClick={() => window.location.reload()} style={{ marginTop: '20px', padding: '10px 20px' }}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
