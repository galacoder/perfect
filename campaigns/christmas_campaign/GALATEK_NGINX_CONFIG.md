# Nginx Configuration for webhook.galatek.dev

**Purpose**: Route webhook.galatek.dev to Christmas Campaign webhook server (port 8000)
**Prerequisites**: Webhook server running on port 8000 via systemd service

---

## Quick Setup (Copy-Paste Ready)

### Step 1: Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/christmas-webhook
```

Paste the following configuration:

```nginx
# Christmas Campaign Webhook Server
# Domain: webhook.galatek.dev
# Backend: localhost:8000 (FastAPI/Uvicorn)

server {
    listen 80;
    listen [::]:80;
    server_name webhook.galatek.dev;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Request size limits (for JSON payloads)
    client_max_body_size 10M;

    # Webhook endpoints
    location /webhook/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;

        # Preserve original request information
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts (webhook triggers background flows, so short timeout is fine)
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;

        # Buffering (disable for streaming responses if needed)
        proxy_buffering off;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;

        # Short timeout for health checks
        proxy_connect_timeout 5s;
        proxy_read_timeout 5s;

        # Allow CORS for health checks from monitoring tools
        add_header Access-Control-Allow-Origin "*" always;
    }

    # Root path (optional - can redirect to Prefect UI or show info page)
    location = / {
        return 200 '{"service":"Christmas Campaign Webhook","status":"online","endpoints":["/webhook/christmas-signup","/webhook/calcom-booking","/health"]}';
        add_header Content-Type application/json;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Logging
    access_log /var/log/nginx/christmas-webhook-access.log;
    error_log /var/log/nginx/christmas-webhook-error.log;
}
```

### Step 2: Enable Site

```bash
# Create symbolic link to enable site
sudo ln -s /etc/nginx/sites-available/christmas-webhook /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx
```

### Step 3: Verify HTTP Access

```bash
# Test health endpoint (should work immediately)
curl http://webhook.galatek.dev/health

# Expected response:
# {"status":"healthy","testing_mode":"true",...}
```

---

## SSL Configuration with Certbot

### Prerequisites

- DNS A record for `webhook.galatek.dev` pointing to server IP
- DNS propagation complete (check with `dig webhook.galatek.dev`)
- Port 80 and 443 open in firewall

### Step 1: Install Certbot (if not already installed)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

### Step 2: Obtain SSL Certificate

```bash
# Certbot will automatically modify Nginx config
sudo certbot --nginx -d webhook.galatek.dev

# Follow prompts:
# 1. Enter email address for renewal notifications
# 2. Agree to Terms of Service
# 3. Choose whether to redirect HTTP to HTTPS (recommend: yes)
```

### Step 3: Verify HTTPS Access

```bash
# Test HTTPS endpoint
curl https://webhook.galatek.dev/health

# Expected: Same response as HTTP, but over TLS
```

### Step 4: Test Auto-Renewal

```bash
# Dry-run renewal to verify it works
sudo certbot renew --dry-run

# Expected: "Congratulations, all simulated renewals succeeded"
```

---

## Final Nginx Configuration (After Certbot)

After running Certbot, your Nginx config will look like this:

```nginx
# HTTP server - redirects to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name webhook.galatek.dev;

    # Certbot will add this redirect
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name webhook.galatek.dev;

    # SSL certificates (managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/webhook.galatek.dev/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/webhook.galatek.dev/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Request size limits
    client_max_body_size 10M;

    # Webhook endpoints
    location /webhook/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        proxy_buffering off;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_connect_timeout 5s;
        proxy_read_timeout 5s;
        add_header Access-Control-Allow-Origin "*" always;
    }

    # Root path
    location = / {
        return 200 '{"service":"Christmas Campaign Webhook","status":"online","endpoints":["/webhook/christmas-signup","/webhook/calcom-booking","/health"]}';
        add_header Content-Type application/json;
    }

    # Deny hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }

    # Logging
    access_log /var/log/nginx/christmas-webhook-access.log;
    error_log /var/log/nginx/christmas-webhook-error.log;
}
```

---

## Integration with Existing Prefect Configuration

If you already have Nginx configuration for `prefect.galatek.dev`, you can add webhook configuration in the same way:

```bash
# List existing Nginx configurations
ls -la /etc/nginx/sites-enabled/

# You likely have something like:
# prefect.galatek.dev -> /etc/nginx/sites-available/prefect

# Now you'll also have:
# christmas-webhook -> /etc/nginx/sites-available/christmas-webhook
```

Both can coexist without conflicts since they use different subdomains.

---

## Testing Production Webhook

### Test 1: Health Check

```bash
# Should return healthy status
curl https://webhook.galatek.dev/health

