#!/usr/bin/env python3
"""Build all OptioHire informational pages from shared chrome + tokens."""

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
SIGNUP = "https://optiohire.com/auth/options?mode=signup"
CANDIDATE = "https://applications.optiohire.com/auth/signup"
HR_SIGNIN = "https://optiohire.com/hr/auth/signin"
CANDIDATE_SIGNIN = "https://applications.optiohire.com/auth/signin"
INSTITUTION_SIGNIN = "https://optiohire.com/institutions"

NAV = [
    ("How it Works", "how-it-works.html"),
    ("Employers", "for-employers.html"),
    ("HR Teams", "for-hr-teams.html"),
    ("Candidates", "for-candidates.html"),
    ("Institutions", "for-institutions.html"),
    ("Resources", "resources.html"),
    ("About", "about.html"),
]

ARROW = """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>"""

ICONS = {
    "inbox": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></svg>',
    "scan": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2M7 12h10"/></svg>',
    "scale": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10M12 3v18M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>',
    "list": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m3 17 2 2 4-4M3 7l2 2 4-4M13 6h8M13 12h8M13 18h8"/></svg>',
    "cal": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 2v4M16 2v4M3 10h18M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/></svg>',
    "trophy": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6M18 9h1.5a2.5 2.5 0 0 0 0-5H18M4 22h16M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>',
    "zap": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/><path d="m9 12 2 2 4-4"/></svg>',
    "eye": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>',
    "building": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2M10 6h4M10 10h4M10 14h4M10 18h4"/></svg>',
    "users": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    "checkuser": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><polyline points="16 11 18 13 22 9"/></svg>',
    "grad": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>',
    "rocket": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/></svg>',
    "quote": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="32" height="32"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z"/></svg>',
}


def chip(icon):
    return f'<div class="icon-chip" aria-hidden="true">{ICONS[icon]}</div>'


OG_IMAGE = "https://optiohire.com/assets/og/og-default.jpg"
SITE = "https://optiohire.com"
DEMO = "contact.html?type=Demo%20Request"
SALES = "contact.html?type=Talk%20to%20Sales"
# CASA: paste real IDs before launch. Empty values mean tags are reserved but not loaded.
GA_MEASUREMENT_ID = ""  # e.g. G-XXXXXXXXXX
GSC_VERIFICATION = ""  # Google Search Console meta content


def logo_wall(count=8, label="Partner institution", blurbs=None):
    """Reusable partner logo grid - shared by /for-institutions and /partners."""
    if blurbs is True:
        blurbs = ["Program / department TBD"] * count
    slots = []
    for i in range(count):
        extra = ""
        if blurbs:
            text = blurbs[i] if i < len(blurbs) else "Program / department TBD"
            extra = f'<p class="logo-slot-blurb">{text}</p>'
        slots.append(
            f'<div class="logo-slot" role="listitem">'
            f'<span class="logo-slot-name">{label}</span>'
            f'<div class="placeholder-note">Logo to be supplied</div>'
            f"{extra}</div>"
        )
    return f'<div class="logo-wall" role="list">{"".join(slots)}</div>'


def logo_imgs(prefix, loading=None):
    variants = (
        ("dark", "OptioHire logo, coral mark on near-black"),
        ("navy", "OptioHire logo, coral mark on navy"),
        ("teal", "OptioHire logo, teal mark on deep teal"),
        ("white", "OptioHire logo, burnt-orange mark on white"),
    )
    extras = ' decoding="async"'
    if loading:
        extras += f' loading="{loading}"'
    return "".join(
        f'<img class="logo-asset" data-logo="{key}" src="{prefix}assets/logos/logo-{key}.jpg" alt="{alt}" width="400" height="235"{extras}>'
        for key, alt in variants
    )


def socials():
    return """
      <div class="socials">
        <a href="https://www.linkedin.com/company/optiohire" aria-label="OptioHire on LinkedIn" rel="noopener" target="_blank">
          <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
        </a>
        <a href="https://x.com/optiohire" aria-label="OptioHire on X" rel="noopener" target="_blank">
          <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.727-8.835L1.254 2.25H8.08l4.251 5.69L18.244 2.25zm-1.161 17.52h1.833L7.084 4.126H5.117L17.083 19.77z"/></svg>
        </a>
        <a href="https://www.instagram.com/optiohire" aria-label="OptioHire on Instagram" rel="noopener" target="_blank">
          <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
        </a>
      </div>"""


def signin_menu():
    return f"""
      <div class="signin-wrap">
        <button class="sign-in" type="button" data-signin-toggle aria-expanded="false" aria-haspopup="true">Sign In</button>
        <div class="signin-menu" data-signin-menu hidden role="menu">
          <a href="{HR_SIGNIN}" role="menuitem">HR / Employer<span>Workspace sign in</span></a>
          <a href="{CANDIDATE_SIGNIN}" role="menuitem">Candidate<span>Applications portal</span></a>
          <a href="{INSTITUTION_SIGNIN}" role="menuitem">Institution<span>Campus console</span></a>
        </div>
      </div>"""


def header(current, theme="dark", prefix=""):
    links = []
    for label, href in NAV:
        cur = ' aria-current="page"' if href == current else ""
        links.append(f'<a href="{prefix}{href}"{cur}>{label}</a>')
    nav = "\n          ".join(links)
    return f"""
<header class="site-header theme-{theme}" data-site-header data-initial-theme="{theme}">
  <div class="wrap header-inner">
    <a class="logo" href="{prefix}index.html" aria-label="OptioHire home">
      {logo_imgs(prefix)}
    </a>
    <nav class="nav-desktop" aria-label="Primary">{nav}</nav>
    <div class="header-actions">
      {signin_menu()}
      <a class="btn btn-primary" href="{SIGNUP}">Get Started</a>
      <button class="menu-toggle" type="button" data-menu-toggle aria-expanded="false" aria-label="Open menu"><span></span></button>
    </div>
  </div>
  <div class="nav-mobile" data-nav-mobile aria-hidden="true">
    <nav class="mobile-links" aria-label="Mobile">{nav}</nav>
    <div class="mobile-cta">
      <div class="mobile-signin">
        <a href="{HR_SIGNIN}">HR / Employer<small>Workspace sign in</small></a>
        <a href="{CANDIDATE_SIGNIN}">Candidate<small>Applications portal</small></a>
        <a href="{INSTITUTION_SIGNIN}">Institution<small>Campus console</small></a>
      </div>
      <a class="btn btn-primary" href="{SIGNUP}">Get Started</a>
    </div>
  </div>
</header>"""


def footer(prefix=""):
    return f"""
<footer class="site-footer theme-dark">
  <div class="wrap">
    <div class="footer-brand">
      <a class="logo" href="{prefix}index.html" aria-label="OptioHire home">
        {logo_imgs(prefix, loading="lazy")}
      </a>
      <p class="footer-tagline">Hire on capability - not CV volume.</p>
    </div>
    <div class="footer-grid">
    <nav aria-label="Product">
      <h4>Product</h4>
      <a href="{prefix}index.html">Home</a>
      <a href="{prefix}how-it-works.html">How it Works</a>
      <a href="{prefix}use-cases.html">Use Cases</a>
      <a href="{prefix}resources.html">Resources</a>
      <a href="{prefix}pricing.html">Pricing</a>
    </nav>
    <nav aria-label="For you">
      <h4>For You</h4>
      <a href="{prefix}for-employers.html">Employers</a>
      <a href="{prefix}for-hr-teams.html">HR Teams</a>
      <a href="{prefix}for-candidates.html">Candidates</a>
      <a href="{prefix}for-institutions.html">Institutions</a>
    </nav>
    <nav aria-label="Company">
      <h4>Company</h4>
      <a href="{prefix}about.html">About</a>
      <a href="{prefix}partners.html">Partners</a>
      <a href="{prefix}customers.html">Customers</a>
      <a href="{prefix}contact.html">Contact</a>
    </nav>
    <nav aria-label="Legal">
      <h4>Legal</h4>
      <a href="{prefix}privacy.html">Privacy Policy</a>
      <a href="{prefix}terms.html">Terms of Service</a>
      <a href="{prefix}security.html">Security &amp; Compliance</a>
      <button type="button" class="linkish" data-cookie-settings>Cookie settings</button>
    </nav>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <div class="footer-meta">
      <a href="mailto:developer@optiohire.com">developer@optiohire.com</a>
      <span>Nairobi, Kenya</span>
    </div>
    {socials()}
    <p class="footer-copy">© 2026 OptioHire · Built by <a href="https://cresdynamics.com" rel="noopener" target="_blank">Cres Dynamics</a></p>
  </div>
</footer>"""


def canonical_url(filename):
    if filename in ("index.html", "", None):
        return f"{SITE}/"
    if filename.startswith("resources/") or filename.startswith("customers/"):
        return f"{SITE}/{filename.replace('.html', '')}"
    return f"{SITE}/{filename.replace('.html', '')}"


def breadcrumbs(items, prefix=""):
    if not items:
        return "", ""
    parts = []
    schema = []
    for i, (label, href) in enumerate(items, 1):
        last = i == len(items)
        if href and not last:
            parts.append(f'<a href="{prefix}{href}">{html.escape(label)}</a>')
        else:
            parts.append(f'<span aria-current="page">{html.escape(label)}</span>')
        if i > 1:
            pass
        item = {
            "@type": "ListItem",
            "position": i,
            "name": label,
        }
        if href:
            clean = href.split("?")[0]
            item["item"] = canonical_url(clean)
        schema.append(item)
    html_nav = (
        '<nav class="crumbs wrap" aria-label="Breadcrumb">'
        + '<span class="crumbs-sep" aria-hidden="true"> / </span>'.join(parts)
        + "</nav>"
    )
    payload = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": schema}
    extra = f'<script type="application/ld+json">{json.dumps(payload, ensure_ascii=False)}</script>'
    return html_nav, extra


def cookie_chrome(prefix=""):
    return f"""
<div class="cookie-banner" data-cookie-banner role="dialog" aria-label="Cookie consent">
  <div class="cookie-inner">
    <p class="cookie-copy">We use cookies to improve your experience and understand how OptioHire is used. By continuing, you agree to our use of cookies. Read the <a href="{prefix}privacy.html">Privacy Policy</a>.</p>
    <div class="cookie-actions">
      <button class="btn btn-primary" type="button" data-cookie-accept>Accept</button>
      <button class="btn btn-text" type="button" data-cookie-manage>Manage preferences</button>
    </div>
  </div>
</div>
<div class="cookie-modal" data-cookie-modal hidden>
  <div class="cookie-dialog" role="dialog" aria-labelledby="cookie-title">
    <h2 id="cookie-title">Cookie preferences</h2>
    <p class="form-note">Non-essential cookies stay off until you opt in - required under Kenya's Data Protection Act (2019).</p>
    <div class="cookie-pref">
      <p><strong>Essential</strong> Needed for the site to work. Always on.</p>
      <input type="checkbox" checked disabled>
    </div>
    <div class="cookie-pref">
      <p><strong>Analytics</strong> Helps us understand how pages are used. Off until you agree.</p>
      <input type="checkbox" name="analytics">
    </div>
    <div class="cookie-pref">
      <p><strong>Marketing</strong> Used only if we run campaigns. Off until you agree.</p>
      <input type="checkbox" name="marketing">
    </div>
    <div class="cta-row" style="margin-top:1.1rem">
      <button class="btn btn-primary" type="button" data-cookie-save>Save preferences</button>
      <button class="btn btn-text" type="button" data-cookie-close>Close</button>
    </div>
  </div>
</div>
"""


