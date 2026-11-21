document.addEventListener('DOMContentLoaded', function() {
    // Check for saved theme preference or respect OS preference
    const savedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const button = document.getElementById('dark-mode-toggle');

    // Icon shows the theme you'd switch TO (sun in dark mode, moon in light mode).
    const syncIcon = () => {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        button.textContent = isDark ? '\u2600\uFE0F' : '\uD83C\uDFA9';
    };

    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        syncIcon();
    }

    syncIcon(); // set the icon on load (not just after a click)
    button.addEventListener('click', toggleTheme);
});