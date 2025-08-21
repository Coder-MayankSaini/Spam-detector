import React, { useState } from 'react';
import { ThemeProvider, useTheme } from './ThemeContext';
import { AuthProvider, useAuth } from './AuthContext';
import { AuthComponent } from './AuthComponent';
import { Navigation } from './components/Navigation';
import { HomePage } from './pages/HomePage';
import { AboutPage } from './pages/AboutPage';
import { ContactPage } from './pages/ContactPage';
import { PrivacyPage } from './pages/PrivacyPage';
import './App.css';

type AppPage = 'home' | 'about' | 'contact' | 'privacy';

const AppContent: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<AppPage>('home');
  const { theme, toggleTheme } = useTheme();
  const { isAuthenticated, isLoading, user, logout } = useAuth();

  const handlePageChange = (page: string) => {
    setCurrentPage(page as AppPage);
  };

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'home':
        return <HomePage />;
      case 'about':
        return <AboutPage />;
      case 'contact':
        return <ContactPage />;
      case 'privacy':
        return <PrivacyPage />;
      default:
        return <HomePage />;
    }
  };

  if (isLoading) {
    return (
      <div className={`app ${theme}`}>
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className={`app ${theme}`}>
        <AuthComponent />
      </div>
    );
  }

  return (
    <div className={`app ${theme}`}>
      <Navigation
        currentPage={currentPage}
        onPageChange={handlePageChange}
        user={user}
        onLogout={logout}
        onToggleTheme={toggleTheme}
        theme={theme}
      />
      
      <main className="app-main">
        {renderCurrentPage()}
      </main>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </AuthProvider>
  );
};

export default App;
