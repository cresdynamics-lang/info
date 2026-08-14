(() => {
  const GA_ID = document.documentElement.dataset.gaId || "";
  const CONSENT_KEY = "optiohire-consent";
  const header = document.querySelector("[data-site-header]");
  const toggle = document.querySelector("[data-menu-toggle]");
  const mobile = document.querySelector("[data-nav-mobile]");
  const signinToggle = document.querySelector("[data-signin-toggle]");
  const signinMenu = document.querySelector("[data-signin-menu]");

  const track = (name, params = {}) => {
    if (typeof window.gtag === "function") window.gtag("event", name, params);
  };

  const loadGA = () => {
    if (!GA_ID || window.gtag) return;
    const s = document.createElement("script");
    s.async = true;
    s.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(GA_ID)}`;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function gtag() {
      window.dataLayer.push(arguments);
    };
    window.gtag("js", new Date());
    window.gtag("config", GA_ID, { anonymize_ip: true });
  };

  const readConsent = () => {
    try {
      return JSON.parse(localStorage.getItem(CONSENT_KEY) || "null");
    } catch {
      return null;
    }
  };

  const saveConsent = (consent) => {
    localStorage.setItem(CONSENT_KEY, JSON.stringify({ ...consent, essential: true, ts: Date.now() }));
    if (consent.analytics) loadGA();
  };

  const applyConsent = () => {
    const consent = readConsent();
    if (consent?.analytics) loadGA();
  };

  const banner = document.querySelector("[data-cookie-banner]");
  const modal = document.querySelector("[data-cookie-modal]");
  const consent = readConsent();
  if (banner) banner.hidden = Boolean(consent);
  applyConsent();

  const openModal = () => {
    if (!modal) return;
    const current = readConsent() || { essential: true, analytics: false, marketing: false };
    const analytics = modal.querySelector("[name='analytics']");
    const marketing = modal.querySelector("[name='marketing']");
    if (analytics) analytics.checked = Boolean(current.analytics);
    if (marketing) marketing.checked = Boolean(current.marketing);
    modal.hidden = false;
  };

  document.querySelector("[data-cookie-accept]")?.addEventListener("click", () => {
    saveConsent({ essential: true, analytics: true, marketing: true });
    if (banner) banner.hidden = true;
    if (modal) modal.hidden = true;
  });

  document.querySelector("[data-cookie-manage]")?.addEventListener("click", openModal);
  document.querySelectorAll("[data-cookie-settings]").forEach((el) => el.addEventListener("click", openModal));
  document.querySelector("[data-cookie-save]")?.addEventListener("click", () => {
    const analytics = modal?.querySelector("[name='analytics']")?.checked;
    const marketing = modal?.querySelector("[name='marketing']")?.checked;
    saveConsent({ essential: true, analytics: Boolean(analytics), marketing: Boolean(marketing) });
    if (banner) banner.hidden = true;
    if (modal) modal.hidden = true;
  });
  document.querySelector("[data-cookie-close]")?.addEventListener("click", () => {
    if (modal) modal.hidden = true;
  });
  modal?.addEventListener("click", (e) => {
    if (e.target === modal) modal.hidden = true;
  });

  if (toggle && header) {
    toggle.addEventListener("click", () => {
      const open = header.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      if (mobile) mobile.setAttribute("aria-hidden", String(!open));
      document.body.style.overflow = open ? "hidden" : "";
      if (signinMenu) {
        signinMenu.hidden = true;
        if (signinToggle) signinToggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  if (signinToggle && signinMenu) {
    signinToggle.addEventListener("click", (e) => {
      e.stopPropagation();
      const open = signinMenu.hidden;
      signinMenu.hidden = !open;
      signinToggle.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("click", (e) => {
      if (!signinMenu.hidden && !e.target.closest(".signin-wrap")) {
        signinMenu.hidden = true;
        signinToggle.setAttribute("aria-expanded", "false");
      }
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        signinMenu.hidden = true;
        if (signinToggle) signinToggle.setAttribute("aria-expanded", "false");
        if (modal) modal.hidden = true;
        if (header?.classList.contains("is-open")) toggle?.click();
      }
    });
  }

  const setHeaderTheme = (theme) => {
    if (!header) return;
    header.classList.remove("theme-dark", "theme-navy", "theme-teal", "theme-white");
    header.classList.add(`theme-${theme}`);
  };

  const initial = header?.dataset.initialTheme || "dark";
  setHeaderTheme(initial);

  const bands = [...document.querySelectorAll("[data-header-theme]")];
  if (header && bands.length) {
    const io = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible) setHeaderTheme(visible.target.dataset.headerTheme);
      },
      { rootMargin: "-12% 0px -70% 0px", threshold: [0, 0.2, 0.5, 1] }
    );
    bands.forEach((el) => io.observe(el));
  }

  const hero = document.querySelector(".band-hero");
  const onScroll = () => {
    if (!header) return;
    const past = hero ? window.scrollY > hero.offsetHeight * 0.55 : window.scrollY > 40;
    header.classList.toggle("is-scrolled", past);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  const counters = document.querySelectorAll("[data-count]");
  if (counters.length) {
    const animate = (el) => {
      const target = Number(el.dataset.count);
      const suffix = el.dataset.suffix || "";
      const prefix = el.dataset.prefix || "";
      const decimals = Number(el.dataset.decimals || 0);
      const duration = 1400;
      const start = performance.now();
      const tick = (now) => {
        const t = Math.min(1, (now - start) / duration);
        const eased = 1 - Math.pow(1 - t, 3);
        const value = target * eased;
        el.textContent = `${prefix}${decimals ? value.toFixed(decimals) : Math.round(value).toLocaleString()}${suffix}`;
        if (t < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };

    const cio = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          animate(entry.target);
          obs.unobserve(entry.target);
        });
      },
      { threshold: 0.4 }
    );
    counters.forEach((el) => cio.observe(el));
  }

  document.querySelectorAll("[data-filter]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const group = btn.closest("[data-filter-group]");
      const value = btn.dataset.filter;
      group.querySelectorAll("[data-filter]").forEach((b) => b.classList.toggle("is-active", b === btn));
      const cards = group.querySelectorAll("[data-category]");
      let visible = 0;
      cards.forEach((card) => {
        const hide = value !== "all" && card.dataset.category !== value;
        card.hidden = hide;
        if (!hide) visible += 1;
      });
      const empty = group.querySelector("[data-filter-empty]");
      if (empty) empty.hidden = visible > 0;
    });
  });

  const presetFilter = new URLSearchParams(window.location.search).get("filter");
  if (presetFilter) {
    document.querySelector(`[data-filter="${presetFilter}"]`)?.click();
  }

  const faqRoot = document.querySelector("[data-faq-tabs]");
  if (faqRoot) {
    faqRoot.querySelectorAll("[data-faq-tab]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const key = btn.dataset.faqTab;
        faqRoot.querySelectorAll("[data-faq-tab]").forEach((b) => {
          const on = b === btn;
          b.classList.toggle("is-active", on);
          b.setAttribute("aria-selected", String(on));
        });
        faqRoot.querySelectorAll("[data-faq-panel]").forEach((panel) => {
          panel.hidden = panel.dataset.faqPanel !== key;
        });
      });
    });
  }

  const pageCampaign = document.body?.dataset.page || "site";
  document.querySelectorAll('a[href*="optiohire.com/auth"], a[href*="applications.optiohire.com"]').forEach((a) => {
    try {
      const url = new URL(a.href);
      if (!url.searchParams.has("utm_source")) {
        url.searchParams.set("utm_source", "optiohire-site");
        url.searchParams.set("utm_medium", a.dataset.utmMedium || "cta");
        url.searchParams.set("utm_campaign", a.dataset.utmCampaign || pageCampaign);
        a.href = url.toString();
      }
    } catch {
      /* ignore relative parse issues */
    }
  });

  document.querySelectorAll("[data-track]").forEach((el) => {
    el.addEventListener("click", () => track(el.dataset.track, { page: pageCampaign }));
  });

  const setBtnState = (btn, state) => {
    if (!btn) return;
    if (!btn.dataset.label) btn.dataset.label = btn.innerHTML;
    btn.classList.toggle("is-loading", state === "loading");
    btn.disabled = state === "loading" || state === "sent";
    if (state === "loading") {
      btn.innerHTML = '<span class="btn-spinner" aria-hidden="true"></span> Sending';
    } else if (state === "sent") {
      btn.innerHTML = "Sent ✓";
    } else {
      btn.innerHTML = btn.dataset.label;
      btn.disabled = false;
    }
  };

  const markField = (input, ok) => {
    const label = input.closest("label");
    if (!label) return;
    label.classList.toggle("is-error", !ok);
    label.classList.toggle("is-valid", ok && Boolean(input.value));
    let err = label.querySelector(".field-error");
    if (!ok) {
      if (!err) {
        err = document.createElement("span");
        err.className = "field-error";
        label.appendChild(err);
      }
      err.textContent = input.type === "email" ? "Enter a valid email." : "This field is required.";
    }
  };

  const validateForm = (form) => {
    let valid = true;
    form.querySelectorAll("[required]").forEach((input) => {
      const ok = input.checkValidity();
      markField(input, ok);
      if (!ok) valid = false;
    });
    return valid;
  };

  document.querySelectorAll("[data-contact-form] [required], [data-newsletter] [required]").forEach((input) => {
    input.addEventListener("blur", () => {
      if (input.value) markField(input, input.checkValidity());
    });
    input.addEventListener("input", () => {
      if (input.closest("label")?.classList.contains("is-error")) markField(input, input.checkValidity());
    });
  });

  const newsletter = document.querySelector("[data-newsletter]");
  if (newsletter) {
    newsletter.addEventListener("submit", (e) => {
      e.preventDefault();
      if (!validateForm(newsletter)) return;
      const btn = newsletter.querySelector("[type='submit']");
      setBtnState(btn, "loading");
      const email = newsletter.querySelector("[name='email']")?.value || "";
      const subject = encodeURIComponent("OptioHire resources list");
      const body = encodeURIComponent(`Please add this email to the resources mailing list:\n${email}`);
      track("newsletter_signup");
      window.setTimeout(() => {
        window.location.href = `mailto:developer@optiohire.com?subject=${subject}&body=${body}`;
        setBtnState(btn, "sent");
        const ok = document.querySelector("[data-newsletter-success]");
        if (ok) {
          ok.hidden = false;
          ok.classList.add("is-visible");
        }
        window.setTimeout(() => setBtnState(btn, "default"), 1800);
      }, 400);
    });
  }

  const form = document.querySelector("[data-contact-form]");
  if (form) {
    const typeSelect = form.querySelector("[data-inquiry-type], [name='type']");
    const preset = new URLSearchParams(window.location.search).get("type");
    if (typeSelect && preset) {
      const match = [...typeSelect.options].some((opt) => opt.value === preset);
      if (match) typeSelect.value = preset;
    }
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (!validateForm(form)) return;
      const btn = form.querySelector("[type='submit']");
      setBtnState(btn, "loading");
      const data = new FormData(form);
      const subject = encodeURIComponent(`OptioHire inquiry - ${data.get("type") || "General"}`);
      const body = encodeURIComponent(
        `Name: ${data.get("name")}\nEmail: ${data.get("email")}\nOrganization: ${data.get("org")}\nType: ${data.get("type")}\n\n${data.get("message")}`
      );
      track("contact_form_submit", { inquiry_type: data.get("type") });
      window.setTimeout(() => {
        window.location.href = `mailto:developer@optiohire.com?subject=${subject}&body=${body}`;
        setBtnState(btn, "sent");
        form.classList.add("is-sent");
      }, 400);
    });
  }
})();
