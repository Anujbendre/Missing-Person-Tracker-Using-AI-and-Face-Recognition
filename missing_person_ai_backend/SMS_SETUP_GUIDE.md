# SMS Notification Setup Guide

## 📱 Overview
Your Missing Person AI System now sends SMS notifications when police officers or citizens register successfully!

## 🔧 Setup Options

### Option 1: Testing Mode (No Configuration Required)
The system will work immediately in **simulation mode**. SMS messages will be printed to the console instead of being sent to your phone. This is perfect for testing!

### Option 2: Real SMS with Twilio (Recommended for Production)

Follow these steps to send actual SMS messages to mobile phones:

#### Step 1: Create a Twilio Account
1. Go to [https://www.twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Sign up for a **free trial account**
3. Verify your email and phone number

#### Step 2: Get Your Credentials
1. Log in to your Twilio console: [https://www.twilio.com/console](https://www.twilio.com/console)
2. You'll see your **Account SID** and **Auth Token** on the dashboard
3. Click **Get a Trial Phone Number** (or use an existing one)

#### Step 3: Configure Your .env File
Open `.env` file in `missing_person_ai_backend` folder and update:

```env
# Replace these with your actual Twilio credentials
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

**Example:**
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

#### Step 4: Verify Phone Numbers (Trial Account Only)
If you're using a **free trial account**, you must verify the recipient phone numbers:
1. Go to [https://www.twilio.com/console/phone-numbers/verified](https://www.twilio.com/console/phone-numbers/verified)
2. Add the phone numbers you want to send SMS to
3. Verify them with the code sent to your phone

**Note:** Upgrade to a paid Twilio account to send SMS to any number without verification.

## 🚀 Testing

### Test in Simulation Mode
1. Start your backend server:
   ```bash
   cd missing_person_ai_backend
   uvicorn app:app --reload
   ```

2. Register a police officer through the frontend
3. Check the console output - you'll see the SMS message printed

### Test with Real SMS
1. Configure Twilio credentials in `.env` (see Step 3 above)
2. Restart your backend server
3. Register a police officer
4. Check your mobile phone for the registration confirmation SMS!

## 📨 SMS Message Format

When a police officer registers, they will receive:

```
Hello [Name],

Your registration as Police Officer in the Missing Person AI System has been completed successfully!

You can now login to your account.

Thank you for joining us in helping find missing persons.

- Missing Person AI Team
```

## 💰 Twilio Pricing

- **Free Trial:** $15 credit (approximately 500-1000 SMS messages)
- **Pay As You Go:** ~$0.0079 per SMS to India
- **Monthly Plans:** Start at $20/month

Visit: [https://www.twilio.com/sms/pricing](https://www.twilio.com/sms/pricing)

## 🇮🇳 India-Specific Configuration

For sending SMS to Indian numbers (+91):

1. **Phone Number Format:** The system automatically adds +91 country code if not provided
2. **DLT Registration:** For production use in India, you may need to register with DLT (Distributed Ledger Technology)
3. **Template Approval:** Twilio will help you register message templates

## 🔒 Security Notes

- Never share your Twilio Auth Token publicly
- Keep your `.env` file secure and never commit it to version control
- The `.gitignore` file already excludes `.env` from git

## 🐛 Troubleshooting

### SMS Not Sending
1. Check console for error messages
2. Verify your Twilio credentials in `.env`
3. Ensure your phone number is verified (trial accounts)
4. Check your Twilio account balance

### Error: "Unverified Recipient"
- This happens with trial accounts
- Verify the recipient phone number in Twilio console
- Or upgrade to a paid account

### Console Shows "SIMULATED SMS"
- This means Twilio is not configured
- Add your credentials to `.env` file
- Restart the backend server

## 📞 Support

For Twilio support:
- Documentation: [https://www.twilio.com/docs/sms](https://www.twilio.com/docs/sms)
- Support: [https://support.twilio.com](https://support.twilio.com)

For project-specific issues, check the console logs and error messages.
