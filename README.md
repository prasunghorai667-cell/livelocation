# Location Sharing Service

A persistent location-sharing service where users can share their location via a link.

## Features

- Generate location links with one click
- View shared locations on a map
- Admin dashboard to manage links
- Persistent storage (links stay until manually deleted)
- Admin authentication required for dashboard

## Admin Credentials

- Username: `admin`
- Password: `admin123`

**Change the password after first login!**

## Deployment to Render.com

1. Create a GitHub repository and push this code
2. Go to [render.com](https://render.com) and create a new Web Service
3. Connect your GitHub repository
4. Set the following:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python3 server/app.py`
   - Environment: `Python 3`
   - Port: `10000`

Or use the `render.yaml` configuration:

```
services:
  - type: web
    name: location-share
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: python3 server/app.py
    envVars:
      - key: PORT
        value: 10000
```

## Local Development

```bash
cd location-share
python3 server/app.py
```

Open http://localhost:3000

## File Structure

```
location-share/
├── server/
│   └── app.py          # Main server
├── public/
│   ├── index.html     # Share location page
│   ├── view.html    # View location page
│   ├── dashboard.html # Manage links (requires login)
│   ├── login.html   # Admin login
│   ├── style.css
│   └── *.js
├── requirements.txt
└── render.yaml
```

## Google Maps API Key

Replace `YOUR_GOOGLE_MAPS_API_KEY` in `index.html` and `view.html` with your actual Google Maps API key.

For production, use environment variables for the API key.