def page(title, description, filename, body, theme="dark", extra_head="", canonical=None, prefix="", og_type="website", crumbs=None, og_image=None, robots="index, follow", body_class=""):
    path = canonical or canonical_url(filename)
    esc_title = html.escape(title, quote=True)
    esc_desc = html.escape(description, quote=True)
    img = og_image or OG_IMAGE
    crumb_html, crumb_schema = breadcrumbs(crumbs, prefix) if crumbs else ("", "")
    gsc = (
        f'\n  <meta name="google-site-verification" content="{html.escape(GSC_VERIFICATION, quote=True)}">'
        if GSC_VERIFICATION
        else ""
    )
    ga_attr = f' data-ga-id="{html.escape(GA_MEASUREMENT_ID, quote=True)}"' if GA_MEASUREMENT_ID else ""
    page_slug = filename.replace(".html", "").replace("/", "-") or "home"
    return f"""<!DOCTYPE html>
<html lang="en"{ga_attr}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc_title}</title>
  <meta name="description" content="{esc_desc}">
  <meta name="author" content="OptioHire · Cres Dynamics">
  <meta name="robots" content="{robots}">
  <link rel="canonical" href="{path}">
  <meta property="og:title" content="{esc_title}">
  <meta property="og:description" content="{esc_desc}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="OptioHire">
  <meta property="og:url" content="{path}">
  <meta property="og:image" content="{img}">
  <meta property="og:image:alt" content="OptioHire">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc_title}">
  <meta name="twitter:description" content="{esc_desc}">
  <meta name="twitter:image" content="{img}">
  <link rel="icon" href="{prefix}assets/icons/favicon.svg" type="image/svg+xml">
  <link rel="icon" href="{prefix}assets/icons/favicon-32x32.png" type="image/png" sizes="32x32">
  <link rel="icon" href="{prefix}assets/icons/favicon-16x16.png" type="image/png" sizes="16x16">
  <link rel="apple-touch-icon" href="{prefix}assets/icons/apple-touch-icon.png" sizes="180x180">
  <link rel="manifest" href="{prefix}site.webmanifest">
  <meta name="theme-color" content="#0D0D0F">
  {gsc}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{prefix}css/site.min.css">
  {extra_head}
  {crumb_schema}
</head>
<body class="{body_class}" data-page="{page_slug}">
  <a class="skip-link" href="#main">Skip to content</a>
  {header(filename if "/" not in filename else filename.split("/")[-1], theme, prefix)}
  {crumb_html}
  <main id="main">
    {body}
  </main>
  {footer(prefix)}
  {cookie_chrome(prefix)}
  <script src="{prefix}js/main.js"></script>
</body>
</html>
"""


def marquee():
    items = "Skills-first ◆ Fair scoring ◆ Audit-ready ◆ Built in Nairobi ◆ Kenya · East Africa"
    bits = "".join(f'<span>{part.strip()} <span class="diamond" aria-hidden="true">◆</span></span>' for part in items.split("◆"))
    return f'<div class="marquee" aria-hidden="true"><div class="marquee-track">{bits}{bits}{bits}{bits}</div></div>'


def x_items(*items):
    return "<ul class='x-list'>" + "".join(f'<li><span class="x-badge" aria-hidden="true">✕</span>{i}</li>' for i in items) + "</ul>"


HOME = f"""
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">Hiring platform · Built in Africa</p>
    <h1>Hiring isn't broken by a lack of talent. It's missing the engine.</h1>
    <p class="lede">OptioHire receives applications, screens CVs, scores candidates fairly, and hands your team interview-ready shortlists - all on one transparent, end-to-end platform.</p>
    <div class="cta-row">
      <a class="btn btn-primary" href="{SIGNUP}">Start Free Trial {ARROW}</a>
      <a class="btn btn-text" href="how-it-works.html">See how it works</a>
    </div>
    <p class="trust-line">Trusted by modern recruitment teams · Faster, fairer hiring · Full decision audit trail</p>
  </div>
</section>

<section class="band band-stats theme-teal" data-header-theme="teal">
  <div class="wrap">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value" data-count="0" data-suffix="+">0+</div>
        <p class="stat-label">Applications screened</p>
      </div>
      <div class="stat-card">
        <div class="stat-value" data-count="0" data-suffix="h">0h</div>
        <p class="stat-label">Avg. time to shortlist</p>
      </div>
      <div class="stat-card">
        <div class="stat-value" data-count="0" data-suffix="x">0x</div>
        <p class="stat-label">Faster hiring cycles</p>
      </div>
      <div class="stat-card">
        <div class="stat-value" data-count="0" data-suffix="%">0%</div>
        <p class="stat-label">Decision audit trail</p>
      </div>
    </div>
  </div>
</section>

<section class="band theme-white" data-header-theme="white">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">The stakes</p>
      <h2>Great hires are lost in the pile - every single week.</h2>
      <p class="lede">The volume of applications has outgrown the humans meant to review them. The cost is measured in missed talent, slow cycles, and frustrated candidates.</p>
    </div>
    <div class="grid-4">
      <article class="card stat-card stat-card--sm"><p class="stat-value">300+</p><p class="stat-label">CVs per open role, too many to read fairly</p></article>
      <article class="card stat-card stat-card--sm"><p class="stat-value">4 days</p><p class="stat-label">Manual shortlisting for a single position</p></article>
      <article class="card stat-card stat-card--sm"><p class="stat-value">75%</p><p class="stat-label">Candidates never hear back at all</p></article>
      <article class="card stat-card stat-card--sm"><p class="stat-value">&lt;1%</p><p class="stat-label">Get any actionable feedback</p></article>
    </div>
  </div>
</section>

<section class="band theme-white" data-header-theme="white" style="padding-top:0">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">Why the old way fails</p>
      <h2>The tools exist. A system that actually decides doesn't.</h2>
    </div>
    <div class="grid-3">
      <article class="card icon-list-card"><h3>Manual CV Screening</h3>{x_items("Hours lost per role","Inconsistent judgement","Fatigue = bias")}</article>
      <article class="card icon-list-card"><h3>Generic ATS Tools</h3>{x_items("Keyword box-ticking","No real evaluation","Candidates ghosted")}</article>
      <article class="card icon-list-card"><h3>Spreadsheets &amp; Inboxes</h3>{x_items("No single source of truth","Lost applications","Zero audit trail")}</article>
    </div>
    <p class="closing-line">You don't need another inbox. You need a system.</p>
  </div>
</section>

<section class="band theme-navy" data-header-theme="navy">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">The engine</p>
      <h2>One chain - from application to hire.</h2>
      <p class="lede">Six steps that turn a flooded inbox into a fair, fast, defensible hiring decision.</p>
    </div>
    <div class="steps-grid">
      <article class="card step-card"><div class="step-num">01</div>{chip("inbox")}<h3>Ingest</h3><p>Applications arrive by email or portal - captured automatically.</p></article>
      <article class="card step-card"><div class="step-num">02</div>{chip("scan")}<h3>Parse</h3><p>CVs are read and structured into clean, comparable data.</p></article>
      <article class="card step-card"><div class="step-num">03</div>{chip("scale")}<h3>Score</h3><p>Every candidate is evaluated against the same role criteria.</p></article>
      <article class="card step-card"><div class="step-num">04</div>{chip("list")}<h3>Shortlist</h3><p>Interview-ready rankings with transparent reasoning.</p></article>
      <article class="card step-card"><div class="step-num">05</div>{chip("cal")}<h3>Interview</h3><p>Schedule and message candidates from one place.</p></article>
      <article class="card step-card"><div class="step-num">06</div>{chip("trophy")}<h3>Hire</h3><p>Decide with confidence - and a full audit trail.</p></article>
    </div>
  </div>
</section>

<section class="band theme-white" data-header-theme="white">
  <div class="wrap">
    <div class="section-head section-head--center">
      <h2>One platform, every path. Where do you fit in?</h2>
    </div>
    <div class="grid-4">
      <a class="card audience-card" href="for-employers.html">{chip("building")}<h3>Employers &amp; HR</h3><p>Screen, score and shortlist with confidence.</p><span class="card-link">Explore {ARROW}</span></a>
      <a class="card audience-card" href="for-hr-teams.html">{chip("checkuser")}<h3>Recruiters</h3><p>Fill roles faster with ranked, evidence-based pipelines.</p><span class="card-link">Explore {ARROW}</span></a>
      <a class="card audience-card" href="for-candidates.html">{chip("users")}<h3>Job Seekers</h3><p>Apply once, track everything, get real feedback.</p><span class="card-link">Explore {ARROW}</span></a>
      <a class="card audience-card" href="for-institutions.html">{chip("shield")}<h3>Enterprises / Institutions</h3><p>One scorecard and audit trail across every department.</p><span class="card-link">Explore {ARROW}</span></a>
    </div>
  </div>
</section>

<section class="band theme-teal" data-header-theme="teal">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">Why we exist</p>
      <h2>Close the gap between a CV and real capability.</h2>
    </div>
    <div class="grid-3">
      <article class="card icon-list-card pillar-card"><span class="pillar-initial">F</span><h3>Fairness</h3><p>Every candidate is judged on the same criteria - structure over gut feel.</p></article>
      <article class="card icon-list-card pillar-card"><span class="pillar-initial">S</span><h3>Speed</h3><p>Shortlists in hours, not weeks. Momentum wins the best people.</p></article>
      <article class="card icon-list-card pillar-card"><span class="pillar-initial">T</span><h3>Transparency</h3><p>Clear reasoning and a full audit trail behind every decision.</p></article>
    </div>
  </div>
</section>

<section class="band theme-white" data-header-theme="white">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">Real journeys</p>
      <h2>From stuck to hired - step by step.</h2>
    </div>
    <div class="testimonial-track">
      <article class="card testimonial-card"><div class="quote-mark">{ICONS["quote"]}</div><p class="quote">We went from four days of CV marathons to a ranked shortlist the same morning. Our hiring managers finally trust the process.</p><div class="person"><span class="avatar">AK</span><div><strong>Amina K.</strong><span>Head of People, Scaling SME</span></div></div></article>
      <article class="card testimonial-card"><div class="quote-mark">{ICONS["quote"]}</div><p class="quote">The audit trail alone is worth it. When a candidate asks why, we have a clear, consistent answer every time.</p><div class="person"><span class="avatar">DM</span><div><strong>David M.</strong><span>Talent Lead, High-growth Startup</span></div></div></article>
      <article class="card testimonial-card"><div class="quote-mark">{ICONS["quote"]}</div><p class="quote">As a candidate I actually knew where I stood. Applied once, tracked everything, got real feedback. Rare.</p><div class="person"><span class="avatar">BO</span><div><strong>Brian O.</strong><span>Software Engineer</span></div></div></article>
    </div>
  </div>
</section>

<section class="band theme-dark cta-band" data-header-theme="dark">
  <div class="wrap">
    <h2>The future of hiring is being built right now.</h2>
    <p class="lede">Screen smarter, decide fairer, and hire faster - all in one place.</p>
    <div class="cta-row" style="justify-content:center">
      <a class="btn btn-primary" href="{SIGNUP}">Start Free Trial {ARROW}</a>
    </div>
  </div>
  {marquee()}
</section>
"""

