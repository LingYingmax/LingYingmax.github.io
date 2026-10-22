const articleList = document.querySelector('[data-articles-list]');

if (articleList) {
  const apiBase = articleList.dataset.apiBase || '/api';
  const fallback = articleList.innerHTML;

  const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (character) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }[character]));

  fetch(`${apiBase}/articles`)
    .then((response) => {
      if (!response.ok) throw new Error('articles unavailable');
      return response.json();
    })
    .then((articles) => {
      if (!articles.length) return;
      articleList.innerHTML = articles.map((article) => `
        <div class="page-box">
          <h2>
            <a class="page-link" href="page/article.html?slug=${encodeURIComponent(article.slug)}">${escapeHtml(article.title)}</a>
          </h2>
          <p>${escapeHtml(article.summary)}</p>
          <div class="time">
            <span>${escapeHtml(article.published_on)}</span>
          </div>
        </div>
      `).join('');
    })
    .catch(() => {
      articleList.innerHTML = fallback;
    });
}
