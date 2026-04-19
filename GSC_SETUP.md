# Search Console Setup Guide

## Google Search Console

1. **Add Property**: https://search.google.com/search-console
2. **Property Type**: URL prefix (recommended) — enter `https://fuelecon.pages.dev`
3. **Verification Method**: HTML tag
   - Copy the meta tag from `public/index.html`:
     ```
     <meta name="google-site-verification" content="GOOGLE_SITE_VERIFICATION_PLACEHOLDER">
     ```
   - After adding the site in GSC, copy the verification code it provides
   - Replace `GOOGLE_SITE_VERIFICATION_PLACEHOLDER` with the real code
4. **Submit Sitemap**: 
   - Go to Sitemaps in GSC
   - Submit: `/sitemap.xml`
5. **URL Inspection** (9 priority URLs):
   - `https://fuelecon.pages.dev/`
   - `https://fuelecon.pages.dev/mpg-converter/`
   - `https://fuelecon.pages.dev/split-fuel/`
   - `https://fuelecon.pages.dev/ev-vs-gas/`
   - `https://fuelecon.pages.dev/commute-cost/`
   - `https://fuelecon.pages.dev/lease-vs-buy-fuel/`
   - `https://fuelecon.pages.dev/about/`
   - `https://fuelecon.pages.dev/contact/`
   - `https://fuelecon.pages.dev/privacy/`
6. **Settings**: Set preferred domain to `fuelecon.pages.dev` (or keep as-is)

---

## Bing Webmaster Tools

1. **Add Site**: https://www.bing.com/webmasters
2. **Verification Method**: HTML tag
   - Copy the meta tag from `public/index.html`:
     ```
     <meta name="msvalidate.01" content="BING_VERIFICATION_PLACEHOLDER">
     ```
   - After adding the site in Bing, replace placeholder with real verification code
3. **Submit Sitemap**: 
   - Go to Configure → Sitemaps
   - Submit: `https://fuelecon.pages.dev/sitemap.xml`