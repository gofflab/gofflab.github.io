// Goff Lab site behaviour: mobile menu, publication search, lazy Altmetric badges.
(function () {
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  var search = document.getElementById('pub-search');
  if (search) {
    var items = Array.prototype.slice.call(document.querySelectorAll('.pub[data-search]'));
    var groups = document.querySelectorAll('[data-year-group]');
    var count = document.getElementById('pub-count');
    var initial = count.textContent;
    search.addEventListener('input', function () {
      var terms = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
      var shown = 0;
      items.forEach(function (li) {
        var hit = terms.every(function (t) { return li.dataset.search.indexOf(t) !== -1; });
        li.hidden = !hit;
        if (hit) shown++;
      });
      groups.forEach(function (g) { g.hidden = !g.querySelector('.pub:not([hidden])'); });
      count.textContent = terms.length ? shown + ' matching' : initial;
    });
  }

  // Load the Altmetric badge script only once someone opens an abstract.
  var loaded = false;
  document.addEventListener('toggle', function (e) {
    if (loaded || !e.target.querySelector || !e.target.querySelector('.altmetric-embed')) return;
    loaded = true;
    var s = document.createElement('script');
    s.src = 'https://d1bxh8uas1mnw7.cloudfront.net/assets/embed.js';
    s.async = true;
    document.body.appendChild(s);
  }, true);
})();

