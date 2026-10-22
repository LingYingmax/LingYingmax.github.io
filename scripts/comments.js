const commentsSection = document.querySelector('[data-comments]');

if (commentsSection) {
  const apiBase = commentsSection.dataset.apiBase || '../api';
  const slug = commentsSection.dataset.articleSlug || new URLSearchParams(window.location.search).get('slug') || 't-1';
  const list = commentsSection.querySelector('[data-comments-list]');
  const form = commentsSection.querySelector('[data-comment-form]');
  const message = commentsSection.querySelector('[data-comment-message]');
  const tokenKey = 'lingyingmax_admin_token';

  const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
  }[character]));

  const loadComments = async () => {
    const response = await fetch(`${apiBase}/articles/${encodeURIComponent(slug)}/comments`);
    if (!response.ok) throw new Error('comments unavailable');
    const comments = await response.json();
    list.innerHTML = comments.length
      ? comments.map((comment) => `<article class="comment"><strong>${escapeHtml(comment.username)}</strong><time>${escapeHtml(comment.created_at)}</time><p>${escapeHtml(comment.content)}</p></article>`).join('')
      : '<p>No comments yet.</p>';
  };

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const token = localStorage.getItem(tokenKey);
    if (!token) {
      message.textContent = 'Please login before leaving a comment.';
      return;
    }
    const content = new FormData(form).get('content');
    const response = await fetch(`${apiBase}/articles/${encodeURIComponent(slug)}/comments`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    });
    if (!response.ok) {
      message.textContent = (await response.json()).detail || 'Unable to submit comment.';
      return;
    }
    form.reset();
    message.textContent = 'Comment submitted.';
    await loadComments();
  });

  loadComments().catch(() => { list.textContent = 'Unable to load comments.'; });
}
