# 🚀 Production Deployment - Quick Start Guide

**Status**: Ready to deploy in 2-3 hours
**Prerequisites**: Server access + Domain configured

---

## Step-by-Step Deployment (Copy-Paste Ready)

### Step 1: SSH to Server
```bash
# Replace with your server details
ssh your-username@your-server-ip
```

### Step 2: Clone Repository
```bash
cd /opt
sudo git clone https://github.com/your-org/perfect.git christmas-campaign
cd christmas-campaign
```

### Step 3: Run Deployment Script
```bash
chmod +x campaigns/christmas_campaign/scripts/deploy_production.sh
./campaigns/christmas_campaign/scripts/deploy_production.sh
```

**The script will prompt you for**:
- Notion API Token
- Notion Email Sequence DB ID
- Notion BusinessX Canada DB ID
- Resend API Key
- Discord Webhook URL (optional)

**Have these ready from your local `.env` file!**

### Step 4: Configure DNS
```
In your DNS provider (Cloudflare, etc.):
- Add A record: webhook.yourdomain.com → your-server-ip
- Wait 5-10 minutes for propagation
```

### Step 5: Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/christmas-webhook
```

Paste:
```nginx
server {
    listen 80;
    server_name webhook.yourdomain.com;

    location /webhook/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
```

Enable and reload:
```bash
sudo ln -s /etc/nginx/sites-available/christmas-webhook /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Step 6: Get SSL Certificate
```bash
sudo certbot --nginx -d webhook.yourdomain.com
```

### Step 7: Update Website Webhook URL
```bash
# In your website repo
cd /path/to/sangletech-tailwindcss

# Update .env.production
echo "PREFECT_WEBHOOK_URL=https://webhook.yourdomain.com/webhook/christmas-signup" >> .env.production

# Deploy
vercel --prod
```

### Step 8: Test Production Endpoint
```bash
# Test health
curl https://webhook.yourdomain.com/health

# Test webhook
curl -X POST https://webhook.yourdomain.com/webhook/christmas-signup \
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
```

Expected response:
```json
{
  "status": "accepted",
  "message": "Christmas signup received and email sequence will begin shortly",
  "email": "production-test@example.com",
  "campaign": "Christmas 2025",
  "timestamp": "2025-11-19T..."
}
```

### Step 9: Verify Services Running
```bash
# Check service status
sudo systemctl status prefect-server
sudo systemctl status prefect-worker
sudo systemctl status christmas-webhook

# View logs
sudo journalctl -u christmas-webhook -f
```

### Step 10: Open Prefect UI
```
http://your-server-ip:4200
```

Check for scheduled flow runs!

---

## 🆘 Quick Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u christmas-webhook -n 50

# Restart
sudo systemctl restart christmas-webhook
```

### DNS not resolving
```bash
# Check DNS propagation
dig webhook.yourdomain.com

# If not resolved yet, wait 5-10 more minutes
```

### SSL certificate fails
```bash
# Make sure DNS is resolved first!
# Then retry:
sudo certbot --nginx -d webhook.yourdomain.com
```

### Webhook returns 500
```bash
# Check environment variables
cat /opt/christmas-campaign/.env | grep -v "TOKEN\|API_KEY"

# Check service logs
sudo journalctl -u christmas-webhook -n 100
```

---

## 📊 Monitoring Commands

```bash
# View webhook logs (live)
sudo journalctl -u christmas-webhook -f

# View Prefect server logs
sudo journalctl -u prefect-server -n 100

# Check service health
sudo systemctl status prefect-server prefect-worker christmas-webhook

# Check disk space
df -h

# Check database size
sudo -u postgres psql -c "SELECT pg_size_pretty(pg_database_size('prefect'));"
```

---

## 🔄 Restart Services

```bash
# Restart all services
sudo systemctl restart prefect-server
sudo systemctl restart prefect-worker
sudo systemctl restart christmas-webhook

# Or individually
sudo systemctl restart christmas-webhook
```

---

## 🎯 What Success Looks Like

After deployment:

1. ✅ `curl https://webhook.yourdomain.com/health` returns `{"status":"healthy"...}`
2. ✅ Test webhook POST returns `{"status":"accepted"...}`
3. ✅ Prefect UI (http://server-ip:4200) shows scheduled flows
4. ✅ Notion Email Sequence DB has new test record
5. ✅ First email sends within 1 minute (check Resend dashboard)
6. ✅ Service logs show no errors: `sudo journalctl -u christmas-webhook -n 50`

---

## 📞 Need Help?

**Full guides**:
- `campaigns/christmas_campaign/PRODUCTION_DEPLOYMENT_CHECKLIST.md`
- `campaigns/christmas_campaign/WAVE4_PRODUCTION_DEPLOYMENT.md`

**Review before deploy**:
- `campaigns/christmas_campaign/LOCAL_TESTING_SESSION_SUMMARY.md`

**Ready when you are!** 🚀
