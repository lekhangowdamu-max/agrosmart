# AgroSmart Advanced Upgrade

This upgrade adds an improved responsive farmer dashboard, a browser-local field checklist, and an authenticated AI Crop Doctor page.

## What changed

- `templates/dashboard.html`: redesigned dashboard using real counts from the current database tables, plus shortcuts to existing modules.
- `static/advanced.css`: styles scoped to the new dashboard and Crop Doctor pages; includes mobile and reduced-motion support.
- `templates/crop_doctor.html`: crop image upload, crop/symptom context, result display, and safety guidance.
- `app.py`: `/crop-doctor` route calls a configured vision-capable OpenAI model from the server. Uploaded images are validated and processed in memory; this app does not save them into its upload folder.
- `templates/base.html`: loads the new stylesheet and adds a navigation link for authenticated users.
- `.env.example`: documents the new AI configuration variables.

## Configure AI Crop Doctor locally

1. Create or update your local `.env` file (never commit it).
2. Set:

   ```env
   OPENAI_API_KEY=your_real_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   ```

3. Restart the Flask server and open `/crop-doctor` while logged in.
4. Use a JPG, PNG, or WEBP image smaller than 5 MB.

The AI feature requires an OpenAI API key and account/API access. API usage may incur charges. The model can make mistakes; results are explicitly framed as possibilities and should not be treated as confirmed diagnosis or pesticide prescriptions.

## Configure on Vercel

In the Vercel project dashboard, open **Settings → Environment Variables** and add `OPENAI_API_KEY` and `OPENAI_MODEL` for the required environments. Redeploy after saving. Keep the API key server-side; never put it in HTML, JavaScript, or a `NEXT_PUBLIC_`/client-exposed variable.

## Run locally

Use the existing setup instructions in `LOCAL_SETUP.md`. Install the project's `requirements.txt`, configure the database and secret key, then run the existing Flask entry point. If the project's virtual environment is already set up, restart the current Flask server after these changes.

## Important notes

- The dashboard metrics are database counts, not fabricated live statistics.
- The checklist is stored only in the current browser's local storage; it is not synced across devices or accounts.
- The Crop Doctor image is sent to the configured AI provider for analysis. Do not upload images containing sensitive personal information.
- This update does not enable real drone flight, motor switching, live sensor telemetry, or automatic irrigation. Those require supported hardware, secure device authentication, and safety controls.
