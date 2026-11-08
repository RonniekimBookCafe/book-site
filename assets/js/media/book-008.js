/*
 * QUAD-01 (book-008) — videos and sample pages for the website.
 *
 * Publish a video : paste its 11-character YouTube ID into "youtube".
 * Playlist        : paste the YouTube playlist URL into "playlist".
 * Add a video     : append to "extraVideos", e.g.
 *   { "id": "Q01-W01", "youtube": "xxxxxxxxxxx", "chapter": "CH20",
 *     "title": { "ko": "제목", "en": "Title" }, "note": { "ko": "볼 것", "en": "What to watch" } }
 * Add a sample    : save the image under assets/images/books/book-008/ and append to "samples", e.g.
 *   { "src": "assets/images/books/book-008/sample-ko-01.webp", "lang": "ko", "alt": "샘플 페이지 1" }
 */
window.RK_MEDIA = window.RK_MEDIA || {};
window.RK_MEDIA["book-008"] = {
  "book": "QUAD-01",
  "playlist": "https://www.youtube.com/watch?v=4-5uGHX3k2E&list=PLHFcPlL2gYbU",
  "videos": {
    "Q01-01-00": {
      "youtube": "4-5uGHX3k2E",
      "chapter": "CH01",
      "title": {
        "ko": "QUAD-01 CH01 WALK 보행 전체 동작",
        "en": "QUAD-01 CH01 WALK: the full walking run"
      }
    },
    "Q01-02-00": {
      "youtube": "X6flRddoA40",
      "chapter": "CH02",
      "title": {
        "ko": "QUAD-01 CH02 ACTION 퍼포먼스 전체 동작",
        "en": "QUAD-01 CH02 ACTION: all the performances"
      }
    },
    "Q01-06-00": {
      "youtube": "LNMvi4Upy6s",
      "chapter": "CH06",
      "title": {
        "ko": "QUAD-01 CH06 LEG1 3자유도 관절 제어",
        "en": "QUAD-01 CH06 LEG1: three joints, one at a time"
      }
    },
    "Q01-11-00": {
      "youtube": "GdoPi8bZAd0",
      "chapter": "CH11",
      "title": {
        "ko": "QUAD-01 CH11 LEG2 역기구학 IK 제어",
        "en": "QUAD-01 CH11 LEG2: inverse kinematics (IK)"
      }
    },
    "Q01-14-00": {
      "youtube": "Q2OSfB5iTNk",
      "chapter": "CH14",
      "title": {
        "ko": "QUAD-01 CH14 LEG3 네 다리 협응 제어",
        "en": "QUAD-01 CH14 LEG3: four legs working together"
      }
    },
    "Q01-15-00": {
      "youtube": "iQcXRLqDBH4",
      "chapter": "CH15",
      "title": {
        "ko": "QUAD-01 CH15 Roll·Pitch·Yaw 몸통 자세 제어",
        "en": "QUAD-01 CH15 ROLL_PITCH_YAW: body posture"
      }
    },
    "Q01-17-00": {
      "youtube": "9OVq32vbYC0",
      "chapter": "CH17",
      "title": {
        "ko": "QUAD-01 CH17 BALANCE IMU·PID 균형 제어",
        "en": "QUAD-01 CH17 BALANCE: IMU and PID balance"
      }
    },
    "Q01-25-00": {
      "youtube": "",
      "chapter": "CH25",
      "title": {
        "ko": "QUAD-01 CH25 4족 보행 최종 미션",
        "en": "QUAD-01 CH25 Final walking mission"
      }
    }
  },
  "extraVideos": [],
  "samples": []
};
