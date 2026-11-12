// Sends the quote form to sign.limeandcedar.com/quote and shows the result without leaving the page.
(function () {
  var form = document.getElementById('quote');
  if (!form) return;
  var ok = form.querySelector('.quote__ok'), err = form.querySelector('.quote__err');
  var button = form.querySelector('button[type=submit]');
  form.elements.page.value = location.pathname;

  // ZIP → "San Jose, CA" under the field, so the customer sees the ZIP is right.
  form.querySelectorAll('[data-zip]').forEach(function (input) {
    var label = input.parentNode.querySelector('.zip-city');
    var hidden = form.elements[input.name + '_city'];
    input.addEventListener('input', function () {
      input.value = input.value.replace(/\D/g, '').slice(0, 5);
      label.textContent = ''; hidden.value = '';
      if (input.value.length !== 5) return;
      var zip = input.value;
      fetch('https://api.zippopotam.us/us/' + zip)
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) {
          if (input.value !== zip) return;
          if (!d) { label.textContent = 'ZIP not found — please check it'; label.className = 'zip-city zip-city--bad'; return; }
          var place = d.places[0]['place name'] + ', ' + d.places[0]['state abbreviation'];
          label.textContent = '✓ ' + place; label.className = 'zip-city';
          hidden.value = place;
        })
        .catch(function () {});
    });
  });

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var bad = null;
    form.querySelectorAll('[required]').forEach(function (el) {
      var v = el.value.trim();
      var wrong = !v || (el.type === 'email' && !/^\S+@\S+\.\S+$/.test(v)) ||
                  (el.type === 'tel' && v.replace(/\D/g, '').length < 10) ||
                  (el.hasAttribute('data-zip') && !/^\d{5}$/.test(v));
      el.classList.toggle('invalid', wrong);
      if (wrong && !bad) bad = el;
    });
    if (bad) { bad.focus(); return; }

    button.disabled = true;
    button.textContent = 'Sending…';
    err.hidden = true;
    fetch(form.action, { method: 'POST', body: new FormData(form) })
      .then(function (r) { if (!r.ok) throw new Error(r.status); })
      .then(function () {
        form.querySelectorAll('label, .row, button, .fine').forEach(function (el) { el.hidden = true; });
        ok.hidden = false;
        if (window.gtag) window.gtag('event', 'generate_lead');
      })
      .catch(function () {
        err.hidden = false;
        button.disabled = false;
        button.textContent = 'Get my quote';
      });
  });
})();
