const article = document.querySelector('[data-article]');

if (article) {
  const apiBase = article.dataset.apiBase || '../api';
  const articleSlug = article.dataset.articleSlug || new URLSearchParams(window.location.search).get('slug') || 't-1';
  const slug = encodeURIComponent(articleSlug);

  fetch(`${apiBase}/articles/${slug}`)
    .then((response) => {
      if (!response.ok) throw new Error('article unavailable');
      return response.json();
    })
    .then((data) => {
      article.querySelector('[data-article-title]').textContent = data.title;
      article.querySelector('[data-article-content]').textContent = data.content;
    })
    .catch(() => {
      // The server-rendered placeholder remains available for static hosting.
    });
}
