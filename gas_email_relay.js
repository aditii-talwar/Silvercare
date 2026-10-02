/**
 * Google Apps Script Email Relay (Port 443 / HTTPS)
 * 
 * Instructions to Deploy:
 * 1. Open https://script.google.com/ and click "New project".
 * 2. Paste this entire code into the editor (replace any default code).
 * 3. Click "Deploy" -> "New deployment".
 * 4. Select type: "Web app".
 * 5. Configuration:
 *    - Description: "Silvercare Email Relay"
 *    - Execute as: "Me (your email)"
 *    - Who has access: "Anyone" (crucial so Flask can send POST requests over HTTPS port 443)
 * 6. Click "Deploy", review/grant permissions for Gmail.
 * 7. Copy the generated Web App URL:
 *    https://script.google.com/macros/s/AKfycb.../exec
 * 8. Set this URL as an environment variable in Flask / Render:
 *    GAS_WEBAPP_URL="https://script.google.com/macros/s/AKfycb.../exec"
 */

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var toEmail = data.to;
    var otp = data.otp;
    var userName = data.name || "Traveller";
    var subject = data.subject || "Your Silvercare Verification Code";

    if (!toEmail || !otp) {
      return ContentService.createTextOutput(JSON.stringify({
        status: "error",
        message: "Missing 'to' or 'otp' parameter"
      })).setMimeType(ContentService.MimeType.JSON);
    }

    var htmlBody = `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px; border: 1px solid #E2D3BA; border-radius: 12px; background: #ffffff;">
        <div style="text-align: center; margin-bottom: 20px;">
          <h2 style="color: #442D1C; margin: 0; letter-spacing: -0.5px;">Silvercare</h2>
          <p style="color: #6B5848; font-size: 14px; margin-top: 4px;">Dignified & Safe Travel for Elders</p>
        </div>
        
        <p style="font-size: 16px; color: #2C1D12;">Hello <strong>${userName}</strong>,</p>
        <p style="font-size: 15px; color: #475569; line-height: 1.5;">
          Thank you for signing up with Silvercare. Please use the One-Time Password (OTP) below to verify your account and activate safe travel companion assistance.
        </p>

        <div style="text-align: center; margin: 30px 0;">
          <div style="display: inline-block; background: #FAF7F2; border: 2px dashed #743014; border-radius: 10px; padding: 14px 32px; font-size: 32px; font-weight: bold; letter-spacing: 6px; color: #743014;">
            ${otp}
          </div>
          <p style="color: #6B5848; font-size: 13px; margin-top: 8px;">This code is valid for 10 minutes. Please do not share it with anyone.</p>
        </div>

        <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 25px 0;">
        <p style="font-size: 12px; color: #94a3b8; text-align: center;">
          If you did not request this OTP, you can safely ignore this email.<br>
          © 2026 Silvercare Travel Assistance.
        </p>
      </div>
    `;

    // MailApp uses Google's standard mail server via HTTPS (Port 443)
    MailApp.sendEmail({
      to: toEmail,
      subject: subject,
      htmlBody: htmlBody
    });

    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      message: "OTP sent successfully to " + toEmail
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  return ContentService.createTextOutput("Silvercare Email Relay Service is Active over HTTPS (Port 443).");
}
