/* Ronnie Kim Books — home page (v1.21): ① featured ② new books ③ series band ④ categories ⑤ resources.
   Data: books-data.js, downloads-data.js. Helpers: site-common.js. Language: ko / en, remembered in localStorage. */
(function () {
  var RK = window.RK;
  var lang = "ko";

  var TEXT = {
    ko: {
      title: "Ronnie Kim Books | 책과 실습 자료",
      nav: { home: "홈", books: "책", res: "자료실", contact: "1:1 문의", privacy: "개인정보 처리방침", search: "책 검색" },
      newBadge: "신간",
      view: "책 보기",
      buy: "구매하기",
      resLink: "실습 자료 →",
      prev: "이전 책",
      next: "다음 책",
      carousel: "신간",
      newTitle: "새로 나온 책",
      newLead: "최근 출간한 책입니다.",
      more: "전체 보기 →",
      seriesTitle: "피지컬 AI로 배우는 RoboCo",
      seriesLead: "완성된 로봇을 먼저 움직이고, 값을 바꿔 결과를 비교하는 실습 시리즈",
      seriesMore: "시리즈 보기 →",
      published: "출간",
      upcoming: "출간 예정",
      catTitle: "분야별로 찾기",
      catLead: "관심 있는 분야의 책을 모아 봅니다.",
      count: function (n, u) { return n + "권" + (u ? " · 출간 예정 " + u + "권" : ""); },
      allBooks: "전체 책 보기 →",
      allCount: function (n) { return "출간 " + n + "권"; },
      resTitle: "자료실",
      resLead: "책에서 쓰는 로봇 파일과 한국어·영어 소스 코드를 받습니다.",
      resLabel: "자료 검색",
      resPh: "책 제목·코드로 자료 찾기 (예: QUAD-01)",
      resGo: "찾기",
      resListTitle: "지금 받을 수 있는 자료",
      resMore: function (n) { return "준비 중인 자료 " + n + "건은 자료실에서 확인할 수 있습니다."; },
      footAbout: "AI·로봇·개발·교육 분야의 책과, 책에서 쓰는 실습 자료를 만듭니다.",
      footNav: "둘러보기",
      footCh: "공식 채널",
      footBlog: "네이버 블로그",
      footNote: "RoboCo는 Filament Games가 만든 게임입니다. 이 사이트의 책과 실습 자료는 RoboCo 공식 자료가 아닙니다."
    },
    en: {
      title: "Ronnie Kim Books | Books and practice files",
      nav: { home: "Home", books: "Books", res: "Resources", contact: "Contact", privacy: "Privacy policy", search: "Search books" },
      newBadge: "New",
      view: "View book",
      buy: "Buy",
      resLink: "Practice files →",
      prev: "Previous book",
      next: "Next book",
      carousel: "New releases",
      newTitle: "New releases",
      newLead: "Recently published books.",
      more: "View all →",
      seriesTitle: "Physical AI with RoboCo",
      seriesLead: "Run a finished robot first, then change one value and compare the result.",
      seriesMore: "View series →",
      published: "Published",
      upcoming: "Coming soon",
      catTitle: "Browse by subject",
      catLead: "Books grouped by subject.",
      count: function (n, u) { return n + (n === 1 ? " book" : " books") + (u ? " · " + u + " coming" : ""); },
      allBooks: "All books →",
      allCount: function (n) { return n + " published"; },
      resTitle: "Resources",
      resLead: "Robot files and Korean and English source code used in the books.",
      resLabel: "Search resources",
      resPh: "Find files by title or code (e.g. QUAD-01)",
      resGo: "Search",
      resListTitle: "Available now",
      resMore: function (n) { return n + " more items are on the way; see Resources."; },
      footAbout: "Books on AI, robotics, software careers, and education, with the practice files they use.",
      footNav: "Explore",
      footCh: "Official channels",
      footBlog: "Naver Blog (Korean)",
      footNote: "RoboCo is a game made by Filament Games. The books and practice files on this site are not official RoboCo materials."
    }
  };

  function $(id) {
    return document.getElementById(id);
  }

  function setText(id, value) {
    var el = $(id);
    if (el) el.textContent = value;
  }

  function cover(book, d, large) {
    return RK.at("./", (large && d.coverLarge) || d.cover);
  }

  function strip(desc, lead) {
    // Avoid repeating the lead line at the start of the description.
    if (!lead || desc.indexOf(lead) !== 0) return desc;
    var rest = desc.slice(lead.length).replace(/^[\s.:,;—-]+/, "");
    return rest.charAt(0).toUpperCase() + rest.slice(1);
  }

  /* ① featured — slides right-to-left on its own: each slide holds HOLD_MS, then moves for SLIDE_MS (set in hub.css,
     .feature-track transition). The last slide is followed by a clone of the first, so 2/2 → 1/2 also moves left.
     No play/pause button; it only waits while the pointer is over it or a link inside it has keyboard focus,
     so the buttons can be clicked, and while the tab is hidden. */
  var HOLD_MS = 1800;
  var carousel = { n: 0, i: 0, timer: null, hover: false, focus: false, busy: false };

  function featured() {
    return RK.books(lang)
      .filter(function (b) { return b.spotlight && !RK.isUpcoming(b); })
      .sort(RK.byNewest)
      .slice(0, 3);
  }

  function slideHtml(b, k, n, clone) {
    var t = TEXT[lang];
    var d = b[lang];
    var s = b.spotlight[lang] || {};
    var href = RK.at("./", d.link);
    var label = clone ? "" : ' aria-label="' + (k + 1) + " / " + n + '"';
    return '<div class="feature-slide" role="group" aria-roledescription="slide"' + label + (clone ? ' aria-hidden="true" inert' : "") + ">" +
      '<div class="feature-grid"><div>' +
      '<p class="feature-eyebrow"><span class="pill">' + t.newBadge + "</span> " + RK.esc(b.seriesCode || "") + (s.capability ? " · " + RK.esc(s.capability) : "") + "</p>" +
      '<h2 class="feature-title">' + RK.esc(s.title || d.title) + "</h2>" +
      (s.lead ? '<p class="lead">' + RK.esc(s.lead) + "</p>" : "") +
      '<p class="desc">' + RK.esc(strip(d.description, s.lead)) + "</p>" +
      '<div class="feature-cta">' +
      '<a class="btn" href="' + href + '">' + t.view + "</a>" +
      '<a class="btn is-ghost" href="' + href + 'buy.html">' + t.buy + "</a>" +
      (b.seriesCode ? '<a class="text-link" href="./' + lang + "/downloads/#" + b.seriesCode + '">' + t.resLink + "</a>" : "") +
      "</div></div>" +
      '<a class="feature-art" href="' + href + '"><img src="' + cover(b, d, true) + '" alt="' + RK.esc(d.alt) + '" width="420" height="622"' + (k ? ' loading="lazy"' : "") + " /></a>" +
      "</div></div>";
  }

  function playing() {
    return carousel.n > 1 && !carousel.hover && !carousel.focus && !document.hidden;
  }

  function schedule() {
    clearTimeout(carousel.timer);
    if (playing()) carousel.timer = setTimeout(function () { move(1); }, HOLD_MS);
  }

  function place(animate) {
    var track = $("feature");
    track.style.transition = animate ? "" : "none";
    track.style.transform = "translateX(" + (-100 * carousel.i) + "%)";
    if (!animate) void track.offsetWidth; // apply the jump before re-enabling transitions
    var real = carousel.i % carousel.n;
    track.querySelectorAll(".feature-slide").forEach(function (el, k) {
      if (k === carousel.n) return; // clone stays inert
      var off = k !== real;
      el.inert = off;
      if (off) el.setAttribute("aria-hidden", "true"); else el.removeAttribute("aria-hidden");
    });
    var count = $("feature-count");
    if (count) count.textContent = (real + 1) + " / " + carousel.n;
  }

  function settle() {
    carousel.busy = false;
    if (carousel.i === carousel.n) { // reached the clone of slide 1: jump back without animation
      carousel.i = 0;
      place(false);
      $("feature").style.transition = "";
    }
    schedule();
  }

  function move(step) {
    if (carousel.n < 2 || carousel.busy) return;
    clearTimeout(carousel.timer);
    if (step < 0 && carousel.i === 0) { // going back from slide 1: jump to the clone, then slide right
      carousel.i = carousel.n;
      place(false);
      $("feature").style.transition = "";
    }
    carousel.i += step;
    carousel.busy = true;
    place(true);
  }

  function renderFeature() {
    var t = TEXT[lang];
    var list = featured();
    if (!list.length) return;
    clearTimeout(carousel.timer);
    carousel.n = list.length;
    carousel.i = 0;
    carousel.busy = false;
    var slides = list.map(function (b, k) { return slideHtml(b, k, list.length, false); });
    if (list.length > 1) slides.push(slideHtml(list[0], 0, list.length, true));
    $("feature").innerHTML = slides.join("");
    $("feature-section").setAttribute("aria-label", t.carousel);

    var pager = $("feature-pager");
    if (list.length > 1) {
      pager.innerHTML =
        '<button type="button" data-step="-1" aria-label="' + t.prev + '">‹</button>' +
        '<span id="feature-count" aria-live="off">1 / ' + list.length + "</span>" +
        '<button type="button" data-step="1" aria-label="' + t.next + '">›</button>';
      pager.hidden = false;
      pager.querySelectorAll("[data-step]").forEach(function (btn) {
        btn.addEventListener("click", function () { move(Number(btn.getAttribute("data-step"))); });
      });
    } else {
      pager.hidden = true;
      pager.innerHTML = "";
    }
    place(false);
    $("feature").style.transition = "";
    schedule();
  }

  (function bindCarousel() {
    var section = $("feature-section");
    var track = $("feature");
    track.addEventListener("transitionend", function (e) {
      if (e.target === track && e.propertyName === "transform") settle();
    });
    section.addEventListener("mouseenter", function () { carousel.hover = true; schedule(); });
    section.addEventListener("mouseleave", function () { carousel.hover = false; schedule(); });
    section.addEventListener("focusin", function (e) {
      // keyboard focus only (a mouse click on an arrow should not stop the slides)
      var kb = true;
      try { kb = e.target.matches(":focus-visible"); } catch (err) { /* older browsers */ }
      carousel.focus = kb;
      schedule();
    });
    section.addEventListener("focusout", function (e) {
      if (!section.contains(e.relatedTarget)) { carousel.focus = false; schedule(); }
    });
    document.addEventListener("visibilitychange", schedule);
  })();

  /* ② new books */
  function card(b, opts) {
    var d = b[lang];
    var t = TEXT[lang];
    var meta = opts && opts.series
      ? (RK.isUpcoming(b) ? t.upcoming : t.published)
      : RK.CATS[lang][b.category] + (b.publishedAt ? " · " + RK.ym(b.publishedAt) : "");
    var badge = "";
    var code = opts && opts.series
      ? '<span class="series-code" style="--sc:' + (RK.SERIES_COLOR[b.seriesCode] || "#9CA3AF") + '">' + RK.esc(b.seriesCode) + "</span>"
      : "";
    return '<a class="bcard" href="' + RK.at("./", d.link) + '">' +
      '<span class="bcard-cover">' + badge + '<img src="' + cover(b, d) + '" alt="' + RK.esc(d.alt) + '" width="420" height="622" loading="lazy" /></span>' +
      code + '<span class="bcard-title">' + RK.esc(d.title) + "</span>" +
      '<span class="bcard-meta">' + RK.esc(meta) + "</span>" + (opts && opts.series ? "" : RK.formatPills(b, lang)) + "</a>";
  }

  function renderNew() {
    var list = RK.books(lang).filter(function (b) { return !RK.isUpcoming(b); }).sort(RK.byNewest).slice(0, 5);
    $("new-row").innerHTML = list.map(function (b) { return card(b); }).join("");
  }

  /* ③ series band */
  function renderSeries() {
    var list = RK.books(lang)
      .filter(function (b) { return b.series === "roboco"; })
      .sort(function (a, b) { return (a.seriesOrder || 0) - (b.seriesOrder || 0); });
    $("series-row").innerHTML = list.map(function (b) { return card(b, { series: true }); }).join("");
  }

  /* ④ categories (bento): widest tile = the category with the most books */
  function renderBento() {
    var t = TEXT[lang];
    var all = RK.books(lang);
    var stats = {};
    all.forEach(function (b) {
      var s = stats[b.category] || (stats[b.category] = { n: 0, u: 0, covers: [] });
      if (RK.isUpcoming(b)) s.u++; else s.n++;
      if (s.covers.length < 3) s.covers.push(b);
    });
    var cats = RK.CAT_ORDER.filter(function (c) { return stats[c]; })
      .sort(function (a, b) { return (stats[b].n + stats[b].u) - (stats[a].n + stats[a].u); });
    var published = all.filter(function (b) { return !RK.isUpcoming(b); }).length;
    var html = cats.map(function (c, i) {
      var s = stats[c];
      var covers = s.covers.slice(0, i === 0 ? 3 : 2).map(function (b) {
        return '<img src="' + cover(b, b[lang]) + '" alt="" width="420" height="622" loading="lazy" />';
      }).join("");
      return '<a class="tile' + (i === 0 ? " is-wide" : "") + '" href="./' + lang + "/books/?cat=" + c + '">' +
        "<div><h3>" + RK.esc(RK.CATS[lang][c]) + '</h3><p class="count">' + t.count(s.n, s.u) + "</p></div>" +
        '<div class="tile-covers">' + covers + "</div></a>";
    }).join("");
    html += '<a class="tile is-all" href="./' + lang + '/books/"><div><h3>' + t.allBooks + '</h3><p class="count">' + t.allCount(published) + "</p></div></a>";
    $("bento").innerHTML = html;
  }

  /* ⑤ resources */
  function renderResources() {
    var t = TEXT[lang];
    var data = window.downloadsData;
    if (!data) return;
    var hub = "./" + lang + "/downloads/";
    $("res-form").setAttribute("action", hub);
    var ready = data.items.filter(function (i) { return i.status === "available"; });
    var later = data.items.length - ready.length;
    $("res-list").innerHTML = ready.map(function (i) {
      var d = i[lang] || i.ko;
      var kinds = [];
      var f = i.files || {};
      if (f.robot && (f.robot.href || f.robot.workshop)) kinds.push(RK.KINDS[lang].robot);
      if ((f.ko && f.ko.href) || (f.en && f.en.href)) kinds.push((lang === "ko" ? "소스 " : "Source ") + (i.version || ""));
      if (i.extras && i.extras.length) kinds.push(RK.KINDS[lang].sheets);
      return '<li><a href="' + hub + "#" + i.code + '"><span class="res-code">' + RK.esc(i.code) + '</span><span class="res-name">' +
        RK.esc(d.name) + '</span><span class="res-kinds">' + RK.esc(kinds.join(" · ")) + "</span></a></li>";
    }).join("");
    setText("res-more", later ? t.resMore(later) : "");
  }

  function renderChrome() {
    var t = TEXT[lang];
    document.documentElement.lang = lang;
    document.title = t.title;
    setText("nav-home", t.nav.home);
    setText("nav-books", t.nav.books);
    setText("nav-res", t.nav.res);
    $("nav-books").href = "./" + lang + "/books/";
    $("nav-res").href = "./" + lang + "/downloads/";
    setText("nav-contact", t.nav.contact);
    $("nav-contact").href = "./" + lang + "/contact/";
    $("nav-search").href = "./" + lang + "/books/#q";
    $("nav-search").setAttribute("aria-label", t.nav.search);
    $("lang-ko").classList.toggle("active", lang === "ko");
    $("lang-en").classList.toggle("active", lang === "en");
    $("lang-ko").setAttribute("aria-pressed", lang === "ko");
    $("lang-en").setAttribute("aria-pressed", lang === "en");

    setText("new-title", t.newTitle);
    setText("new-lead", t.newLead);
    setText("new-more", t.more);
    $("new-more").href = "./" + lang + "/books/";
    setText("series-title", t.seriesTitle);
    setText("series-lead", t.seriesLead);
    setText("series-more", t.seriesMore);
    $("series-more").href = "./" + lang + "/books/?series=roboco";
    setText("cat-title", t.catTitle);
    setText("cat-lead", t.catLead);
    setText("cat-more", t.more);
    $("cat-more").href = "./" + lang + "/books/";
    setText("res-title", t.resTitle);
    setText("res-lead", t.resLead);
    setText("res-q-label", t.resLabel);
    $("res-q").placeholder = t.resPh;
    setText("res-submit", t.resGo);
    setText("res-list-title", t.resListTitle);

    setText("foot-about", t.footAbout);
    setText("foot-nav-title", t.footNav);
    setText("foot-home", t.nav.home);
    setText("foot-books", t.nav.books);
    setText("foot-res", t.nav.res);
    $("foot-books").href = "./" + lang + "/books/";
    $("foot-res").href = "./" + lang + "/downloads/";
    setText("foot-contact", t.nav.contact);
    $("foot-contact").href = "./" + lang + "/contact/";
    setText("foot-privacy", t.nav.privacy);
    $("foot-privacy").href = "./" + lang + "/privacy/";
    setText("foot-ch-title", t.footCh);
    setText("foot-blog", t.footBlog);
    setText("foot-note", t.footNote);
  }

  function setLanguage(next) {
    lang = TEXT[next] ? next : "ko";
    try { localStorage.setItem("siteLanguage", lang); } catch (e) { /* storage unavailable */ }
    renderChrome();
    renderFeature();
    renderNew();
    renderSeries();
    renderBento();
    renderResources();
  }

  $("lang-ko").addEventListener("click", function () { setLanguage("ko"); });
  $("lang-en").addEventListener("click", function () { setLanguage("en"); });

  var saved = null;
  try { saved = localStorage.getItem("siteLanguage"); } catch (e) { /* storage unavailable */ }
  var browser = (navigator.language || "").toLowerCase();
  setLanguage(saved || (browser.indexOf("ko") === 0 ? "ko" : "en"));
})();
