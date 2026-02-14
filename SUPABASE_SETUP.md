# How to Get Your Supabase Connection String

1.  **Log in to Supabase**: Go to [https://supabase.com/dashboard](https://supabase.com/dashboard) and sign in.
2.  **Create a New Project**:
    *   Click on **"New Project"**.
    *   Choose your organization.
    *   **Name**: `X Algo` (or similar).
    *   **Database Password**: **IMPORTANT!** Click "Generate a password" or type one. **COPY THIS PASSWORD NOW** to a safe place. You cannot see it again later.
    *   Click **"Create new project"**.
3.  **Get Connection String**:
    *   Wait for the project to finish "Setting up..." (takes ~2 minutes).
    *   Once active, go to **Settings** (gear icon at the bottom of the left sidebar).
    *   Click on **"Database"** in the "Configuration" section.
    *   Scroll down to **"Connection parameters"**.
    *   Look for **"Connection String"** and ensure **"URI"** is selected (not JDBC or .NET).
    *   **Copy the string**. It looks like: `postgresql://postgres.xxyyzz:+ms-bT-T3@34@kj@aws-0-us-east-1.pooler.supabase.com:6543/postgres`
4.  **Update Your `.env` file**:
    *   Paste the string into your `backend/.env` file as `DATABASE_URL`.
    *   **Replace `+ms-bT-T3@34@kj`** with the actual password you saved in Step 2.
    *   **Important**: Remove the brackets `[]` around the password too!
    *   Example final string: `postgresql://postgres.xxyyzz:mypassword123@aws-0-us-east-1.pooler.supabase.com:6543/postgres`

## Troubleshooting
-   **Password issues**: If you forgot the password, go to **Settings -> Database** and look for "Reset database password".
-   **Connection Refused**: Ensure you are using the correct port. Supabase Transaction Pooler uses `6543`, Session Pooler uses `5432`. Either usually works for this app, but `5432` is safer for SQLAlchemy in some modes.
