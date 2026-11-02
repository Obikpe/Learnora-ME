# Gmail API setup for Learnora

Learnora sends verification and password-reset emails through the Gmail API over HTTPS. This avoids direct SMTP connections and does not require Resend or a custom sending domain.

## 1. Choose the sending Gmail account

Use a Gmail account controlled by Learnora. Keep its address available; it becomes `GMAIL_USER_EMAIL`. The account must be able to send mail normally.

If you want a different From address, configure it first as a verified “Send mail as” alias in Gmail. Otherwise, use the same address for `GMAIL_USER_EMAIL` and `GMAIL_FROM_EMAIL`.

## 2. Create a Google Cloud project and enable Gmail API

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create or select a project dedicated to Learnora email delivery.
3. Open **APIs & Services → Library**, find **Gmail API**, and enable it.
4. Configure the OAuth consent screen / Google Auth Platform. Use an external audience for an ordinary consumer Gmail account. Add the sending Gmail account as a test user while configuring the integration.
5. Add only this Gmail scope: `https://www.googleapis.com/auth/gmail.send`.

Google classifies `gmail.send` as a **sensitive** scope. Public use may require OAuth app verification. Do not request broad Gmail access such as `https://mail.google.com/`; Learnora only needs permission to send messages.

## 3. Create an OAuth client

1. In **Google Auth Platform → Clients** (or **APIs & Services → Credentials**), create an OAuth client ID.
2. Choose **Web application**.
3. Add this authorised redirect URI:

   `https://developers.google.com/oauthplayground`

4. Save the client and copy its client ID and client secret into a secure temporary location. Never commit them to GitHub or put them in frontend variables.

## 4. Generate the offline refresh token

1. Open [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground).
2. Open its settings (gear icon), enable **Use your own OAuth credentials**, and enter the client ID and client secret created above.
3. In the scope input, enter exactly:

   `https://www.googleapis.com/auth/gmail.send`

4. Authorise the API using the Gmail account selected in step 1.
5. Exchange the authorisation code for tokens.
6. Copy the **refresh token** from the token response. The backend uses this long-lived credential to obtain short-lived access tokens; it does not store or log the access token.

If Google does not return a refresh token, revoke the test grant for this OAuth app and authorise again with consent. Do not substitute the one-hour access token for the refresh token.

**Important:** Google states that refresh tokens issued while an external OAuth app is in **Testing** status expire after seven days when Gmail scopes are requested. Testing mode is therefore only suitable for a short integration check. For ongoing production sending, complete the applicable Google OAuth verification requirements and publish the consent configuration. Google identifies `gmail.send` as sensitive, so verification may be required before unrestricted use.

## 5. Configure the backend deployment

In the **Learnora backend Vercel project** (`learnora-backend-v02`), add these variables for the Production environment:

| Variable | Value |
| --- | --- |
| `GMAIL_OAUTH_CLIENT_ID` | OAuth client ID |
| `GMAIL_OAUTH_CLIENT_SECRET` | OAuth client secret |
| `GMAIL_OAUTH_REFRESH_TOKEN` | Refresh token from OAuth Playground |
| `GMAIL_USER_EMAIL` | Gmail account that granted permission |
| `GMAIL_FROM_EMAIL` | Optional; defaults to `GMAIL_USER_EMAIL`. A different address must be a verified send-as alias |
| `GMAIL_FROM_NAME` | Optional; defaults to `Learnora Me` |

Keep all credentials server-side. Never add them to `NEXT_PUBLIC_*` variables, frontend projects, source files, screenshots, or chat messages. After the Gmail API configuration is in place, remove the old `SMTP_*` variables from the backend deployment; this code no longer reads them.

## 6. Verify delivery

After the variables are saved, deploy the backend and test:
- a new registration email;
- the resend-verification action;
- a password-reset email.

A successful Gmail API response means Google accepted the message for sending; also check the sender account's Sent folder and the recipient inbox/spam folder. Do not repeatedly retry an ambiguous send failure, because the provider may have accepted the first request.

If the OAuth refresh token is revoked, expires, or is invalidated, the backend will report a safe delivery error. Generate and configure a replacement refresh token; do not expose the token in logs.

## Implementation details

- Token refresh: `https://oauth2.googleapis.com/token`.
- Send endpoint: `POST https://gmail.googleapis.com/gmail/v1/users/me/messages/send`.
- MIME content is encoded as base64url in Gmail's `raw` message field.
- The implementation does not retry a send after an ambiguous API failure, avoiding duplicate verification or password-reset emails.
- Registration, resend, token hashing, expiry, and password-reset logic remain unchanged. Only the email transport has changed.