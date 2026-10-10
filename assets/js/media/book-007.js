/*
 * CORE-03 (book-007) — videos and sample pages for the website.
 *
 * Publish a video : paste its 11-character YouTube ID into "youtube".
 * Playlist        : paste the YouTube playlist URL into "playlist".
 * Add a video     : append to "extraVideos", e.g.
 *   { "id": "C03-W09", "youtube": "xxxxxxxxxxx", "chapter": "CH17",
 *     "title": { "ko": "제목", "en": "Title" }, "note": { "ko": "볼 것", "en": "What to watch" } }
 * Add a sample    : save the image under assets/images/books/book-007/ and append to "samples", e.g.
 *   { "src": "assets/images/books/book-007/sample-ko-01.webp", "lang": "ko", "alt": "샘플 페이지 1" }
 */
window.RK_MEDIA = window.RK_MEDIA || {};
window.RK_MEDIA["book-007"] = {
  "book": "CORE-03",
  "playlist": "",
  "videos": {
    "C03-25-00": {
      "youtube": "",
      "chapter": "CH25",
      "title": {
        "ko": "CORE-03 CH25 CORE-03 최종 물체 옮기기 미션",
        "en": "CORE-03 CH25 final mission"
      }
    }
  },
  "extraVideos": [],
  "samples": []
};
