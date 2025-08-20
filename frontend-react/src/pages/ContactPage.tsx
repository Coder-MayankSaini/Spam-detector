import React, { useState } from 'react';
import { apiService } from '../apiService';
import './ContactPage.css';

interface ContactForm {
  name: string;
  email: string;
  subject: string;
  message: string;
}

export const ContactPage: React.FC = () => {
  const [formData, setFormData] = useState<ContactForm>({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    // Validate form
    if (!formData.name || !formData.email || !formData.subject || !formData.message) {
      setError('Please fill in all fields');
      setIsSubmitting(false);
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      setIsSubmitting(false);
      return;
    }

    try {
      // Send form data to backend API
      await apiService.submitContactForm(formData);
      
      setIsSubmitted(true);
      setFormData({ name: '', email: '', subject: '', message: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const contactMethods = [
    {
      icon: '📧',
      title: 'Email Support',
      value: 'support@spamdetector.ai',
      description: 'Get help with technical issues and account questions'
    },
    {
      icon: '💬',
      title: 'Live Chat',
      value: 'Available 24/7',
      description: 'Chat with our support team in real-time'
    },
    {
      icon: '📞',
      title: 'Phone Support',
      value: '+1 (555) 123-4567',
      description: 'Speak directly with our experts'
    },
    {
      icon: '📍',
      title: 'Office Location',
      value: 'San Francisco, CA',
      description: 'Visit our headquarters for in-person support'
    }
  ];

  const faqs = [
    {
      question: 'How accurate is the spam detection?',
      answer: 'Our AI models achieve over 99.9% accuracy in detecting spam and phishing emails through advanced machine learning algorithms.'
    },
    {
      question: 'Is my data secure and private?',
      answer: 'Yes, we use end-to-end encryption and never store your email content. All analysis happens in real-time with immediate deletion.'
    },
    {
      question: 'Can I integrate this with my email client?',
      answer: 'We offer API integration and plugins for popular email clients. Contact our support team for integration assistance.'
    },
    {
      question: 'What file types are supported for image analysis?',
      answer: 'We support JPG, PNG, GIF, PDF, and most common image formats with our OCR technology.'
    }
  ];

  if (isSubmitted) {
    return (
      <div className="contact-page">
        <div className="contact-success">
          <div className="success-content">
            <div className="success-icon">✅</div>
            <h2>Thank You!</h2>
            <p>Your message has been sent successfully. We'll get back to you within 24 hours.</p>
            <button 
              className="back-button"
              onClick={() => setIsSubmitted(false)}
            >
              Send Another Message
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="contact-page">
      <div className="contact-hero">
        <div className="contact-hero-content">
          <h1>📞 Contact Us</h1>
          <p>Get in touch with our team - we're here to help!</p>
        </div>
      </div>

      <div className="contact-content">
        <div className="contact-grid">
          <div className="contact-form-section">
            <div className="form-header">
              <h2>Send us a Message</h2>
              <p>Have a question or need support? Fill out the form below and we'll respond promptly.</p>
            </div>

            <form onSubmit={handleSubmit} className="contact-form">
              {error && <div className="error-message">{error}</div>}
              
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="name">Full Name *</label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    disabled={isSubmitting}
                    placeholder="Enter your full name"
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="email">Email Address *</label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                    disabled={isSubmitting}
                    placeholder="Enter your email address"
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="subject">Subject *</label>
                <select
                  id="subject"
                  name="subject"
                  value={formData.subject}
                  onChange={handleInputChange}
                  required
                  disabled={isSubmitting}
                >
                  <option value="">Select a subject</option>
                  <option value="technical-support">Technical Support</option>
                  <option value="account-help">Account Help</option>
                  <option value="billing">Billing Question</option>
                  <option value="feature-request">Feature Request</option>
                  <option value="partnership">Partnership Inquiry</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="message">Message *</label>
                <textarea
                  id="message"
                  name="message"
                  value={formData.message}
                  onChange={handleInputChange}
                  required
                  disabled={isSubmitting}
                  placeholder="Please describe your question or issue in detail..."
                  rows={6}
                />
              </div>

              <button 
                type="submit" 
                className="submit-button"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <span className="spinner"></span>
                    Sending...
                  </>
                ) : (
                  'Send Message'
                )}
              </button>
            </form>
          </div>

          <div className="contact-info-section">
            <div className="contact-methods">
              <h3>Other Ways to Reach Us</h3>
              {contactMethods.map((method, index) => (
                <div key={index} className="contact-method">
                  <div className="method-icon">{method.icon}</div>
                  <div className="method-details">
                    <h4>{method.title}</h4>
                    <p className="method-value">{method.value}</p>
                    <p className="method-description">{method.description}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="business-hours">
              <h3>Business Hours</h3>
              <div className="hours-list">
                <div className="hours-item">
                  <span>Monday - Friday</span>
                  <span>9:00 AM - 6:00 PM PST</span>
                </div>
                <div className="hours-item">
                  <span>Saturday</span>
                  <span>10:00 AM - 4:00 PM PST</span>
                </div>
                <div className="hours-item">
                  <span>Sunday</span>
                  <span>Closed</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="faq-section">
          <h2>Frequently Asked Questions</h2>
          <div className="faq-grid">
            {faqs.map((faq, index) => (
              <div key={index} className="faq-item">
                <h4>{faq.question}</h4>
                <p>{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
