(() => {
  const toc = document.querySelector('.book-toc');
  if (!toc) return;
  const search = document.getElementById('toc-search');
  const filter = document.getElementById('toc-filter');
  const result = document.getElementById('toc-result');
  const initialResult = result.textContent;
  const chapters = [...toc.querySelectorAll('.toc-chapter')];
  const rows = [...toc.querySelectorAll('.toc-row')];
  const expand = document.getElementById('toc-expand');
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase();
  let savedOpen = null;

  function updateExpandLabel() {
    const visible = chapters.filter(chapter => !chapter.hidden);
    expand.textContent = visible.length && visible.every(chapter => chapter.open) ? '收起全部' : '展开全部';
  }

  function update() {
    const terms = normalize(search.value).trim().split(/\s+/).filter(Boolean);
    const active = terms.length > 0 || filter.value !== 'all';
    if (active && savedOpen === null) savedOpen = chapters.map(chapter => chapter.open);
    let matches = 0;
    let ready = 0;
    rows.forEach(row => {
      const isReady = row.dataset.ready === 'true';
      const isArticle = row.dataset.kind === 'article';
      const matchesFilter = filter.value === 'all' || (isArticle && (filter.value === 'ready' ? isReady : !isReady));
      const haystack = normalize(row.dataset.search);
      row.hidden = !matchesFilter || !terms.every(term => haystack.includes(term));
      if (!row.hidden) { matches++; if (isReady) ready++; }
    });
    chapters.forEach((chapter, i) => {
      chapter.hidden = ![...chapter.querySelectorAll('.toc-row')].some(row => !row.hidden);
      if (active && !chapter.hidden) chapter.open = true;
      else if (!active && savedOpen !== null) chapter.open = savedOpen[i];
    });
    if (!active) savedOpen = null;
    result.textContent = active ? `找到 ${matches} 个目录项 · ${ready} 篇已上线` : initialResult;
    document.getElementById('toc-empty').hidden = matches > 0;
    updateExpandLabel();
  }

  search.addEventListener('input', update);
  filter.addEventListener('change', update);
  expand.addEventListener('click', () => {
    const visible = chapters.filter(chapter => !chapter.hidden);
    const open = !visible.every(chapter => chapter.open);
    visible.forEach(chapter => chapter.open = open);
    updateExpandLabel();
  });
  chapters.forEach(chapter => chapter.addEventListener('toggle', updateExpandLabel));

  function showHashTarget() {
    const target = document.getElementById(location.hash.slice(1));
    if (target?.classList.contains('toc-chapter')) {
      search.value = ''; filter.value = 'all'; update();
      target.open = true;
      target.scrollIntoView();
    }
  }
  window.addEventListener('hashchange', showHashTarget);
  document.querySelectorAll('.site-nav a[href^="#chapter-"]').forEach(link => {
    link.addEventListener('click', () => {
      search.value = ''; filter.value = 'all'; update();
      document.getElementById(link.hash.slice(1)).open = true;
    });
  });
  toc.querySelector('.toc-tools').hidden = false;
  updateExpandLabel();
  if (location.hash) showHashTarget();
})();
