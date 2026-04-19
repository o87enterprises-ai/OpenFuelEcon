(function() {
  const localeFromPath = (() => {
    const parts = window.location.pathname.split('/').filter(Boolean);
    const known = ['en-us', 'en-gb', 'en-ca', 'en-au'];
    if (parts.length && known.includes(parts[0])) return parts[0];
    return 'en-us';
  })();

  function defineT(strings) {
    window.FUELECON_STRINGS = strings || window.FUELECON_STRINGS || {};
    window.FUELECON_LOCALE = window.FUELECON_LOCALE || localeFromPath;
    window.t = function(key, fallback) {
      if (!key) return fallback;
      return key.split('.').reduce((obj, k) => (obj ? obj[k] : null), window.FUELECON_STRINGS) || fallback;
    };
  }

  // If already provided by build (homepage), just define the helper and exit.
  if (window.FUELECON_STRINGS) {
    defineT(window.FUELECON_STRINGS);
    return;
  }

  const i18nUrl = `/i18n/${localeFromPath}.json`;

  // Expose a promise for async loading
  window.I18N_READY = fetch(i18nUrl)
    .then(r => {
      if (!r.ok) throw new Error('i18n fetch failed: ' + r.status);
      return r.json();
    })
    .then(data => {
      defineT(data.js || {});
      document.dispatchEvent(new Event('i18n-ready'));
    })
    .catch(err => {
      console.error('[i18n]', err);
      defineT({});
      document.dispatchEvent(new Event('i18n-ready'));
    });

  // Also provide synchronous fallback: if someone calls t() before load, they get fallback
  defineT({}); // temporary empty; will be overwritten when fetch completes
})();