HOW = f"""
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">The Process</p>
    <h1>Three hundred applicants down to your best five.</h1>
    <p class="lede">Built for HR managers and hiring leads who need one place to post a role, receive every application, get candidates ranked fairly by AI, and move the right people to interview - faster than doing it by hand ever could.</p>
  </div>
  <div class="wrap">
    <div class="stats-grid stats-grid-3 stats-grid--hero">
      <div class="stat-card">
        <div class="stat-value" data-count="0" data-suffix="x">0x</div>
        <p class="stat-label">Quicker shortlisting, even on high-volume roles</p>
      </div>
      <div class="stat-card">
        <div class="stat-value" data-count="0" data-suffix="%">0%</div>
        <p class="stat-label">Strong candidates surfaced on the first pass</p>
      </div>
      <div class="stat-card">
        <div class="stat-value" data-count="0" data-suffix="%">0%</div>
        <p class="stat-label">Fewer spreadsheets, threads, and inbox chaos</p>
      </div>
    </div>
    <p class="lede hero-note">Every stage stays visible and traceable, so your team can back up a hiring call with real reasoning, and candidates get treated professionally throughout.</p>
    <div class="cta-row" style="justify-content:center">
      <a class="btn btn-text" href="#process">See the process</a>
      <a class="btn btn-primary" href="{SIGNUP}">Start free trial {ARROW}</a>
    </div>
  </div>
</section>

<section class="band theme-white" data-header-theme="white" id="process">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">From posting to hire</p>
      <h2>A workflow built for how real hiring teams actually operate.</h2>
    </div>
    <div class="stages">
      <article class="card step-card step-card--lg">
        <div class="step-num">01</div>
        <h3>Post the role, gather every application</h3>
        <p>Your team sets up a job listing with the requirements that actually matter for the role. Every candidate who applies through your channel lands in a single pipeline, sorted to the right opening automatically.</p>
        <ul class="check-list">
          <li>Requirements laid out clearly upfront</li>
          <li>Applications sorted to the correct job, no manual filing</li>
          <li>One pipeline per role instead of scattered inboxes</li>
        </ul>
      </article>
      <article class="card step-card step-card--lg">
        <div class="step-num">02</div>
        <h3>Fair, AI-assisted ranking</h3>
        <p>Each applicant gets compared against the role's actual requirements, with the reasoning behind every score laid out plainly. Candidates land in shortlist, flagged, or not-a-fit categories, using identical criteria for everyone.</p>
        <ul class="check-list">
          <li>Scoring tied directly to the role's requirements</li>
          <li>HR can see exactly why a candidate scored the way they did</li>
          <li>Same standard applied to every applicant, no drift</li>
        </ul>
      </article>
      <article class="card step-card step-card--lg">
        <div class="step-num">03</div>
        <h3>Keep candidates informed, book interviews fast</h3>
        <p>Outcome messages go out automatically as candidates move through the pipeline. For anyone shortlisted, your team can schedule interviews and send meeting invites right from the dashboard, with the full history of that decision on record.</p>
        <ul class="check-list">
          <li>Shortlist and rejection updates sent without manual follow-up</li>
          <li>Interview scheduling in a couple of clicks</li>
          <li>A complete record behind every decision, ready if anyone asks</li>
        </ul>
      </article>
    </div>
  </div>
</section>

<section class="band theme-navy" data-header-theme="navy">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">What each side of the process sees</p>
      <h2>Built for HR judgement - and for candidates who deserve an answer.</h2>
    </div>
    <div class="split">
      <article class="card icon-list-card">
        <h3>Inside the HR dashboard</h3>
        <ul class="check-list">
          <li>A single view of every candidate for a role, with status, score, and reasoning side by side</li>
          <li>Match strength shown per candidate, not just a pass/fail flag</li>
          <li>Key skills, relevant experience, and any red flags surfaced automatically</li>
          <li>Clear shortlist / flagged / not-a-fit labeling, no guesswork</li>
          <li>Ranked recommendations to act on, plus a full scoring breakdown per candidate</li>
          <li>Interview scheduling and a record of every message sent, all in one place</li>
        </ul>
      </article>
      <article class="card icon-list-card">
        <h3>What it feels like to apply</h3>
        <ul class="check-list">
          <li>Every applicant assessed against the same standard, regardless of who they are or where they come from</li>
          <li>A real answer instead of silence - status updates that actually arrive</li>
          <li>Personal data handled carefully, with privacy and professionalism throughout the process</li>
        </ul>
      </article>
    </div>
  </div>
</section>

<section class="band theme-teal" data-header-theme="teal">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">What changes for teams that switch</p>
      <h2>Faster cycles. Better hires. Less wasted effort.</h2>
    </div>
    <div class="stats-grid stats-grid-3">
      <div class="stat-card">
        <div class="stat-value" data-count="0" data-suffix="x">0x</div>
        <p class="stat-label">Faster hiring process</p>
      </div>
      <div class="stat-card">
        <div class="stat-value" data-count="0" data-suffix="%">0%</div>
        <p class="stat-label">Improvement in hire quality</p>
      </div>
      <div class="stat-card">
        <div class="stat-value" data-count="0" data-suffix="%">0%</div>
        <p class="stat-label">Reduction in time wasted on screening</p>
      </div>
    </div>
    <p class="evidence-note">Only verified customer results get published here - case studies and named testimonials will appear as they're confirmed.</p>
    <div class="case-slots" aria-label="Case study placeholders">
      <a class="card case-slot" href="customers.html"><p class="eyebrow">Case study</p><h3>Coming soon</h3><p>A verified customer story will sit here once approved for publication.</p></a>
      <a class="card case-slot" href="customers.html"><p class="eyebrow">Case study</p><h3>Coming soon</h3><p>A verified customer story will sit here once approved for publication.</p></a>
      <a class="card case-slot" href="customers.html"><p class="eyebrow">Case study</p><h3>Coming soon</h3><p>A verified customer story will sit here once approved for publication.</p></a>
    </div>
  </div>
</section>

<section class="band theme-dark cta-band" data-header-theme="dark">
  <div class="wrap">
    <h2>See what a real hiring workflow feels like.</h2>
    <p class="lede">Replace the scattered steps - email threads, spreadsheets, guesswork - with one workflow your team can actually trust, from the first application to a booked interview.</p>
    <div class="cta-row" style="justify-content:center">
      <a class="btn btn-primary" href="{SIGNUP}">Start free trial {ARROW}</a>
      <a class="btn btn-outline" href="for-institutions.html">Apply as enterprise</a>
    </div>
  </div>
</section>
"""

EMPLOYERS = f"""
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">For Employers &amp; Hiring Companies</p>
    <h1>Hire on merit, not on who reads fastest.</h1>
    <p class="lede">When two hundred people apply for one role, the best candidate shouldn't depend on whoever happened to skim the pile last. OptioHire gives your team a consistent, defensible way to find the right hire - quickly.</p>
    <div class="cta-row">
      <a class="btn btn-primary" href="{SIGNUP}">Start hiring {ARROW}</a>
      <a class="btn btn-text" href="how-it-works.html">See the workflow</a>
    </div>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">What's actually costing you</p>
      <h2>Every extra day a role stays open is a day your competitors move faster.</h2>
      <p class="lede">Manual review doesn't scale past a handful of applicants. Past that point, decisions get inconsistent, good candidates fall through, and nobody can fully explain afterward why one person got the offer and another didn't.</p>
    </div>
    <div class="grid-3">
      <article class="card icon-list-card">{chip("zap")}<h3>Slow cycles</h3><p>Slow cycles cost you top candidates to competitors.</p></article>
      <article class="card icon-list-card">{chip("scale")}<h3>Inconsistent review</h3><p>Inconsistent review invites bias and disputes.</p></article>
      <article class="card icon-list-card">{chip("shield")}<h3>No clear record</h3><p>No clear record if a hiring decision gets questioned later.</p></article>
    </div>
  </div>
</section>
<section class="band theme-white" data-header-theme="white" style="padding-top:0">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">What changes once you switch</p>
      <h2>A faster, fairer path from job post to signed offer.</h2>
    </div>
    <div class="grid-4">
      <article class="card icon-list-card">{chip("zap")}<h3>Shortlisting in a fraction of the time</h3><p>Move from a full applicant pool to a ranked shortlist in hours, not days.</p></article>
      <article class="card icon-list-card">{chip("scale")}<h3>Scoring that treats everyone the same</h3><p>Every applicant measured against identical role criteria, reducing fatigue-driven inconsistency.</p></article>
      <article class="card icon-list-card">{chip("shield")}<h3>A record behind every decision</h3><p>Full reasoning trail your team can point to, internally or with a candidate who asks.</p></article>
      <article class="card icon-list-card">{chip("eye")}<h3>Visibility as applications roll in</h3><p>Know the moment a role hits a meaningful applicant threshold, instead of checking manually.</p></article>
    </div>
  </div>
</section>
<section class="band theme-navy" data-header-theme="navy">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">What this looks like in practice</p>
      <h2>Monday: post the role. Wednesday: review your shortlist.</h2>
      <p class="lede narrative">A hiring manager posts an open role Monday morning with the requirements that matter. By Wednesday, instead of an inbox full of unsorted CVs, they open a ranked shortlist with clear reasoning behind each name - and move straight to scheduling interviews with the top candidates.</p>
    </div>
  </div>
</section>
<section class="band theme-dark cta-band" data-header-theme="dark">
  <div class="wrap">
    <h2>Ready to hire without the guesswork?</h2>
    <div class="cta-row" style="justify-content:center"><a class="btn btn-primary" href="{SIGNUP}" data-track="start_free_trial" data-utm-campaign="employers">Start hiring {ARROW}</a>
      <a class="btn btn-outline" href="{DEMO}" data-track="book_demo">Book a demo</a>
    </div>
  </div>
</section>
"""

HR = f"""
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">For HR Teams &amp; Recruiters</p>
    <h1>One workspace, from job post to booked interview.</h1>
    <p class="lede">No more juggling spreadsheets, email threads, and separate scheduling tools. See every candidate, every score, and every next step in one place.</p>
    <div class="cta-row">
      <a class="btn btn-text" href="how-it-works.html">See the workflow</a>
      <a class="btn btn-primary" href="{SIGNUP}">Start free trial {ARROW}</a>
    </div>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">The daily reality</p>
      <h2>Recruiting shouldn't mean rebuilding the same tracker every week.</h2>
      <p class="lede">Manually screening every CV eats hours you don't have. Judgment gets less consistent as fatigue sets in. And when a candidate or hiring manager asks "where are we on this role," the honest answer is often scattered across three different tools.</p>
    </div>
    <div class="grid-3">
      <article class="card icon-list-card">{chip("zap")}<h3>Hours lost</h3><p>Hours lost to manual review, every single week.</p></article>
      <article class="card icon-list-card">{chip("scale")}<h3>Fatigue</h3><p>Consistency slips as reviewer fatigue builds.</p></article>
      <article class="card icon-list-card">{chip("inbox")}<h3>Scattered tools</h3><p>No single source of truth across the team.</p></article>
    </div>
  </div>
</section>
<section class="band theme-white" data-header-theme="white" style="padding-top:0">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">What your workspace actually does</p>
      <h2>Everything your team needs to run a role, without leaving the platform.</h2>
    </div>
    <div class="grid-4">
      <article class="card icon-list-card">{chip("eye")}<h3>One candidate view per role</h3><p>Status, score, and reasoning together - instantly clear who to move forward, flag, or pass on.</p></article>
      <article class="card icon-list-card">{chip("list")}<h3>Built-in decision support</h3><p>Ranked recommendations and a detailed scoring breakdown, so you're never starting from a blank read.</p></article>
      <article class="card icon-list-card">{chip("cal")}<h3>Scheduling without the back-and-forth</h3><p>Book interviews and send invites directly to shortlisted candidates.</p></article>
      <article class="card icon-list-card">{chip("inbox")}<h3>A full communication history</h3><p>Every outcome message sent is logged automatically - nothing gets lost or duplicated.</p></article>
    </div>
  </div>
</section>
<section class="band theme-navy" data-header-theme="navy">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">What this looks like in practice</p>
      <h2>From "just posted" to "five interviews booked" - same week.</h2>
      <p class="lede narrative">An HR coordinator posts a role Monday, watches applications land in one pipeline through the week, reviews a ranked shortlist by Thursday, and has five interviews booked directly from the dashboard by Friday - no spreadsheet, no separate scheduling tool, no lost thread.</p>
    </div>
  </div>
</section>
<section class="band theme-dark cta-band" data-header-theme="dark">
  <div class="wrap">
    <h2>Give your team a workflow that keeps up.</h2>
    <div class="cta-row" style="justify-content:center"><a class="btn btn-primary" href="{SIGNUP}">Start free trial {ARROW}</a></div>
  </div>
</section>
"""

