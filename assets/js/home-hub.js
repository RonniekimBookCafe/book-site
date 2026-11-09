/* Ronnie Kim Books — home hub (v1.20): top nav, hero actions, download quick panel, category tiles.
 * home.js calls window.renderHomeHub(lang) from setLanguage(). Data: books-data.js, downloads-data.js */
(function () {
  var TEXT = {
    ko: {
      nav: { books: "책", downloads: "실습 자료 다운로드", youtube: "YouTube", blog: "블로그" },
      actions: [
        { key: "books", strong: "책 둘러보기", small: function (n, c) { return "출간 " + n + "권 · " + c + "개 분야"; } },
        { key: "downloads", strong: "실습 자료 다운로드", small: function () { return "로봇 파일 · 한국어 · 영어 소스 코드"; } },
        { key: "videos", strong: "실습 영상 보기", small: function () { return "공식 YouTube · 로봇이 움직이는 장면"; } }
      ],
      booksLead: "분야를 고르거나 제목으로 찾아보세요.",
      all: "전체",
      unit: function (n, u) { return n + "권" + (u ? " · 출간 예정 " + u : ""); },
      categories: { career: "커리어", arduino: "아두이노", education: "교육", essay: "에세이", tech: "기술", robotics: "로봇·피지컬 AI" },
      dlTitle: "실습 자료 다운로드",
      dlLead: "책에서 쓰는 로봇 파일과 소스 코드를 바로 받습니다. 설치 순서와 확인값은 실습 자료 페이지에 있습니다.",
      dlMore: "전체 실습 자료 보기 →",
      robot: "로봇 파일",
      src: { ko: "한국어 소스", en: "영어 소스" },
      workshop: "Steam Workshop 준비 중",
      next: "다음 공개",
      soon: { coming: "출간 예정", planned: "공개 예정" }
    },
    en: {
      nav: { books: "Books", downloads: "Downloads", youtube: "YouTube", blog: "Blog (Korean)" },
      actions: [
        { key: "books", strong: "Browse the books", small: function (n, c) { return n + " books · " + c + " subjects"; } },
        { key: "downloads", strong: "Download practice files", small: function () { return "Robot files · Korean & English source code"; } },
        { key: "videos", strong: "Watch the robots run", small: function () { return "Official YouTube channel"; } }
      ],
      booksLead: "Pick a subject or search by title.",
      all: "All",
      unit: function (n, u) { return n + (n === 1 ? " book" : " books") + (u ? " · " + u + " coming" : ""); },
      categories: { career: "Career", arduino: "Arduino", education: "Education", essay: "Essay", tech: "Technology", robotics: "Robotics & Physical AI" },
      dlTitle: "Practice file downloads",
      dlLead: "Get the robot files and source code used in the books. Setup steps and checksums are on the Downloads page.",
      dlMore: "All downloads →",
      robot: "Robot files",
      src: { ko: "Korean source", en: "English source" },
      workshop: "Steam Workshop coming",
      next: "Coming next",
      soon: { coming: "Coming soon", planned: "Planned" }
    }
  };

  var ICONS = {
    books: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5a2 2 0 0 1 2-2h5v17H6a2 2 0 0 0-2 2zM20 5a2 2 0 0 0-2-2h-5v17h5a2 2 0 0 1 2 2z"/></svg>',
    downloads: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12m-5-5 5 5 5-5M4 20h16"/></svg>',
    videos: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="3"/><path d="M10 9v6l5-3z"/></svg>'
  };
  var DL = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11m-5-5 5 5 5-5M5 20h14"/></svg>';

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function kb(b) {
    return Math.round(b / 1024) + " KB";
  }

  function books(lang) {
    return (window.booksData || []).filter(function (b) { return b[lang]; });
  }

  function renderNav(lang, t) {
    var map = { "nav-books": t.nav.books, "nav-downloads": t.nav.downloads, "nav-youtube": t.nav.youtube, "nav-blog": t.nav.blog };
    Object.keys(map).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.textContent = map[id];
    });
    var dl = document.getElementById("nav-downloads");
    if (dl) dl.href = "./" + lang + "/downloads/";
  }

  function renderActions(lang, t) {
    var el = document.getElementById("hero-actions");
    if (!el) return;
    var list = books(lang);
    var published = list.filter(function (b) { return b.status !== "upcoming"; }).length;
    var cats = {};
    list.forEach(function (b) { cats[b.category] = 1; });
    var hrefs = { books: "#books", downloads: "./" + lang + "/downloads/", videos: "https://www.youtube.com/@ronniekim486" };
    el.innerHTML = t.actions.map(function (a) {
      var ext = a.key === "videos" ? ' target="_blank" rel="noopener"' : "";
      return '<a class="hero-action' + (a.key === "downloads" ? " is-primary" : "") + '" href="' + hrefs[a.key] + '"' + ext + ">" +
        '<span class="ha-icon">' + ICONS[a.key] + "</span>" +
        '<span class="ha-text"><strong>' + a.strong + "</strong><small>" + a.small(published, Object.keys(cats).length) + "</small></span>" +
        '<span class="ha-arrow" aria-hidden="true">' + (ext ? "↗" : "→") + "</span></a>";
    }).join("");
  }

  function renderDownloads(lang, t) {
    var el = document.getElementById("downloads-quick");
    var data = window.downloadsData;
    if (!el || !data) return;
    var hub = "./" + lang + "/downloads/";
    var ready = data.items.filter(function (i) { return i.status === "available"; });
    var later = data.items.filter(function (i) { return i.status !== "available"; });

    var cards = ready.map(function (i) {
      var d = i[lang] || i.ko;
      var btns = [];
      var r = i.files.robot;
      if (r && r.href) btns.push('<a class="dl-btn" href="./' + r.href + '" download>' + DL + t.robot + " <small>" + kb(r.bytes) + "</small></a>");
      else if (r && r.workshop) btns.push('<a class="dl-btn is-outline" href="' + esc(r.workshop) + '" target="_blank" rel="noopener">Steam Workshop ↗</a>');
      else if (r) btns.push('<span class="dl-pending">' + t.workshop + "</span>");
      ["ko", "en"].forEach(function (k) {
        var f = i.files[k];
        if (f && f.href) {
          btns.push('<a class="dl-btn' + (k === lang ? "" : " is-outline") + '" href="./' + f.href + '" download>' + DL + t.src[k] + " <small>" + kb(f.bytes) + "</small></a>");
        }
      });
      return '<article class="dlq-card" style="--accent:' + (i.color || "#111827") + '">' +
        '<a href="' + hub + "#" + i.code + '"><img src="./' + i.cover.replace("{lang}", lang) + '" alt="' + esc(d.name) + '" width="420" height="622" loading="lazy" /></a>' +
        "<div><h3>" + i.code + " · " + esc(d.name) + "</h3>" +
        '<p class="dlq-meta">' + esc(d.robot) + (i.version ? " · " + i.version : "") + "</p>" +
        '<div class="dlq-buttons">' + btns.join("") + "</div></div></article>";
    }).join("");

    var chips = later.map(function (i) {
      var d = i[lang] || i.ko;
      var label = i.cover ? i.code : d.name;
      var icon = i.icon && window.downloadIcons ? window.downloadIcons[i.icon] : "";
      return '<a class="dlq-chip" href="' + hub + "#" + i.code + '">' + icon + esc(label) +
        ' <span class="is-soon">' + (t.soon[i.status] || "") + "</span></a>";
    }).join("");

    el.innerHTML =
      '<div class="home-section-head"><h2 id="dlq-title">' + t.dlTitle + '</h2><a class="more-link" href="' + hub + '">' + t.dlMore + "</a>" +
      "<p>" + t.dlLead + "</p></div>" +
      '<div class="dlq-grid">' + cards + "</div>" +
      '<div class="dlq-more"><span class="dlq-more-label">' + t.next + "</span>" + chips + "</div>";
    el.hidden = false;
  }

  function renderTiles(lang, t) {
    var el = document.getElementById("cat-tiles");
    var select = document.getElementById("book-category");
    if (!el || !select) return;
    var counts = {};
    var soon = {};
    var list = books(lang);
    list.forEach(function (b) {
      if (b.status === "upcoming") soon[b.category] = (soon[b.category] || 0) + 1;
      else counts[b.category] = (counts[b.category] || 0) + 1;
    });
    var total = 0;
    var totalSoon = 0;
    Object.keys(counts).forEach(function (k) { total += counts[k]; });
    Object.keys(soon).forEach(function (k) { totalSoon += soon[k]; });
    var order = ["robotics", "career", "arduino", "education", "tech", "essay"];
    var tiles = [{ key: "all", label: t.all, n: total, u: totalSoon }].concat(
      order.filter(function (k) { return counts[k] || soon[k]; }).map(function (k) {
        return { key: k, label: t.categories[k], n: counts[k] || 0, u: soon[k] || 0 };
      })
    );
    el.innerHTML = tiles.map(function (c) {
      return '<button type="button" class="cat-tile" data-cat="' + c.key + '" aria-pressed="' + (select.value === c.key) + '">' +
        "<strong>" + c.label + "</strong><small>" + t.unit(c.n, c.u) + "</small></button>";
    }).join("");
    el.querySelectorAll(".cat-tile").forEach(function (btn) {
      btn.addEventListener("click", function () {
        select.value = btn.getAttribute("data-cat");
        select.dispatchEvent(new Event("change"));
      });
    });
  }

  function syncTiles() {
    var select = document.getElementById("book-category");
    document.querySelectorAll(".cat-tile").forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-cat") === select.value ? "true" : "false");
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var select = document.getElementById("book-category");
    if (select) select.addEventListener("change", syncTiles);
  });

  window.renderHomeHub = function (lang) {
    var t = TEXT[lang] || TEXT.ko;
    renderNav(lang, t);
    renderActions(lang, t);
    renderDownloads(lang, t);
    renderTiles(lang, t);
    var lead = document.getElementById("books-lead");
    if (lead) lead.textContent = t.booksLead;
  };
})();
