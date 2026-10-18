# rdrs
Ransomeware detection and defense system
# Ransomware Detection and Response System (RDRS)

A defensive cybersecurity application monitoring file-system telemetry and active process telemetry patterns using sliding-window tracking.

## Local Operational Quickstart
1. Install requirements: `pip install -r requirements.txt`
2. Launch daemon execution: `python app/main.py`

## Deploying the Monitoring Webpage via GitHub Pages
Since GitHub Pages hosts **static content only**, the live telemetry stream cannot be executed directly via a live Python server. RDRS bridges this by utilizing client-side JSON ingestion tracking:

1. Create a `docs/` folder in your repository root.
2. Put this static `index.html` file into `docs/index.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>RDRS Live Deployment Security Status</title>
    <style>body { font-family: monospace; background: #0f141c; color: #76e38c; padding: 5%; }</style>
</head>
<body>
    <h2>RDRS Cloud Monitoring Matrix Node</h2>
    <div id="view">Awaiting status database update data matrix...</div>
    <script>
        fetch('./dashboard_data.json')
            .then(res => res.json())
            .then(data => {
                document.getElementById('view').innerHTML = `
                    <p><b>Last Status Synchronization:</b> ${data.last_updated}</p>
                    <p><b>Total Sandbox Operations Logged:</b> ${data.total_events}</p>
                    <h3>Recent System Alert Logs</h3>
                    <ul>${data.alerts.map(a => `<li>[Score: \${a.score}] Process: a.process - {a.desc}</li>`).join('')}</ul>
                `;
            }).catch(e => { document.getElementById('view').innerText = "Telemetry json file not yet populated."; });
    </script>
</body>
</html>
```

3. Configure your local system or automated scheduler to hit the POST endpoint `http://localhost:8000/api/export/gh-pages` periodically. This automatically updates `docs/dashboard_data.json`.
4. Commit and push the `docs/` folder updates to your branch to make the data visible on your public GitHub Pages website.