# Expected response:
{
  "status": "healthy",
  "testing_mode": "true",
  "notion_configured": true,
  "resend_configured": true,
  "discord_configured": false,
  "prefect_api_url": "https://prefect.galatek.dev/api",
  "timestamp": "2025-11-19T..."
}
```

### Test 2: Christmas Signup Webhook

```bash
curl -X POST https://webhook.galatek.dev/webhook/christmas-signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "production-test@example.com",
    "first_name": "Production",
    "business_name": "Test Corp",
    "assessment_score": 65,
    "red_systems": 1,
    "orange_systems": 1,
    "yellow_systems": 1,
    "green_systems": 0,
    "gps_score": 50,
    "money_score": 70,
    "marketing_score": 75,
    "weakest_system_1": "GPS System",
    "weakest_system_2": "Money System",
    "revenue_leak_total": 624
  }'

# Expected response:
{
  "status": "accepted",
  "message": "Christmas signup received and email sequence will begin shortly",
  "email": "production-test@example.com",
  "campaign": "Christmas 2025",
  "timestamp": "2025-11-19T..."
}
```

### Test 3: Verify Flow Run in Prefect

```bash
# Open Prefect UI
# https://prefect.galatek.dev/

# Check for new flow run:
# - Flow name: "christmas-signup-handler"
# - Email: "production-test@example.com"
# - Status: SCHEDULED or RUNNING
```

### Test 4: Verify Notion Email Sequence

```bash
# Check Notion Email Sequence Database
# Should have new record with:
# - Email: production-test@example.com
# - Segment: URGENT (1 red system)
# - Email 1 Sent: true (within 1 minute if TESTING_MODE=true)
# - Email 1 Scheduled: [timestamp]
```

---

## Troubleshooting

### Issue: Nginx config test fails

```bash
sudo nginx -t
# Error: nginx: [emerg] invalid parameter "proxy_pass"

# Solution: Check for typos in config file
sudo nano /etc/nginx/sites-available/christmas-webhook
# Ensure all directives end with semicolon
```

### Issue: 502 Bad Gateway

```bash
# Symptom: curl https://webhook.galatek.dev/health returns 502

# Cause: Webhook server not running on port 8000

# Check service status:
sudo systemctl status christmas-webhook

# If not running, start it:
sudo systemctl start christmas-webhook

# Check logs:
sudo journalctl -u christmas-webhook -n 50
```

### Issue: 504 Gateway Timeout

```bash
# Symptom: Webhook times out after 30s

# Cause: Backend flow taking too long (shouldn't happen - webhook uses BackgroundTasks)

# Solution: Increase timeout in Nginx config
location /webhook/ {
    proxy_read_timeout 60s;  # Increase from 30s to 60s
}

# Reload Nginx
sudo systemctl reload nginx
```

### Issue: SSL certificate renewal fails

```bash
# Check certificate expiry
sudo certbot certificates

# Manually renew
sudo certbot renew --force-renewal

# Check renewal logs
sudo cat /var/log/letsencrypt/letsencrypt.log
```

### Issue: CORS errors from website

```bash
# If website (Vercel) gets CORS errors when calling webhook

# Add CORS headers to Nginx config:
location /webhook/ {
    # Add these lines
    add_header Access-Control-Allow-Origin "https://yourdomain.com" always;
    add_header Access-Control-Allow-Methods "POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Content-Type" always;

    # Handle preflight requests
    if ($request_method = OPTIONS) {
        return 204;
    }

    proxy_pass http://localhost:8000;
    # ... rest of config
}
```

---

## Monitoring and Logs

### View Nginx Access Logs

```bash
# Real-time access log
sudo tail -f /var/log/nginx/christmas-webhook-access.log

# Example entry:
# 203.0.113.50 - [19/Nov/2025:14:23:45 +0000] "POST /webhook/christmas-signup HTTP/2.0" 200 156 "-" "Mozilla/5.0..."
```

### View Nginx Error Logs

```bash
# Real-time error log
sudo tail -f /var/log/nginx/christmas-webhook-error.log

# Should be empty if everything working correctly
```

### View Webhook Service Logs

```bash
# Real-time webhook server logs
sudo journalctl -u christmas-webhook -f

# Filter for specific email
sudo journalctl -u christmas-webhook | grep "production-test@example.com"
```

### Check Nginx Status

```bash
# Nginx service status
sudo systemctl status nginx

# Reload config without downtime
sudo systemctl reload nginx

