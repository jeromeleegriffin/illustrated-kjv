(() => {
  const byId = id => document.getElementById(id);
  let previousDisabled = true, nextDisabled = true;
  const selectedText = () => Boolean(window.getSelection?.()?.toString());
  const blocked = () => selectedText() ||
    [...document.querySelectorAll('.modal-backdrop')].some(el => !el.hidden) ||
    byId('studyPanel')?.classList.contains('open');

  window.ReaderNavigation = {
    init(onStep) {
      const scripture = byId('scripture');
      const navigate = delta => {
        if (delta < 0 ? previousDisabled : nextDisabled) return;
        onStep(delta);
        byId('chapterTitle')?.focus({preventScroll: true});
      };
      byId('previousChapterBottom').onclick = () => navigate(-1);
      byId('nextChapterBottom').onclick = () => navigate(1);
      let gesture = null;
      scripture.addEventListener('touchstart', event => {
        gesture = null;
        if (event.touches.length !== 1 || blocked()) return;
        // Leave browser edge gestures and small study-note controls alone.
        if (event.target.closest('a,input,select,textarea,[contenteditable],.bullinger-verse-button')) return;
        const touch = event.touches[0];
        if (touch.clientX < 25 || touch.clientX > window.innerWidth - 25) return;
        gesture = {id: touch.identifier, x: touch.clientX, y: touch.clientY,
          time: Date.now(), scrollY: window.scrollY};
      }, {passive: true});
      scripture.addEventListener('touchmove', event => {
        if (!gesture) return;
        if (event.touches.length !== 1 || blocked()) { gesture = null; return; }
        const touch = event.touches[0];
        if (touch.identifier !== gesture.id || Math.abs(touch.clientY - gesture.y) > 40 ||
            Math.abs(window.scrollY - gesture.scrollY) > 10) gesture = null;
      }, {passive: true});
      scripture.addEventListener('touchend', event => {
        const start = gesture;
        gesture = null;
        if (!start || event.touches.length || blocked() || Date.now() - start.time > 1000 ||
            Math.abs(window.scrollY - start.scrollY) > 10) return;
        const touch = [...event.changedTouches].find(t => t.identifier === start.id);
        if (!touch) return;
        const dx = touch.clientX - start.x, dy = touch.clientY - start.y;
        if (Math.abs(dx) < 75 || Math.abs(dy) > 40 || Math.abs(dx) < Math.abs(dy) * 2) return;
        // Cancel the synthetic word click only after a deliberate horizontal swipe.
        if (event.cancelable) event.preventDefault();
        navigate(dx < 0 ? 1 : -1);
      }, {passive: false});
      scripture.addEventListener('touchcancel', () => { gesture = null; }, {passive: true});
    },
    update(data, book, chapter) {
      previousDisabled = book === 0 && chapter === 1;
      nextDisabled = book === data.books.length - 1 && chapter === data.books[book].chapters.length;
      for (const id of ['previousChapter', 'previousChapterBottom']) byId(id).disabled = previousDisabled;
      for (const id of ['nextChapter', 'nextChapterBottom']) byId(id).disabled = nextDisabled;
      byId('bottomChapterReference').textContent = `${data.books[book].name} ${chapter}`;
    }
  };
})();
