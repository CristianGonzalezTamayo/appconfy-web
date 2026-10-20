/* Confy · theme.js — único JavaScript del sitio: modo claro/oscuro.
   Sin elección guardada, sigue la preferencia del sistema. */
(function () {
  var KEY = 'confy-theme', root = document.documentElement;
  var mq = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  function stored() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function apply() { root.setAttribute('data-theme', stored() || (mq && mq.matches ? 'dark' : 'light')); }
  apply();
  if (mq && mq.addEventListener) mq.addEventListener('change', function () { if (!stored()) apply(); });
  document.addEventListener('DOMContentLoaded', function () {
    var btns = document.querySelectorAll('.theme-toggle');
    function sync() { for (var i = 0; i < btns.length; i++) btns[i].setAttribute('aria-pressed', root.getAttribute('data-theme') === 'dark' ? 'true' : 'false'); }
    sync();
    for (var i = 0; i < btns.length; i++) btns[i].addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(KEY, next); } catch (e) {}
      root.setAttribute('data-theme', next); sync();
    });
  });
})();
