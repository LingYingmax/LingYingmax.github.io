const loginPanel = document.querySelector('#login-panel');
const adminPanel = document.querySelector('#admin-panel');
const loginForm = document.querySelector('#login-form');
const articleForm = document.querySelector('#article-form');
const articleList = document.querySelector('#article-list');
const loginMessage = document.querySelector('#login-message');
const articleMessage = document.querySelector('#article-message');
const tokenKey = 'lingyingmax_admin_token';
const apiBase = '/api';

const setLoggedIn = (loggedIn) => {
  loginPanel.classList.toggle('is-hidden', loggedIn);
  adminPanel.classList.toggle('is-hidden', !loggedIn);
};

const resetArticleForm = () => {
  articleForm.reset();
  articleForm.elements.id.value = '';
  articleForm.elements.published.checked = true;
  articleForm.elements.published_on.value = new Date().toISOString().slice(0, 10);
};

const authHeaders = () => ({
  Authorization: `Bearer ${localStorage.getItem(tokenKey)}`,
  'Content-Type': 'application/json'
});

const renderArticles = (articles) => {
  articleList.innerHTML = articles.map((article) => `
    <article class="admin-article">
      <h3>${article.title}</h3>
      <p>${article.slug} · ${article.published ? 'published' : 'draft'} · ${article.published_on}</p>
      <button type="button" data-edit-id="${article.id}">Edit</button>
      <button type="button" data-delete-id="${article.id}">Delete</button>
    </article>
  `).join('');
};

const loadArticles = async () => {
  const response = await fetch(`${apiBase}/admin/articles`, { headers: authHeaders() });
  if (!response.ok) throw new Error('administrator role required');
  renderArticles(await response.json());
};

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(loginForm);
  const response = await fetch(`${apiBase}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(Object.fromEntries(formData))
  });
  if (!response.ok) {
    loginMessage.textContent = 'Invalid username or password.';
    return;
  }
  const data = await response.json();
  localStorage.setItem(tokenKey, data.access_token);
  localStorage.setItem('lingyingmax_user_role', data.role || 'user');
  if (data.role !== 'admin') {
    loginMessage.textContent = '普通用户登录成功，可以返回文章页面留言。';
    return;
  }
  setLoggedIn(true);
  resetArticleForm();
  await loadArticles();
});

articleForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(articleForm);
  const payload = Object.fromEntries(formData);
  payload.published = formData.has('published');
  delete payload.id;
  const id = articleForm.elements.id.value;
  const response = await fetch(`${apiBase}/admin/articles${id ? `/${id}` : ''}`, {
    method: id ? 'PUT' : 'POST', headers: authHeaders(), body: JSON.stringify(payload)
  });
  if (!response.ok) {
    articleMessage.textContent = (await response.json()).detail || 'Unable to save article.';
    return;
  }
  articleMessage.textContent = 'Article saved.';
  resetArticleForm();
  await loadArticles();
});

articleList.addEventListener('click', async (event) => {
  const editId = event.target.dataset.editId;
  const deleteId = event.target.dataset.deleteId;
  if (editId) {
    const response = await fetch(`${apiBase}/admin/articles`, { headers: authHeaders() });
    const article = (await response.json()).find((item) => String(item.id) === editId);
    if (!article) return;
    for (const [key, value] of Object.entries(article)) {
      if (articleForm.elements[key]) articleForm.elements[key].value = value;
    }
    articleForm.elements.published.checked = article.published;
    articleForm.elements.id.value = article.id;
  }
  if (deleteId && window.confirm('Delete this article?')) {
    const response = await fetch(`${apiBase}/admin/articles/${deleteId}`, { method: 'DELETE', headers: authHeaders() });
    if (response.ok) await loadArticles();
  }
});

document.querySelector('#cancel-edit').addEventListener('click', resetArticleForm);
document.querySelector('#logout-button').addEventListener('click', () => {
  localStorage.removeItem(tokenKey);
  localStorage.removeItem('lingyingmax_user_role');
  setLoggedIn(false);
});

setLoggedIn(false);