CANDIDATES = f"""
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">For Job Seekers &amp; Students</p>
    <h1>Apply once. Know exactly where you stand.</h1>
    <p class="lede">No more sending a CV into silence. Build one profile, apply to roles that fit, and actually see your progress instead of wondering if anyone looked.</p>
    <div class="cta-row">
      <a class="btn btn-primary" href="{CANDIDATE}">Find your next role {ARROW}</a>
      <a class="btn btn-text" href="how-it-works.html">See how it works</a>
    </div>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">What job hunting usually feels like</p>
      <h2>You did the work. You deserve more than silence back.</h2>
      <p class="lede">Most applications disappear into a black hole - no confirmation, no update, no explanation if you don't get through. You're left guessing whether your CV was even opened, let alone fairly considered.</p>
    </div>
    <div class="grid-3">
      <article class="card icon-list-card">{chip("inbox")}<h3>Silence</h3><p>Applications vanish with no response.</p></article>
      <article class="card icon-list-card">{chip("eye")}<h3>No visibility</h3><p>No visibility into where you stand.</p></article>
      <article class="card icon-list-card">{chip("list")}<h3>Empty rejections</h3><p>Rejections, when they come at all, explain nothing.</p></article>
    </div>
  </div>
</section>
<section class="band theme-white" data-header-theme="white" style="padding-top:0">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">What changes for you</p>
      <h2>A process that treats your application like it matters.</h2>
    </div>
    <div class="grid-4">
      <article class="card icon-list-card">{chip("zap")}<h3>One profile, apply everywhere</h3><p>Build your profile once, then apply to roles in a single step - no re-entering the same details each time.</p></article>
      <article class="card icon-list-card">{chip("eye")}<h3>Real status, in real time</h3><p>Check exactly where each application stands, without guessing or emailing to ask.</p></article>
      <article class="card icon-list-card">{chip("scale")}<h3>Judged on what you can actually do</h3><p>Evaluation looks past keyword-matching on a CV, toward real skills and experience.</p></article>
      <article class="card icon-list-card">{chip("cal")}<h3>Interviews scheduled directly</h3><p>Move straight from shortlisted to a booked interview and message the hiring team in the same place.</p></article>
    </div>
  </div>
</section>
<section class="band theme-navy" data-header-theme="navy">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">What this looks like in practice</p>
      <h2>Applied Tuesday. Heard back by Friday - either way.</h2>
      <p class="lede narrative">A candidate builds their profile once, applies to a role that fits their background, and checks their status a few days later without needing to email anyone. Whether the outcome is an interview invite or a clear rejection, they know where they stand instead of being left to wonder.</p>
    </div>
  </div>
</section>
<section class="band theme-dark cta-band" data-header-theme="dark">
  <div class="wrap">
    <h2>Stop applying into the void.</h2>
    <div class="cta-row" style="justify-content:center"><a class="btn btn-primary" href="{CANDIDATE}">Find your next role {ARROW}</a></div>
  </div>
</section>
"""

INSTITUTIONS = f"""
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">For Colleges, Universities &amp; Enterprises</p>
    <h1>Placement outcomes you can actually see, cohort by cohort.</h1>
    <p class="lede">Scale hiring and placement across departments, programs, or entire student cohorts - with one system tracking outcomes instead of scattered spreadsheets per department.</p>
    <div class="cta-row">
      <a class="btn btn-primary" href="contact.html?type=Institution%20Partnership">Apply now {ARROW}</a>
    </div>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">What makes this hard today</p>
      <h2>Placement success shouldn't depend on which department kept the best records.</h2>
      <p class="lede">Coordinating hiring or placement across multiple departments, programs, or student cohorts usually means no shared view of outcomes, inconsistent processes from one program to the next, and no easy way to show partners or leadership what's actually working.</p>
    </div>
    <div class="grid-3">
      <article class="card icon-list-card">{chip("building")}<h3>No unified view</h3><p>No unified view across departments or cohorts.</p></article>
      <article class="card icon-list-card">{chip("list")}<h3>Inconsistent tracking</h3><p>Every program tracking outcomes differently, or not at all.</p></article>
      <article class="card icon-list-card">{chip("shield")}<h3>Hard to prove</h3><p>Hard to prove placement results to partners or leadership.</p></article>
    </div>
  </div>
</section>
<section class="band theme-white" data-header-theme="white" style="padding-top:0">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">What an institutional partnership includes</p>
      <h2>Built to operate at the scale institutions actually need.</h2>
    </div>
    <div class="grid-4">
      <article class="card icon-list-card">{chip("building")}<h3>One scorecard, every department</h3><p>A consistent view and audit trail across teams, programs, or business units.</p></article>
      <article class="card icon-list-card">{chip("grad")}<h3>Cohort-level management</h3><p>Onboard an entire student cohort or intake group and track outcomes as a group, start to finish.</p></article>
      <article class="card icon-list-card">{chip("rocket")}<h3>A guided setup, not a self-serve login</h3><p>Our team walks you through onboarding, configuration, and a tailored rollout for your organization.</p></article>
      <article class="card icon-list-card">{chip("shield")}<h3>A dedicated point of contact</h3><p>A partner who adapts the platform to how your institution or enterprise actually hires or places people.</p></article>
    </div>
  </div>
</section>
<section class="band theme-navy" data-header-theme="navy">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">Working with Kenya's leading institutions</p>
      <h2>Trusted by colleges and universities across the country.</h2>
    </div>
    {logo_wall()}
    <p class="lede" style="margin:1.5rem auto 0;text-align:center">Interested in partnering your institution with OptioHire? <a href="contact.html?type=Institution%20Partnership">Get in touch</a>.</p>
  </div>
</section>
<section class="band theme-dark cta-band" data-header-theme="dark">
  <div class="wrap">
    <h2>Bring structured, fair placement to your entire institution.</h2>
    <div class="cta-row" style="justify-content:center"><a class="btn btn-primary" href="contact.html?type=Institution%20Partnership" data-track="institution_apply">Apply now {ARROW}</a>
      <a class="btn btn-outline" href="{DEMO}" data-track="book_demo">Book a demo</a>
    </div>
  </div>
</section>
"""

_use_cards = "".join(
    f"""<article class="card icon-list-card use-case-card">
      {chip(icon)}
      <h3>{title}</h3>
      <p class="use-label">Situation</p>
      <p>{sit}</p>
      <p class="use-label">What breaks with old tools</p>
      <p>{brk}</p>
      <p class="use-label">How OptioHire handles it</p>
      <p>{how}</p>
    </article>"""
    for icon, title, sit, brk, how in [
        (
            "grad",
            "High-volume graduate hiring",
            "Hundreds of graduate applicants competing for a handful of entry-level roles.",
            "Manual review can't keep pace, and strong candidates get missed simply from reviewer fatigue.",
            "Every applicant scored against the same criteria, so volume stops being the bottleneck.",
        ),
        (
            "scan",
            "Technical &amp; engineering roles",
            "Specialized roles where generic keyword matching misses real capability.",
            "Generic ATS tools filter on buzzwords, not actual skill fit.",
            "Scoring reflects the specific requirements of the role, not just keyword overlap.",
        ),
        (
            "building",
            "Retail &amp; hourly staffing",
            "Frequent, high-turnover hiring across multiple locations or shifts.",
            "Spreadsheets and WhatsApp threads collapse under repeat, high-frequency hiring.",
            "One pipeline per role, repeatable and fast enough to keep up with constant turnover.",
        ),
        (
            "users",
            "Remote-first teams",
            "Hiring across locations with no in-person interview stage to fall back on.",
            "Without face-to-face signals, teams lean too hard on CV formatting and guesswork.",
            "Structured, criteria-based scoring gives a consistent read regardless of location.",
        ),
        (
            "cal",
            "Campus recruitment drives",
            "Recruiting an entire graduating cohort within a tight seasonal window.",
            "Coordinating volume and timing across a whole cohort manually is unmanageable.",
            "Cohort-level tracking keeps a whole intake moving through the pipeline together.",
        ),
        (
            "shield",
            "Multi-department enterprise hiring",
            "Different departments each running their own inconsistent hiring process.",
            "No shared view of outcomes, no consistent standard across teams.",
            "One scorecard and audit trail spans every department.",
        ),
    ]
)

USE = f"""
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">Use Cases</p>
    <h1>Built for how different teams actually hire.</h1>
    <p class="lede">Hiring doesn't look the same for a five-person startup, a university placement office, or a retail chain filling forty shifts a month. Here's how OptioHire fits each situation.</p>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <div class="wrap">
    <div class="grid-3">
      {_use_cards}
    </div>
  </div>
</section>
<section class="band theme-dark cta-band" data-header-theme="dark">
  <div class="wrap">
    <h2>Find the path that fits how your team hires.</h2>
    <div class="cta-row" style="justify-content:center">
      <a class="btn btn-primary" href="{SIGNUP}">Start free trial {ARROW}</a>
    </div>
    <p class="lede" style="margin:1.35rem auto 0.65rem">Explore for your team</p>
    <div class="cta-row" style="justify-content:center">
      <a class="btn btn-text" href="for-employers.html">Employers</a>
      <a class="btn btn-text" href="for-hr-teams.html">HR Teams</a>
      <a class="btn btn-text" href="for-institutions.html">Institutions</a>
    </div>
  </div>
</section>
"""

PARTNERS = f"""
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">Institutional Partners</p>
    <h1>Partnered with Kenya's leading colleges and universities.</h1>
    <p class="lede">We work directly with academic institutions to help graduating cohorts move from classroom to career - with real placement tracking behind it.</p>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">Our partners</p>
      <h2>Institutions working with OptioHire</h2>
    </div>
    {logo_wall(blurbs=True)}
  </div>
</section>
<section class="band theme-teal" data-header-theme="teal">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">How the partnership works</p>
      <h2>A structured path from student to shortlisted candidate.</h2>
    </div>
    <div class="grid-3">
      <article class="card icon-list-card">{chip("grad")}<h3>Cohort onboarding</h3><p>Entire graduating classes or programs onboarded as a group, ready to apply to partner roles.</p></article>
      <article class="card icon-list-card">{chip("rocket")}<h3>Guided setup</h3><p>Our team configures the console and walks your staff through it directly.</p></article>
      <article class="card icon-list-card">{chip("eye")}<h3>Ongoing visibility</h3><p>Placement outcomes tracked and visible to your institution over time.</p></article>
    </div>
  </div>
</section>
<section class="band theme-dark cta-band" data-header-theme="dark">
  <div class="wrap">
    <h2>Bring your institution's cohort onto OptioHire.</h2>
    <div class="cta-row" style="justify-content:center"><a class="btn btn-primary" href="contact.html?type=Institution%20Partnership">Partner with us {ARROW}</a></div>
  </div>
</section>
"""

ABOUT = f"""
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">About OptioHire</p>
    <h1>Built by people who lived the problem first.</h1>
    <p class="lede">OptioHire started from a hard truth: hiring in Kenya doesn't fail from a lack of talent - it fails from a lack of a system that treats every applicant fairly.</p>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">Where this started</p>
      <h2>A job search that didn't go the way it should have.</h2>
      <p class="lede narrative">After relocating to Nairobi, our founder went through a job search that showed, firsthand, how disconnected and impersonal hiring can be for the person on the other side of the application. Hundreds of applications, a small team skimming CVs at night, and the best people vanishing into the pile - he saw that loop from both sides of the table. That experience became the reason Cres Dynamics exists - and, later, the reason OptioHire was built specifically to fix the hiring process itself, not just digitize the old one.</p>
    </div>
  </div>
</section>
<section class="band theme-teal" data-header-theme="teal">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">Why we exist</p>
      <h2>Fairness. Speed. Transparency.</h2>
    </div>
    <div class="grid-3">
      <article class="card icon-list-card pillar-card"><span class="pillar-initial">F</span><h3>Fairness</h3><p>Every candidate measured against the same standard - structure over gut feel, every time.</p></article>
      <article class="card icon-list-card pillar-card"><span class="pillar-initial">S</span><h3>Speed</h3><p>Momentum matters. The best candidates don't wait around for a slow process to catch up.</p></article>
      <article class="card icon-list-card pillar-card"><span class="pillar-initial">T</span><h3>Transparency</h3><p>A decision your team can always explain, backed by a clear reasoning trail.</p></article>
    </div>
  </div>
</section>
<section class="band theme-navy" data-header-theme="navy">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">The company behind the platform</p>
      <h2>OptioHire is a product of Cres Dynamics.</h2>
      <p class="lede narrative"><a href="https://cresdynamics.com">Cres Dynamics</a> is a Nairobi-based software and systems development company. OptioHire is built and maintained by that same team - meaning it's backed by an established systems house, not a standalone experiment.</p>
    </div>
  </div>
</section>
<section class="band theme-white band-compact" data-header-theme="white">
  <div class="wrap" style="text-align:center">
    <p class="location-line">Based in Nairobi, Kenya - building for East Africa's hiring teams.</p>
  </div>
</section>
<section class="band theme-dark cta-band" data-header-theme="dark">
  <div class="wrap">
    <h2>See what a fairer hiring process looks like.</h2>
    <div class="cta-row" style="justify-content:center">
      <a class="btn btn-primary" href="{SIGNUP}">Start free trial {ARROW}</a>
    </div>
  </div>
</section>
"""

