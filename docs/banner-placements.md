# Рекомендации по размещению рекламных баннеров

Документ описывает, где и как размещать рекламные блоки в Wiki.js под тему Viking Rise. Все примеры — адаптивные и минималистичные, подойдут для вставки в Layout или шаблоны страниц через админку.

## Ключевые зоны
1. **Верхняя панель (Hero/Topbar):** короткий баннер сразу под шапкой статьи или вверху главной страницы.
2. **Сайдбар:** вертикальный блок с изображением или CTA, который остаётся заметным при прокрутке.
3. **Внутри гайда:** горизонтальный баннер после первых 2–3 абзацев или перед блоком «Рекомендуемые гайды».
4. **Нижний колонтитул:** широкий баннер перед футером с предложением подписки или перехода в Telegram/Discord.

## Общие правила
- **Размеры:** избегайте фиксированных размеров; используйте гибкую ширину и `max-width`. Картинки подгоняйте через `object-fit: cover`.
- **Текст:** 1–2 строки (до ~50 символов) и короткий CTA. Избегайте перегруженности.
- **Контраст:** фон баннера тёмно-серый или глубокий синий (`#1f2833`), кнопка — золотой акцент `#d9a441`.
- **Адаптивность:** на мобильных баннеры складываются в колонку; уменьшайте внутренние отступы и размер текста.

## HTML/CSS примеры
Ниже приведены готовые блоки. Их можно вставить в шаблон или на страницу с помощью Custom HTML. Все классы стилизованы в `assets/custom-theme.css`.

### 1. Горизонтальный баннер для контента
```html
<div class="vr-banner vr-banner--wide">
  <div class="vr-banner__body">
    <div>
      <p class="vr-banner__label">Поддержи проект</p>
      <h3 class="vr-banner__title">Получай редкие ресурсы быстрее</h3>
      <p class="vr-banner__text">Топовые советы по фарму + ежедневные бонусы в нашем Telegram.</p>
    </div>
    <a class="vr-button" href="https://t.me/example" target="_blank" rel="noopener">Перейти</a>
  </div>
  <div class="vr-banner__media">
    <img src="https://placehold.co/480x220/png" alt="Пример баннера" loading="lazy" />
  </div>
</div>
```

### 2. Сайдбарный баннер
```html
<aside class="vr-banner vr-banner--sidebar">
  <img class="vr-banner__media" src="https://placehold.co/360x640/png" alt="Сайдбар баннер" loading="lazy" />
  <div class="vr-banner__body">
    <p class="vr-banner__label">Скидка на бусты</p>
    <h3 class="vr-banner__title">-20% для новых командиров</h3>
    <p class="vr-banner__text">Акция действует до конца недели. Успей забрать!</p>
    <a class="vr-button vr-button--ghost" href="https://example.com" target="_blank" rel="noopener">Подробнее</a>
  </div>
</aside>
```

### 3. Внутри гайда (inline)
```html
<div class="vr-banner vr-banner--inline">
  <div class="vr-banner__body">
    <p class="vr-banner__label">Рекомендуем</p>
    <h4 class="vr-banner__title">Лучшие связки героев для KvK</h4>
    <p class="vr-banner__text">Подборки сетапов и ротаций для любых задач.</p>
  </div>
  <a class="vr-button" href="https://example.com/guides" target="_blank" rel="noopener">Читать гайд</a>
</div>
```

## Подсказки по вставке в Wiki.js
1. **Layout:** `Administration → Theme → Layout` — вставьте HTML блоки в нужные места (например, после `block content`).
2. **Custom CSS:** добавьте стили из `assets/custom-theme.css` в раздел `Custom CSS` (Look & Feel).
3. **Отступы:** если Wiki.js уже добавляет собственные паддинги, при необходимости оборачивайте баннер в контейнер `<div class="vr-section"> ... </div>` — в CSS есть готовые отступы.
4. **Локализация:** подменяйте тексты CTA под аудиторию (Telegram/Discord/YouTube). Избегайте агрессивных формулировок.
5. **Изображения:** используйте оптимизированные (WEBP/AVIF) версии и `loading="lazy"` для производительности.

## Быстрая адаптация
- Замените ссылки `example.com` и `t.me/example` на реальные кампании.
- Для тёмных страниц уменьшите прозрачность фона (`--vr-banner-bg`) или усилите тень, чтобы баннеры выделялись.
- Если нужно отключить изображения, удалите блок `<div class="vr-banner__media">` — баннеры останутся читабельными.
