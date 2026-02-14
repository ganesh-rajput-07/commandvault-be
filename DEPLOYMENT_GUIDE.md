# Deploying CommandVault Backend to Vercel

This guide will help you deploy your Django backend (`CommandVault-BE`) to Vercel.

## Prerequisites

1.  **Vercel Account**: Sign up at [vercel.com](https://vercel.com).
2.  **PostgreSQL Database**: Vercel is serverless and ephemeral (files are reset). You **MUST** use an external database like [Neon](https://neon.tech), [Supabase](https://supabase.com), or [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres). **Local `db.sqlite3` will NOT work.**

## Steps to Deploy

### 1. Prepare Your Database
Create a PostgreSQL database on a provider (e.g., Neon or Supabase).
Get the connection details:
-   `DB_NAME`
-   `DB_USER`
-   `DB_PASSWORD`
-   `DB_HOST`
-   `DB_PORT`

### 2. Push Code to GitHub/GitLab
Ensure this project (`CommandVault`) is pushed to a repository on GitHub, GitLab, or Bitbucket.

### 3. Import Project in Vercel
1.  Go to your Vercel Dashboard.
2.  Click **"Add New..."** -> **"Project"**.
3.  Import your `CommandVault-BE` repository.

### 4. Configure Project Settings
In the "Configure Project" screen:

-   **Framework Preset**: Select **Other**.
-   **Root Directory**: Ensure it points to `CommandVault` (if your repo has nested folders, otherwise leave as `./`).
-   **Build Command**: Enter:
    ```bash
    bash build_files.sh
    ```
-   **Output Directory**: `staticfiles_build` (optional, as we serve via Whitenoise, but Vercel might use this).
-   **Install Command**: Leave effectively blank or default (Vercel installs from `requirements.txt` automatically).

### 5. Environment Variables
Add the following Environment Variables in the Vercel UI:

| Variable Name | Value | Description |
| :--- | :--- | :--- |
| `DJANGO_SETTINGS_MODULE` | `promptdeck.settings` | Required |
| `SECRET_KEY` | `your-secret-key` | A long random string |
| `DEBUG` | `False` | Turn off debug in production |
| `DATABASE_URL` | `postgres://user:pass@host:port/dbname` | Full connection string (from Neon/Supabase) |
| `CLOUDINARY_CLOUD_NAME` | `...` | For media upload |
| `CLOUDINARY_API_KEY` | `...` | For media upload |
| `CLOUDINARY_API_SECRET` | `...` | For media upload |
| `GOOGLE_CLIENT_ID_1` | `...` | For Google Auth (if used) |
| `GOOGLE_CLIENT_SECRET_2` | `...` | For Google Auth (if used) |

### 6. Deploy
Click **"Deploy"**.

Vercel will build the project using `build_files.sh` (installing dependencies and collecting static files) and then deploy the serverless function.

## Post-Deployment
-   **Migrations**: Since Vercel builds are ephemeral, running migrations during build is risky.
    -   Option A: Connect to your database from your local machine (update `.env` locally to point to production DB) and run:
        ```bash
        python manage.py migrate
        ```
    -   Option B: Use the Vercel specialized migration integration if available, but Option A is safest.

## Troubleshooting
-   **Static Files not loading?**: Ensure `whitenoise` is installed and `build_files.sh` ran successfully.
-   **Database Error?**: Check your Environment Variables and ensure your database accepts connections from internet (0.0.0.0/0 or Vercel IP ranges).
