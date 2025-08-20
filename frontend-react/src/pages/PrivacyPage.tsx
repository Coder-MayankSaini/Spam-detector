import React from 'react';
import './PrivacyPage.css';

export const PrivacyPage: React.FC = () => {
  return (
    <div className="privacy-page">
      <div className="privacy-hero">
        <div className="privacy-hero-content">
          <h1>🔒 Privacy Policy</h1>
          <p className="hero-subtitle">Your privacy is our priority</p>
          <div className="last-updated">Last updated: August 20, 2025</div>
        </div>
      </div>

      <div className="privacy-content">
        <div className="privacy-nav">
          <h3>Quick Navigation</h3>
          <ul>
            <li><a href="#information-collection">Information We Collect</a></li>
            <li><a href="#information-use">How We Use Information</a></li>
            <li><a href="#data-protection">Data Protection</a></li>
            <li><a href="#data-sharing">Information Sharing</a></li>
            <li><a href="#cookies">Cookies & Tracking</a></li>
            <li><a href="#user-rights">Your Rights</a></li>
            <li><a href="#data-retention">Data Retention</a></li>
            <li><a href="#security">Security Measures</a></li>
            <li><a href="#children">Children's Privacy</a></li>
            <li><a href="#changes">Policy Changes</a></li>
            <li><a href="#contact">Contact Information</a></li>
          </ul>
        </div>

        <div className="privacy-main">
          <section className="privacy-section introduction">
            <div className="section-content">
              <p className="intro-text">
                At Spam Detector, we are committed to protecting your privacy and ensuring the security of your personal information. 
                This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our AI-powered 
                spam detection service. Please read this policy carefully to understand our views and practices regarding your personal data.
              </p>
            </div>
          </section>

          <section id="information-collection" className="privacy-section">
            <h2>📋 Information We Collect</h2>
            <div className="section-content">
              <div className="info-category">
                <h3>Personal Information</h3>
                <ul>
                  <li><strong>Account Information:</strong> Email address, password (encrypted), and profile preferences</li>
                  <li><strong>Contact Information:</strong> Name, email address when you contact support</li>
                  <li><strong>Communication Preferences:</strong> Notification settings and language preferences</li>
                </ul>
              </div>

              <div className="info-category">
                <h3>Usage Information</h3>
                <ul>
                  <li><strong>Analysis Data:</strong> Email content and images submitted for spam detection (processed in real-time and not stored)</li>
                  <li><strong>Service Usage:</strong> Feature usage, analysis frequency, and performance metrics</li>
                  <li><strong>Technical Data:</strong> IP address, browser type, device information, and operating system</li>
                </ul>
              </div>

              <div className="info-category">
                <h3>Automatically Collected Information</h3>
                <ul>
                  <li><strong>Log Data:</strong> Server logs, error reports, and system diagnostics</li>
                  <li><strong>Analytics Data:</strong> User interactions, feature usage patterns, and performance metrics</li>
                  <li><strong>Cookies & Tracking:</strong> Session cookies, authentication tokens, and preference cookies</li>
                </ul>
              </div>
            </div>
          </section>

          <section id="information-use" className="privacy-section">
            <h2>🎯 How We Use Your Information</h2>
            <div className="section-content">
              <div className="use-category">
                <h3>Service Provision</h3>
                <ul>
                  <li>Provide and maintain our spam detection services</li>
                  <li>Process and analyze email content for spam detection</li>
                  <li>Personalize your user experience and service recommendations</li>
                  <li>Maintain and improve service performance and accuracy</li>
                </ul>
              </div>

              <div className="use-category">
                <h3>Communication</h3>
                <ul>
                  <li>Send important service updates and security notifications</li>
                  <li>Respond to your inquiries and provide customer support</li>
                  <li>Send marketing communications (with your consent)</li>
                  <li>Conduct user surveys and feedback collection</li>
                </ul>
              </div>

              <div className="use-category">
                <h3>Legal & Security</h3>
                <ul>
                  <li>Comply with legal obligations and regulatory requirements</li>
                  <li>Protect against fraud, abuse, and security threats</li>
                  <li>Enforce our terms of service and user agreements</li>
                  <li>Resolve disputes and investigate violations</li>
                </ul>
              </div>
            </div>
          </section>

          <section id="data-protection" className="privacy-section">
            <h2>🛡️ Data Protection Measures</h2>
            <div className="section-content">
              <div className="protection-grid">
                <div className="protection-item">
                  <div className="protection-icon">🔐</div>
                  <h4>End-to-End Encryption</h4>
                  <p>All data transmissions are encrypted using industry-standard TLS protocols</p>
                </div>
                <div className="protection-item">
                  <div className="protection-icon">🗃️</div>
                  <h4>Minimal Data Storage</h4>
                  <p>Email content is processed in real-time and immediately deleted after analysis</p>
                </div>
                <div className="protection-item">
                  <div className="protection-icon">🔒</div>
                  <h4>Access Controls</h4>
                  <p>Strict access controls and authentication for all system components</p>
                </div>
                <div className="protection-item">
                  <div className="protection-icon">🏢</div>
                  <h4>Secure Infrastructure</h4>
                  <p>Data centers with physical security and 24/7 monitoring</p>
                </div>
              </div>
            </div>
          </section>

          <section id="data-sharing" className="privacy-section">
            <h2>🤝 Information Sharing</h2>
            <div className="section-content">
              <p><strong>We do not sell, trade, or rent your personal information to third parties.</strong> We may share your information only in the following limited circumstances:</p>
              
              <div className="sharing-list">
                <div className="sharing-item">
                  <h4>🔧 Service Providers</h4>
                  <p>Third-party vendors who assist in providing our services (cloud hosting, analytics) under strict confidentiality agreements</p>
                </div>
                <div className="sharing-item">
                  <h4>⚖️ Legal Requirements</h4>
                  <p>When required by law, court order, or to protect our rights and the safety of our users</p>
                </div>
                <div className="sharing-item">
                  <h4>🏢 Business Transfers</h4>
                  <p>In connection with a merger, acquisition, or sale of assets, with proper notice to users</p>
                </div>
                <div className="sharing-item">
                  <h4>👤 With Your Consent</h4>
                  <p>When you explicitly consent to sharing your information for specific purposes</p>
                </div>
              </div>
            </div>
          </section>

          <section id="cookies" className="privacy-section">
            <h2>🍪 Cookies & Tracking Technologies</h2>
            <div className="section-content">
              <p>We use cookies and similar technologies to enhance your experience:</p>
              
              <div className="cookie-types">
                <div className="cookie-type">
                  <h4>Essential Cookies</h4>
                  <p>Required for basic site functionality, authentication, and security</p>
                </div>
                <div className="cookie-type">
                  <h4>Performance Cookies</h4>
                  <p>Help us understand how users interact with our service to improve performance</p>
                </div>
                <div className="cookie-type">
                  <h4>Preference Cookies</h4>
                  <p>Remember your settings and preferences for a personalized experience</p>
                </div>
              </div>
            </div>
          </section>

          <section id="user-rights" className="privacy-section">
            <h2>👤 Your Rights</h2>
            <div className="section-content">
              <p>You have the following rights regarding your personal information:</p>
              
              <div className="rights-grid">
                <div className="right-item">
                  <div className="right-icon">👁️</div>
                  <h4>Right to Access</h4>
                  <p>Request copies of your personal data we hold</p>
                </div>
                <div className="right-item">
                  <div className="right-icon">✏️</div>
                  <h4>Right to Rectification</h4>
                  <p>Request correction of inaccurate or incomplete data</p>
                </div>
                <div className="right-item">
                  <div className="right-icon">🗑️</div>
                  <h4>Right to Erasure</h4>
                  <p>Request deletion of your personal data</p>
                </div>
                <div className="right-item">
                  <div className="right-icon">⏸️</div>
                  <h4>Right to Restrict</h4>
                  <p>Request limitation of processing your data</p>
                </div>
                <div className="right-item">
                  <div className="right-icon">📦</div>
                  <h4>Data Portability</h4>
                  <p>Request your data in a portable format</p>
                </div>
                <div className="right-item">
                  <div className="right-icon">❌</div>
                  <h4>Right to Object</h4>
                  <p>Object to processing for marketing purposes</p>
                </div>
              </div>
            </div>
          </section>

          <section id="data-retention" className="privacy-section">
            <h2>📅 Data Retention</h2>
            <div className="section-content">
              <div className="retention-info">
                <h4>Account Information</h4>
                <p>Retained for the duration of your account plus 30 days after deletion</p>
              </div>
              <div className="retention-info">
                <h4>Email Analysis Data</h4>
                <p>Not stored - processed in real-time and immediately discarded</p>
              </div>
              <div className="retention-info">
                <h4>Usage Analytics</h4>
                <p>Aggregated and anonymized data retained for service improvement (2 years maximum)</p>
              </div>
              <div className="retention-info">
                <h4>Support Communications</h4>
                <p>Retained for 3 years to provide ongoing support and resolve issues</p>
              </div>
            </div>
          </section>

          <section id="security" className="privacy-section">
            <h2>🔐 Security Measures</h2>
            <div className="section-content">
              <p>We implement comprehensive security measures to protect your data:</p>
              
              <div className="security-measures">
                <div className="security-item">✅ Industry-standard encryption for data in transit and at rest</div>
                <div className="security-item">✅ Regular security audits and penetration testing</div>
                <div className="security-item">✅ Multi-factor authentication for administrative access</div>
                <div className="security-item">✅ Continuous monitoring for security threats</div>
                <div className="security-item">✅ Employee security training and background checks</div>
                <div className="security-item">✅ Incident response procedures and breach notification protocols</div>
              </div>
            </div>
          </section>

          <section id="children" className="privacy-section">
            <h2>👶 Children's Privacy</h2>
            <div className="section-content">
              <p>
                Our service is not intended for children under 13 years of age. We do not knowingly collect personal 
                information from children under 13. If you are a parent or guardian and believe your child has provided 
                us with personal information, please contact us immediately so we can delete such information.
              </p>
            </div>
          </section>

          <section id="changes" className="privacy-section">
            <h2>📝 Policy Changes</h2>
            <div className="section-content">
              <p>
                We may update this Privacy Policy from time to time. We will notify you of any changes by posting the 
                new Privacy Policy on this page and updating the "Last Updated" date. We encourage you to review this 
                Privacy Policy periodically for any changes.
              </p>
            </div>
          </section>

          <section id="contact" className="privacy-section">
            <h2>📞 Contact Information</h2>
            <div className="section-content">
              <p>If you have any questions about this Privacy Policy or our data practices, please contact us:</p>
              
              <div className="contact-details">
                <div className="contact-method">
                  <strong>Email:</strong> privacy@spamdetector.ai
                </div>
                <div className="contact-method">
                  <strong>Address:</strong> 123 Privacy Street, San Francisco, CA 94102
                </div>
                <div className="contact-method">
                  <strong>Phone:</strong> +1 (555) 123-4567
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};
