# 🧓🤝 Silvercare - Elderly Travel & Companion Assistance Platform

> **Safe, dignified, and independent travel for senior citizens.**
> Built with **Python & Flask** based on the **Product Development Canvas**, **Empathy Canvas**, and **Ideation Canvas**.

---

## 🌟 Key Features

1. **Elder & Family Booking Portal**:
   - Booking for self or on behalf of parents/relatives.
   - 1-click destination presets (Central Railway Station, City Hospital, Airport, Bank, Market).
   - Accessibility options (Wheelchair support, Luggage/trolley handling, Ticket guidance, Walking pace assistance).
2. **Verified Companions Directory**:
   - Police-verified badges, background check indicators, user ratings, and specialized mobility skills.
3. **Live Milestone & Reassurance Tracking**:
   - Real-time journey tracking for families (Companion Assigned ➔ Arrived at Pickup ➔ In Transit ➔ Safely Reached).
   - Auto-refreshing status beacon.
4. **Companion Operations Portal**:
   - Companions can view assigned trips and update journey milestones in real-time.
5. **Simplified Post-Task Payment & Reviews**:
   - 1-click UPI / auto-pay or cash handover.
   - Star rating and feedback system to continuously revalidate companion credentials.
6. **Built-in AI Assistant ("SilverBot")**:
   - Floating conversational assistant to guide seniors and non-tech-savvy family members with booking and answering questions.

---

## 🚀 How to Run Locally on Your Computer

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
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🌐 How to Deploy for Free to the Cloud (Render.com)

"Deploying" means putting this app onto a cloud server so anyone (teachers, judges, family members, or users) can open it on their phones with a public link (e.g. `https://silvercare.onrender.com`).

Here is the exact step-by-step procedure:

### Part A: Push your code to GitHub (One-time setup)

1. Open your terminal in `C:\Users\aditi\OneDrive\Desktop\Silvercare` and initialize Git:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Silvercare app"
   ```
2. Go to [github.com](https://github.com) and click **New Repository**.
   - Name it: `silvercare`
   - Set it to **Public**
   - Click **Create repository**
3. Link your local project to your GitHub repo and push:
   ```bash
   git branch -M main
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/silvercare.git
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
🎉 **`https://silvercare-xxxx.onrender.com`**

Whenever you make changes to your code and push to GitHub (`git push`), Render will automatically update your live site!
