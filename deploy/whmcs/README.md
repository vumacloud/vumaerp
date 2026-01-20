# VumaERP WHMCS Integration

Automated provisioning of VumaERP instances via WHMCS.

## Architecture

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│     WHMCS       │  HTTP   │  Provision API  │ Docker  │     Odoo        │
│  portal.vuma   │ ──────► │  (Flask/Python) │ ──────► │   PostgreSQL    │
│  cloud.com      │         │  Port 5000      │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

## Setup

### 1. Add to docker-compose.yml

Add this service to your `docker-compose.yml`:

```yaml
  provision-api:
    build:
      context: ./whmcs
      dockerfile: Dockerfile
    container_name: vumaerp-provision
    restart: unless-stopped
    ports:
      - "127.0.0.1:5000:5000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./.env:/app/.env:ro
      - ./backups:/opt/vumaerp/deploy/backups
    environment:
      - WHMCS_API_TOKEN=${WHMCS_API_TOKEN}
    networks:
      - vumaerp-net
```

### 2. Configure Environment

Add to your `.env`:

```bash
# WHMCS Integration
WHMCS_API_TOKEN=your_secure_random_token_here
PROVISION_API_PORT=5000
```

### 3. Configure WHMCS

#### Option A: Use API Directly (Recommended)

Create a custom server in WHMCS:
1. Go to Setup → Products/Services → Servers
2. Add New Server
3. Set:
   - Name: VumaERP
   - Hostname: your-droplet-ip
   - Type: Custom

Then create a Server Module Hook or use WHMCS's API Credentials feature.

#### Option B: Install WHMCS Module

Copy `whmcs_module/vumaerp/` to your WHMCS `/modules/servers/` directory.

## API Reference

All endpoints require `X-API-Token` header for authentication.

### Create Account (Provision)

```bash
POST /api/v1/provision
Content-Type: application/json
X-API-Token: your_token

{
    "db_name": "acme_ltd",
    "country": "ke",
    "admin_email": "admin@acme.co.ke",
    "company_name": "Acme Ltd"
}
```

Response:
```json
{
    "success": true,
    "db_name": "acme_ltd",
    "url": "https://acme-ltd.vumacloud.com",
    "admin_email": "admin@acme.co.ke",
    "admin_password": "generated_password",
    "country": "Kenya"
}
```

### Suspend Account

```bash
POST /api/v1/suspend
X-API-Token: your_token

{
    "db_name": "acme_ltd"
}
```

### Unsuspend Account

```bash
POST /api/v1/unsuspend
X-API-Token: your_token

{
    "db_name": "acme_ltd"
}
```

### Terminate Account

```bash
POST /api/v1/terminate
X-API-Token: your_token

{
    "db_name": "acme_ltd",
    "skip_backup": false
}
```

### Get Status

```bash
GET /api/v1/status?db_name=acme_ltd
X-API-Token: your_token
```

### List All Databases

```bash
GET /api/v1/list
X-API-Token: your_token
```

## WHMCS Product Configuration

Create products in WHMCS for each country:

| Product Name | Custom Field: country | Custom Field: db_name |
|--------------|----------------------|----------------------|
| VumaERP Kenya | ke | (from order) |
| VumaERP Nigeria | ng | (from order) |
| VumaERP Ghana | gh | (from order) |

### Custom Fields

Add these custom fields to your products:
1. `db_name` (Text) - Database name, admin input
2. `country` (Dropdown) - ke, ng, gh, ug

### Module Settings

- API URL: `http://your-server-ip:5000`
- API Token: `your_whmcs_api_token`

## Testing

```bash
# Test health
curl http://localhost:5000/health

# Test provision (replace token)
curl -X POST http://localhost:5000/api/v1/provision \
    -H "X-API-Token: your_token" \
    -H "Content-Type: application/json" \
    -d '{
        "db_name": "test_company",
        "country": "ke",
        "admin_email": "test@example.com",
        "company_name": "Test Company"
    }'

# Test status
curl "http://localhost:5000/api/v1/status?db_name=test_company" \
    -H "X-API-Token: your_token"
```

## Security Notes

1. **Never expose port 5000 publicly** - Keep it on 127.0.0.1
2. Use a strong API token (32+ characters)
3. Consider adding IP whitelisting for WHMCS server
4. All communications should go through nginx with SSL
5. Regularly rotate API tokens

## Nginx Proxy (Optional)

To expose the API via HTTPS:

```nginx
location /provision/ {
    proxy_pass http://127.0.0.1:5000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;

    # IP whitelist for WHMCS server only
    allow 1.2.3.4;  # Your WHMCS server IP
    deny all;
}
```
