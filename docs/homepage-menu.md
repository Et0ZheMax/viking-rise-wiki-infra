# Домашняя страница Wiki.js: меню тем и подтем

Этот шаблон помогает быстро собрать визуально выразительную главную страницу в стиле Viking Rise: hero-зона, кнопки-переходы, карточки разделов и неоновые подсказки для новичков.

> Важно: перед использованием убедитесь, что CSS из `assets/custom-theme.css` уже добавлен в **Administration → Look & Feel → Custom CSS**.

---

## 1) Как использовать в Wiki.js

1. Откройте страницу, которую хотите сделать главной (например, `home`).
2. Переключите редактор в режим Markdown.
3. Вставьте HTML-блок ниже целиком.
4. Обновите ссылки (`/start`, `/heroes`, `/events` и т.д.) под ваши реальные пути.

---

## 2) Готовый блок для главной страницы

```html
<!--
  Домашний экран с темами/подтемами.
  Можно вставлять целиком на страницу home в Wiki.js.
  Все стили берутся из assets/custom-theme.css (блоки .vr-home* и .vr-topic-*).
-->
<div class="vr-home">
  <section class="vr-home-hero">
    <div class="vr-home-hero__inner">
      <p class="vr-home-hero__badge">Viking Rise Wiki</p>
      <h1 class="vr-home-hero__title">Навигационный <span>портал знаний</span></h1>
      <p class="vr-home-hero__subtitle">
        Выбирайте тему, переходите к нужным подтемам и получайте быстрые подсказки,
        чтобы не теряться между гайдами, событиями и развитием аккаунта.
      </p>

      <!-- Быстрые кнопки CTA: вход в ключевые сценарии для игрока -->
      <div class="vr-home-quick-actions">
        <a class="vr-button" href="/start">🚀 Начать с нуля</a>
        <a class="vr-button vr-button--ghost" href="/events">🛡 Актуальные события</a>
        <a class="vr-button vr-button--ghost" href="/faq">❓ Быстрая справка</a>
      </div>

      <!-- Чипы-теги: быстрый переход к крупным разделам -->
      <div class="vr-home-chips">
        <a class="vr-home-chip" href="/heroes">Герои</a>
        <a class="vr-home-chip" href="/builds">Билды</a>
        <a class="vr-home-chip" href="/economy">Экономика</a>
        <a class="vr-home-chip" href="/pvp">PvP</a>
        <a class="vr-home-chip" href="/alliances">Союзы</a>
        <a class="vr-home-chip" href="/media">Медиа</a>
      </div>
    </div>
  </section>

  <!-- Неоновая подсказка: помогает направить пользователя в правильный сценарий -->
  <aside class="vr-neon-hint">
    <strong>Подсказка:</strong> если вы новичок, сначала откройте раздел «Старт на сервере»,
    затем «Фарм ресурсов и экономика», и только после этого переходите к PvP-билдам.
  </aside>

  <!-- Карточки тем и подтем: основное меню, построенное по docs/content-structure.md -->
  <section class="vr-topic-grid">
    <article class="vr-topic-card">
      <h3>Старт на сервере</h3>
      <p>Быстрый вход в игру без потери ресурсов в первые дни.</p>
      <ul>
        <li><a href="/start/first-steps">Первые шаги</a></li>
        <li><a href="/start/daily-routine">Ежедневные задачи новичка</a></li>
        <li><a href="/start/common-mistakes">Типовые ошибки старта</a></li>
      </ul>
    </article>

    <article class="vr-topic-card">
      <h3>Герои и синергии</h3>
      <p>Подбор героев, талантов, экипировки и связок под задачи.</p>
      <ul>
        <li><a href="/heroes/roles">Роли и специализации</a></li>
        <li><a href="/heroes/rarity">Герои по редкости</a></li>
        <li><a href="/heroes/synergy">Синергии отрядов</a></li>
      </ul>
    </article>

    <article class="vr-topic-card">
      <h3>Билды и отряды</h3>
      <p>Готовые сборки под PvE, PvP и ивентовые активности.</p>
      <ul>
        <li><a href="/builds/pve">PvE билды</a></li>
        <li><a href="/builds/pvp">PvP билды</a></li>
        <li><a href="/builds/formations">Шаблоны расстановок</a></li>
      </ul>
    </article>

    <article class="vr-topic-card">
      <h3>Экономика и развитие</h3>
      <p>Фарм, город, исследования и стабильный рост аккаунта.</p>
      <ul>
        <li><a href="/economy/farm">Сбор ресурсов</a></li>
        <li><a href="/economy/city">Управление городом</a></li>
        <li><a href="/economy/research">Технологии</a></li>
      </ul>
    </article>

    <article class="vr-topic-card">
      <h3>События</h3>
      <p>Календарь и рекомендации по прохождению ивентов.</p>
      <ul>
        <li><a href="/events/calendar">Календарь событий</a></li>
        <li><a href="/events/recurring">Повторяющиеся ивенты</a></li>
        <li><a href="/events/rewards">Награды и приоритеты</a></li>
      </ul>
    </article>

    <article class="vr-topic-card">
      <h3>FAQ и медиа</h3>
      <p>Быстрые ответы и полезные видео/схемы для команды.</p>
      <ul>
        <li><a href="/faq">Частые вопросы</a></li>
        <li><a href="/glossary">Словарь терминов</a></li>
        <li><a href="/media">Галерея и видеогайды</a></li>
      </ul>
    </article>
  </section>
</div>
```

---

## 3) Что можно кастомизировать

- Тексты кнопок и ссылок под структуру вашей wiki.
- Количество карточек (например, добавить «Союзы и взаимодействие»).
- Порядок блоков под основной сценарий пользователя.
- Неоновую подсказку (`.vr-neon-hint`) под текущую мету/ивент недели.

