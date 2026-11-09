/* Ronnie Kim Books — book list (/ko/books/, /en/books/), v1.21.
   Subject tiles with counts, search, series, status, sort, grid/list view, 24 per page.
   The state lives in the URL (?cat=&series=&status=&sort=&view=&q=&page=) so filters can be shared and the back button works. */
(function () {
  var RK = window.RK;
  var body = document.body;
  var lang = body.getAttribute("data-lang") === "en" ? "en" : "ko";
  var root = body.getAttribute("data-root") || "../../";
  var PER_PAGE = 24;

  var T = {
    ko: {
      all: "전체",
      summary: function (n, p, u) { return "전체 " + n + "권 · 출간 " + p + "권 · 출간 예정 " + u + "권"; },
      count: function (n) { return n + "권"; },
      shown: function (n, from, to) { return n ? "총 " + n + "권 중 " + from + "–" + to : ""; },
      upcoming: "출간 예정",
      empty: "조건에 맞는 책이 없습니다.",
      reset: "조건 지우기",
      prev: "이전",
      next: "다음",
      view: "책 보기",
      pending: "준비 중"
    },
    en: {
      all: "All",
      summary: function (n, p, u) { return n + " books · " + p + " published · " + u + " coming"; },
      count: function (n) { return String(n); },
      shown: function (n, from, to) { return n ? from + "–" + to + " of " + n : ""; },
      upcoming: "Coming soon",
      empty: "No books match these filters.",
      reset: "Clear filters",
      prev: "Prev",
      next: "Next",
      view: "View book",
      pending: "coming"
    }
  }[lang];

  var $ = function (id) { return document.getElementById(id); };
  var all = RK.books(lang);

  var params = new URLSearchParams(location.search);
  var state = {
    cat: params.get("cat") || "",
    series: params.get("series") || "",
    status: params.get("status") || "",
    sort: params.get("sort") || "newest",
    view: params.get("view") || "grid",
    q: params.get("q") || "",
    page: Math.max(1, parseInt(params.get("page") || "1", 10) || 1)
  };

  function saveUrl() {
    var p = new URLSearchParams();
    if (state.cat) p.set("cat", state.cat);
    if (state.series) p.set("series", state.series);
    if (state.status) p.set("status", state.status);
    if (state.sort !== "newest") p.set("sort", state.sort);
    if (state.view !== "grid") p.set("view", state.view);
    if (state.q) p.set("q", state.q);
    if (state.page > 1) p.set("page", state.page);
    var qs = p.toString();
    history.replaceState(null, "", location.pathname + (qs ? "?" + qs : "") + location.hash);
  }

  function matches(b, ignoreCat) {
    if (!ignoreCat && state.cat && b.category !== state.cat) return false;
    if (state.series && b.series !== state.series) return false;
    if (state.status === "published" && RK.isUpcoming(b)) return false;
    if (state.status === "upcoming" && !RK.isUpcoming(b)) return false;
    if (state.q) {
      var d = b[lang];
      var hay = [d.title, d.description, b.seriesCode || "", RK.CATS[lang][b.category]].join(" ").toLowerCase();
      if (hay.indexOf(state.q.toLowerCase()) === -1) return false;
    }
    return true;
  }

  function sorted(list) {
    var out = list.slice();
    if (state.sort === "title") {
      out.sort(function (a, b) { return a[lang].title.localeCompare(b[lang].title, lang); });
    } else {
      // Published first by date; coming-soon books after them in series order.
      out.sort(function (a, b) {
        var ua = RK.isUpcoming(a), ub = RK.isUpcoming(b);
        if (ua !== ub) return ua ? 1 : -1;
        if (ua) return (a.seriesOrder || 0) - (b.seriesOrder || 0);
        var c = (a.publishedAt || "").localeCompare(b.publishedAt || "");
        return state.sort === "oldest" ? c : -c;
      });
    }
    return out;
  }

  /* subject tiles: counts follow the other filters (series, status, search) */
  function renderCats() {
    var base = all.filter(function (b) { return matches(b, true); });
    var counts = {};
    base.forEach(function (b) { counts[b.category] = (counts[b.category] || 0) + 1; });
    var cells = [{ key: "", label: T.all, n: base.length }].concat(
      RK.CAT_ORDER.filter(function (c) { return all.some(function (b) { return b.category === c; }); })
        .map(function (c) { return { key: c, label: RK.CATS[lang][c], n: counts[c] || 0 }; })
    );
    $("cat-grid").innerHTML = cells.map(function (c) {
      return '<button type="button" class="cat-cell" data-cat="' + c.key + '" aria-pressed="' + (state.cat === c.key) + '">' +
        "<span>" + RK.esc(c.label) + "</span><small>" + T.count(c.n) + "</small></button>";
    }).join("");
    $("cat-grid").querySelectorAll(".cat-cell").forEach(function (btn) {
      btn.addEventListener("click", function () {
        state.cat = btn.getAttribute("data-cat");
        state.page = 1;
        update();
      });
    });
  }

  function meta(b) {
    var cat = RK.CATS[lang][b.category];
    return RK.isUpcoming(b) ? cat + " · " + T.upcoming : cat + (b.publishedAt ? " · " + RK.ym(b.publishedAt) : "");
  }

  function badge(b) {
    var d = b[lang];
    if (RK.isUpcoming(b)) return "";
    return d.badge ? '<span class="bcard-badge is-new">' + RK.esc(d.badge) + "</span>" : "";
  }

  function resourceBadges(b) {
    var r = RK.resources(b.id, lang);
    if (!r) return "";
    var hub = root + lang + "/downloads/#" + r.code;
    var K = RK.KINDS[lang];
    var out = [];
    [["robot", r.robot], ["source", r.source], ["sheets", r.sheets]].forEach(function (k) {
      out.push(k[1] ? '<a href="' + hub + '">' + K[k[0]] + "</a>" : "<span>" + K[k[0]] + "</span>");
    });
    out.push(r.videos ? '<a href="' + root + r.videos + '">' + K.videos + "</a>" : "<span>" + K.videos + "</span>");
    return '<div class="badges">' + out.join("") + "</div>";
  }

  function coverHtml(b) {
    var d = b[lang];
    return '<span class="bcard-cover"><img src="' + RK.at(root, d.cover) + '" alt="' + RK.esc(d.alt) +
      '" width="420" height="622" loading="lazy" /></span>';
  }

  function gridItem(b) {
    var d = b[lang];
    return '<a class="bcard" href="' + RK.at(root, d.link) + '">' + coverHtml(b) +
      '<span class="bcard-title">' + RK.esc(d.title) + '</span><span class="bcard-meta">' + badge(b) + RK.esc(meta(b)) + "</span></a>";
  }

  function listItem(b) {
    var d = b[lang];
    var href = RK.at(root, d.link);
    return '<li class="lrow"><a class="bcard" href="' + href + '" tabindex="-1" aria-hidden="true">' + coverHtml(b) + "</a><div>" +
      '<h3><a href="' + href + '">' + RK.esc(d.title) + "</a></h3>" +
      '<p class="lmeta">' + badge(b) + RK.esc(meta(b)) + (b.seriesCode ? " · " + RK.esc(b.seriesCode) : "") + "</p>" +
      '<p class="ldesc">' + RK.esc(d.description) + "</p>" + resourceBadges(b) + "</div></li>";
  }

  function renderPager(pages) {
    var el = $("pager");
    if (pages <= 1) {
      el.innerHTML = "";
      return;
    }
    var html = '<button type="button" data-page="' + (state.page - 1) + '"' + (state.page === 1 ? " disabled" : "") + ">" + T.prev + "</button>";
    for (var i = 1; i <= pages; i++) {
      html += '<button type="button" data-page="' + i + '"' + (i === state.page ? ' aria-current="page"' : "") + ">" + i + "</button>";
    }
    html += '<button type="button" data-page="' + (state.page + 1) + '"' + (state.page === pages ? " disabled" : "") + ">" + T.next + "</button>";
    el.innerHTML = html;
    el.querySelectorAll("button[data-page]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        state.page = parseInt(btn.getAttribute("data-page"), 10);
        update();
        $("list").scrollIntoView({ block: "start" });
      });
    });
  }

  function renderList() {
    var list = sorted(all.filter(function (b) { return matches(b); }));
    var pages = Math.max(1, Math.ceil(list.length / PER_PAGE));
    if (state.page > pages) state.page = pages;
    var from = (state.page - 1) * PER_PAGE;
    var slice = list.slice(from, from + PER_PAGE);
    $("list-count").textContent = T.shown(list.length, from + 1, from + slice.length);
    if (!list.length) {
      $("list").innerHTML = '<div class="list-empty"><p>' + T.empty + '</p><button type="button" class="btn is-ghost" id="reset">' + T.reset + "</button></div>";
      $("reset").addEventListener("click", function () {
        state.cat = state.series = state.status = state.q = "";
        state.page = 1;
        $("q").value = "";
        update();
      });
    } else if (state.view === "list") {
      $("list").innerHTML = '<ul class="list-rows">' + slice.map(listItem).join("") + "</ul>";
    } else {
      $("list").innerHTML = '<div class="list-grid">' + slice.map(gridItem).join("") + "</div>";
    }
    renderPager(pages);
  }

  function syncControls() {
    $("q").value = state.q;
    $("series").value = state.series;
    $("sort").value = state.sort;
    document.querySelectorAll("#status-seg button").forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-status") === state.status ? "true" : "false");
    });
    document.querySelectorAll("#view-seg button").forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-view") === state.view ? "true" : "false");
    });
  }

  function update() {
    syncControls();
    renderCats();
    renderList();
    saveUrl();
  }

  var published = all.filter(function (b) { return !RK.isUpcoming(b); }).length;
  $("list-summary").textContent = T.summary(all.length, published, all.length - published);

  var timer = null;
  $("q").addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(function () {
      state.q = $("q").value.trim();
      state.page = 1;
      renderCats();
      renderList();
      saveUrl();
    }, 150);
  });
  $("series").addEventListener("change", function () { state.series = $("series").value; state.page = 1; update(); });
  $("sort").addEventListener("change", function () { state.sort = $("sort").value; state.page = 1; update(); });
  document.querySelectorAll("#status-seg button").forEach(function (b) {
    b.addEventListener("click", function () { state.status = b.getAttribute("data-status"); state.page = 1; update(); });
  });
  document.querySelectorAll("#view-seg button").forEach(function (b) {
    b.addEventListener("click", function () { state.view = b.getAttribute("data-view"); update(); });
  });

  update();
  if (location.hash === "#q") $("q").focus();
})();
