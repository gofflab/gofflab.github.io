// Goff Lab site behaviour: mobile menu, publication search, accent movies.
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
    // Match against everything shown for an entry: title, authors, venue, DOI/PMID and abstract.
    var items = Array.prototype.slice.call(document.querySelectorAll('.pub'));
    items.forEach(function (li) { li.searchText = li.textContent.replace(/\s+/g, ' ').toLowerCase(); });
    var groups = document.querySelectorAll('[data-year-group]');
    var sections = document.querySelectorAll('[data-pub-section]');
    var count = document.getElementById('pub-count');
    var initial = count.textContent;
    search.addEventListener('input', function () {
      var terms = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
      var shown = 0;
      items.forEach(function (li) {
        var hit = terms.every(function (t) { return li.searchText.indexOf(t) !== -1; });
        li.hidden = !hit;
        if (hit) shown++;
      });
      groups.forEach(function (g) { g.hidden = !g.querySelector('.pub:not([hidden])'); });
      sections.forEach(function (s) { s.hidden = !s.querySelector('.pub:not([hidden])'); });
      count.textContent = terms.length ? shown + ' matching' : initial;
    });
  }

  // Accent movies play only on wide screens with motion allowed; otherwise the still stays and nothing downloads.
  if (window.matchMedia('(min-width: 761px) and (prefers-reduced-motion: no-preference)').matches) {
    document.querySelectorAll('.accent--video').forEach(function (accent) {
      var v = accent.querySelector('video');
      v.querySelectorAll('source[data-src]').forEach(function (s) { s.src = s.dataset.src; });
      v.muted = true;
      v.load();
      accent.classList.add('is-playing');
      var playing = v.play();
      if (playing) playing.catch(function () { accent.classList.remove('is-playing'); });
    });
  }
})();
