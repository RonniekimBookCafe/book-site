/*
 * QUAD-02 (book-009) — videos and sample pages for the website.
 *
 * Publish a video : paste its 11-character YouTube ID into "youtube".
 * Playlist        : paste the YouTube playlist URL into "playlist".
 * Add a video     : append to "extraVideos", e.g.
 *   { "id": "Q02-W09", "youtube": "xxxxxxxxxxx", "chapter": "CH17",
 *     "title": { "ko": "제목", "en": "Title" }, "note": { "ko": "볼 것", "en": "What to watch" } }
 * Add a sample    : save the image under assets/images/books/book-009/ and append to "samples", e.g.
 *   { "src": "assets/images/books/book-009/sample-ko-01.webp", "lang": "ko", "alt": "샘플 페이지 1" }
 */
window.RK_MEDIA = window.RK_MEDIA || {};
window.RK_MEDIA["book-009"] = {
  "book": "QUAD-02",
  "playlist": "",
  "videos": {
    "Q02-25-00": {
      "youtube": "",
      "chapter": "CH25",
      "title": {
        "ko": "QUAD-02 CH25 AI 자율보행 최종 미션",
        "en": "QUAD-02 CH25 final mission"
      }
    }
  },
  "extraVideos": [],
  "samples": []
};
