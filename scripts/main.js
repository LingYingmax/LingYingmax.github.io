//导航栏
const btn = document.querySelector('.menu-btn-mobile');
const menu = document.querySelector('.mobile-menu');

btn.addEventListener('click', () => {
    menu.classList.toggle('show');
});

window.addEventListener('resize', () => {
  if (window.innerWidth > 768) {
    menu.classList.remove('show'); // 清除展开状态
  }
});

const memubtn = document.querySelectorAll('[data-theme-toggle]');
const html = document.documentElement;

// 初始从 localStorage 读取
const savedTheme = localStorage.getItem('theme');

// 优先使用用户选择的
if (savedTheme === 'dark') {
  html.classList.add('dark');
} else if (savedTheme === 'light') {
  html.classList.remove('dark');
} else {
  // 若未选择 → 跟随系统
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    html.classList.add('dark');
  }
}

// 点击切换主题（正确）
memubtn.forEach(btn => {
  btn.addEventListener('click', () => {
    html.classList.toggle('dark');

    localStorage.setItem(
      'theme',
      html.classList.contains('dark') ? 'dark' : 'light'
    );
  });
});
