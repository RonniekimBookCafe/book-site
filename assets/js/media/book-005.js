/*
 * CORE-01 (book-005) — videos and sample pages for the website.
 *
 * Publish a video : paste its 11-character YouTube ID into "youtube".
 * Playlist        : paste the YouTube playlist URL into "playlist".
 * Add a video     : append to "extraVideos", e.g.
 *   { "id": "C01-W09", "youtube": "xxxxxxxxxxx", "chapter": "CH17",
 *     "title": { "ko": "제목", "en": "Title" }, "note": { "ko": "볼 것", "en": "What to watch" } }
 * Add a sample    : save the image under assets/images/books/book-005/ and append to "samples", e.g.
 *   { "src": "assets/images/books/book-005/sample-ko-01.webp", "lang": "ko", "alt": "샘플 페이지 1" }
 */
window.RK_MEDIA = window.RK_MEDIA || {};
window.RK_MEDIA["book-005"] = {
  "book": "CORE-01",
  "playlist": "",
  "videos": {
    "C01-25-00": {
      "youtube": "CD96tZ2EnUM",
      "chapter": "CH25",
      "title": {
        "ko": "CORE-01 CH25 이동 안내 로봇 최종 미션",
        "en": "CORE-01 CH25 Guide robot final mission"
      }
    },
    "C01-06-00": {
      "youtube": "9eBLvXMD51U",
      "chapter": "CH06",
      "title": {
        "ko": "CORE-01 CH06 로봇 구성과 분해도",
        "en": "CORE-01 CH06 Robot structure and exploded view"
      }
    },
    "C01-07-00": {
      "youtube": "TCCaK7J9d48",
      "chapter": "CH07",
      "title": {
        "ko": "CORE-01 CH07 Microcontroller Port 연결",
        "en": "CORE-01 CH07 Microcontroller Port connections"
      }
    },
    "C01-W01": {
      "youtube": "Rox7nBVuzTo",
      "chapter": "CH10",
      "title": {
        "ko": "8가지 움직임 — 키 하나씩",
        "en": "Eight motions, one key at a time"
      }
    },
    "C01-W02": {
      "youtube": "kfBA4yUwPuk",
      "chapter": "CH17",
      "title": {
        "ko": "경사로 오르기 — RPM 낮음 vs 높음",
        "en": "Slope climb — low vs. high RPM"
      }
    },
    "C01-W03": {
      "youtube": "rbUbGB2ueI8",
      "chapter": "CH19",
      "title": {
        "ko": "정지 거리 — 제동 시간 짧게 vs 길게",
        "en": "Stopping distance — short vs. long braking"
      }
    },
    "C01-W04": {
      "youtube": "AW76p-tNCHw",
      "chapter": "CH18",
      "title": {
        "ko": "조향 전환 — 앞뒤 동시 vs 시간차",
        "en": "Steering change — front and rear together vs. staggered"
      }
    },
    "C01-W05": {
      "youtube": "sHlhZDKaORM",
      "chapter": "CH17",
      "title": {
        "ko": "실패: 오르막에서 바퀴만 도는 장면",
        "en": "Failure: wheels spin on a slope"
      }
    },
    "C01-W06": {
      "youtube": "SAlQcQ_8GWs",
      "chapter": "CH12 · CH24",
      "title": {
        "ko": "실패: 키를 눌러도 반응이 없는 장면",
        "en": "Failure: key pressed, nothing happens"
      }
    },
    "C01-W07": {
      "youtube": "OhDsglJrOVw",
      "chapter": "CH23 · CH25",
      "title": {
        "ko": "실패: 미션이 목표 지점을 지나치는 장면",
        "en": "Failure: mission overshoots"
      }
    },
    "C01-W08": {
      "youtube": "UJiqc7WV-II",
      "chapter": "시작하기",
      "title": {
        "ko": "설치·첫 실행 화면 녹화",
        "en": "Install and first-run recording"
      }
    }
  },
  "extraVideos": [],
  "samples": []
};