# Additional Comparisons titles to draft later (do not name a competitor product
# without Nelson's sign-off):
# - OptioHire vs. spreadsheet-based hiring: what changes
# - What sets a Kenya-built hiring platform apart from global tools
ARTICLES = [
    {
        "file": "why-candidates-never-hear-back.html",
        "slug": "why-candidates-never-hear-back",
        "category": "Hiring Trends",
        "title": "Why so many strong candidates never hear back",
        "excerpt": "A look at what happens to applications after they're submitted, and why silence has become the default.",
        "date": "2026-07-08",
        "date_label": "8 July 2026",
        "read": "6 min",
        "author": "OptioHire Team",
        "thumb": "articles/never-hear-back.svg",
        "alt": "Abstract illustration of applications fading into an unread inbox",
    },
    {
        "file": "cv-screening-bias.html",
        "slug": "cv-screening-bias",
        "category": "HR Playbooks",
        "title": "What CV screening bias actually costs a hiring team",
        "excerpt": "The real cost of inconsistent, fatigue-driven review, and what a structured alternative looks like.",
        "date": "2026-07-22",
        "date_label": "22 July 2026",
        "read": "7 min",
        "author": "OptioHire Team",
        "thumb": "articles/screening-bias.svg",
        "alt": "Abstract illustration of uneven CV stacks being weighed on a tilted scale",
    },
    {
        "file": "shortlisting-in-hours.html",
        "slug": "shortlisting-in-hours",
        "category": "HR Playbooks",
        "title": "Getting from a full inbox to a shortlist in hours, not days",
        "excerpt": "A practical breakdown of what a fast, defensible shortlisting process requires.",
        "date": "2026-08-01",
        "date_label": "1 August 2026",
        "read": "8 min",
        "author": "OptioHire Team",
        "thumb": "articles/shortlist-hours.svg",
        "alt": "Abstract illustration of a crowded inbox narrowing into a short ranked list",
    },
    {
        "file": "skills-first-hiring.html",
        "slug": "skills-first-hiring",
        "category": "Candidate Tips",
        "title": 'What "skills-first" hiring actually means for applicants',
        "excerpt": "How evaluation beyond keyword-matching changes what candidates should focus on.",
        "date": "2026-08-12",
        "date_label": "12 August 2026",
        "read": "5 min",
        "author": "OptioHire Team",
        "thumb": "articles/skills-first.svg",
        "alt": "Abstract illustration of skills rising above a keyword-matched CV",
    },
    {
        "file": "optiohire-vs-generic-ats.html",
        "slug": "optiohire-vs-generic-ats",
        "category": "Comparisons",
        "title": "OptioHire vs. generic ATS platforms: what's actually different",
        "excerpt": "Applicant tracking and hiring decision support are not the same thing. Here is what actually changes.",
        "date": "2026-08-14",
        "date_label": "14 August 2026",
        "read": "7 min",
        "author": "OptioHire Team",
        "thumb": "articles/vs-ats.svg",
        "alt": "Abstract illustration of a keyword filter versus a scored shortlist",
    },
]


def cat_slug(cat):
    return cat.lower().replace(" ", "-")


def article_card(art, prefix="", lazy=True):
    loading = ' loading="lazy"' if lazy else ""
    return f"""<a class="card article-card" href="{prefix}resources/{art["file"]}" data-category="{cat_slug(art["category"])}">
      <img class="article-thumb" src="{prefix}assets/{art["thumb"]}" alt="{html.escape(art["alt"], quote=True)}" width="640" height="360"{loading} decoding="async">
      <div class="article-card-body">
        <p class="article-meta">{html.escape(art["category"])}</p>
        <h3>{html.escape(art["title"])}</h3>
        <p>{html.escape(art["excerpt"])}</p>
        <p class="article-card-meta"><span>{art["read"]} read</span><time datetime="{art["date"]}">{art["date_label"]}</time></p>
      </div>
    </a>"""


def resources_page():
    cards = "".join(article_card(art, lazy=i > 0) for i, art in enumerate(ARTICLES))
    return f"""
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">Resources</p>
    <h1>Ideas on fairer, faster hiring.</h1>
    <p class="lede">Practical thinking on recruitment, screening, and what it actually takes to run a hiring process people trust.</p>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <div class="wrap" data-filter-group>
    <div class="filters" role="tablist" aria-label="Article categories">
      <button class="filter-btn is-active" type="button" data-filter="all">All</button>
      <button class="filter-btn" type="button" data-filter="hiring-trends">Hiring Trends</button>
      <button class="filter-btn" type="button" data-filter="hr-playbooks">HR Playbooks</button>
      <button class="filter-btn" type="button" data-filter="candidate-tips">Candidate Tips</button>
      <button class="filter-btn" type="button" data-filter="product-updates">Product Updates</button>
      <button class="filter-btn" type="button" data-filter="comparisons">Comparisons</button>
    </div>
    <div class="grid-2 article-grid">{cards}</div>
    <p class="filter-empty" data-filter-empty hidden>No articles in this category yet.</p>
  </div>
</section>
<section class="band theme-teal" data-header-theme="teal">
  <div class="wrap newsletter-band">
    <h3>Get new articles as they publish.</h3>
    <!-- CASA: connect mailing tool backend before this list collects live subscribers. -->
    <form class="newsletter-form" data-newsletter>
      <label class="sr-only" for="newsletter-email">Email</label>
      <input id="newsletter-email" type="email" name="email" required autocomplete="email" placeholder="Work email">
      <button class="btn btn-primary" type="submit">Subscribe {ARROW}</button>
    </form>
    <p class="newsletter-success" data-newsletter-success hidden>Thanks - we'll add you when the mailing list goes live.</p>
    <p class="form-note">Mailing list backend to be confirmed.</p>
  </div>
</section>
"""


FAQ_GROUPS = [
    (
        "employers",
        "For Employers",
        [
            (
                "How is scoring kept fair across candidates?",
                "Every applicant is evaluated against the same role requirements, with the reasoning behind each score visible to your team.",
            ),
            (
                "Can we set custom requirements per role?",
                "Yes - requirements are configured per job listing, not applied as a one-size-fits-all filter.",
            ),
            (
                "What happens to candidates we don't shortlist?",
                "They receive an automated outcome update rather than being left without a response.",
            ),
        ],
    ),
    (
        "hr-teams",
        "For HR Teams",
        [
            (
                "Do we still need spreadsheets alongside this?",
                "No - the candidate pipeline, scoring, and scheduling all live in one workspace.",
            ),
            (
                "Can multiple team members review the same role?",
                "Yes, the dashboard is built for shared team access on each job.",
            ),
            (
                "How are interviews scheduled?",
                "Directly from the shortlist, with invites sent from the platform.",
            ),
        ],
    ),
    (
        "candidates",
        "For Candidates",
        [
            (
                "Do I need a separate profile for every application?",
                "No - build one profile and apply to roles with it.",
            ),
            (
                "Will I actually hear back either way?",
                "Yes, outcome updates are sent automatically as your application moves through the process.",
            ),
            (
                "Is my data kept private?",
                "Yes, candidate data is handled with defined privacy and security practices - see the Security page for detail.",
            ),
        ],
    ),
    (
        "institutions",
        "For Institutions",
        [
            (
                "How does onboarding a cohort work?",
                "Our team walks your staff through setup and configures the console for your specific programs.",
            ),
            (
                "Can we track placement outcomes over time?",
                "Yes, cohort-level tracking is built into the institution console.",
            ),
            (
                "Who do we contact for support?",
                "A dedicated partner contact is assigned once onboarding begins.",
            ),
        ],
    ),
]


def faq_page():
    tabs = []
    panels = []
    for i, (key, label, qs) in enumerate(FAQ_GROUPS):
        selected = "true" if i == 0 else "false"
        active = " is-active" if i == 0 else ""
        hidden = "" if i == 0 else " hidden"
        tabs.append(
            f'<button class="filter-btn{active}" type="button" role="tab" aria-selected="{selected}" aria-controls="faq-{key}" id="tab-{key}" data-faq-tab="{key}">{label}</button>'
        )
        items = "".join(
            f'<details class="faq-item"><summary>{q}</summary><p>{a}</p></details>' for q, a in qs
        )
        panels.append(
            f'<div class="faq-group" id="faq-{key}" role="tabpanel" aria-labelledby="tab-{key}" data-faq-panel="{key}"{hidden}><h2 class="sr-only">{label}</h2>{items}</div>'
        )
    return f"""
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">FAQ</p>
    <h1>Answers, grouped by who's asking.</h1>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <div class="wrap" data-faq-tabs>
    <div class="filters" role="tablist" aria-label="FAQ audience">{''.join(tabs)}</div>
    {''.join(panels)}
  </div>
</section>
<section class="band theme-dark cta-band" data-header-theme="dark">
  <div class="wrap">
    <h3>Still have a question?</h3>
    <div class="cta-row" style="justify-content:center"><a class="btn btn-primary" href="contact.html">Contact us {ARROW}</a></div>
  </div>
</section>
"""


def faq_schema_script():
    entities = []
    for _key, _label, qs in FAQ_GROUPS:
        for q, a in qs:
            entities.append(
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a},
                }
            )
    payload = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": entities}
    return f'<script type="application/ld+json">{json.dumps(payload, ensure_ascii=False)}</script>'


CONTACT = f"""
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">Contact</p>
    <h1>Let's talk about how OptioHire fits your team.</h1>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <div class="wrap split">
    <form class="form" data-contact-form>
      <div class="form-fields">
        <label>Name <input name="name" required autocomplete="name"></label>
        <label>Email <input type="email" name="email" required autocomplete="email"></label>
        <label>Organization <input name="org" autocomplete="organization"></label>
        <label>Inquiry type
          <select name="type" required data-inquiry-type>
            <option value="Employer">Employer</option>
            <option value="HR / Recruiting Team">HR / Recruiting Team</option>
            <option value="Institution Partnership">Institution Partnership</option>
            <option value="Demo Request">Demo Request</option>
            <option value="Talk to Sales">Talk to Sales</option>
            <option value="Press">Press</option>
            <option value="Other">Other</option>
          </select>
        </label>
        <label>Message <textarea name="message" required></textarea></label>
        <button class="btn btn-primary" type="submit">Send message {ARROW}</button>
        <p class="form-note">Submits via your email client to developer@optiohire.com</p>
      </div>
      <p class="form-success">Opening your email client. If nothing happens, write us directly at developer@optiohire.com.</p>
    </form>
    <aside class="contact-aside">
      <article class="card">
        <h3>Direct details</h3>
        <p style="margin-top:.7rem"><strong>Email</strong><br><a href="mailto:developer@optiohire.com">developer@optiohire.com</a></p>
        <p><strong>Location</strong><br>Nairobi, Kenya</p>
        <p><strong>Social</strong></p>
        {socials()}
        <p class="form-note" style="margin-top:1.1rem">For institution partnerships, use the dropdown above so your inquiry reaches the right team directly.</p>
      </article>
    </aside>
  </div>
</section>
"""

