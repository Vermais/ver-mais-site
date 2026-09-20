(function () {
  var root = document.documentElement;
  var nav = document.getElementById('nav');
  var toggle = document.getElementById('toggle');
  var menu = document.getElementById('menu');
  var themeToggle = document.getElementById('themeToggle');

  function updateThemeLabel() {
    var dark = root.dataset.theme === 'dark';
    themeToggle.setAttribute('aria-label', dark ? 'Ativar modo claro' : 'Ativar modo escuro');
    themeToggle.setAttribute('aria-pressed', String(dark));
  }
  themeToggle.addEventListener('click', function () {
    var next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    function applyTheme() {
      root.dataset.theme = next;
      localStorage.setItem('vermais-theme', next);
      updateThemeLabel();
    }
    if (!matchMedia('(prefers-reduced-motion: reduce)').matches && document.startViewTransition) {
      document.startViewTransition(applyTheme);
    } else {
      applyTheme();
    }
  });
  updateThemeLabel();

  function closeMenu(returnFocus) {
    menu.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'Abrir menu');
    if (returnFocus) toggle.focus();
  }
  toggle.addEventListener('click', function () {
    var open = !menu.classList.contains('open');
    menu.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
  });
  menu.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () { closeMenu(false); });
  });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && menu.classList.contains('open')) closeMenu(true);
  });
  addEventListener('resize', function () {
    if (innerWidth > 900 && menu.classList.contains('open')) closeMenu(false);
  });
  addEventListener('scroll', function () { nav.classList.toggle('scrolled', scrollY > 12); }, { passive: true });

  var reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var observer = !reduceMotion && 'IntersectionObserver' in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) { entry.target.classList.add('visible'); observer.unobserve(entry.target); }
    });
  }, { threshold: 0.1 }) : null;
  document.querySelectorAll('.reveal').forEach(function (element) {
    if (observer) observer.observe(element); else element.classList.add('visible');
  });

  var downloadButton = document.getElementById('downloadBtn');
  var downloadLabel = document.getElementById('downloadLabel');
  downloadButton.addEventListener('click', function (event) {
    event.preventDefault();
    if (downloadButton.classList.contains('loading')) return;

    var base = downloadButton.dataset.downloadBase;
    var partCount = Number(downloadButton.dataset.downloadParts);
    var parts = Array.from({ length: partCount }, function (_, index) {
      return base + String(index + 1).padStart(2, '0');
    });

    downloadButton.classList.add('loading');
    downloadButton.setAttribute('aria-busy', 'true');
    downloadLabel.textContent = 'Preparando download…';

    Promise.all(parts.map(function (part) {
      return fetch(part).then(function (response) {
        if (!response.ok) throw Error('Parte do aplicativo indisponível');
        return response.arrayBuffer();
      });
    })).then(function (buffers) {
      var blob = new Blob(buffers, { type: 'application/vnd.android.package-archive' });
      var objectUrl = URL.createObjectURL(blob);
      var link = document.createElement('a');
      link.href = objectUrl;
      link.download = 'Ver + v0.5.apk';
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(function () { URL.revokeObjectURL(objectUrl); }, 60000);
      downloadLabel.textContent = 'Download iniciado';
    }).catch(function () {
      downloadLabel.textContent = 'Ver lançamentos no GitHub';
      window.location.href = downloadButton.href;
    }).finally(function () {
      downloadButton.classList.remove('loading');
      downloadButton.removeAttribute('aria-busy');
      setTimeout(function () { downloadLabel.textContent = 'Baixar versão 0.5'; }, 3500);
    });
  });

  var records = [
    { src: 'assets/g1.jpg', date: '12 de agosto de 2026', dateISO: '2026-08-12', title: 'Registro 16', type: 'Desenvolvimento do projeto', description: 'Desenvolvimento do projeto Ver+, com revisão do aplicativo, testes e melhorias.' },
    { src: 'assets/g2.jpg', date: '12 de agosto de 2026', dateISO: '2026-08-12', title: 'Registro 8', type: 'Desenvolvimento do projeto', description: 'Desenvolvimento do projeto Ver+, organização dos materiais e evolução das funcionalidades.' },
    { src: 'assets/g3.jpg', date: '12 de agosto de 2026', dateISO: '2026-08-12', title: 'Registro 6', type: 'Desenvolvimento do projeto', description: 'Desenvolvimento do projeto Ver+, com programação, ajustes e validação da experiência.' },
    { src: 'assets/g4.jpg', date: '6 de agosto de 2026', dateISO: '2026-08-06', title: 'Registro 2', type: 'Etapas finais', description: 'Alinhamento das etapas finais, revisão do modelo e organização da documentação do projeto.' }
  ];
  var recordIndex = 0;
  var fieldGallery = document.querySelector('.field-gallery');
  var fieldStage = document.querySelector('.field-stage');
  var fieldImage = document.getElementById('fieldImage');
  var fieldThumbs = document.getElementById('fieldThumbs');
  var fieldStatus = document.getElementById('fieldStatus');
  var prevButton = document.getElementById('fieldPrev');
  var nextButton = document.getElementById('fieldNext');

  function showRecord(index, options) {
    options = options || {};
    recordIndex = (index + records.length) % records.length;
    var record = records[recordIndex];
    fieldImage.src = record.src;
    fieldImage.alt = record.title + ': ' + record.description + ' Data: ' + record.date + '.';
    document.getElementById('fieldCurrent').textContent = String(recordIndex + 1).padStart(2, '0');
    document.getElementById('fieldTitle').textContent = record.title;
    document.getElementById('fieldType').textContent = record.type;
    document.getElementById('fieldDescription').textContent = record.description;
    var date = document.getElementById('fieldDate');
    date.textContent = record.date;
    date.dateTime = record.dateISO;
    fieldThumbs.querySelectorAll('button').forEach(function (button, i) {
      var active = i === recordIndex;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    var activeThumb = fieldThumbs.children[recordIndex];
    if (activeThumb) {
      activeThumb.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'nearest', inline: 'center' });
      if (options.focusThumb) activeThumb.focus();
    }
    if (options.announce) fieldStatus.textContent = record.title + ', item ' + (recordIndex + 1) + ' de ' + records.length + '. ' + record.date + '. ' + record.description;
  }

  records.forEach(function (record, index) {
    var button = document.createElement('button');
    button.className = 'field-thumb';
    button.type = 'button';
    button.setAttribute('aria-label', 'Mostrar ' + record.title + ', ' + record.date);
    button.setAttribute('aria-pressed', 'false');
    var image = document.createElement('img');
    image.src = record.src;
    image.alt = '';
    image.loading = 'lazy';
    button.appendChild(image);
    button.addEventListener('click', function () { showRecord(index, { announce: true }); });
    fieldThumbs.appendChild(button);
  });
  document.getElementById('fieldTotal').textContent = String(records.length).padStart(2, '0');
  prevButton.addEventListener('click', function () { showRecord(recordIndex - 1, { announce: true }); });
  nextButton.addEventListener('click', function () { showRecord(recordIndex + 1, { announce: true }); });
  fieldGallery.addEventListener('keydown', function (event) {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
    event.preventDefault();
    showRecord(recordIndex + (event.key === 'ArrowRight' ? 1 : -1), { announce: true, focusThumb: true });
  });
  var touchStartX = 0;
  var touchStartY = 0;
  fieldStage.addEventListener('touchstart', function (event) {
    touchStartX = event.changedTouches[0].clientX;
    touchStartY = event.changedTouches[0].clientY;
  }, { passive: true });
  fieldStage.addEventListener('touchend', function (event) {
    var dx = event.changedTouches[0].clientX - touchStartX;
    var dy = event.changedTouches[0].clientY - touchStartY;
    if (Math.abs(dx) > 55 && Math.abs(dx) > Math.abs(dy) * 1.25) showRecord(recordIndex + (dx < 0 ? 1 : -1), { announce: true });
  }, { passive: true });

  showRecord(0);
  document.getElementById('year').textContent = new Date().getFullYear();
})();
