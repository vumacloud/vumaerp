# VumaERP Deployment Guide

Production deployment for VumaERP on DigitalOcean.

## Recommended Droplet

| Spec | Value | Cost |
|------|-------|------|
| **CPU** | 8 vCPU (Premium Intel) | |
| **RAM** | 16 GB | |
| **Storage** | 320 GB NVMe | |
| **Type** | Premium Intel | ~$96/mo |
| **Region** | Frankfurt (FRA1) or Amsterdam (AMS3) | |

This handles 50+ concurrent users comfortably.

## Quick Deploy

```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Run deployment script
curl -sSL https://raw.githubusercontent.com/vumacloud/vumaerp/main/deploy/scripts/deploy.sh | bash
```

## Manual Deployment

```bash
# 1. Clone repository
git clone https://github.com/vumacloud/vumaerp.git /opt/vumaerp
cd /opt/vumaerp/deploy

# 2. Configure environment
cp .env.example .env
nano .env  # Set your passwords

# 3. Start services
docker compose up -d

# 4. Setup SSL (after DNS is configured)
./scripts/setup-ssl.sh
```

## Customer Provisioning

Create a new customer database:

```bash
# Syntax: ./scripts/new-customer.sh <db_name> <country> [admin_email]

# Kenya customer
./scripts/new-customer.sh acme_kenya ke admin@acme.co.ke

# Nigeria customer
./scripts/new-customer.sh widgets_ng ng admin@widgets.ng

# Ghana customer
./scripts/new-customer.sh goldcoast gh admin@goldcoast.gh
```

Modules installed per country:

| Country | Code | Modules |
|---------|------|---------|
| Kenya | `ke` | l10n_ke, l10n_ke_etims, l10n_ke_payroll |
| Nigeria | `ng` | l10n_ng, l10n_ng_tax, l10n_ng_payroll |
| Ghana | `gh` | l10n_gh, l10n_gh_evat, l10n_gh_payroll |
| Uganda | `ug` | l10n_ug, l10n_ug_efris, l10n_ug_payroll |

## DNS Configuration

Point these records to your droplet IP:

```
A     vuma.cloud       → <droplet-ip>
A     *.vuma.cloud     → <droplet-ip>
```

Or use Cloudflare (recommended) with proxy enabled.

## Backups

Automated daily backups at 3 AM:

```bash
# Manual backup
./scripts/backup.sh

# Check backup status
ls -la backups/
```

Backups are uploaded to DigitalOcean Spaces if configured.

## Useful Commands

```bash
cd /opt/vumaerp/deploy

# View logs
docker compose logs -f odoo
docker compose logs -f nginx

# Restart services
docker compose restart odoo
docker compose restart

# Stop everything
docker compose down

# Update VumaERP modules
cd /opt/vumaerp
git pull origin main
docker compose restart odoo

# Database shell
docker compose exec db psql -U odoo

# Odoo shell
docker compose exec odoo odoo shell -d <database_name>
```

## Monitoring

Check service health:

```bash
# All services
docker compose ps

# Odoo health
curl http://localhost:8069/web/health

# Database connections
docker compose exec db psql -U odoo -c "SELECT count(*) FROM pg_stat_activity;"
```

## Scaling (When Needed)

When you outgrow a single droplet:

1. **Vertical**: Resize droplet (takes 1 minute)
2. **Database**: Move to DO Managed PostgreSQL ($15/mo+)
3. **Horizontal**: Add droplets behind DO Load Balancer ($12/mo)

## Security Checklist

- [x] UFW firewall enabled (80, 443, 22 only)
- [x] Fail2ban installed
- [x] SSL/TLS enforced
- [x] Rate limiting on login/API
- [x] No database listing (list_db = False)
- [ ] Change default SSH port (optional)
- [ ] Setup SSH key auth (recommended)
- [ ] Enable DO monitoring