PRIVACY = """
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">Legal</p>
    <h1>Privacy Policy</h1>
    <p class="lede">Last updated: 14 August 2026</p>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <!-- Legal review recommended before publishing. -->
  <div class="wrap prose prose--legal">
    <p>This policy describes how OptioHire, a product of Cres Dynamics in Nairobi, Kenya, collects and uses information when you visit this site or use the hiring platform. It is written as static public information; a legal review is recommended before treating it as a binding privacy notice.</p>
    <h2>What data OptioHire collects</h2>
    <p>Depending on how you use OptioHire, we may collect:</p>
    <ul>
      <li>Contact details such as name, email address, phone number, and organisation</li>
      <li>Account and role information for employer, HR, institution, and candidate users</li>
      <li>Candidate profile material - CVs, work history, skills, and application answers</li>
      <li>Hiring process records - scores, shortlist decisions, interview scheduling, and outcome messages</li>
      <li>Usage data such as device, browser, pages visited, and how features are used</li>
    </ul>
    <h2>How candidate and employer data is used</h2>
    <p>Candidate data is used to run applications: matching people to roles, scoring against the requirements of a listing, communicating outcomes, and scheduling interviews. Employer and HR data is used to operate workspaces, job listings, and team access. We also use information to provide support, improve the product, and meet legal obligations. We do not sell personal information.</p>
    <h2>Data sharing and third parties</h2>
    <p>We share information only as needed to run the service: with the employer or institution that owns a given hiring process, with infrastructure and email providers under contract, or when required by law. Institution partners see cohort-level placement information they are authorised to view. Service providers are expected to handle data under confidentiality and security terms.</p>
    <h2>Data retention</h2>
    <p>We keep information for as long as an account or hiring process requires it, and for a limited period afterward where we need records for security, disputes, or legal retention. When data is no longer needed, we delete or anonymise it according to the product’s retention rules.</p>
    <h2>Candidate rights and data requests</h2>
    <p>You may request access to the personal data we hold about you, ask for a correction, object to certain processing, or request deletion or portability where those rights apply - including under Kenya’s Data Protection Act and, where relevant, GDPR-aligned practice. We will need enough information to verify the request.</p>
    <h2>Cookies</h2>
    <p>Essential cookies keep this site working. Analytics and marketing cookies stay off until you opt in through the cookie banner - they are not set first and disclosed later. You can change that choice any time via Cookie settings in the footer. See also Kenya’s Data Protection Act (2019).</p>
    <h2>Contact for privacy questions</h2>
    <p>Privacy questions and data requests: <a href="mailto:developer@optiohire.com">developer@optiohire.com</a> · Nairobi, Kenya.</p>
  </div>
</section>
"""

SECURITY = """
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">Legal</p>
    <h1>Security &amp; Compliance</h1>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <div class="wrap prose prose--legal">
    <h2>How candidate data is protected</h2>
    <p>Candidate information exists to run a fair hiring process - not to be sold or reused as a marketing list. Access is limited to the employer, HR, or institution workspace that owns the role or cohort, and to OptioHire staff who need it to operate or support the product. Outcome messages and scores stay inside that process so a candidate is not left without a record of what happened.</p>
    <h2>Access controls for HR and employer accounts</h2>
    <p>Workspaces use authenticated accounts and role-based permissions so team members only see the jobs and candidates their role requires. Shared review on a listing is intentional; open access across unrelated departments is not. Session handling and authentication are designed to keep hiring data inside the right team.</p>
    <h2>Data storage and encryption practices</h2>
    <p>Data is encrypted in transit and at rest. We collect what the hiring workflow needs, store it on contracted infrastructure, and back it up as part of normal operations. Retention follows the privacy policy: keep records while the process needs them, then delete or anonymise.</p>
    <h2>Reporting a security concern</h2>
    <p>If you believe you have found a security issue, contact us at <a href="mailto:developer@optiohire.com">developer@optiohire.com</a> or through the <a href="contact.html">contact form</a> so we can investigate. Please include enough detail to reproduce the concern, and avoid sharing unrelated candidate files unless we ask for them.</p>
  </div>
</section>
"""

ARTICLE_BODIES = {
    "why-candidates-never-hear-back.html": """
      <p>Most applications do not end in a no. They end in nothing. After a CV is submitted, it lands in a pile that nobody can finish, and silence becomes the default - not because the candidate was weak, but because the process ran out of attention.</p>
      <p>A look at what happens after submit is rarely flattering. A coordinator opens a role, hundreds of applications arrive, and a handful of people are pulled forward. Everyone else is not rejected. They are abandoned. There is no confirmation, no update, and no explanation. The person who did the work is left to guess whether anyone opened the file.</p>
      <blockquote class="pull-quote">Silence has become the default because it is cheaper than a sentence - until you count the talent you will need next quarter.</blockquote>
      <h2>What happens after an application is submitted</h2>
      <p>In a high-volume process, “received” is not a status anyone can see. Applications sit in inboxes, shared drives, or an ATS that still expects a human to read every PDF. First-pass review starts strong and degrades by the afternoon. Formatting, familiar school names, and who looks polished fill the gaps that fatigue opens.</p>
      <p>By the time a shortlist exists, the decision trail is oral: a few names, a few hunches, a spreadsheet that only one person understands. There is no owner for the “no,” so the “no” is never sent.</p>
      <h2>Why silence became the default</h2>
      <p>Volume outgrew the humans assigned to it. Generic tools tick keywords and still leave a person to decide. Spreadsheets lose rows. Writing two hundred outcome emails is treated as optional. The cost is not only unkind - it is operational. Strong candidates drop out, re-apply elsewhere, and tell the next person what your process felt like.</p>
      <h2>What a response actually requires</h2>
      <p>You cannot bolt courtesy onto a pile. You need a system that captures every application, scores it against the same requirements, and sends an outcome from the same workflow that produced the decision. That is how silence stops being the rounding error of hiring.</p>
    """,
    "cv-screening-bias.html": """
      <p>Bias in CV screening is often described as a character problem. Operationally, it is a fatigue problem. The third CV and the two-hundredth are not read with the same attention. Inconsistent, fatigue-driven review is not a rounding error - it is how you miss people who can do the work and advance people who wrote a better PDF.</p>
      <blockquote class="pull-quote">The real cost is not only the hire you make. It is the hire you cannot explain.</blockquote>
      <h2>The real cost of inconsistent review</h2>
      <p>When every reviewer applies a slightly different bar, the shortlist becomes a record of who was tired, who liked a layout, and who recognised a company name. Stakeholders ask why one person advanced. There is no scorecard to point to - only a feeling that arrived after lunch. Disputes get harder. Employer brand takes the hit when strong applicants hear nothing, or hear a no with no reasoning.</p>
      <p>Fatigue also invites the shortcuts everyone claims they do not use: pedigree, polish, and keyword theatre. Those shortcuts are fast. They are not fair, and they are not defensible if a decision is questioned later.</p>
      <h2>What a structured alternative looks like</h2>
      <p>Write the criteria for the role. Apply them to every applicant. Keep the reasoning. That is the whole alternative - structure over gut feel, the same bar for everyone, a trail when someone asks why. Scoring does not replace the hiring manager. It stops the first pass from being a lottery of attention.</p>
      <p>A structured pass still reads the CV. It refuses to let layout and last-company brand be the score. The team still interviews. They just interview people who were measured the same way.</p>
    """,
    "shortlisting-in-hours.html": """
      <p>If shortlisting takes four days, your hiring manager is a document processor. The people you want will take another offer while you are still on page forty. A fast, defensible shortlist is not a slogan - it is a workflow with requirements, a single pipeline, and a record behind every name.</p>
      <h2>What the hours version actually requires</h2>
      <p>First, the role has to say what it needs. Vague listings produce vague piles. Capture requirements when the job is posted so scoring has something real to use - not a generic keyword list.</p>
      <p>Second, every application has to land in one place. Inboxes, WhatsApp threads, and side-door PDFs are how people disappear. One pipeline per role is the only way volume stays visible.</p>
      <blockquote class="pull-quote">Monday: post the role. Hours later, you should be looking at a ranked list with reasons - not a folder.</blockquote>
      <h3>From pile to ranked list</h3>
      <p>Parse the CVs into comparable data. Score everyone against the same criteria. Hand the team a shortlist with reasoning they can inspect. Interviews get booked from that screen, not from a calendar scavenger hunt.</p>
      <h2>Defensible, not just fast</h2>
      <p>Speed without a trail is just a quicker gut feel. The process has to leave a record: why this person, against which requirement, who signed off. That is what lets a founder, a board, or a candidate who asks get a straight answer. Hours are the target. The audit trail is how you live with the target.</p>
    """,
    "skills-first-hiring.html": """
      <p>Skills-first is easy to print on a careers page and hard to run in a real process. For applicants, it is not a vibe. It is a change in what gets measured: evaluation looks past keyword-matching on a CV, toward evidence of what you can actually do.</p>
      <h2>What changes when keywords stop being the score</h2>
      <p>Keyword filters reward people who guessed the right nouns. They punish people who did the work under a different job title, in a smaller company, or in language the ATS was not fed. A skills-first pass still reads the CV - it just refuses to let a buzzword list be the decision.</p>
      <p>That means your application is judged against the requirements of the role, consistently, instead of against whoever skimmed fastest. Formatting still matters as courtesy. It should not be the ranking.</p>
      <blockquote class="pull-quote">Focus on evidence of the work, not on stuffing the document with the words a filter might catch.</blockquote>
      <h2>What candidates should actually focus on</h2>
      <p>Be specific about the work you have done: tools, outcomes, scope, and the problems you owned. Match yourself to the stated requirements, not to a fantasy version of the title. Keep one profile current so you are not re-entering the same story for every listing.</p>
      <p>When a process is skills-first, you should also expect a real status and a real outcome. Silence is not a skills-first result. A score against published criteria, a shortlist you can see move, and a yes or no you can understand - that is what the phrase is supposed to mean from the other side of the application.</p>
    """,
    "optiohire-vs-generic-ats.html": """
      <p>Most hiring software is built to store applications. That is useful. It is also not the same job as deciding who should move forward. “Applicant tracking” and “hiring decision support” get sold as one category. They are not.</p>
      <p>A generic ATS is a filing system with workflow around it: receive CVs, park them in a pipeline, hope a human still has time to read. Keyword filters take the first pass. Manual review still does the actual ranking. Status updates, when they happen, are extra work. Reasoning lives in someone’s head, or in a Slack thread that the next coordinator never sees.</p>
      <blockquote class="pull-quote">Tracking where a CV sat is not the same as explaining why a person advanced.</blockquote>
      <h2>What actually differs</h2>
      <table class="compare-table">
        <thead>
          <tr><th></th><th>Generic ATS</th><th>OptioHire</th></tr>
        </thead>
        <tbody>
          <tr><td>First pass</td><td>Keyword filtering</td><td>Requirement-based scoring</td></tr>
          <tr><td>Review load</td><td>Manual review still required to make a shortlist</td><td>Ranked shortlist with visible reasoning</td></tr>
          <tr><td>Why this person?</td><td>No scoring reasoning on the record</td><td>Transparent reasoning against the role</td></tr>
          <tr><td>Candidate communication</td><td>Status updates are manual, so silence is common</td><td>Automated outcome updates from the same workflow</td></tr>
          <tr><td>After the fact</td><td>Hard to reconstruct the decision</td><td>Full audit trail</td></tr>
        </tbody>
      </table>
      <h2>Where a generic ATS still makes sense</h2>
      <p>If you hire a handful of people a year, for highly niche roles where one hiring manager will read every file anyway, a lightweight tracker can be enough. The pile is small. The decision is already sitting in one person’s head. Buying decision infrastructure for that volume is optional.</p>
      <p>The gap shows up when volume arrives: campus intakes, retail turnover, engineering roles with two hundred applicants, or more than one department sharing a process. At that point keyword theatre and unread PDFs are not a tooling preference. They are the process.</p>
      <h2>What to do next</h2>
      <p>If you need a system that scores fairly, explains itself, and tells candidates what happened, start a free trial and run one live role through it. That is the only comparison that matters.</p>
    """,
}


