# Technical Troubleshooting Guide

## Dashboard Not Loading

### Symptoms
- Blank white screen after login
- "Loading..." spinner that never completes
- Error: "Failed to fetch" in browser console

### Resolution Steps
1. **Hard refresh**: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
2. **Clear cache**: Ctrl+Shift+Delete > Clear cached images and files
3. **Try Incognito mode**: Eliminates extension conflicts
4. **Check status page**: status.adsparkx.com for ongoing incidents
5. **Disable VPN**: Some VPNs interfere with our CDN
6. **Whitelist our domains**: app.adsparkx.com, api.adsparkx.com, cdn.adsparkx.com

If none work, collect the following and contact support:
- Browser console errors (F12 > Console)
- Network tab errors (F12 > Network)
- Your browser version and OS

## Analytics Data Discrepancies

### Why Don't My Numbers Match?

**Adsparkx vs. Google Analytics**
- Attribution window differs (Adsparkx: 7-day click, 1-day view; GA: last-click)
- GA may filter bot traffic differently
- Cross-device tracking methodology varies

**Impressions vs. Reach**
- Impressions = total times ad was shown (same user can see multiple times)
- Reach = unique users who saw the ad

### Data Processing Delay
- Real-time metrics: 5-10 minute delay
- Conversion data: Up to 24-hour delay
- Final daily totals locked at 2:00 AM UTC

## API Integration Issues

### 500 Internal Server Error
- Usually a temporary server issue
- Implement retry logic with exponential backoff:
```python
import time
import requests

def api_call_with_retry(url, headers, max_retries=3):
    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        if response.status_code == 500:
            time.sleep(2 ** attempt)  # 1s, 2s, 4s
            continue
        return response
    raise Exception("Max retries exceeded")
```

### Webhook Not Receiving Events
1. Verify endpoint URL is publicly accessible (not localhost)
2. Check webhook signature validation in your code
3. Confirm your endpoint returns HTTP 200 within 5 seconds
4. Check Webhook Logs in Settings > Developer > Webhook Logs
5. Test with: Dashboard > Settings > Developer > Send Test Event

### Webhook Signature Validation (Python)
```python
import hmac
import hashlib

def validate_webhook(payload_body, signature_header, secret):
    expected = hmac.new(
        secret.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature_header)
```

## Pixel / Conversion Tracking Issues

### Pixel Not Firing
1. Install browser extension: Adsparkx Pixel Helper
2. Check the pixel fires on target pages (shows green check)
3. Verify pixel ID matches Dashboard > Settings > Pixel
4. Ensure pixel code is in `<head>` section before `</head>`

### Conversions Not Tracking
- Conversion event must match the event name in your campaign settings
- Check for duplicate pixel installations (fires twice = inflated numbers)
- Verify the `fbq('track', 'Purchase')` call fires AFTER the transaction is confirmed
- Cross-domain tracking: Add additional configuration for multi-domain funnels

## Mobile App SDK Issues

### SDK Initialization Failure
```
Error: AdsparkxSDK not initialized. Call Adsparkx.init() before any other methods.
```
**Fix**: Ensure `Adsparkx.init(API_KEY)` is called in your app's entry point before any other SDK methods.

### iOS Tracking Authorization
- iOS 14.5+ requires `requestTrackingAuthorization()` before tracking
- Add `NSUserTrackingUsageDescription` to Info.plist
- Reference: developer.apple.com/documentation/apptrackingtransparency

## Error Code Reference
| Code | Meaning                    | Action                        |
|------|----------------------------|-------------------------------|
| 400  | Bad Request                | Check request parameters      |
| 401  | Unauthorized               | Verify API key                |
| 403  | Forbidden                  | Check permissions             |
| 404  | Not Found                  | Verify endpoint URL           |
| 409  | Conflict                   | Resource already exists       |
| 422  | Validation Error           | Review request body format    |
| 429  | Rate Limit Exceeded        | Implement backoff             |
| 500  | Server Error               | Retry; contact support if persists |
| 503  | Service Unavailable        | Check status.adsparkx.com    |
