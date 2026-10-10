/*
 * RoboCo series media renderer (videos + sample pages).
 *
 * Content lives in assets/js/media/{book-id}.js. To publish a video or add a
 * sample page, edit only that data file — no HTML changes are needed.
 *
 *   [data-video-id="C01-25-00"]   placeholder that becomes a YouTube embed
 *   [data-playlist-link]          link shown when a playlist URL is set
 *   #rk-extra-videos              section listing videos added later
 *   #rk-sample-gallery            section listing sample page images
 */
(function () {
  "use strict";

  var script = document.currentScript;
  var bookId = script && script.getAttribute("data-book");
  var root = (script && script.getAttribute("data-root")) || "";
  var all = window.RK_MEDIA || {};
  var media = all[bookId];
  if (!media) return;

  var lang = (document.documentElement.lang || "ko").slice(0, 2) === "en" ? "en" : "ko";
  var LABEL = {
    ko: { watch: "YouTube에서 보기", chapter: "책에서 이어 보기", playlist: "YouTube 재생목록 전체 보기", newTab: "새 탭에서 열림" },
    en: { watch: "Watch on YouTube", chapter: "Continue in the book", playlist: "Open the full YouTube playlist", newTab: "opens in a new tab" }
  }[lang];

  function pick(value) {
    if (!value) return "";
    if (typeof value === "string") return value;
    return value[lang] || value.ko || value.en || "";
  }

  function validId(id) {
    return typeof id === "string" && /^[A-Za-z0-9_-]{11}$/.test(id.trim());
  }

  function iframe(youtubeId, title) {
    var f = document.createElement("iframe");
    f.src = "https://www.youtube-nocookie.com/embed/" + youtubeId.trim();
    f.title = title || "YouTube video";
    f.loading = "lazy";
    f.allow = "accelerometer; encrypted-media; gyroscope; picture-in-picture; web-share";
    f.referrerPolicy = "strict-origin-when-cross-origin";
    f.allowFullscreen = true;
    return f;
  }

  function watchLink(youtubeId) {
    var p = document.createElement("p");
    p.className = "rk-video-meta rk-watch-link";
    var a = document.createElement("a");
    a.href = "https://www.youtube.com/watch?v=" + youtubeId.trim();
    a.target = "_blank";
    a.rel = "noopener";
    a.textContent = LABEL.watch + " ↗";
    var sr = document.createElement("span");
    sr.className = "sr-only";
    sr.textContent = " (" + LABEL.newTab + ")";
    a.appendChild(sr);
    p.appendChild(a);
    return p;
  }

  function embedInto(el, video, id) {
    var title = pick(video.title) || id;
    el.innerHTML = "";
    el.removeAttribute("role");
    el.removeAttribute("aria-label");
    el.classList.add("is-live");
    el.appendChild(iframe(video.youtube, title + " [" + id + "]"));
    el.insertAdjacentElement("afterend", watchLink(video.youtube));
  }

  // 1. Fill every placeholder whose video now has a YouTube ID.
  var videos = media.videos || {};
  Array.prototype.forEach.call(document.querySelectorAll("[data-video-id]"), function (el) {
    var id = el.getAttribute("data-video-id");
    var video = videos[id];
    if (el.classList.contains("is-live")) return; // already rendered at build time
    if (video && validId(video.youtube)) embedInto(el, video, id);
  });

  // 2. Playlist link.
  if (media.playlist) {
    Array.prototype.forEach.call(document.querySelectorAll("[data-playlist-link]"), function (a) {
      a.href = media.playlist;
      a.hidden = false;
      var wrap = a.closest("[data-playlist-wrap]");
      if (wrap) wrap.hidden = false;
    });
  }

  // 3. Videos added later (not tied to a fixed slot on the page).
  var extraSection = document.getElementById("rk-extra-videos");
  var extras = (media.extraVideos || []).filter(function (v) { return validId(v.youtube); });
  if (extraSection && extras.length) {
    var grid = extraSection.querySelector("[data-extra-grid]");
    extras.forEach(function (v) {
      var card = document.createElement("article");
      card.className = "rk-vcard";
      var thumb = document.createElement("div");
      thumb.className = "rk-video rk-video-card";
      thumb.appendChild(iframe(v.youtube, pick(v.title)));
      var body = document.createElement("div");
      body.className = "rk-vbody";
      var h = document.createElement("h3");
      h.textContent = pick(v.title);
      body.appendChild(h);
      if (v.note) {
        var p = document.createElement("p");
        p.textContent = pick(v.note);
        body.appendChild(p);
      }
      if (v.chapter) {
        var a = document.createElement("a");
        a.className = "rk-book-link";
        a.href = "../toc.html";
        a.textContent = LABEL.chapter + " · " + v.chapter;
        body.appendChild(a);
      }
      card.appendChild(thumb);
      card.appendChild(body);
      grid.appendChild(card);
    });
    extraSection.hidden = false;
  }

  // 4. Sample page gallery.
  var gallery = document.getElementById("rk-sample-gallery");
  var samples = (media.samples || []).filter(function (s) { return !s.lang || s.lang === lang; });
  if (gallery && samples.length) {
    var sgrid = gallery.querySelector("[data-sample-grid]");
    samples.forEach(function (s) {
      var a = document.createElement("a");
      a.href = root + s.src;
      a.target = "_blank";
      a.rel = "noopener";
      var img = document.createElement("img");
      img.src = root + s.src;
      img.alt = pick(s.alt);
      img.loading = "lazy";
      img.className = "sample-image";
      a.appendChild(img);
      sgrid.appendChild(a);
    });
    gallery.hidden = false;
  }
})();
