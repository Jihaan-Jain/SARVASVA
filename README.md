<div align="center">
<h1>SARVASVA (सर्वस्व)</h1>
</div>

# 🌟 FinTech : Multilingual Conversational Loan Advisor

## Overview

This project is a _multilingual conversational AI assistant_ crafted to assist users with:

- _Loan Eligibility Checks_
- _Customized Loan Application Guidance_
- _Financial Literacy Tips_

The assistant is built to simplify the loan process within the Indian banking context by supporting multiple languages and integrating seamless text and voice interactions.

> _Key Highlight:_ The solution leverages _Sarvam AI APIs_ to power robust language translation and speech processing, ensuring an inclusive experience for all users.

---

## Demonstration Video

Watch the full system functionality demonstration: [Watch Video](https://drive.google.com/file/d/1OIGaMOnIItUIccnwX20GQE03ZYlcOoo5/view?usp=drive_link)

---

## ✨ Features

### 1. Loan Eligibility Check

- _Interactive Assessment:_ Gathers essential financial details from users.
- _Dynamic Evaluation:_ Assesses eligibility based on factors like income, credit score, and employment.
- _Clear Outcome:_ Delivers an explicit decision (approved or not) with detailed justifications.

### 2. Loan Application Guidance

- _Step-by-Step Process:_ Provides detailed instructions tailored to the chosen loan type.
- _Document Checklist:_ Offers a comprehensive list of required documents along with specific Indian banking requirements.
- _Expert Recommendations:_ Shares professional advice for optimizing the loan application process.

### 3. Financial Literacy Tips

- _Actionable Advice:_ Delivers practical tips on savings, credit management, and debt handling.
- _Alternative Solutions:_ Suggests other financing options when loan eligibility isn't met.

---

### 4. 🔍 Smart Loan Comparison & Recommendation

_AI-powered multi-bank loan comparison engine_

- _Compare Multiple Banks:_ Analyzes interest rates, processing fees, and terms across lenders
- _Personalized Recommendations:_ Suggests best loan option based on your profile
- _Transparent Display:_ Shows EMIs, total payable amount, and hidden charges upfront
- _Time-Saving:_ Get best rates in seconds instead of visiting multiple banks

### 5. 👤 Credit Twin - Personalized AI Credit Coach

_Your virtual financial twin for credit improvement_

- _Predictive Analysis:_ "Save ₹500/month → Boost eligibility by 12%"
- _Gamified Progress:_ Level up your financial credibility with actionable milestones
- _Future Simulations:_ See how financial decisions impact your loan eligibility
- _Privacy First:_ Credit twin data secured on blockchain ledger

### 6. 👻 AI Ghost Transaction Simulator

_Test your loan before committing_

- _Pre-Commitment Visualization:_ See exact monthly impact before taking loan
- _Interactive Sandbox:_ Test different loan amounts, tenures, and interest rates
- _Cash Flow Forecast:_ Understand how EMI affects your monthly budget
- _Risk Assessment:_ Get warnings about over-borrowing or financial strain

### 7. 🎤 Voice-Based Vernacular Document Reader

_Understand loan documents in your own language_

- _OCR Technology:_ Upload any loan document (PDF, image)
- _Read Aloud:_ AI reads document in your native language using Sarvam TTS
- _Jargon Simplification:_ Explains complex terms like "collateral," "floating rate," "moratorium"
- _Highlight Key Clauses:_ Automatically identifies important sections

## 🤖 Sarvam AI API Integration

The assistant's multilingual capabilities are powered by _Sarvam AI APIs_, which include:

- _Translate Text:_ Seamlessly converts text between multiple Indian languages and English.
- _Speech to Text:_ Transcribes real-time speech into text, supporting interactive voice applications.
- _Speech to Text Translate:_ Translates spoken language in real time while transcribing.
- _Text to Speech:_ Reads loan documents aloud in user's native language.

---

## 📝 AI-Driven Response Structure

The assistant generates responses in a clear, structured format:

### _A. Loan Eligibility Assessment_

- States whether the loan is _approved or not_.
- Provides detailed _reasons_ for the decision.

### _B. If Loan is Eligible:_

1. _Loan Acquisition Process:_
   - Step-by-step guidance for the loan application.
   - Detailed bank procedures and expected timelines.
2. _Required Documentation:_
   - List of necessary documents with preparation tips.
3. _Professional Financial Recommendations:_
   - Strategies for loan optimization and long-term planning.

### _C. If Loan is Not Eligible:_

1. _Reasons for Rejection:_
   - A detailed explanation of the decision.
2. _Actionable Improvement Strategies:_
   - Steps to enhance creditworthiness and financial health.
3. _Alternative Financial Guidance:_
   - Suggestions for alternative financing and future planning.

---

## 💻 Technology Stack

- _Backend:_ Python (Flask)
- _AI Processing:_ OpenAI API (GPT-4)
- _Language & Speech:_ _Sarvam AI APIs_ (Translation, Speech-to-Text, Text-to-Speech)
- _Blockchain:_ Solidity, Web3.js, Polygon Network
- _OCR:_ Tesseract, Google Cloud Vision API
- _Geolocation:_ Google Maps API / Mapbox
- _Database:_ PostgreSQL, MongoDB
- _Caching:_ Redis
- _Frontend:_ Web-based chatbot (React.js, Tailwind CSS) & Telegram Bot
- _Hosting:_ Planned on AWS / Google Cloud / RunAnywhere SDK

---

## 🚀 Project Setup

### 1. Clone the Repository

bash
git clone https://github.com/Jihaan-Jain/Sarvasva.git
cd loan-advisor-ai

### 2. Create a Virtual Environment

bash
python -m venv venv
source venv/bin/activate # On macOS/Linux
venv\Scripts\activate # On Windows

### 3. Install Dependencies

bash
pip install -r requirements.txt

### 4. Set Up Environment Variables

Create a .env file in the root directory with your API keys:

env

# OpenAI

OPENAI_API_KEY=your_openai_api_key

# Sarvam AI

SARVAM_API_KEY=your_sarvam_api_key

# Blockchain (Polygon)

INFURA_PROJECT_ID=your_infura_project_id
PRIVATE_KEY=your_wallet_private_key

### 5. Run the Application

bash
python app.py

### 6. Running the Telegram Bot

While the Telegram bot is available for an alternative interface, the core functionality remains the conversational AI assistant:

bash
cd telebot
python bot.py

```

---

## 📸 Screenshots

<div align="center">
  <img src="https://github.com/user-attachments/assets/a5020efb-d67c-4d0c-a32a-435f7c9161e0" width="600" alt="Home Page">
  <p><strong>Home Page</strong></p>
</div>

<div align="center">
  <img src="https://github.com/user-attachments/assets/6eb29d78-a270-4a06-9616-02935d10b47b" width="600" alt="Loan Eligibility Check">
  <p><strong>Loan Eligibility Check</strong></p>
</div>

<div align="center">
  <img src="https://github.com/user-attachments/assets/16109fd8-0424-40d0-88b7-7d6084771035" width="600" alt="Loan Application Guidance">
  <p><strong>Loan Application Guidance</strong></p>
</div>

---

## 🌍 Supported Languages

*10+ Indian Languages:*
- Hindi (हिन्दी)
- Kannada (ಕನ್ನಡ)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Bengali (বাংলা)
- Marathi (मराठी)
- Gujarati (ગુજરાતી)
- Malayalam (മലയാളം)
- Punjabi (ਪੰਜਾਬੀ)
- Odia (ଓଡ଼ିଆ)

---

## 📊 Impact & Vision

### *Problem We Solve:*
- *₹2+ Trillion* in idle household gold unlocked for productive use
- *400M+ vernacular speakers* gain access to formal credit
- *7-14 days* traditional loan process reduced to *5 minutes*
- *Complex loan documents* made understandable in native languages

### *Target Users:*
- First-time borrowers (18-35 age group)
- Rural users needing vernacular support
- Gold owners seeking liquidity without selling
- Daily wage workers needing micro-loans

---

## 🛣 Roadmap

### *Phase 1: Core Features (Current)*
- ✅ Multilingual chatbot with voice support
- ✅ Loan eligibility assessment
- ✅ Basic gold tokenization demo
- ✅ Document reader prototype

### *Phase 2: Integration (Next 3 Months)*
- 🔄 Partner bank API connections
- 🔄 Live gold price integration
- 🔄 Video KYC verification
- 🔄 Mobile app development

### *Phase 3: Scale (6-12 Months)*
- 📅 Temple partnerships for bulk tokenization
- 📅 Multi-chain blockchain support
- 📅 UPI integration for instant disbursals
- 📅 Pan-India lender network

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

---

## 📄 License

This project is open-source and available under the MIT License.

---

## Conclusion

This project stands as a *user-friendly AI loan advisor* that transforms the loan application process with a focus on inclusivity and ease-of-use. By harnessing the power of *Sarvam AI APIs* and *blockchain technology*, it ensures smooth, multilingual interactions that cater to the diverse needs of users in the Indian banking environment.

*SARVASVA bridges the gap between India's cultural wealth (gold) and modern financial access—all in your mother tongue.*

---

## 🔗 Links

- *Live Website:* [https://sarvasva.onrender.com/](https://sarvasva.onrender.com/)
- *Demo Video:* [Watch on Google Drive](https://drive.google.com/file/d/1OIGaMOnIItUIccnwX20GQE03ZYlcOoo5/view?usp=drive_link)
- *GitHub Repository:* [https://github.com/Jihaan-Jain/Sarvasva](https://github.com/Jihaan-Jain/Sarvasva)

---

<div align="center">

*Made with 💛 by Team S-11 for Hack-Ula 2025*

Your Gold Stays Home. Your Money Comes to You.

</div>
```
