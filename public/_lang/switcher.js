(function () {
  "use strict";
  // 現在ページのURLから言語と対応パスを判定
  const path = window.location.pathname;
  const prefix = "/yoshiichi-com";
  const rest = path.startsWith(prefix) ? path.slice(prefix.length) : path;

  // 言語判定
  let currentLang = "ja";
  let pathWithoutLang = rest;
  if (rest.startsWith("/en/") || rest === "/en") {
    currentLang = "en";
    pathWithoutLang = rest.replace(/^\/en/, "") || "/";
  } else if (rest.startsWith("/zh/") || rest === "/zh") {
    currentLang = "zh";
    pathWithoutLang = rest.replace(/^\/zh/, "") || "/";
  }

  // 日本語 slug → EN/ZH slug マッピング
  const slugMap = {
    "/": "",
    "/事業概要/": "services/",
    "/%e4%ba%8b%e6%a5%ad%e6%a6%82%e8%a6%81/": "services/",
    "/会社概要/": "about/",
    "/%e4%bc%9a%e7%a4%be%e6%a6%82%e8%a6%81/": "about/",
    "/会社沿革/": "history/",
    "/%e4%bc%9a%e7%a4%be%e6%b2%bf%e9%9d%a9/": "history/",
    "/企業理念/": "philosophy/",
    "/%e4%bc%81%e6%a5%ad%e7%90%86%e5%bf%b5/": "philosophy/",
    "/お問い合わせ/": "contact/",
    "/%e3%81%8a%e5%95%8f%e3%81%84%e5%90%88%e3%82%8f%e3%81%9b/": "contact/",
    "/取引をご希望の皆様へ/": "business-inquiry/",
    "/%e5%8f%96%e5%bc%95%e3%82%92%e3%81%94%e5%b8%8c%e6%9c%9b%e3%81%ae%e7%9a%86%e6%a7%98%e3%81%b8/": "business-inquiry/",
  };

  // 英語スラッグ → 日本語への逆マップ
  const reverseSlugMap = {
    "": "/",
    "services/": "/%e4%ba%8b%e6%a5%ad%e6%a6%82%e8%a6%81/",
    "about/": "/%e4%bc%9a%e7%a4%be%e6%a6%82%e8%a6%81/",
    "history/": "/%e4%bc%9a%e7%a4%be%e6%b2%bf%e9%9d%a9/",
    "philosophy/": "/%e4%bc%81%e6%a5%ad%e7%90%86%e5%bf%b5/",
    "contact/": "/%e3%81%8a%e5%95%8f%e3%81%84%e5%90%88%e3%82%8f%e3%81%9b/",
    "business-inquiry/": "/%e5%8f%96%e5%bc%95%e3%82%92%e3%81%94%e5%b8%8c%e6%9c%9b%e3%81%ae%e7%9a%86%e6%a7%98%e3%81%b8/",
  };

  // 現在ページの各言語URLを計算
  function urlFor(lang) {
    let slug;
    if (currentLang === "ja") {
      slug = slugMap[pathWithoutLang] ?? "";
    } else {
      // /en/about/ 等から日本語スラグ復元
      const enSlug = pathWithoutLang.replace(/^\//, "");
      slug = enSlug;
    }
    if (lang === "ja") {
      // JPトップ or 日本語スラグ
      const jaSlug = currentLang === "ja" ? pathWithoutLang : (reverseSlugMap[slug] ?? "/");
      return prefix + jaSlug;
    }
    return `${prefix}/${lang}/${slug}`;
  }

  const languages = [
    { code: "ja", label: "日本語", short: "JP" },
    { code: "en", label: "English", short: "EN" },
    { code: "zh", label: "中文", short: "ZH" },
  ];

  const current = languages.find((l) => l.code === currentLang) || languages[0];

  const items = languages
    .map((l) => {
      const isCurrent = l.code === current.code;
      return `<li role="none"><a class="lang-switcher__link" role="menuitem" href="${urlFor(l.code)}" ${isCurrent ? 'aria-current="true"' : ""}>${l.label}</a></li>`;
    })
    .join("");

  const template = `
    <div class="lang-switcher" data-open="false">
      <button type="button" class="lang-switcher__btn" aria-haspopup="true" aria-expanded="false" aria-label="Language">
        <span class="lang-switcher__current">${current.short}</span>
        <svg class="lang-switcher__caret" viewBox="0 0 10 6" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path d="M1 1l4 4 4-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <ul class="lang-switcher__menu" role="menu">${items}</ul>
    </div>
  `.trim();

  function mountSwitcher(targetEl, pos) {
    const wrap = document.createElement("div");
    wrap.innerHTML = template;
    const switcher = wrap.firstElementChild;
    if (pos === "after") targetEl.insertAdjacentElement("afterend", switcher);
    else targetEl.insertAdjacentElement("afterbegin", switcher);

    const btn = switcher.querySelector(".lang-switcher__btn");
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const isOpen = switcher.getAttribute("data-open") === "true";
      switcher.setAttribute("data-open", String(!isOpen));
      btn.setAttribute("aria-expanded", String(!isOpen));
    });
    document.addEventListener("click", () => {
      switcher.setAttribute("data-open", "false");
      btn.setAttribute("aria-expanded", "false");
    });
  }

  // PCヘッダー: l-header__right の中（nav の後）
  document.addEventListener("DOMContentLoaded", () => {
    document.documentElement.lang = currentLang === "zh" ? "zh-CN" : currentLang;

    const headerNav = document.querySelector(".l-header__right > nav");
    if (headerNav) mountSwitcher(headerNav, "after");

    // モバイルドロワーにも追加
    const drawerNav = document.querySelector(".l-drawer__body .c-listMenu, .l-drawer__body > *:first-child");
    if (drawerNav) mountSwitcher(drawerNav, "before");
  });
})();