# Restart Nginx (brief downtime)
sudo systemctl restart nginx
```

---

## Security Best Practices

### 1. Rate Limiting (Prevent Abuse)

Add to Nginx config to prevent spam:

```nginx
# Define rate limit zone (outside server block)
limit_req_zone $binary_remote_addr zone=webhook_limit:10m rate=10r/m;

# Apply to webhook endpoints (inside location block)
location /webhook/ {
    limit_req zone=webhook_limit burst=5 nodelay;
    # ... rest of config
}
```

**Effect**: Max 10 requests per minute per IP, with burst of 5.

### 2. IP Whitelisting (Optional)

If webhook only called from known IPs (e.g., Vercel):

```nginx
location /webhook/ {
    # Allow Vercel IP ranges (example - get real IPs from Vercel docs)
    allow 76.76.21.0/24;
    allow 76.76.22.0/24;
    deny all;

    proxy_pass http://localhost:8000;
    # ... rest of config
}
```

### 3. Disable Server Version

In `/etc/nginx/nginx.conf`:

```nginx
http {
    server_tokens off;  # Don't expose Nginx version
    # ... rest of config
}
```

### 4. Monitor for Suspicious Activity

```bash
# Check for unusual request patterns
sudo grep "POST /webhook/" /var/log/nginx/christmas-webhook-access.log | awk '{print $1}' | sort | uniq -c | sort -rn

# Top IPs making requests:
# 145 203.0.113.50   <- Legitimate (Vercel)
# 12  198.51.100.22  <- Suspicious (investigate)
```

---

## Complete Deployment Checklist

- [ ] DNS A record added: `webhook.galatek.dev` → server IP
- [ ] DNS propagation verified: `dig webhook.galatek.dev`
- [ ] Webhook service running: `sudo systemctl status christmas-webhook`
- [ ] Nginx config created: `/etc/nginx/sites-available/christmas-webhook`
- [ ] Nginx config enabled: `ln -s` to `/etc/nginx/sites-enabled/`
- [ ] Nginx config tested: `sudo nginx -t`
- [ ] Nginx reloaded: `sudo systemctl reload nginx`
- [ ] HTTP health check works: `curl http://webhook.galatek.dev/health`
- [ ] SSL certificate obtained: `sudo certbot --nginx -d webhook.galatek.dev`
- [ ] HTTPS health check works: `curl https://webhook.galatek.dev/health`
- [ ] Production webhook tested: `curl -X POST https://webhook.galatek.dev/webhook/christmas-signup ...`
- [ ] Flow run appears in Prefect UI: https://prefect.galatek.dev/
- [ ] Email sequence record in Notion Email Sequence DB
- [ ] First email sends via Resend (check Resend dashboard)
- [ ] Website webhook URL updated: `PREFECT_WEBHOOK_URL=https://webhook.galatek.dev/webhook/christmas-signup`

---

## Next Steps After Nginx Setup

1. **Update Website Configuration**:
   ```bash
   # In your website repository (Vercel)
   # Update .env.production or Vercel environment variables:
   PREFECT_WEBHOOK_URL=https://webhook.galatek.dev/webhook/christmas-signup

   # Redeploy website:
   vercel --prod
   ```

2. **Test End-to-End from Website**:
   - Fill out Christmas signup form on website
   - Submit form
   - Verify webhook receives request (check logs)
   - Verify flow runs in Prefect UI
   - Verify email sequence starts

3. **Monitor First 24 Hours**:
   - Check webhook logs for errors: `sudo journalctl -u christmas-webhook -f`
   - Check Nginx logs: `sudo tail -f /var/log/nginx/christmas-webhook-access.log`
   - Check Prefect UI for flow runs: https://prefect.galatek.dev/
   - Check Resend dashboard for email delivery
   - Check Notion Email Sequence DB for tracking updates

4. **Switch to Production Timing** (after validation):
   ```bash
   # Edit .env on server
   sudo nano /opt/christmas-campaign/.env

   # Change:
   TESTING_MODE=false  # Production timing (24h, 72h, etc.)

   # Restart webhook service
   sudo systemctl restart christmas-webhook
   ```

---

## Support

**Nginx Documentation**: https://nginx.org/en/docs/
**Certbot Documentation**: https://certbot.eff.org/
**Deployment Guide**: `campaigns/christmas_campaign/GALATEK_DEPLOYMENT_PLAN.md`
**Troubleshooting**: `campaigns/christmas_campaign/PRODUCTION_DEPLOYMENT_CHECKLIST.md`

---

**Ready to configure Nginx!** Run the commands above after DNS is configured and webhook service is running.
