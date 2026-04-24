"""
SMS Service Module
Handles sending SMS notifications using Twilio
"""
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SMSService:
    """Service for sending SMS notifications"""
    
    def __init__(self):
        """Initialize Twilio client with credentials from environment"""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_phone = os.getenv('TWILIO_PHONE_NUMBER')
        
        # Initialize client only if credentials are available and not placeholders
        if (self.account_sid and self.auth_token and self.from_phone and 
            self.account_sid != 'your_account_sid_here' and 
            self.auth_token != 'your_auth_token_here' and 
            self.from_phone != 'your_twilio_phone_number_here'):
            try:
                self.client = Client(self.account_sid, self.auth_token)
                self.is_configured = True
                print("✅ Twilio SMS service initialized successfully")
            except Exception as e:
                print(f"⚠️ Twilio initialization error: {e}")
                self.client = None
                self.is_configured = False
        else:
            print("⚠️ Twilio SMS service not configured - SMS will be simulated")
            print("   To enable real SMS, configure Twilio credentials in .env file")
            self.client = None
            self.is_configured = False
    
    def send_sms(self, to_phone: str, message: str) -> dict:
        """
        Send SMS to a phone number
        
        Args:
            to_phone: Phone number to send SMS to (with country code, e.g., +919876543210)
            message: Message content
            
        Returns:
            dict: {'success': bool, 'message': str, 'sid': str or None}
        """
        try:
            # Format phone number - ensure it has country code
            if not to_phone.startswith('+'):
                # Default to India country code (+91)
                to_phone = '+91' + to_phone
            
            if self.is_configured and self.client:
                # Send actual SMS via Twilio
                message_instance = self.client.messages.create(
                    body=message,
                    from_=self.from_phone,
                    to=to_phone
                )
                
                print(f"✅ SMS sent successfully to {to_phone}")
                print(f"   Message SID: {message_instance.sid}")
                
                return {
                    'success': True,
                    'message': 'SMS sent successfully',
                    'sid': message_instance.sid
                }
            else:
                # Simulate SMS sending (for development/testing)
                print("\n" + "="*60)
                print("📱 SIMULATED SMS (Twilio not configured)")
                print(f"To: {to_phone}")
                print(f"Message: {message}")
                print("="*60 + "\n")
                
                return {
                    'success': True,
                    'message': 'SMS simulated (configure Twilio for real SMS)',
                    'sid': None
                }
                
        except TwilioRestException as e:
            error_msg = f"Twilio error: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'message': error_msg,
                'sid': None
            }
        except Exception as e:
            error_msg = f"SMS sending failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                'success': False,
                'message': error_msg,
                'sid': None
            }
    
    def send_registration_success_sms(self, phone: str, name: str, role: str = "User") -> dict:
        """
        Send registration success SMS
        
        Args:
            phone: User's phone number
            name: User's name
            role: User role (Police, Citizen, etc.)
            
        Returns:
            dict: Result of SMS sending
        """
        message = (
            f"Hello {name},\n\n"
            f"Your registration as {role} in the Missing Person AI System "
            f"has been completed successfully!\n\n"
            f"You can now login to your account.\n\n"
            f"Thank you for joining us in helping find missing persons.\n\n"
            f"- Missing Person AI Team"
        )
        
        return self.send_sms(phone, message)
    
    def send_login_success_sms(self, phone: str, name: str, role: str = "User") -> dict:
        """
        Send login success SMS
        
        Args:
            phone: User's phone number
            name: User's name
            role: User role (Police, Citizen, etc.)
            
        Returns:
            dict: Result of SMS sending
        """
        from datetime import datetime
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = (
            f"Hello {name},\n\n"
            f"You have successfully logged in to the Missing Person AI System "
            f"as {role}.\n\n"
            f"Login Time: {current_time}\n\n"
            f"If this wasn't you, please secure your account immediately.\n\n"
            f"- Missing Person AI Team"
        )
        
        return self.send_sms(phone, message)


# Create a singleton instance
sms_service = SMSService()
