/* Ronnie Kim Books — shared helpers for the home page and the book list (v1.21). */
(function () {
  var CATS = {
    ko: { robotics: "로봇·피지컬 AI", career: "커리어", arduino: "아두이노", education: "교육", tech: "기술", essay: "에세이" },
    en: { robotics: "Robotics & Physical AI", career: "Career", arduino: "Arduino", education: "Education", tech: "Technology", essay: "Essay" }
  };
  var CAT_ORDER = ["robotics", "career", "arduino", "education", "tech", "essay"];

  // Series colours: used only in the series band and on series items (policy: one dark band, colours stay inside it).
  var SERIES_COLOR = {
    "CORE-01": "#FFD91A",
    "CORE-02": "#20D6D9",
    "CORE-03": "#9CA3AF", // accent not decided yet (cover draft pending)
    "QUAD-01": "#FF8A34",
    "QUAD-02": "#8159E8",
    "QUAD-03": "#EF4E45"
  };

  var KINDS = {
    ko: { robot: "로봇 파일", source: "소스 코드", sheets: "기록지", videos: "영상" },
    en: { robot: "Robot files", source: "Source code", sheets: "Record sheets", videos: "Videos" }
  };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  // books-data paths start with "./" (site root); pages below the root pass their own prefix.
  function at(root, path) {
    if (!path) return "";
    if (/^https?:/.test(path)) return path;
    return root + path.replace(/^\.\//, "");
  }

  function ym(date) {
    return date ? date.slice(0, 7).replace("-", ".") : "";
  }

  function books(lang) {
    return (window.booksData || []).filter(function (b) { return b[lang]; });
  }

  function isUpcoming(b) {
    return b.status === "upcoming";
  }

  function byNewest(a, b) {
    return (b.publishedAt || "").localeCompare(a.publishedAt || "");
  }

  // Resource kinds a book offers, from downloads-data.js (item.book === book id).
  function resources(bookId, lang) {
    var data = window.downloadsData;
    if (!data) return null;
    var item = data.items.filter(function (i) { return i.book === bookId; })[0];
    if (!item) return null;
    var f = item.files || {};
    var has = function (x) { return !!(x && (x.href || x.workshop)); };
    return {
      code: item.code,
      status: item.status,
      robot: has(f.robot),
      source: has(f.ko) || has(f.en),
      sheets: !!(item.extras && item.extras.length),
      videos: item.videos ? item.videos[lang] || item.videos.ko : ""
    };
  }

  window.RK = {
    CATS: CATS,
    CAT_ORDER: CAT_ORDER,
    SERIES_COLOR: SERIES_COLOR,
    KINDS: KINDS,
    esc: esc,
    at: at,
    ym: ym,
    books: books,
    isUpcoming: isUpcoming,
    byNewest: byNewest,
    resources: resources
  };
})();