def article_schema_script(art):
    payload = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": art["title"],
        "description": art["excerpt"],
        "datePublished": art["date"],
        "author": {"@type": "Organization", "name": art["author"]},
        "publisher": {
            "@type": "Organization",
            "name": "OptioHire",
            "logo": {"@type": "ImageObject", "url": OG_IMAGE},
        },
        "image": f"{SITE}/assets/{art['thumb']}",
        "mainEntityOfPage": f"{SITE}/resources/{art['slug']}",
    }
    return f'<script type="application/ld+json">{json.dumps(payload, ensure_ascii=False)}</script>'


SCHEMA = (
    '<script type="application/ld+json">\n'
    + json.dumps(
        {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Organization",
                    "name": "OptioHire",
                    "url": f"{SITE}/",
                    "logo": OG_IMAGE,
                    "email": "developer@optiohire.com",
                    "address": {
                        "@type": "PostalAddress",
                        "addressLocality": "Nairobi",
                        "addressCountry": "KE",
                    },
                    "contactPoint": {
                        "@type": "ContactPoint",
                        "email": "developer@optiohire.com",
                        "contactType": "customer support",
                        "areaServed": "KE",
                        "availableLanguage": ["en"],
                    },
                    "parentOrganization": {
                        "@type": "Organization",
                        "name": "Cres Dynamics",
                        "url": "https://cresdynamics.com",
                    },
                    "sameAs": [
                        "https://www.linkedin.com/company/optiohire",
                        "https://x.com/optiohire",
                        "https://www.instagram.com/optiohire",
                    ],
                },
                {
                    "@type": "SoftwareApplication",
                    "name": "OptioHire",
                    "applicationCategory": "HR/recruitment software",
                    "operatingSystem": "Web",
                    "description": "OptioHire helps HR teams run faster, fairer hiring with automated applicant screening, transparent scoring, and interview-ready shortlists.",
                    "url": f"{SITE}/",
                    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
                    "provider": {"@type": "Organization", "name": "OptioHire"},
                },
            ],
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n</script>"
)


def related_cards(current_file):
    others = [a for a in ARTICLES if a["file"] != current_file][:3]
    return "".join(article_card(art, prefix="../", lazy=True) for art in others)


def article_html(art):
    crumbs = [
        ("Home", "index.html"),
        ("Resources", "resources.html"),
        (art["category"], f"resources.html?filter={cat_slug(art['category'])}"),
        (art["title"], None),
    ]
    inner = f"""
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">{html.escape(art["category"])}</p>
    <h1>{html.escape(art["title"])}</h1>
    <p class="article-byline"><time datetime="{art["date"]}">{art["date_label"]}</time> · {art["read"]} read · {html.escape(art["author"])}</p>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <div class="wrap prose article-body">{ARTICLE_BODIES[art["file"]]}</div>
</section>
<section class="band theme-white" data-header-theme="white" style="padding-top:0">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">Keep reading</p>
      <h2>Related articles</h2>
    </div>
    <div class="grid-3">{related_cards(art["file"])}</div>
  </div>
</section>
<section class="band theme-dark cta-band" data-header-theme="dark">
  <div class="wrap">
    <h2>See what a fairer hiring process looks like.</h2>
    <div class="cta-row" style="justify-content:center">
      <a class="btn btn-primary" href="{SIGNUP}" data-track="start_free_trial" data-utm-campaign="resources">Start Free Trial {ARROW}</a>
    </div>
  </div>
</section>
"""
    extra = article_schema_script(art)
    extra += f'\n  <meta property="article:published_time" content="{art["date"]}">'
    extra += f'\n  <meta property="article:author" content="{html.escape(art["author"], quote=True)}">'
    return page(
        f"{art['title']} | OptioHire",
        art["excerpt"],
        art["file"],
        inner,
        "dark",
        extra,
        canonical=f"{SITE}/resources/{art['slug']}",
        prefix="../",
        og_type="article",
        crumbs=crumbs,
    )


PRICING = f"""
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">Pricing</p>
    <h1>Straightforward pricing, built for how your team hires.</h1>
    <p class="lede">Start free, then choose the plan that matches your hiring volume - no hidden fees, no per-CV surprise charges.</p>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <div class="wrap">
    <!-- CASA: price points are placeholders - Nelson to confirm figures before publishing. -->
    <div class="grid-3 pricing-grid">
      <article class="card pricing-card">
        <h3 class="plan-name">Starter</h3>
        <p>For small teams hiring a handful of roles at a time</p>
        <p class="plan-price">Free trial, then [price/mo]</p>
        <p class="plan-note">Figures to be confirmed before publishing.</p>
        <ul>
          <li>Core screening &amp; scoring</li>
          <li>Single pipeline per role</li>
          <li>Standard support</li>
        </ul>
        <a class="btn btn-primary" href="{SIGNUP}" data-track="start_free_trial" data-utm-campaign="pricing-starter">Start Free Trial {ARROW}</a>
      </article>
      <article class="card pricing-card is-featured">
        <p class="plan-badge">Recommended</p>
        <h3 class="plan-name">Growth</h3>
        <p>For growing teams with steady hiring volume</p>
        <p class="plan-price">[price/mo]</p>
        <p class="plan-note">Figures to be confirmed before publishing.</p>
        <ul>
          <li>Everything in Starter</li>
          <li>Multiple concurrent roles</li>
          <li>Priority support</li>
          <li>Milestone insights</li>
        </ul>
        <a class="btn btn-primary" href="{SIGNUP}" data-track="start_free_trial" data-utm-campaign="pricing-growth">Start Free Trial {ARROW}</a>
      </article>
      <article class="card pricing-card">
        <h3 class="plan-name">Enterprise / Institution</h3>
        <p>For organizations hiring at scale across departments or cohorts</p>
        <p class="plan-price">Custom - talk to us</p>
        <ul>
          <li>Everything in Growth</li>
          <li>Multi-department/cohort management</li>
          <li>Dedicated onboarding &amp; support</li>
          <li>Custom scorecards</li>
        </ul>
        <a class="btn btn-outline" href="{SALES}" data-track="talk_to_sales">Talk to Sales</a>
      </article>
    </div>
  </div>
</section>
<section class="band theme-teal" data-header-theme="teal">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">Pricing questions</p>
      <h2>How billing works</h2>
    </div>
    <details class="faq-item"><summary>Is there a free trial?</summary><p>Yes, every plan starts with a free trial period before billing begins.</p></details>
    <details class="faq-item"><summary>Do you charge per candidate or per role?</summary><p>[Nelson to confirm model - flat monthly vs. per-role vs. per-seat]</p></details>
    <details class="faq-item"><summary>Can we switch plans later?</summary><p>Yes, upgrading or downgrading is handled from account settings.</p></details>
    <details class="faq-item"><summary>What's included in Enterprise/Institution pricing?</summary><p>Custom scope based on department count, cohort size, and support needs - contact sales for a tailored quote.</p></details>
  </div>
</section>
<section class="band theme-dark cta-band" data-header-theme="dark">
  <div class="wrap">
    <h2>Not sure which plan fits?</h2>
    <div class="cta-row" style="justify-content:center">
      <a class="btn btn-primary" href="{SIGNUP}" data-track="start_free_trial" data-utm-campaign="pricing">Start Free Trial {ARROW}</a>
      <a class="btn btn-outline" href="{SALES}" data-track="talk_to_sales">Talk to Sales</a>
      <a class="btn btn-text" href="{DEMO}" data-track="book_demo">Book a demo</a>
    </div>
  </div>
</section>
"""

TERMS = """
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">Legal</p>
    <h1>Terms of Service</h1>
    <p class="lede">Last updated: 14 August 2026</p>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <!-- Legal review recommended before publishing. -->
  <div class="wrap prose prose--legal">
    <h2>Acceptance of terms</h2>
    <p>By using OptioHire’s website or platform, you agree to these terms. If you are using OptioHire for an organisation, you confirm you have authority to bind that organisation. If you do not agree, do not use the service.</p>
    <h2>Description of the service</h2>
    <p>OptioHire is a hiring platform that receives applications, scores candidates against role requirements, supports shortlisting, interview scheduling, and outcome communication. Features available to you depend on your account type and plan. See <a href="pricing.html">Pricing</a> for plan structure.</p>
    <h2>Account responsibilities</h2>
    <p>Employer and HR accounts must keep login details secure, use the product only for legitimate hiring, and treat candidate data as confidential. Candidate accounts must provide information that is accurate to the best of their knowledge. Institution accounts are responsible for authorised staff access and for how cohort data is used inside their organisation. You are responsible for activity under your account.</p>
    <h2>Acceptable use policy</h2>
    <p>You may not use OptioHire to discriminate unlawfully, scrape or resell candidate data, probe the system for vulnerabilities except through a reported security concern, or interfere with other customers’ use of the platform. We may suspend access that violates this policy.</p>
    <h2>Data ownership and candidate data handling</h2>
    <p>Employers and institutions retain responsibility for the hiring processes they run. Candidate personal data is handled as described in the <a href="privacy.html">Privacy Policy</a>. OptioHire does not sell candidate information. You must only upload data you are entitled to process.</p>
    <h2>Payment terms and cancellation</h2>
    <p>Paid plans bill according to the plan you select. Free trials convert only after the trial period described at signup. You can upgrade, downgrade, or cancel from account settings as described on <a href="pricing.html">Pricing</a>. Fees already incurred are not refunded unless required by law. Exact price points will be confirmed before paid billing is offered publicly.</p>
    <h2>Limitation of liability</h2>
    <p>OptioHire assists hiring decisions; humans remain responsible for who is hired. To the extent permitted by Kenyan law, Cres Dynamics and OptioHire are not liable for indirect or consequential loss, or for hiring outcomes. Nothing in these terms limits liability that cannot legally be limited.</p>
    <h2>Termination</h2>
    <p>You may stop using the service at any time. We may suspend or end an account that breaches these terms, fails to pay, or creates risk to candidates or the platform. After termination, we retain or delete data as described in the Privacy Policy.</p>
    <h2>Governing law</h2>
    <p>These terms are governed by the laws of Kenya. Disputes will be handled in the courts of Kenya, unless a mandatory consumer or data-protection rule says otherwise.</p>
    <h2>Contact for legal questions</h2>
    <p>Legal questions: <a href="mailto:developer@optiohire.com">developer@optiohire.com</a> · Nairobi, Kenya · or the <a href="contact.html">contact form</a>.</p>
  </div>
</section>
"""

NOT_FOUND = f"""
<div class="page-404 theme-dark">
  <div>
    <svg class="mark-404" viewBox="0 0 56 40" fill="none" aria-hidden="true">
      <circle cx="18" cy="20" r="15" stroke="currentColor" stroke-width="3.1"/>
      <circle cx="38" cy="20" r="15" stroke="currentColor" stroke-width="3.1"/>
    </svg>
    <h1>This page didn't make the shortlist.</h1>
    <p class="lede">The page you're looking for doesn't exist or has moved.</p>
    <div class="cta-row" style="justify-content:center">
      <a class="btn btn-primary" href="index.html">Back to Home {ARROW}</a>
      <a class="btn btn-text" href="contact.html">Contact us</a>
    </div>
  </div>
</div>
"""

