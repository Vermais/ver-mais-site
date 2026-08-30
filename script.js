(function(){
  // Menu mobile acessível
  var navToggle = document.getElementById('navToggle');
  var navMenu = document.getElementById('navMenu');

  function closeMenu(){
    navMenu.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', 'Abrir menu de navegação');
  }
  function openMenu(){
    navMenu.classList.add('open');
    navToggle.setAttribute('aria-expanded', 'true');
    navToggle.setAttribute('aria-label', 'Fechar menu de navegação');
  }
  navToggle.addEventListener('click', function(){
    if (navMenu.classList.contains('open')) closeMenu(); else openMenu();
  });
  navMenu.querySelectorAll('a').forEach(function(link){
    link.addEventListener('click', closeMenu);
  });
  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape' && navMenu.classList.contains('open')){
      closeMenu();
      navToggle.focus();
    }
  });
  window.addEventListener('resize', function(){
    if (window.innerWidth > 920) closeMenu();
  });

  // Lightbox acessível (foco, navegação por teclado, leitura por TalkBack/VoiceOver)
  var thumbs = Array.prototype.slice.call(document.querySelectorAll('.gthumb'));
  var lightbox = document.getElementById('lightbox');
  var lbImg = document.getElementById('lightboxImg');
  var lbCaption = document.getElementById('lightboxCaption');
  var lbClose = document.getElementById('lightboxClose');
  var lbPrev = document.getElementById('lightboxPrev');
  var lbNext = document.getElementById('lightboxNext');
  var current = 0;
  var lastFocused = null;

  function focusableInLightbox(){
    return [lbClose, lbPrev, lbNext];
  }

  function open(i){
    current = i;
    var img = thumbs[i].querySelector('img');
    lbImg.src = img.src;
    lbImg.alt = img.alt;
    lbCaption.textContent = img.alt + ' — foto ' + (i + 1) + ' de ' + thumbs.length;
    lightbox.classList.add('open');
    document.body.style.overflow = 'hidden';
    lbClose.focus();
  }
  function openFromThumb(i){
    lastFocused = document.activeElement;
    open(i);
  }
  function close(){
    lightbox.classList.remove('open');
    document.body.style.overflow = '';
    if (lastFocused) lastFocused.focus();
  }
  function next(){ open((current + 1) % thumbs.length); }
  function prev(){ open((current - 1 + thumbs.length) % thumbs.length); }

  thumbs.forEach(function(btn, i){
    btn.setAttribute('aria-label', (btn.querySelector('img').alt || 'Ver foto') + ' — ampliar');
    btn.addEventListener('click', function(){ openFromThumb(i); });
  });
  lbClose.addEventListener('click', close);
  lbNext.addEventListener('click', next);
  lbPrev.addEventListener('click', prev);
  lightbox.addEventListener('click', function(e){ if (e.target === lightbox) close(); });

  document.addEventListener('keydown', function(e){
    if (!lightbox.classList.contains('open')) return;
    if (e.key === 'Escape'){ close(); return; }
    if (e.key === 'ArrowRight'){ next(); return; }
    if (e.key === 'ArrowLeft'){ prev(); return; }
    if (e.key === 'Tab'){
      // Prende o foco dentro do lightbox (focus trap)
      var focusables = focusableInLightbox();
      var idx = focusables.indexOf(document.activeElement);
      e.preventDefault();
      var nextIdx;
      if (e.shiftKey){
        nextIdx = idx <= 0 ? focusables.length - 1 : idx - 1;
      } else {
        nextIdx = idx === -1 || idx === focusables.length - 1 ? 0 : idx + 1;
      }
      focusables[nextIdx].focus();
    }
  });
})();
