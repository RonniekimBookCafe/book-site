/* Ronnie Kim Books — 자료실 (Resources) renderer (v1.20, v1.21). Data: assets/js/downloads-data.js */
(function () {
  var data = window.downloadsData;
  var icons = window.downloadIcons || {};
  var body = document.body;
  var lang = body.getAttribute("data-lang") === "en" ? "en" : "ko";
  var root = body.getAttribute("data-root") || "../../";
  if (!data) return;

  var T = {
    ko: {
      head: ["책·로봇", "로봇 파일", "한국어 소스", "영어 소스"],
      headProject: "로봇",
      allPending: { coming: "로봇 파일·한국어 소스·영어 소스 — 책 출간에 맞춰 공개합니다", planned: "로봇 파일·한국어 소스·영어 소스 — 준비되는 대로 공개합니다" },
      labels: { robot: "로봇 파일", ko: "한국어 소스", en: "영어 소스" },
      status: { available: "내려받기 가능", coming: "출간 예정", planned: "공개 예정" },
      pending: "준비 중",
      workshopSoon: "Steam Workshop · 주소 등록 예정",
      workshop: "Steam Workshop",
      book: "책 페이지",
      guide: "설치 안내",
      dl: "받기",
      empty: "조건에 맞는 자료가 없습니다.",
      count: function (n) { return n + "개 표시"; },
      hashName: "파일",
      hashSize: "크기",
      zip: "ZIP"
    },
    en: {
      head: ["Book · robot", "Robot files", "Korean source", "English source"],
      headProject: "Robot",
      allPending: { coming: "Robot files, Korean and English source: released with the book", planned: "Robot files, Korean and English source: released when ready" },
      labels: { robot: "Robot files", ko: "Korean source", en: "English source" },
      status: { available: "Available", coming: "Coming soon", planned: "Planned" },
      pending: "Coming soon",
      workshopSoon: "Steam Workshop · links coming",
      workshop: "Steam Workshop",
      book: "Book page",
      guide: "Setup guide",
      dl: "Download",
      empty: "Nothing matches your search.",
      count: function (n) { return n + " shown"; },
      hashName: "File",
      hashSize: "Size",
      zip: "ZIP"
    }
  }[lang];

  var DL_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11m-5-5 5 5 5-5M5 20h14"/></svg>';

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function size(bytes) {
    if (!bytes) return "";
    if (bytes >= 1024 * 1024) return (bytes / 1024 / 1024).toFixed(1) + " MB";
    return Math.round(bytes / 1024) + " KB";
  }

  function fileName(href) {
    return href.split("/").pop();
  }

  function langPath(p) {
    return typeof p === "object" && p ? p[lang] || p.ko : p;
  }

  function fileCell(item, key) {
    var f = item.files && item.files[key];
    var label = '<span class="dl-file-label">' + T.labels[key] + "</span>";
    if (!f) return '<div class="dl-file">' + label + '<span class="dl-pending">—</span></div>';
    var note = f.note ? '<small class="dl-note">' + esc(f.note[lang] || f.note.ko) + "</small>" : "";
    if (f.href) {
      var ext = fileName(f.href).split(".").pop().toUpperCase();
      var aria = item.code + " " + T.labels[key] + " — " + fileName(f.href) + ", " + size(f.bytes);
      return '<div class="dl-file">' + label +
        '<a class="dl-btn' + (key === lang || key === "robot" ? "" : " is-outline") + '" href="' + root + f.href + '" download aria-label="' + esc(aria) + '">' +
        DL_ICON + ext + " <small>" + size(f.bytes) + "</small></a>" + note + "</div>";
    }
    if (f.workshop !== undefined) {
      if (f.workshop) {
        return '<div class="dl-file">' + label + '<a class="dl-btn is-outline" href="' + esc(f.workshop) + '" target="_blank" rel="noopener">' +
          T.workshop + " ↗</a>" + note + "</div>";
      }
      return '<div class="dl-file">' + label + '<span class="dl-pending">' + T.workshopSoon + "</span></div>";
    }
    return '<div class="dl-file">' + label + '<span class="dl-pending">' + T.pending + "</span>" + note + "</div>";
  }

  function allPending(item) {
    return ["robot", "ko", "en"].every(function (k) {
      var f = item.files && item.files[k];
      return !f || (!f.href && f.workshop === undefined);
    });
  }

  function itemRow(item) {
    var d = item[lang] || item.ko;
    var visual;
    if (item.cover) {
      var alt = (lang === "ko" ? d.name + " 표지" : "Cover of " + item.code);
      visual = '<img src="' + root + item.cover.replace("{lang}", lang) + '" alt="' + esc(alt) + '" width="420" height="622" loading="lazy" />';
    } else {
      visual = '<span class="dl-icon">' + (icons[item.icon] || "") + "</span>";
    }
    var links = [];
    if (item.page) links.push('<a href="' + root + langPath(item.page) + '">' + T.book + "</a>");
    if (item.guide) links.push('<a href="' + root + langPath(item.guide) + '">' + T.guide + "</a>");
    var meta = esc(d.robot) + (item.version ? " · " + esc(item.version) : "");
    var extras = "";
    if (item.extras && item.extras.length) {
      extras = '<div class="dl-extras">' + item.extras.map(function (x) {
        return '<a href="' + root + langPath(x.href) + '" download>+ ' + esc(x.label[lang] || x.label.ko) + "</a>";
      }).join("") + "</div>";
    }
    var accent = item.color ? ' style="--accent:' + item.color + '"' : "";
    return '<article class="dl-row' + (item.status === "available" ? "" : " is-muted") + '" id="' + esc(item.code) + '"' + accent + ">" +
      '<div class="dl-item">' + visual + "<div>" +
      '<p class="dl-code">' + (item.cover ? '<span class="code">' + esc(item.code) + "</span>" : "") +
      (item.capability ? '<span class="cap">' + esc(item.capability) + "</span>" : "") +
      '<span class="dl-status is-' + item.status + '">' + T.status[item.status] + "</span></p>" +
      "<h3>" + esc(d.name) + "</h3>" +
      '<p class="dl-robot">' + meta + "</p>" +
      (links.length ? '<p class="dl-links">' + links.join("") + "</p>" : "") +
      "</div></div>" +
      (allPending(item)
        ? '<div class="dl-file is-span"><span class="dl-pending">' + (T.allPending[item.status] || T.pending) + "</span></div>"
        : fileCell(item, "robot") + fileCell(item, "ko") + fileCell(item, "en")) + extras +
      "</article>";
  }

  var groupsEl = document.getElementById("dl-groups");
  var searchEl = document.getElementById("dl-search");
  var countEl = document.getElementById("dl-count");
  var filter = "all";

  function matches(item, q) {
    if (filter === "available" && item.status !== "available") return false;
    if (filter !== "all" && filter !== "available" && item.group !== filter) return false;
    if (!q) return true;
    var hay = [item.code, item.capability, item.ko.name, item.ko.robot, item.en.name, item.en.robot].join(" ").toLowerCase();
    return hay.indexOf(q) !== -1;
  }

  function render() {
    var q = (searchEl.value || "").trim().toLowerCase();
    var html = "";
    var shown = 0;
    data.groups.forEach(function (g) {
      var items = data.items.filter(function (it) { return it.group === g.id && matches(it, q); });
      if (!items.length) return;
      shown += items.length;
      var gt = g[lang] || g.ko;
      html += '<section class="dl-group" aria-labelledby="g-' + g.id + '"><h2 id="g-' + g.id + '">' + esc(gt.title) + "</h2>" +
        "<p>" + esc(gt.lead) + "</p>" +
        '<div class="dl-table"><div class="dl-head" aria-hidden="true"><span>' + [g.id === "projects" ? T.headProject : T.head[0]].concat(T.head.slice(1)).join("</span><span>") + "</span></div>" +
        items.map(itemRow).join("") + "</div></section>";
    });
    groupsEl.innerHTML = html || '<p class="dl-empty">' + T.empty + "</p>";
    if (countEl) countEl.textContent = T.count(shown);
  }

  function renderStats() {
    var el = document.getElementById("dl-stats");
    if (!el) return;
    var books = data.items.filter(function (i) { return i.group === "roboco"; });
    var avail = books.filter(function (i) { return i.status === "available"; }).length;
    var proj = data.items.filter(function (i) { return i.group === "projects"; }).length;
    var files = 0;
    data.items.forEach(function (i) {
      ["robot", "ko", "en"].forEach(function (k) { if (i.files && i.files[k] && i.files[k].href) files++; });
    });
    el.innerHTML = lang === "ko"
      ? "<li><strong>" + avail + "권</strong> 지금 받기</li><li><strong>" + (books.length - avail) + "권</strong> 출간 예정</li><li><strong>" + proj + "종</strong> 로봇 프로젝트 준비 중</li><li><strong>" + files + "개</strong> 파일</li>"
      : "<li><strong>" + avail + "</strong> books ready</li><li><strong>" + (books.length - avail) + "</strong> books coming</li><li><strong>" + proj + "</strong> robot projects planned</li><li><strong>" + files + "</strong> files</li>";
  }

  function renderHashes() {
    var tb = document.getElementById("dl-hash-body");
    if (!tb) return;
    var rows = [];
    data.items.forEach(function (i) {
      ["robot", "ko", "en"].forEach(function (k) {
        var f = i.files && i.files[k];
        if (f && f.href && f.sha256) {
          rows.push("<tr><td><code>" + esc(fileName(f.href)) + "</code><br /><small>" + esc(i.code) + " · " + T.labels[k] + "</small></td><td>" +
            size(f.bytes) + "</td><td><code>" + f.sha256 + "</code></td></tr>");
        }
      });
    });
    tb.innerHTML = rows.join("");
  }

  document.querySelectorAll(".dl-filter").forEach(function (btn) {
    btn.addEventListener("click", function () {
      filter = btn.getAttribute("data-filter");
      document.querySelectorAll(".dl-filter").forEach(function (b) {
        b.setAttribute("aria-pressed", b === btn ? "true" : "false");
      });
      render();
    });
  });
  searchEl.addEventListener("input", render);
  // ?q= from the home page search box
  var q0 = new URLSearchParams(location.search).get("q");
  if (q0) searchEl.value = q0;

  renderStats();
  render();
  renderHashes();

  function highlight() {
    var id = decodeURIComponent((location.hash || "").slice(1));
    if (!id) return;
    var el = document.getElementById(id);
    if (!el || !el.classList.contains("dl-row")) return;
    document.querySelectorAll(".dl-row.is-target").forEach(function (r) { r.classList.remove("is-target"); });
    el.classList.add("is-target");
    el.scrollIntoView({ block: "center" });
  }
  window.addEventListener("hashchange", highlight);
  highlight();
})();
