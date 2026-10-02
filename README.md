# Silvercare - Elderly Travel & Companion Assistance Platform

> **Safe, dignified, and independent travel for senior citizens.**
> Built with **Python & Flask** based on the **Product Development Canvas**, **Empathy Canvas**, and **Ideation Canvas**.

---

## Key Features & Indian Tech Stack

1. **Dual Role Authentication & OTP Verification**:
   - Distinct logins for **Traveller / Family** and **Companion**.
   - Sign up with 6-digit OTP verification.
   - **Smart Email Relay**: Dispatches real emails via Google Apps Script over HTTPS (Port 443).
   - **Demo Mode**: Demo emails (e.g. `user@demo.com`) display the OTP on screen in an alert badge for effortless testing & evaluation.
2. **Bhashini Multilingual AI Assistant ("SilverBot")**:
   - Powered by MeitY Bhashini / NLTM architecture.
   - Live language selector supporting 7 Indian languages: English, Hindi (हिन्दी), Gujarati (ગુજરાતી), Marathi (मराठी), Bengali (বাংলা), Tamil (தமிழ்), Telugu (తెలుగు).
   - Instant contextual travel advice & pre-filled booking suggestions.
3. **Mappls (MapmyIndia) Dynamic Distance & Fare Matrix**:
   - Replaced fixed rates with sovereign Indian road distance calculation.
   - Live interactive fare breakdown: Base Fare (₹200 for first 4 km) + ₹18/km extra distance surcharge.
   - Real-time transit duration estimates.
4. **Indian Payment Gateway (Razorpay & NPCI Dynamic UPI QR)**:
   - **NPCI Dynamic UPI QR**: Generates an instant, scannable QR code for Google Pay, PhonePe, Paytm, BHIM, CRED with direct mobile app launching.
   - **Razorpay Checkout**: Full support for Debit/Credit Cards, RuPay, and Indian Netbanking (SBI, HDFC, ICICI, etc.).
   - **Cash Handover**: Physical cash option for traditional senior travelers.
5. **DigiLocker & Aadhaar Verification (India Stack)**:
   - Companions are verified via UIDAI Aadhaar e-KYC and State Police Clearance Certificates.
   - Clickable DigiLocker credential inspector modal for complete family reassurance.
6. **Fast2SMS / MSG91 Indian SMS Gateway**:
   - Dispatches transactional SMS to 10-digit Indian numbers (`+91`) for booking confirmations and payment receipts.
   - Broadcasts instant 112 SOS Emergency alert SMS with live GPS coordinates to family contacts.
7. **Elder & Family Booking Portal**:
   - Booking for self or on behalf of parents/relatives with 1-click presets.
   - Accessibility options (Wheelchair support, Luggage/trolley handling, Ticket guidance, Walking pace).
8. **Live Milestone & Reassurance Tracking**:
   - Real-time journey tracking for families (Companion Assigned -> Arrived at Pickup -> In Transit -> Safely Reached) with auto-refreshing beacon.
9. **Companion Operations Portal**:
   - Companions can log in to view assigned trips and advance journey milestones.

---

## How to Run Locally on Your Computer

### Step 1: Open Terminal / Command Prompt
Navigate to the project directory:
```bash
cd "C:\Users\aditi\OneDrive\Desktop\Silvercare"
```

### Step 2: Run the Application
```bash
python app.py
```

### Step 3: Open in Browser
Open your browser and visit:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## How to Deploy for Free to the Cloud (Render.com)

"Deploying" means putting this app onto a cloud server so anyone (teachers, judges, family members, or users) can open it on their phones with a public link (e.g. `https://silvercare.onrender.com`).

Here is the exact step-by-step procedure:

### Part A: Push your code to GitHub (One-time setup)

1. Open your terminal in `C:\Users\aditi\OneDrive\Desktop\Silvercare` and push:
   ```bash
   git push -u origin main
   ```

---

### Part B: Deploy on Render.com (Takes 3 minutes)

1. Go to [render.com](https://render.com) and click **Sign Up** (or Log In) using your **GitHub** account.
2. Once logged in, click the **"New +"** button at the top right and select **"Web Service"**.
3. Choose **"Build and deploy from a Git repository"** and select your `silvercare` repository.
4. Fill in the simple settings:
   - **Name:** `silvercare` (or any unique name you like)
   - **Region:** Any close region (e.g., Singapore or Frankfurt)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** Select **Free**
5. Click **"Deploy Web Service"** at the bottom!

Render will automatically build your app and give you a free live URL:
**`https://silvercare-xxxx.onrender.com`**

Whenever you make changes to your code and push to GitHub (`git push`), Render will automatically update your live site!

---

## Google Apps Script Email Relay (Port 443 / HTTPS)

To deliver real OTP emails without being blocked by cloud providers on SMTP ports (25, 465, 587):
1. Open [script.google.com](https://script.google.com/) and create a new project.
2. Copy & paste the code from [gas_email_relay.js](file:///C:/Users/aditi/OneDrive/Desktop/Silvercare/gas_email_relay.js).
3. Click **Deploy -> New deployment -> Web app**.
   - Execute as: **Me**
   - Who has access: **Anyone**
4. Copy the Web App URL (`https://script.google.com/macros/s/.../exec`).
5. Set `GAS_WEBAPP_URL` in your environment (in Render's Environment Variables or your `.env`):
   ```bash
   GAS_WEBAPP_URL="https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec"
   ```

*Note: If no URL is set, or if an email containing `demo` or `test` is used (e.g. `user@demo.com`), Silvercare automatically displays the OTP directly on screen for testing!*

---

## Bhashini Multilingual AI (MeitY)

SilverBot is configured to work with the official Bhashini Dhruva / ULCA API.
- **Offline / Default**: Functions out-of-the-box in 7 languages (Hindi, Gujarati, Marathi, Bengali, Tamil, Telugu, English) using native domain dictionaries.
- **Live MeitY API**: Set the following environment variables to enable live Bhashini pipeline inference:
  ```bash
  BHASHINI_USER_ID="your_user_id"
  BHASHINI_API_KEY="your_api_key"
  BHASHINI_PIPELINE_ID="your_pipeline_id"
  ```
