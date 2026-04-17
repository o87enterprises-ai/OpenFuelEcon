#!/usr/bin/env python3
"""
FuelEcon · Legal page generator
Builds /about, /privacy, /terms, /disclosure, /contact from shared layout.

Run: python3 scripts/build_legal_pages.py
Output: public/<slug>/index.html for each page
"""

from pathlib import Path
from datetime import date

PUBLIC = Path(__file__).resolve().parent.parent / "public"
EFFECTIVE_DATE = date.today().strftime("%B %d, %Y")
ENTITY = "o87 Enterprises / TruegleAi"

# Email addresses — all forward to truegleai@proton.me via Cloudflare Email Routing
# (configured on trumpafi.online as the email-bearing domain)
CONTACT_EMAIL = "hello@trumpafi.online"   # general inbox
PRIVACY_EMAIL = "privacy@trumpafi.online" # GDPR/CCPA requests
PRESS_EMAIL   = "press@trumpafi.online"   # press & partnerships
ABUSE_EMAIL   = "abuse@trumpafi.online"   # abuse reports, required for AdSense legitimacy

SITE_URL = "https://fuelecon.pages.dev"
APP_NAME = "FuelEcon"

# ------------------------------------------------------------------
# Shared layout
# ------------------------------------------------------------------
def layout(slug: str, title: str, description: str, body_html: str) -> str:
    canonical = f"{SITE_URL}/{slug}/" if slug else SITE_URL
    nav_items = [
        ("/",            "Calculator"),
        ("/about/",      "About"),
        ("/privacy/",    "Privacy"),
        ("/terms/",      "Terms"),
        ("/disclosure/", "Disclosure"),
        ("/contact/",    "Contact"),
    ]
    nav_html = "\n      ".join(
        f'<a href="{href}"{ " class=\"active\"" if href.strip("/") == slug else "" }>{label}</a>'
        for href, label in nav_items
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="#1A5F3F">
  <title>{title} · {APP_NAME}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{canonical}">
  <meta name="robots" content="index, follow">

  <!-- Open Graph -->
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{APP_NAME}">
  <meta property="og:title" content="{title} · {APP_NAME}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">

  <!-- Icons + fonts -->
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/manifest.json">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <link rel="stylesheet" href="/css/static.css">
</head>
<body>
<div class="container">

  <header class="site-header">
    <a href="/" class="brand-link">
      <h1 class="brand"><i class="fas fa-leaf"></i> FuelEcon</h1>
      <span class="tagline">Fuel economy for dummies</span>
    </a>
    <nav class="site-nav">
      {nav_html}
    </nav>
  </header>

  {body_html}

  <footer class="site-footer">
    <div class="footer-grid">
      <div class="footer-col">
        <h4>FuelEcon</h4>
        <p style="max-width: 300px; font-size: 0.82rem; line-height: 1.55;">
          Plain-English tools for figuring out what driving actually costs.
          Built by drivers, for drivers.
        </p>
      </div>
      <div class="footer-col">
        <h4>Tools</h4>
        <a href="/">Trip cost calculator</a>
        <a href="/mpg-converter/">MPG ⇄ L/100km</a>
        <a href="/split-fuel/">Split fuel cost</a>
        <a href="/ev-vs-gas/">EV vs gas break-even</a>
      </div>
      <div class="footer-col">
        <h4>About</h4>
        <a href="/about/">About FuelEcon</a>
        <a href="/contact/">Contact</a>
      </div>
      <div class="footer-col">
        <h4>Legal</h4>
        <a href="/privacy/">Privacy policy</a>
        <a href="/terms/">Terms of use</a>
        <a href="/disclosure/">Ad disclosure</a>
      </div>
    </div>
    <div class="footer-legal">
      © 2026 FuelEcon · Published by {ENTITY} · Estimates only — your mileage may vary (literally).
    </div>
  </footer>

</div>
</body>
</html>
"""


# ------------------------------------------------------------------
# Page content
# ------------------------------------------------------------------

ABOUT = f"""
  <section class="page-hero">
    <h1>About FuelEcon</h1>
    <p class="lead">Plain-English tools for figuring out what driving actually costs — no jargon, no spec-sheet required.</p>
    <div class="meta">
      <span><strong>Published by:</strong> {ENTITY}</span>
      <span><strong>Contact:</strong> <a href="/contact/">{CONTACT_EMAIL}</a></span>
    </div>
  </section>

  <article class="prose">
    <h2>What is FuelEcon?</h2>
    <p>FuelEcon is a free web application that helps everyday drivers calculate the cost of a trip, understand their vehicle's real fuel economy, and find small habits that save money at the pump. We built it because most fuel calculators are either buried inside bigger sites or written like owner's manuals. We wanted a tool that answers the question in plain English.</p>

    <h2>Our tools</h2>
    <p>FuelEcon is designed as a small family of single-purpose calculators, each built around one common driving question:</p>
    <ul>
      <li><strong>Trip cost calculator</strong> — what will a specific drive cost in gas?</li>
      <li><strong>MPG ⇄ L/100km converter</strong> — translating between the two most common fuel-economy units.</li>
      <li><strong>Split fuel cost</strong> — dividing gas money between riders or roommates.</li>
      <li><strong>EV vs gas break-even</strong> — when does switching to an EV actually pay off?</li>
      <li><strong>Lease vs buy fuel factor</strong> — how fuel cost should influence the lease-or-buy decision.</li>
      <li><strong>Commute cost</strong> — what a regular commute really costs each week and month.</li>
    </ul>

    <h2>Where our numbers come from</h2>
    <p>FuelEcon uses fuel economy averages grounded in public <a href="https://www.fueleconomy.gov/" rel="noopener">EPA fuel economy data</a>. Gas prices in our dynamic pages come from the U.S. Energy Information Administration (<a href="https://www.eia.gov/" rel="noopener">EIA</a>) weekly retail series. Our route calculations and mapping use OpenStreetMap data via the OSRM routing engine and Nominatim geocoding service.</p>
    <p>Because we use averages, our numbers are estimates, not guarantees. Driving style, weather, traffic, and vehicle condition will affect real-world fuel use. See our <a href="/terms/">Terms of Use</a> for the full disclaimer.</p>

    <h2>Who we are</h2>
    <p>FuelEcon is published and operated by <strong>{ENTITY}</strong>, an independent software studio focused on small, useful tools for the open web. We are not affiliated with any vehicle manufacturer, fuel retailer, or automotive association. We don't sell your data, and we don't take sponsored placements that affect our recommendations.</p>

    <h2>How we pay for FuelEcon</h2>
    <p>FuelEcon is free to use. We cover hosting and development costs through display advertising served by Google AdSense and through referral links to third-party products we genuinely recommend. For the full picture, see our <a href="/disclosure/">Ad Disclosure</a>.</p>

    <h2>Contact</h2>
    <p>For feedback, corrections, press, partnerships, or to report a bug, please use our <a href="/contact/">contact page</a> or email <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>

    <div class="callout info">
      <strong>One promise:</strong> If a FuelEcon tool tells you something, we want it to be clear, honest, and easy to verify. If we ever get something wrong, let us know — we'll fix it fast.
    </div>
  </article>
"""


PRIVACY = f"""
  <section class="page-hero">
    <h1>Privacy Policy</h1>
    <p class="lead">What data FuelEcon collects, why we collect it, and the controls you have over it — written in plain English, with the legal details you need.</p>
    <div class="meta">
      <span><strong>Effective:</strong> {EFFECTIVE_DATE}</span>
      <span><strong>Publisher:</strong> {ENTITY}</span>
    </div>
  </section>

  <div class="prose">

    <div class="toc">
      <h4>Contents</h4>
      <ol>
        <li><a href="#summary">Short summary</a></li>
        <li><a href="#collected">Information we collect</a></li>
        <li><a href="#how-use">How we use information</a></li>
        <li><a href="#ads">Advertising &amp; cookies</a></li>
        <li><a href="#third-parties">Third-party services</a></li>
        <li><a href="#storage">Local storage &amp; device data</a></li>
        <li><a href="#rights">Your privacy rights</a></li>
        <li><a href="#children">Children</a></li>
        <li><a href="#security">Security &amp; retention</a></li>
        <li><a href="#changes">Changes to this policy</a></li>
        <li><a href="#contact">Contact</a></li>
      </ol>
    </div>

    <article class="prose">

      <h2 id="summary">1. Short summary</h2>
      <p>FuelEcon is a free web calculator. We don't require you to create an account, and we don't sell your personal information. The data we collect falls into three buckets:</p>
      <ul>
        <li><strong>Basic server logs</strong> (IP address, browser type, pages visited) used to keep the site running and secure.</li>
        <li><strong>Advertising data</strong> collected by Google AdSense to serve ads and measure performance.</li>
        <li><strong>Local-only data</strong> — your saved vehicles and preferences — stored in your own browser and never sent to us.</li>
      </ul>

      <h2 id="collected">2. Information we collect</h2>

      <h3>Information you voluntarily provide</h3>
      <p>When you use our calculators, you can enter data such as vehicle MPG, gas price, trip distance, and vehicle nicknames. This information is saved in your browser's local storage (IndexedDB) and is not transmitted to our servers unless you explicitly use a feature that requires syncing (for example, a future synced garage feature, which is not live as of the effective date of this policy).</p>
      <p>If you contact us via the <a href="/contact/">contact page</a> or by email, we receive the name, email address, and message you send.</p>

      <h3>Information collected automatically</h3>
      <p>Like most websites, our hosting provider (Cloudflare) automatically collects technical information when you visit, including IP address, browser user agent, referrer, and the time of the request. This is used for security, abuse prevention, and aggregate analytics. We do not use this information to identify individual visitors.</p>

      <h2 id="how-use">3. How we use information</h2>
      <ul>
        <li>To provide and maintain the FuelEcon service.</li>
        <li>To improve the accuracy and usefulness of our calculators.</li>
        <li>To respond to your inquiries or feedback.</li>
        <li>To detect, prevent, and address technical issues or abuse.</li>
        <li>To serve relevant advertising through Google AdSense (see below).</li>
        <li>To comply with legal obligations.</li>
      </ul>
      <p>We do not sell your personal information. We do not share your data with third parties for their own marketing purposes.</p>

      <h2 id="ads">4. Advertising &amp; cookies</h2>
      <p>FuelEcon uses <strong>Google AdSense</strong> to display advertisements. Google is a third-party vendor that uses cookies to serve ads based on your prior visits to FuelEcon and other sites. Specifically:</p>
      <ul>
        <li>Google uses cookies to serve ads based on your visits to our site and other sites on the internet.</li>
        <li>You can opt out of personalized advertising by visiting <a href="https://www.google.com/settings/ads" rel="noopener">Google Ads Settings</a>.</li>
        <li>Alternatively, you can opt out of some third-party vendors' use of cookies for personalized advertising by visiting <a href="https://www.aboutads.info/" rel="noopener">aboutads.info</a> or <a href="https://www.youronlinechoices.com/" rel="noopener">youronlinechoices.com</a> (EEA/UK).</li>
      </ul>
      <p>Google's use of advertising cookies is governed by the <a href="https://policies.google.com/technologies/ads" rel="noopener">Google Ads policies</a>. We do not have access to the data collected by these cookies.</p>

      <div class="callout warn">
        <strong>Cookie consent (EEA, UK, Switzerland):</strong> If you visit from the European Economic Area, United Kingdom, or Switzerland, we display a consent prompt before any non-essential cookies are set. You can change or withdraw your consent at any time by clearing your cookies and revisiting the site.
      </div>

      <h2 id="third-parties">5. Third-party services</h2>
      <p>We use the following third-party services, each with its own privacy policy:</p>
      <ul>
        <li><strong>Cloudflare</strong> — hosting, CDN, and security. <a href="https://www.cloudflare.com/privacypolicy/" rel="noopener">Privacy policy</a>.</li>
        <li><strong>Google AdSense</strong> — advertising. <a href="https://policies.google.com/privacy" rel="noopener">Privacy policy</a>.</li>
        <li><strong>OpenStreetMap / CartoDB</strong> — map tiles for FuelEcon Maps. <a href="https://wiki.osmfoundation.org/wiki/Privacy_Policy" rel="noopener">OSM privacy</a>.</li>
        <li><strong>Nominatim</strong> — geocoding of addresses to coordinates. Operated by the OpenStreetMap Foundation.</li>
        <li><strong>OSRM</strong> — routing and distance calculation on open data.</li>
      </ul>

      <h2 id="storage">6. Local storage &amp; device data</h2>
      <p>FuelEcon uses your browser's <strong>IndexedDB</strong> and <strong>LocalStorage</strong> to save your vehicle presets, preferences, and recent trips. This data lives entirely on your device. You can clear it at any time through your browser's site settings.</p>
      <p>FuelEcon is also a Progressive Web App (PWA). If you install it to your home screen, a service worker caches static assets so the app works offline. The cache does not contain any identifying information.</p>

      <h2 id="rights">7. Your privacy rights</h2>

      <h3>Rights under GDPR (EEA, UK)</h3>
      <p>If you are in the European Economic Area or the United Kingdom, you have the right to:</p>
      <ul>
        <li>Access the personal data we hold about you.</li>
        <li>Request correction or deletion of that data.</li>
        <li>Object to or restrict certain processing.</li>
        <li>Request data portability.</li>
        <li>Withdraw consent where processing is based on consent.</li>
        <li>Lodge a complaint with your local data protection authority.</li>
      </ul>

      <h3>Rights under CCPA / CPRA (California)</h3>
      <p>California residents have the right to:</p>
      <ul>
        <li>Know what personal information is collected and how it is used.</li>
        <li>Request deletion of personal information.</li>
        <li>Opt out of the sale or sharing of personal information.</li>
        <li>Non-discrimination for exercising these rights.</li>
      </ul>
      <p>FuelEcon does not sell personal information. To exercise any of these rights, email us at <a href="mailto:{PRIVACY_EMAIL}">{PRIVACY_EMAIL}</a>.</p>

      <h2 id="children">8. Children</h2>
      <p>FuelEcon is not directed at children under 13, and we do not knowingly collect personal information from children under 13. If you believe a child has provided us with personal information, please contact us so we can delete it.</p>

      <h2 id="security">9. Security &amp; retention</h2>
      <p>We use industry-standard security practices (TLS encryption in transit, Cloudflare's edge security, minimal data collection) to protect any information we hold. Server logs are retained for a maximum of 30 days except where retention is required for legal compliance or abuse investigation.</p>

      <h2 id="changes">10. Changes to this policy</h2>
      <p>We may update this Privacy Policy from time to time. Material changes will be reflected in the "Effective" date at the top of this page. Continued use of FuelEcon after changes are posted constitutes acceptance of the updated policy.</p>

      <h2 id="contact">11. Contact</h2>
      <p>Questions about this policy, or a privacy-related request, can be sent to:</p>
      <p><strong>{ENTITY}</strong><br>
      Email: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a><br>
      Or use our <a href="/contact/">contact page</a>.</p>

      <div class="callout info">
        <strong>Not legal advice:</strong> This policy is provided in good faith and aims to comply with applicable privacy laws. For binding legal interpretation, please consult a qualified attorney in your jurisdiction.
      </div>

    </article>
  </div>
"""


TERMS = f"""
  <section class="page-hero">
    <h1>Terms of Use</h1>
    <p class="lead">The ground rules for using FuelEcon. Plain language, with the legal bits where they matter.</p>
    <div class="meta">
      <span><strong>Effective:</strong> {EFFECTIVE_DATE}</span>
      <span><strong>Publisher:</strong> {ENTITY}</span>
    </div>
  </section>

  <div class="prose">

    <div class="toc">
      <h4>Contents</h4>
      <ol>
        <li><a href="#agreement">Agreement</a></li>
        <li><a href="#service">The service</a></li>
        <li><a href="#estimates">Estimates, not guarantees</a></li>
        <li><a href="#acceptable-use">Acceptable use</a></li>
        <li><a href="#ip">Intellectual property</a></li>
        <li><a href="#third-parties">Third-party services</a></li>
        <li><a href="#disclaimer">Disclaimer of warranties</a></li>
        <li><a href="#liability">Limitation of liability</a></li>
        <li><a href="#indemnification">Indemnification</a></li>
        <li><a href="#termination">Termination</a></li>
        <li><a href="#changes">Changes to terms</a></li>
        <li><a href="#law">Governing law</a></li>
        <li><a href="#contact">Contact</a></li>
      </ol>
    </div>

    <article class="prose">

      <h2 id="agreement">1. Agreement</h2>
      <p>By accessing or using FuelEcon (the "Service"), operated by <strong>{ENTITY}</strong> ("we," "our," or "us"), you agree to be bound by these Terms of Use. If you do not agree, please do not use the Service.</p>

      <h2 id="service">2. The service</h2>
      <p>FuelEcon is a free, browser-based set of calculators that help users estimate vehicle fuel economy, trip costs, and related metrics. The Service is provided for general informational purposes only.</p>

      <h2 id="estimates">3. Estimates, not guarantees</h2>
      <p><strong>FuelEcon provides estimates, not guarantees.</strong> All numbers produced by our calculators are based on averages from public data sources (including EPA fuel economy data and EIA gas prices) and the information you enter. Real-world fuel use depends on many factors we cannot account for, including driving style, weather, traffic, elevation changes, vehicle condition, and cargo weight.</p>
      <p>You should not rely on FuelEcon's output for decisions with significant financial, legal, or safety consequences without independent verification. For example, don't rent a U-Haul on the strength of one trip estimate without checking a second source.</p>

      <h2 id="acceptable-use">4. Acceptable use</h2>
      <p>You agree not to:</p>
      <ul>
        <li>Use the Service in violation of any applicable law or regulation.</li>
        <li>Attempt to interfere with or disrupt the Service or its infrastructure.</li>
        <li>Scrape, mirror, or systematically download our content beyond reasonable personal use.</li>
        <li>Use automated tools to overload our third-party services (geocoding, routing, tile servers).</li>
        <li>Misrepresent FuelEcon output or attribute fabricated numbers to FuelEcon.</li>
        <li>Use the Service to build a competing commercial product without our written permission.</li>
      </ul>
      <p>To report abuse, suspected fraud, or a violation of these Terms, please email <a href="mailto:{ABUSE_EMAIL}">{ABUSE_EMAIL}</a>.</p>

      <h2 id="ip">5. Intellectual property</h2>
      <p>The FuelEcon name, logo, design, user interface, and original code are the property of {ENTITY}. You may not use our brand assets without written permission.</p>
      <p>Where we use open-source libraries or open data (Leaflet, OpenStreetMap, EPA data, EIA data), those assets are used under their respective licenses and remain the property of their creators.</p>
      <p>You retain ownership of any content you enter into the Service. By entering data, you grant us a limited, non-exclusive license to process it for the purpose of providing the Service to you.</p>

      <h2 id="third-parties">6. Third-party services</h2>
      <p>FuelEcon integrates with third-party services, including Cloudflare (hosting), Google AdSense (advertising), and OpenStreetMap ecosystem tools (maps and routing). Your use of features that rely on these services is also subject to those providers' terms. We are not responsible for third-party services' availability, accuracy, or conduct.</p>

      <h2 id="disclaimer">7. Disclaimer of warranties</h2>
      <p>THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE," WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, OR ACCURACY. WE DO NOT WARRANT THAT THE SERVICE WILL BE UNINTERRUPTED, ERROR-FREE, OR THAT DEFECTS WILL BE CORRECTED.</p>

      <h2 id="liability">8. Limitation of liability</h2>
      <p>TO THE MAXIMUM EXTENT PERMITTED BY LAW, {ENTITY.upper()} AND ITS AFFILIATES SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, WHETHER INCURRED DIRECTLY OR INDIRECTLY, ARISING OUT OF YOUR USE OF OR INABILITY TO USE THE SERVICE. OUR TOTAL LIABILITY FOR ANY CLAIM ARISING FROM OR RELATING TO THE SERVICE SHALL NOT EXCEED ONE HUNDRED U.S. DOLLARS (USD $100).</p>

      <h2 id="indemnification">9. Indemnification</h2>
      <p>You agree to defend, indemnify, and hold harmless {ENTITY} and its affiliates from any claims, damages, or expenses (including reasonable attorney fees) arising from your violation of these Terms or your misuse of the Service.</p>

      <h2 id="termination">10. Termination</h2>
      <p>We reserve the right to suspend or terminate access to the Service at any time, with or without notice, for any reason, including violation of these Terms. The sections of these Terms that by their nature should survive termination (disclaimers, liability limits, governing law, intellectual property) will survive.</p>

      <h2 id="changes">11. Changes to terms</h2>
      <p>We may revise these Terms at any time. The updated version will be reflected in the "Effective" date at the top of this page. Continued use of the Service after changes are posted constitutes acceptance of the revised Terms.</p>

      <h2 id="law">12. Governing law</h2>
      <p>These Terms are governed by the laws of the jurisdiction in which {ENTITY} is established, without regard to conflict-of-laws principles. Any disputes shall be resolved in the courts of that jurisdiction, except where mandatory consumer-protection laws require otherwise.</p>

      <h2 id="contact">13. Contact</h2>
      <p>For questions about these Terms, contact us at <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> or via our <a href="/contact/">contact page</a>.</p>

      <div class="callout info">
        <strong>Not legal advice:</strong> These Terms are drafted in good faith to be fair and enforceable. If you rely on these Terms for a material business decision, please have them reviewed by a qualified attorney in your jurisdiction.
      </div>

    </article>
  </div>
"""


DISCLOSURE = f"""
  <section class="page-hero">
    <h1>Advertising &amp; Affiliate Disclosure</h1>
    <p class="lead">How FuelEcon makes money, and how we keep that separate from what we recommend.</p>
    <div class="meta">
      <span><strong>Effective:</strong> {EFFECTIVE_DATE}</span>
      <span><strong>Publisher:</strong> {ENTITY}</span>
    </div>
  </section>

  <article class="prose">

    <h2>The short version</h2>
    <p>FuelEcon is free to use. We pay for it in two ways: <strong>display advertising</strong> (via Google AdSense) and, in some places, <strong>affiliate links</strong>. Both are disclosed here, on every relevant page, and we keep advertising money separate from the recommendations we make.</p>

    <h2>Display advertising</h2>
    <p>Pages on FuelEcon may display advertisements served by Google AdSense and its advertising partners. These ads are selected automatically by Google based on the page content and, where you have not opted out, your browsing interests.</p>
    <p>We do not choose the specific ads that appear. We do not accept payment to feature particular advertisers more prominently than others in our ad slots. We do control where ad slots appear on the page and which ad categories are allowed.</p>

    <h2>Affiliate links</h2>
    <p>Some links on FuelEcon — for example, links to products referenced in our explainer content — may be "affiliate links." When you click an affiliate link and make a qualifying purchase, we may earn a small commission at no additional cost to you.</p>
    <p>Our editorial policy is simple: we only include affiliate links to products or services we would recommend even without the commission. If an affiliate relationship would affect our recommendation, we disclose it explicitly next to the link. We do not accept paid placements that compromise the recommendation itself.</p>

    <h2>What we don't do</h2>
    <ul>
      <li>We do not accept payment in exchange for positive reviews.</li>
      <li>We do not accept "sponsored content" that is not clearly marked as sponsored.</li>
      <li>We do not sell your personal data to advertisers (see our <a href="/privacy/">Privacy Policy</a>).</li>
      <li>We do not use deceptive ad formats, such as ads that impersonate calculator results or native interface elements.</li>
    </ul>

    <h2>FTC compliance (U.S. visitors)</h2>
    <p>This disclosure is provided to comply with the U.S. Federal Trade Commission's <a href="https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers" rel="noopener">Guides Concerning the Use of Endorsements and Testimonials in Advertising</a> (16 CFR Part 255). Where specific content includes affiliate links, that content also carries an inline disclosure.</p>

    <h2>EU/UK compliance</h2>
    <p>This disclosure, together with our <a href="/privacy/">Privacy Policy</a>, is intended to meet the transparency requirements of the EU Digital Services Act, the UK Advertising Standards Authority (ASA) guidance on online advertising, and the ePrivacy Directive's requirements regarding cookie consent for non-essential cookies used in ad personalization.</p>

    <h2>Questions</h2>
    <p>If you believe any content on FuelEcon is not correctly disclosed, or you have a question about our advertising or affiliate relationships, please contact us at <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>

    <div class="callout info">
      <strong>Why this matters:</strong> Ad revenue is what lets FuelEcon stay free and independent. The wall between "what pays the bills" and "what we recommend" is the reason our tools stay useful — and we take that wall seriously.
    </div>

  </article>
"""


CONTACT = f"""
  <section class="page-hero">
    <h1>Contact FuelEcon</h1>
    <p class="lead">Feedback, corrections, press, or partnerships — we read everything.</p>
    <div class="meta">
      <span><strong>Publisher:</strong> {ENTITY}</span>
      <span><strong>Response time:</strong> usually within 2 business days</span>
    </div>
  </section>

  <article class="prose">

    <h2>Email</h2>
    <p>For most inquiries, email is the fastest way to reach us:</p>
    <p><a href="mailto:{CONTACT_EMAIL}"><strong>{CONTACT_EMAIL}</strong></a></p>

    <h3>What to include</h3>
    <ul>
      <li><strong>Bug reports:</strong> the tool you were using, what you expected, what happened, and your browser / device if relevant.</li>
      <li><strong>Corrections:</strong> the page URL and what you believe should be changed, with a source if possible.</li>
      <li><strong>Feature requests:</strong> the problem you're trying to solve (not just the feature idea).</li>
      <li><strong>Press / partnerships:</strong> who you are, what you're proposing, and a deadline if you have one.</li>
    </ul>

    <h2>Quick message form</h2>
    <div class="contact-form">
      <form id="contactForm" onsubmit="return handleContactSubmit(event)">
        <div class="form-row">
          <label for="cf-name">Your name</label>
          <input type="text" id="cf-name" name="name" required autocomplete="name">
        </div>
        <div class="form-row">
          <label for="cf-email">Email</label>
          <input type="email" id="cf-email" name="email" required autocomplete="email">
        </div>
        <div class="form-row">
          <label for="cf-topic">Topic</label>
          <select id="cf-topic" name="topic" required>
            <option value="">Pick one…</option>
            <option value="bug">Bug report</option>
            <option value="correction">Correction</option>
            <option value="feature">Feature request</option>
            <option value="press">Press / partnerships</option>
            <option value="privacy">Privacy / data request</option>
            <option value="other">Something else</option>
          </select>
        </div>
        <div class="form-row">
          <label for="cf-message">Message</label>
          <textarea id="cf-message" name="message" required placeholder="Tell us what's on your mind…"></textarea>
        </div>
        <div class="form-row">
          <button type="submit"><i class="fas fa-paper-plane"></i> Send message</button>
        </div>
      </form>
      <p id="cf-status" style="font-size: 0.9rem; color: var(--c-muted); margin-top: 12px;"></p>
    </div>

    <h2>Privacy &amp; data requests</h2>
    <p>If you are submitting a GDPR, CCPA, or CPRA-related request (access, correction, deletion, opt-out), please select "Privacy / data request" as the topic or email us directly at <a href="mailto:{PRIVACY_EMAIL}">{PRIVACY_EMAIL}</a> with "Privacy request" in the subject line.</p>

    <h2>Press</h2>
    <p>For press and media inquiries, please include your publication, deadline, and any specific data or quotes you need. Our brand assets (logo, screenshots, short bio) are available on request. Press contacts can write directly to <a href="mailto:{PRESS_EMAIL}">{PRESS_EMAIL}</a>.</p>

    <h2>Publisher</h2>
    <p><strong>{ENTITY}</strong><br>
    <em>FuelEcon is an independent publication of {ENTITY}.</em></p>

    <div class="callout info">
      <strong>Not a help desk:</strong> If you're asking "what's the best MPG for my commute?" — you probably want the <a href="/">trip calculator</a> itself. We're happy to answer product questions, but we can't give personalized driving or vehicle-purchase advice.
    </div>

  </article>

  <script>
    /* Contact form: opens the user's mail client with a pre-filled draft.
       Phase 3 will replace this with a Pages Function that forwards to our inbox. */
    function handleContactSubmit(e) {{
      e.preventDefault();
      const name    = document.getElementById('cf-name').value.trim();
      const email   = document.getElementById('cf-email').value.trim();
      const topic   = document.getElementById('cf-topic').value;
      const message = document.getElementById('cf-message').value.trim();
      const status  = document.getElementById('cf-status');

      if (!name || !email || !topic || !message) {{
        status.textContent = 'Please fill in all fields.';
        status.style.color = 'var(--c-warn)';
        return false;
      }}

      const subject = encodeURIComponent(`[FuelEcon · ${{topic}}] from ${{name}}`);
      const body    = encodeURIComponent(`${{message}}\\n\\n—\\nFrom: ${{name}} <${{email}}>`);
      window.location.href = `mailto:{CONTACT_EMAIL}?subject=${{subject}}&body=${{body}}`;

      status.textContent = 'Opening your email client… if nothing happens, please email {CONTACT_EMAIL} directly.';
      status.style.color = 'var(--c-primary)';
      return false;
    }}
  </script>
"""


# ------------------------------------------------------------------
# Build
# ------------------------------------------------------------------
PAGES = [
    ("about",      "About",                    "Who's behind FuelEcon, what we build, and where our data comes from.", ABOUT),
    ("privacy",    "Privacy Policy",           "What data FuelEcon collects, why we collect it, and the controls you have over it.", PRIVACY),
    ("terms",      "Terms of Use",             "The ground rules for using FuelEcon. Plain language, with the legal bits where they matter.", TERMS),
    ("disclosure", "Advertising Disclosure",   "How FuelEcon makes money, and how we keep that separate from what we recommend.", DISCLOSURE),
    ("contact",    "Contact",                  "Feedback, corrections, press, or partnerships — we read everything.", CONTACT),
]

def build():
    for slug, title, description, body in PAGES:
        out_path = PUBLIC / slug / "index.html"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(layout(slug, title, description, body), encoding="utf-8")
        print(f"✓ built {out_path.relative_to(PUBLIC.parent)}")

if __name__ == "__main__":
    build()
