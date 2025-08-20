# User Guide

Welcome to the Spam Detector! This guide will help you get started with using the application to classify emails as spam or legitimate (ham).

## Table of Contents
1. [Getting Started](#getting-started)
2. [Using the Web Interface](#using-the-web-interface)
3. [Understanding Results](#understanding-results)
4. [Managing Email History](#managing-email-history)
5. [Retraining the Model](#retraining-the-model)
6. [Tips and Best Practices](#tips-and-best-practices)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Accessing the Application
Access the Spam Detector through the React TypeScript interface:

- **URL**: `http://localhost:3000`
- **Features**: Modern, feature-rich interface with dark/light theme, real-time search, and advanced filtering

### System Requirements
- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- JavaScript enabled
- Internet connection (for initial setup only)

## Using the Web Interface

### Main Interface Overview

#### React Interface
```
┌─────────────────────────────────────────┐
│ [🌙] Spam Detector           [Settings] │ Header
├─────────────────────────────────────────┤
│                                         │
│ Email Analysis                          │ Main Section
│ ┌─────────────────────────────────────┐ │
│ │ Enter email content here...         │ │
│ │                                     │ │
│ │                                     │ │
│ └─────────────────────────────────────┘ │
│ [Analyze Email] [Clear]                 │
│                                         │
│ Results:                                │
│ • Classification: Ham                   │
│ • Confidence: 85%                       │
│ • Keywords: meeting, tomorrow, project  │
├─────────────────────────────────────────┤
│ Email History                           │ History Section
│ [Search...] [All ▼] [Spam] [Ham]       │
│                                         │
│ Recent Analyses:                        │
│ 📧 "Project update meeting..."  Ham     │
│ 📧 "FREE MONEY NOW!!!"         Spam    │
│ 📧 "Lunch appointment..."       Ham     │
│                                         │
│ [← Previous] Page 1 of 3 [Next →]      │
└─────────────────────────────────────────┘
```

### Analyzing Emails

#### Step 1: Enter Email Content
1. Click in the text area labeled "Enter email content here..."
2. Paste or type the email content you want to analyze
3. The system accepts any text length (recommended: up to 10,000 characters)

#### Step 2: Submit for Analysis
1. Click the **"Analyze Email"** button
2. Watch the progress indicator (React interface only)
3. Results will appear below the input area

#### Step 3: Review Results
The analysis provides:
- **Classification**: Spam or Ham (legitimate email)
- **Confidence Score**: How certain the model is (0-100%)
- **Keywords**: Important words that influenced the decision
- **Threshold**: The decision boundary used (usually 60%)

### Theme Toggle (React Interface Only)
- Click the moon/sun icon in the header to switch between dark and light themes
- Your preference is automatically saved for future visits

## Understanding Results

### Classification Types
- **🔴 Spam**: Unwanted, potentially malicious emails
- **🟢 Ham**: Legitimate, wanted emails

### Confidence Levels
| Confidence | Interpretation |
|------------|----------------|
| 90-100% | Very confident prediction |
| 70-89% | Confident prediction |
| 60-69% | Moderately confident (near threshold) |
| 40-59% | Low confidence |
| 0-39% | Very low confidence |

### Example Results

#### Spam Email Example
```
Input: "CONGRATULATIONS! You've won $1,000,000! 
        Click here to claim your prize NOW!"

Results:
✅ Classification: Spam
✅ Confidence: 94%
✅ Keywords: congratulations, won, million, claim, prize
✅ Explanation: High confidence spam due to typical 
   promotional language and urgency indicators
```

#### Legitimate Email Example
```
Input: "Hi John, can we schedule the project meeting 
        for tomorrow at 2 PM? Let me know if this works."

Results:
✅ Classification: Ham
✅ Confidence: 87%
✅ Keywords: schedule, project, meeting, tomorrow
✅ Explanation: Business communication with specific 
   details and reasonable tone
```

### Common Spam Indicators
The model looks for these patterns:
- **Urgency**: "Act now!", "Limited time!", "Hurry!"
- **Money**: "Free", "Win", "Prize", "$$$", "Cash"
- **Suspicious links**: "Click here", "Verify account"
- **Poor grammar**: Excessive caps, misspellings
- **Generic greetings**: "Dear customer", "Valued member"

### Common Ham Indicators
- **Personal names**: Specific people or companies
- **Business terms**: "Meeting", "project", "deadline"
- **Specific details**: Times, dates, locations
- **Professional language**: Proper grammar and spelling
- **Context-appropriate**: Relevant to normal communication

## Managing Email History

### Viewing History
1. Scroll down to the "Email History" section
2. See all previously analyzed emails with timestamps
3. Each entry shows: email preview, classification, and confidence

### Searching History (React Interface)
1. Use the search box to find specific emails
2. Search works across email content
3. Results update in real-time as you type

### Filtering History (React Interface)
- **All**: Show both spam and ham emails
- **Spam**: Show only spam emails
- **Ham**: Show only legitimate emails

### Pagination
- Navigate through pages using Previous/Next buttons
- Each page shows 10 results by default
- Page information displays current page and total pages

### Export History
Currently, history export is not available through the interface. Contact your administrator for data export options.

## Retraining the Model

### When to Retrain
Consider retraining when:
- You notice frequent misclassifications
- You have new types of spam/ham to teach the model
- Performance degrades over time
- You want to adapt to your specific email patterns

### How to Retrain (Advanced Users)
⚠️ **Note**: Retraining requires technical knowledge and is typically done by administrators.

1. Collect training data in the format:
   ```json
   [
     {"text": "Free money now!", "label": 1},
     {"text": "Meeting at 3pm", "label": 0}
   ]
   ```
   Where: 1 = spam, 0 = ham

2. Use the API endpoint or contact your administrator

### What Happens During Retraining
- The model learns from new examples
- Previous knowledge is preserved
- Classification accuracy may improve
- The process takes 1-5 seconds depending on data size

## Tips and Best Practices

### For Best Results
1. **Use complete emails**: Include subject lines and full content
2. **Clean your text**: Remove excessive formatting or HTML
3. **Check context**: Consider if the email would be spam in your context
4. **Review confidence**: Low confidence results may need human review

### Performance Tips
1. **React Interface**: Use search and filters to find emails quickly
2. **Batch processing**: Analyze similar emails together
3. **Clear cache**: Refresh the page if you encounter issues

### Security Considerations
1. **Sensitive data**: Don't analyze emails with sensitive information
2. **Privacy**: Be aware that analyzed emails are stored locally
3. **False positives**: Always review emails marked as spam
4. **False negatives**: Report spam that wasn't caught

## Troubleshooting

### Common Issues

#### "Failed to analyze email"
**Causes**:
- Server is not running
- Network connection issues
- Email text is empty

**Solutions**:
1. Check that the backend server is running
2. Verify your internet connection
3. Ensure you've entered email content
4. Try refreshing the page

#### "Low confidence results"
**Causes**:
- Email content is ambiguous
- New type of email not in training data
- Email is very short or generic

**Solutions**:
1. Add more context to the email
2. Consider manual review
3. Report for retraining if pattern repeats

#### "Page not loading"
**Causes**:
- JavaScript disabled
- Browser compatibility issues
- Server not accessible

**Solutions**:
1. Enable JavaScript in your browser
2. Use a supported browser version
3. Check server status
4. Clear browser cache

#### "Search not working" (React Interface)
**Causes**:
- JavaScript errors
- Large dataset causing delays
- Browser performance issues

**Solutions**:
1. Refresh the page
2. Clear browser cache
3. Try a different browser
4. Contact administrator if issue persists

### Performance Issues

#### Slow analysis
- **Expected**: 1-3 seconds for normal emails
- **Slow**: 5+ seconds may indicate server issues
- **Solution**: Check server resources or try again later

#### Interface lag
- **React Interface**: May be slower on older devices
- **Solution**: Try refreshing the page or using a different browser

### Getting Help

#### Self-Service
1. Check this user guide
2. Try the troubleshooting steps
3. Refresh the application

#### Contact Support
If issues persist:
1. Note the exact error message
2. Describe what you were trying to do
3. Include browser and operating system information
4. Contact your system administrator

### Frequently Asked Questions

**Q: How accurate is the spam detection?**
A: The model typically achieves 90-95% accuracy on training data. Real-world performance may vary based on your specific email patterns.

**Q: Can I analyze emails in languages other than English?**
A: The current model is primarily trained on English emails. Non-English emails may have lower accuracy.

**Q: Is my email content stored permanently?**
A: Analyzed emails are stored locally for history purposes. They are not sent to external servers.

**Q: Can I delete emails from history?**
A: Currently, deletion is not available through the interface. Contact your administrator for data management.

**Q: Why does the confidence change for the same email?**
A: If the model has been retrained between analyses, confidence scores may vary slightly.

**Q: What features does the React interface offer?**
A: The React interface offers advanced features like themes, real-time search, advanced filtering, pagination, client-side caching, and a responsive mobile-friendly design.

---

For technical support or feature requests, please contact your system administrator or refer to the project documentation.
