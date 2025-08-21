import React from 'react';
import './AboutPage.css';

export const AboutPage: React.FC = () => {
  return (
    <div className="about-page">
      <div className="about-hero">
        <div className="about-hero-content">
          <h1>🛡️ About SpamWall</h1>
          <p className="hero-subtitle">Empowering users with AI-driven email security</p>
        </div>
      </div>

      <div className="about-content">
        <section className="about-section">
          <div className="section-header">
            <h2>🚀 Our Mission</h2>
          </div>
          <div className="section-content">
            <p>
              At SpamWall, we're on a mission to protect your digital communication from unwanted and malicious content. 
              Our advanced AI-powered platform combines cutting-edge machine learning with intelligent text and image analysis 
              to provide comprehensive email security solutions.
            </p>
            <p>
              We believe that everyone deserves a clean, secure inbox. That's why we've developed sophisticated algorithms 
              that can detect spam, phishing attempts, and malicious content with remarkable accuracy, giving you peace of mind 
              in your daily digital interactions.
            </p>
          </div>
        </section>

        <section className="about-section">
          <div className="section-header">
            <h2>🤖 Our Technology</h2>
          </div>
          <div className="section-content">
            <div className="tech-grid">
              <div className="tech-item">
                <div className="tech-icon">🧠</div>
                <h3>Machine Learning</h3>
                <p>Advanced ML algorithms trained on millions of email samples to identify patterns and detect threats with high precision.</p>
              </div>
              <div className="tech-item">
                <div className="tech-icon">📝</div>
                <h3>Text Analysis</h3>
                <p>Natural language processing techniques that analyze email content, headers, and metadata for suspicious patterns.</p>
              </div>
              <div className="tech-item">
                <div className="tech-icon">👁️</div>
                <h3>Image OCR</h3>
                <p>Optical character recognition technology that can detect spam content hidden within images and attachments.</p>
              </div>
              <div className="tech-item">
                <div className="tech-icon">⚡</div>
                <h3>Real-time Processing</h3>
                <p>Lightning-fast analysis that provides instant results without compromising on accuracy or security.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="about-section">
          <div className="section-header">
            <h2>🎯 Key Features</h2>
          </div>
          <div className="section-content">
            <div className="features-list">
              <div className="feature-row">
                <div className="feature-icon">🔍</div>
                <div className="feature-details">
                  <h4>Comprehensive Analysis</h4>
                  <p>Both text and image analysis capabilities for complete email security coverage.</p>
                </div>
              </div>
              <div className="feature-row">
                <div className="feature-icon">📊</div>
                <div className="feature-details">
                  <h4>Detailed Reports</h4>
                  <p>In-depth analysis results with confidence scores and threat categorization.</p>
                </div>
              </div>
              <div className="feature-row">
                <div className="feature-icon">📱</div>
                <div className="feature-details">
                  <h4>User-Friendly Interface</h4>
                  <p>Clean, intuitive design that makes email security accessible to everyone.</p>
                </div>
              </div>
              <div className="feature-row">
                <div className="feature-icon">🔒</div>
                <div className="feature-details">
                  <h4>Privacy Focused</h4>
                  <p>Your data stays private with secure processing and user-specific data isolation.</p>
                </div>
              </div>
              <div className="feature-row">
                <div className="feature-icon">📈</div>
                <div className="feature-details">
                  <h4>Continuous Learning</h4>
                  <p>AI models that adapt and improve over time to stay ahead of emerging threats.</p>
                </div>
              </div>
              <div className="feature-row">
                <div className="feature-icon">🌐</div>
                <div className="feature-details">
                  <h4>Cross-Platform</h4>
                  <p>Works across all devices and platforms for consistent protection everywhere.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="about-section">
          <div className="section-header">
            <h2>👥 Our Team</h2>
          </div>
          <div className="section-content">
            <p>
              Our team consists of passionate cybersecurity experts, machine learning engineers, and user experience designers 
              who are dedicated to creating the most effective and user-friendly spam detection solution available.
            </p>
            <p>
              We combine deep technical expertise with a user-first approach, ensuring that our platform not only delivers 
              superior protection but also provides an exceptional user experience.
            </p>
          </div>
        </section>

        <section className="about-section cta-section">
          <div className="section-header">
            <h2>🌟 Join Our Mission</h2>
          </div>
          <div className="section-content">
            <p>
              Ready to experience the future of email security? Join thousands of users who trust SpamWall to keep 
              their inboxes clean and secure.
            </p>
            <div className="cta-stats">
              <div className="stat-item">
                <div className="stat-number">99.9%</div>
                <div className="stat-label">Accuracy Rate</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">10M+</div>
                <div className="stat-label">Emails Analyzed</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">50K+</div>
                <div className="stat-label">Active Users</div>
              </div>
              <div className="stat-item">
                <div className="stat-number">24/7</div>
                <div className="stat-label">Protection</div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};