CUSTOMERS = f"""
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">Customers</p>
    <h1>Verified stories, when they're ready to share.</h1>
    <p class="lede">Named case studies go live only after the customer has approved them. Until then, this is the home those stories will occupy.</p>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <div class="wrap">
    <div class="case-slots" aria-label="Case study placeholders">
      <article class="card case-slot"><p class="eyebrow">Case study</p><h3>Coming soon</h3><p>A verified customer story will sit here once approved for publication.</p></article>
      <article class="card case-slot"><p class="eyebrow">Case study</p><h3>Coming soon</h3><p>A verified customer story will sit here once approved for publication.</p></article>
      <article class="card case-slot"><p class="eyebrow">Case study</p><h3>Coming soon</h3><p>A verified customer story will sit here once approved for publication.</p></article>
    </div>
    <p class="lede" style="margin:2rem auto 0;text-align:center">The layout for a published story is ready - see the <a href="customers/template.html">case study template</a>.</p>
  </div>
</section>
<section class="band theme-dark cta-band" data-header-theme="dark">
  <div class="wrap">
    <h2>Want results like this for your team?</h2>
    <div class="cta-row" style="justify-content:center">
      <a class="btn btn-primary" href="{SIGNUP}" data-track="start_free_trial" data-utm-campaign="customers">Start Free Trial {ARROW}</a>
    </div>
  </div>
</section>
"""


def case_study_html(study, prefix="../"):
    crumbs = [
        ("Home", "index.html"),
        ("Customers", "customers.html"),
        (study["company"], None),
    ]
    stats = "".join(
        f'<div class="stat-card"><div class="stat-value">{html.escape(v)}</div><p class="stat-label">{html.escape(lbl)}</p></div>'
        for v, lbl in study["stats"]
    )
    inner = f"""
<section class="band band-hero theme-dark" data-header-theme="dark">
  <div class="wrap hero-copy hero-copy--center">
    <p class="eyebrow eyebrow--pill">{html.escape(study.get("industry", "Customer story"))}</p>
    <p class="industry-tag">{html.escape(study["company"])}</p>
    <h1>{html.escape(study["headline"])}</h1>
  </div>
  <div class="wrap">
    <div class="stats-grid stats-grid-3 stats-grid--hero">{stats}</div>
  </div>
</section>
<section class="band theme-white" data-header-theme="white">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">The challenge</p>
      <h2>What hiring looked like before.</h2>
      <p class="lede narrative">{html.escape(study["challenge"])}</p>
    </div>
  </div>
</section>
<section class="band theme-white" data-header-theme="white" style="padding-top:0">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">The solution</p>
      <h2>How they used OptioHire.</h2>
      <p class="lede narrative">{html.escape(study["solution"])}</p>
    </div>
  </div>
</section>
<section class="band theme-teal" data-header-theme="teal">
  <div class="wrap">
    <div class="section-head section-head--center">
      <p class="eyebrow">The results</p>
      <h2>What changed.</h2>
    </div>
    <div class="stats-grid stats-grid-3">{stats}</div>
    <blockquote class="quote-block">
      <p class="quote">{html.escape(study["quote"])}</p>
      <div class="person" style="justify-content:center"><span class="avatar">{html.escape(study.get("initials", "OH"))}</span><div><strong>{html.escape(study["person"])}</strong><span>{html.escape(study["role"])}</span></div></div>
    </blockquote>
  </div>
</section>
<section class="band theme-dark cta-band" data-header-theme="dark">
  <div class="wrap">
    <h2>Want results like this for your team?</h2>
    <div class="cta-row" style="justify-content:center">
      <a class="btn btn-primary" href="{SIGNUP}" data-track="start_free_trial" data-utm-campaign="case-study">Start Free Trial {ARROW}</a>
    </div>
  </div>
</section>
"""
    return page(
        f"{study['headline']} | OptioHire",
        study["excerpt"],
        f"customers/{study['slug']}.html",
        inner,
        "dark",
        "",
        canonical=f"{SITE}/customers/{study['slug']}",
        prefix=prefix,
        crumbs=crumbs,
        robots=study.get("robots", "index, follow"),
    )


CASE_TEMPLATE = {
    "slug": "template",
    "company": "[Company]",
    "industry": "[Industry]",
    "headline": "How [Company] cut shortlisting time by [X]%",
    "excerpt": "Template layout for a verified customer story. Replace placeholders when a case study is approved.",
    "stats": [("[X]%", "Time saved"), ("[n]", "Roles filled"), ("[n]", "Applicant volume handled")],
    "challenge": "What the company's hiring process looked like before, in their own words and context. Replace this paragraph when the story is approved.",
    "solution": "How they implemented OptioHire, and which features mattered most for their situation. Replace this paragraph when the story is approved.",
    "quote": "A fuller quote from the client will sit here.",
    "person": "[Name]",
    "role": "[Title]",
    "initials": "CS",
    "robots": "noindex, follow",
}

PAGE_CRUMBS = {
    "for-employers.html": [("Home", "index.html"), ("Employers", None)],
    "for-hr-teams.html": [("Home", "index.html"), ("HR Teams", None)],
    "for-candidates.html": [("Home", "index.html"), ("Candidates", None)],
    "for-institutions.html": [("Home", "index.html"), ("Institutions", None)],
    "pricing.html": [("Home", "index.html"), ("Pricing", None)],
    "customers.html": [("Home", "index.html"), ("Customers", None)],
}


PAGES = [
    ("index.html", "AI-Powered Recruitment Platform | OptioHire",
     "OptioHire is a B2B HR tech SaaS by Cres Dynamics (Nairobi, Kenya) that helps companies hire 3x faster with AI-powered smart screening, fair evaluation, and confident hiring decisions.",
     HOME, "dark", SCHEMA),
    ("how-it-works.html", "Three Hundred Applicants Down to Your Best Five | OptioHire",
     "Post a role, receive every application, get candidates ranked fairly by AI, and move the right people to interview - in one visible, traceable workflow.",
     HOW, "dark", ""),
    ("for-employers.html", "For Employers | Hire on Merit, Not Who Reads Fastest | OptioHire",
     "When two hundred people apply for one role, the best candidate shouldn't depend on who skimmed the pile last. A consistent, defensible way to hire - quickly.",
     EMPLOYERS, "dark", ""),
    ("for-hr-teams.html", "For HR Teams | One Workspace from Job Post to Interview | OptioHire",
     "See every candidate, every score, and every next step in one place - without spreadsheets, email threads, or a separate scheduling tool.",
     HR, "dark", ""),
    ("for-candidates.html", "For Candidates | Apply Once. Know Exactly Where You Stand. | OptioHire",
     "No more sending a CV into silence. Build one profile, apply to roles that fit, and actually see your progress instead of wondering if anyone looked.",
     CANDIDATES, "dark", ""),
    ("for-institutions.html", "For Institutions | Placement Outcomes You Can Actually See | OptioHire",
     "Scale hiring and placement across departments, programs, or entire student cohorts - with one system tracking outcomes instead of scattered spreadsheets.",
     INSTITUTIONS, "dark", ""),
    ("use-cases.html", "Use Cases | Built for How Different Teams Actually Hire | OptioHire",
     "Hiring doesn't look the same for a five-person startup, a university placement office, or a retail chain filling forty shifts a month. Here's how OptioHire fits each situation.",
     USE, "dark", ""),
    ("partners.html", "Partners | Kenya's Leading Colleges and Universities | OptioHire",
     "We work directly with academic institutions to help graduating cohorts move from classroom to career - with real placement tracking behind it.",
     PARTNERS, "dark", ""),
    ("about.html", "About | Built by People Who Lived the Problem First | OptioHire",
     "Hiring in Kenya doesn't fail from a lack of talent - it fails from a lack of a system that treats every applicant fairly. The Nairobi origin of OptioHire.",
     ABOUT, "dark", ""),
    ("resources.html", "Resources | Ideas on Fairer, Faster Hiring | OptioHire",
     "Practical thinking on recruitment, screening, and what it actually takes to run a hiring process people trust.",
     resources_page(), "dark", ""),
    ("faq.html", "FAQ | Answers, Grouped by Who's Asking | OptioHire",
     "Answers for employers, HR teams, candidates, and institutions - scoring, requirements, outcomes, cohorts, and privacy.",
     faq_page(), "dark", faq_schema_script()),
    ("contact.html", "Contact | Let's Talk About How OptioHire Fits Your Team",
     "Write to OptioHire in Nairobi. Employer, HR, institution partnership, press, or other - developer@optiohire.com.",
     CONTACT, "dark", ""),
    ("privacy.html", "Privacy Policy | OptioHire",
     "What data OptioHire collects, how candidate and employer data is used, retention, rights, and how to reach us with privacy questions.",
     PRIVACY, "dark", ""),
    ("security.html", "Security & Compliance | OptioHire",
     "How candidate data is protected, access controls for HR accounts, encryption practices, and how to report a security concern.",
     SECURITY, "dark", ""),
    ("pricing.html", "Pricing | Straightforward Plans for How Your Team Hires | OptioHire",
     "Start free, then choose Starter, Growth, or Enterprise / Institution. No hidden fees, no per-CV surprise charges.",
     PRICING, "dark", ""),
    ("terms.html", "Terms of Service | OptioHire",
     "Terms of Service for the OptioHire hiring platform. Last updated 14 August 2026. Governed by the laws of Kenya.",
     TERMS, "dark", ""),
    ("customers.html", "Customers | Verified Stories When They're Ready | OptioHire",
     "Named case studies go live only after the customer has approved them. Until then, this is the home those stories will occupy.",
     CUSTOMERS, "dark", ""),
]


SITEMAP_PATHS = [
    "index.html",
    "how-it-works.html",
    "for-employers.html",
    "for-hr-teams.html",
    "for-candidates.html",
    "for-institutions.html",
    "use-cases.html",
    "partners.html",
    "about.html",
    "resources.html",
    "faq.html",
    "contact.html",
    "privacy.html",
    "security.html",
    "terms.html",
    "pricing.html",
    "customers.html",
]


def minify_css(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*([{}:;,])\s*", r"\1", text)
    return text.strip()


def write_min_css():
    raw = (ROOT / "css" / "tokens.css").read_text(encoding="utf-8")
    raw += "\n" + (ROOT / "css" / "main.css").read_text(encoding="utf-8")
    (ROOT / "css" / "site.min.css").write_text(minify_css(raw), encoding="utf-8")


def main():
    write_min_css()
    for filename, title, desc, body, theme, extra in PAGES:
        (ROOT / filename).write_text(
            page(
                title,
                desc,
                filename,
                body,
                theme,
                extra,
                crumbs=PAGE_CRUMBS.get(filename),
            ),
            encoding="utf-8",
        )
        print("wrote", filename)

    (ROOT / "404.html").write_text(
        page(
            "Page not found | OptioHire",
            "This page didn't make the shortlist. The page you're looking for doesn't exist or has moved.",
            "404.html",
            NOT_FOUND,
            "dark",
            robots="noindex, follow",
            body_class="is-404",
        ),
        encoding="utf-8",
    )
    print("wrote 404.html")

    resources_dir = ROOT / "resources"
    resources_dir.mkdir(exist_ok=True)
    keep = {art["file"] for art in ARTICLES}
    for art in ARTICLES:
        (resources_dir / art["file"]).write_text(article_html(art), encoding="utf-8")
        print("wrote resources/" + art["file"])
    for stale in resources_dir.glob("*.html"):
        if stale.name not in keep:
            stale.unlink()
            print("removed resources/" + stale.name)

    customers_dir = ROOT / "customers"
    customers_dir.mkdir(exist_ok=True)
    (customers_dir / "template.html").write_text(case_study_html(CASE_TEMPLATE), encoding="utf-8")
    print("wrote customers/template.html")

    locs = [canonical_url(p) for p in SITEMAP_PATHS]
    locs += [f"{SITE}/resources/{art['slug']}" for art in ARTICLES]
    urls = "\n".join(
        f"  <url><loc>{loc}</loc><changefreq>weekly</changefreq></url>" for loc in locs
    )
    (ROOT / "sitemap.xml").write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
""",
        encoding="utf-8",
    )
    (ROOT / "robots.txt").write_text(
        f"""User-agent: *
Allow: /

Sitemap: {SITE}/sitemap.xml
""",
        encoding="utf-8",
    )
    print("wrote sitemap.xml robots.txt css/site.min.css")


if __name__ == "__main__":
    main()
