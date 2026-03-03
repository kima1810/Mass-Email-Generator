EMAIL DRAFT GENERATOR
=====================

OVERVIEW:
This application creates personalized Gmail emails from a CSV file. 
Please note that it will only create DRAFTS of these emails and you will still have to send the emails yourself.

HOW TO USE:
1. Double-click "generate_email.exe" to launch the application
2. Enter your email subject line
3. Enter your email template (use {{first_name}} where you want to personalize)
4. Check "Include Signature" if you want your Gmail signature added automatically
5. Click "Create Drafts" and select your CSV file

TEMPLATE FEATURES:
- Personalization: Use {{first_name}} to insert the recipient's first name
- Hyperlinks: Use [link text](url) to add clickable links
  Example: Check out our [website](https://example.com)
- Bold text: Use **text** or __text__
  Example: **Important announcement**
- Italic text: Use *text* or _text_
  Example: *Please note*
- Underline text: Use ~~text~~
  Example: ~~Underlined text~~
- Colored text: Use {color:text}
  Example: {red:This is red text} or {blue:Blue text}
  Supported colors: red, blue, green, orange, purple, etc.

CSV FILE FORMAT:
Your CSV file must have these columns:
- email: recipient's email address
- first_name: recipient's first name (for personalization)

Example:
email,first_name
john@example.com,John
jane@example.com,Jane

FIRST-TIME SETUP:
When you first run the app, you'll be asked to login to your Google account.
A browser window will open - complete the authentication there.
Your login will be saved for future use.

SWITCHING ACCOUNTS:
To use a different Google account, delete the token file located at:
Windows: C:\Users\YourUsername\.email_draft_generator\token.json
Then run the app again and login with the new account.

NOTES:
- credentials.json is required for Google authentication
- email_template.txt is just a reference - you can type templates directly in the app
- Drafts are created in your Gmail account, not sent automatically
- You can review and edit drafts in Gmail before sending
- Emails are sent as HTML to support hyperlinks

TROUBLESHOOTING:
- If authentication fails, ensure you have a default web browser set
- Check that your firewall is not blocking the application
- Make sure you have an active internet connection
- If the browser doesn't open automatically, check your default browser settings
