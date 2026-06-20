# Third-Party Integrations Guide

## Available Integrations

### CRM Integrations
- **Salesforce**: Sync leads generated from campaigns to Salesforce CRM
- **HubSpot**: Automatically create contacts from lead gen campaigns
- **Zoho CRM**: Bi-directional sync for leads and customer data

### Analytics Integrations
- **Google Analytics 4**: Import Adsparkx conversions as GA4 events
- **Mixpanel**: Track user journey from ad click to conversion
- **Segment**: Route Adsparkx events through your data pipeline

### E-commerce Integrations
- **Shopify**: One-click integration for conversion tracking and product catalog sync
- **WooCommerce**: WordPress plugin available
- **Magento**: Available for Enterprise customers

### Automation & Workflow
- **Zapier**: 50+ triggers and actions available
- **Make (Integromat)**: Full API integration module available
- **n8n**: Community-supported connector

## Setting Up an Integration

### Example: HubSpot Integration
1. Go to Settings > Integrations > HubSpot
2. Click "Connect HubSpot" and authorize the connection
3. Map Adsparkx lead fields to HubSpot contact properties:
   - Email → Email
   - Name → First Name + Last Name
   - Phone → Phone Number
   - Campaign → Lead Source
4. Set sync frequency (real-time recommended)
5. Test with a sample form submission

### Example: Google Analytics 4 Integration
1. Go to Settings > Integrations > Google Analytics
2. Enter your GA4 Measurement ID (G-XXXXXXXXXX)
3. Choose which events to import:
   - ad_click
   - conversion
   - purchase
4. Verify events appear in GA4 > Admin > Data Streams > Measurement Protocol within 24 hours

## Shopify Quick Setup
1. Install "Adsparkx for Shopify" from the Shopify App Store
2. Enter your Adsparkx API key when prompted
3. The app automatically:
   - Installs the Adsparkx pixel on all pages
   - Sets up Purchase and Add to Cart conversion events
   - Syncs your product catalog for dynamic ads

## API-Based Custom Integrations
Use our REST API for custom integrations:
- Base URL: https://api.adsparkx.com/v1
- Full documentation: developer.adsparkx.com
- Postman collection: developer.adsparkx.com/postman

### Common Integration Endpoints
- `GET /campaigns` — List all campaigns
- `POST /campaigns` — Create a campaign
- `GET /analytics/report` — Pull analytics data
- `POST /audiences/upload` — Upload custom audience
- `GET /conversions` — Fetch conversion events

## Webhook Setup for Real-Time Integration
```json
{
  "url": "https://your-server.com/webhooks/adsparkx",
  "events": ["campaign.status_change", "conversion.recorded", "ad.approved"],
  "secret": "your_webhook_secret"
}
```
Verify webhook at Settings > Developer > Webhooks > Test Delivery

## Data Sync Troubleshooting

### CRM Sync Not Working
1. Re-authorize the integration (tokens expire after 60 days for some providers)
2. Check field mappings — required fields must be mapped
3. Verify permissions: integration user must have create/update permission in CRM
4. Check Integration Logs at Settings > Integrations > [Name] > Logs

### GA4 Events Not Appearing
- GA4 has up to 24-hour delay for conversion data
- Verify Measurement ID is correct (starts with G-)
- Check that ad-blocking is not filtering events in test environment
- Use GA4 DebugView for real-time event validation

## Integration Request
Don't see the integration you need?
- Vote for it on community.adsparkx.com/feature-requests
- Enterprise customers can request custom integrations
- Submit requests to integrations@adsparkx.com
