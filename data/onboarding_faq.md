# Onboarding FAQ

## Getting Started

### Q: How do I set up my account after signing up?
A: After email verification, complete your profile:
1. Add your company name and website
2. Connect a payment method (required for paid plans)
3. Install the tracking pixel on your website
4. Create your first campaign
Our onboarding wizard guides you through all steps automatically.

### Q: How long does account verification take?
A: Email verification is instant. Identity verification for higher spend limits (>$10,000/month) takes 1-2 business days and requires:
- Business registration document
- Government-issued ID of account owner

### Q: Can I invite team members?
A: Yes. Go to Settings > Team > Invite Member. You can assign these roles:
- Admin: Full access including billing
- Manager: Can create/edit campaigns, cannot access billing
- Analyst: Read-only access to analytics
- Viewer: Dashboard view only

### Q: What is the Adsparkx pixel and do I need it?
A: The pixel is a small JavaScript snippet that tracks website visitor behavior for:
- Conversion tracking (measuring campaign ROI)
- Custom audience creation (retarget website visitors)
- Optimization (auto-optimize campaigns toward converters)
It's optional but highly recommended for performance campaigns. Find it at Settings > Pixel.

## Campaign Questions

### Q: How quickly do campaigns get approved?
A: Standard approval takes 2-4 hours during business hours. Complex creatives or new advertisers may take up to 24 hours. Avoid starting campaigns requiring immediate launch without buffer time.

### Q: What content is prohibited?
Prohibited categories:
- Adult content
- Alcohol (without age-gating approval)
- Tobacco and vaping products
- Gambling (without license verification)
- Misleading health claims
- Weapons and firearms
- Political advertising (requires registration)
Full policy: adsparkx.com/ad-policies

### Q: What is the minimum campaign budget?
A: Minimum $5/day or $50 lifetime budget. For statistically meaningful results, we recommend at least $20/day for 7 days minimum.

### Q: Can I run campaigns in multiple countries simultaneously?
A: Yes. When setting up your audience, select multiple countries. Note that billing currency is fixed at account creation (USD, EUR, or INR available).

## Billing Questions

### Q: When will I be charged?
A: Charges occur at the start of each billing cycle (monthly or annually). Campaign spend is charged when your prepaid balance depletes or at end of month, whichever comes first.

### Q: Is there a free trial?
A: The Free plan is permanently free (no credit card required). Paid plans don't have a trial, but we offer a 30-day pro-rated refund for annual plans if you're not satisfied.

### Q: What happens if my payment fails?
A: We retry 3 times over 7 days. If payment is not resolved, your account is downgraded to Free and campaigns are paused. Data is retained for 30 days.

## Technical Questions

### Q: What are the API rate limits?
A: Rate limits depend on your plan (see API Authentication Guide). All plans support burst requests but sustained requests beyond limits return 429 errors.

### Q: Do you support webhooks?
A: Yes. Configure webhooks at Settings > Developer > Webhooks. Available events:
- campaign.status_change
- ad.approved / ad.rejected
- budget.depleted
- conversion.recorded

### Q: Is there an SDK for mobile apps?
A: Yes, we have official SDKs for:
- iOS (Swift/Objective-C) — via CocoaPods or Swift Package Manager
- Android (Kotlin/Java) — via Gradle
- React Native — via npm
- Flutter — via pub.dev
Documentation: developer.adsparkx.com

### Q: How do I export my data?
A: Analytics data can be exported as CSV or PDF from Analytics > Export. For bulk data export via API, use the `/v1/reports/export` endpoint.

## Support Resources

### Q: Where can I find help?
- Help Center: help.adsparkx.com (searchable documentation)
- API Documentation: developer.adsparkx.com
- Community Forum: community.adsparkx.com
- Support Email: support@adsparkx.com
- Live Chat: Available in-app for Pro and Enterprise customers

### Q: What are support hours?
- Free/Starter: Email support, 9 AM – 6 PM IST, Mon–Fri
- Pro: Priority email + live chat, Mon–Fri 9 AM – 9 PM IST
- Enterprise: 24/7 support with dedicated account manager
