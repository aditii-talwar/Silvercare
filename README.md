# Silvercare - Elderly Travel & Companion Assistance Platform

> **Safe, dignified, and independent travel for senior citizens.**

---

## Key Features & Tech Stack

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
