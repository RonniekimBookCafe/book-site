/*
 * Ronnie Kim Books — Download Center data (v1.20)
 * Used by /ko/downloads/, /en/downloads/ (assets/js/downloads.js) and the home page quick panel (assets/js/home-hub.js).
 *
 * Add a new robot or book:
 *   1. Put the files in the site (for a book: ko/books/book-NNN/downloads/ and en/books/book-NNN/downloads/;
 *      for a project robot: downloads/projects/<code>/).
 *   2. Append an item below. Paths are relative to the site root (no leading "./").
 *   3. status: "available" (files ready) · "coming" (book page exists, files not yet) · "planned" (announced only).
 *      page = book page, guide = the book's own install/setup page (optional).
 *   4. A file entry may be:
 *        { href: "path/to/file.zip", bytes: 12345, sha256: "..." }      → Download button
 *        { workshop: "https://steamcommunity.com/..." }                  → Steam Workshop link
 *        { pending: true }                                               → "Coming soon" label
 *      Leave a file key out (or null) when that file does not apply.
 *   5. Bump ?v= on downloads-data.js in index.html and ko|en/downloads/index.html.
 */
window.downloadsData = {
  updated: "2026-11-09",

  groups: [
    {
      id: "roboco",
      ko: {
        title: "피지컬 AI로 배우는 RoboCo 시리즈",
        lead: "책에서 쓰는 로봇 파일과 실습 코드입니다. 책 표지 왼쪽 위의 코드(CORE-01, QUAD-01 …)로 찾으세요."
      },
      en: {
        title: "Physical AI with RoboCo series",
        lead: "Robot files and practice code used in the books. Find your book by the code at the top left of its cover (CORE-01, QUAD-01 …)."
      }
    },
    {
      id: "projects",
      ko: {
        title: "RoboCo 로봇 프로젝트",
        lead: "책 밖에서 이어 가는 실습 로봇입니다. 준비되는 대로 로봇 파일과 코드를 이곳에 차례로 공개합니다."
      },
      en: {
        title: "RoboCo robot projects",
        lead: "Practice robots beyond the books. Robot files and code will appear here as each one is ready."
      }
    }
  ],

  items: [
    {
      code: "CORE-01",
      group: "roboco",
      capability: "MOVE / CONTROL",
      color: "#E4D234",
      book: "book-005",
      cover: "assets/images/books/book-005/cover-thumb-{lang}.webp?v=1.18",
      status: "available",
      version: "v1.6.3",
      ko: { name: "피지컬 AI로 배우는 RoboCo 로봇 구조와 Python 제어", robot: "4륜 독립 구동·독립 조향 로봇" },
      en: { name: "Physical AI with RoboCo: Robot Structure and Python Control", robot: "Four-wheel independent drive and steering robot" },
      files: {
        robot: {
          href: "ko/books/book-005/downloads/Book-CORE-01-Robot-Files.zip",
          bytes: 154892,
          sha256: "cc3978810bfd9d289208c6b84b155c59fa6ae4b9b9e1aa30c3e19f2fa98d1397",
          note: { ko: "로봇 2종 (.robo)", en: "2 robots (.robo)" }
        },
        ko: {
          href: "ko/books/book-005/downloads/Book_C01_Robot_release_v1.6.3_kr.zip",
          bytes: 50809,
          sha256: "8ccad6d51b2a89d150235f9f89efd8356fffc953bd9af7baca8a86403fdcb1ca"
        },
        en: {
          href: "en/books/book-005/downloads/Book_C01_Robot_release_v1.6.3_en.zip",
          bytes: 46780,
          sha256: "24b30515276a661a21f0966f88971714bbdfc1042ee3105e47dad4695a679b70"
        }
      },
      extras: [
        {
          href: { ko: "ko/books/book-005/downloads/record-sheets/CORE-01_record-sheets_ko.pdf", en: "en/books/book-005/downloads/record-sheets/CORE-01_record-sheets_en.pdf" },
          label: { ko: "실험·미션 기록지 PDF", en: "Experiment & mission record sheets (PDF)" }
        }
      ],
      page: { ko: "ko/books/book-005/", en: "en/books/book-005/" },
      guide: { ko: "ko/books/book-005/downloads/", en: "en/books/book-005/downloads/" },
      preview: "assets/images/books/book-005/robot/robot-controls.webp"
    },
    {
      code: "CORE-02",
      group: "roboco",
      capability: "SENSE / REACT",
      color: "#E4D234",
      book: "book-006",
      cover: "assets/images/books/book-006/cover-thumb-ko.webp?v=1.18",
      status: "coming",
      ko: { name: "피지컬 AI로 배우는 RoboCo 센서와 로봇 제어", robot: "4륜 로봇 + 전개형 센서 그리퍼" },
      en: { name: "Physical AI with RoboCo: Sensors and Robot Control", robot: "Four-wheel robot with a deployable sensor gripper" },
      files: { robot: { pending: true }, ko: { pending: true }, en: { pending: true } },
      page: { ko: "ko/books/book-006/", en: "ko/books/book-006/" }
    },
    {
      code: "CORE-03",
      group: "roboco",
      capability: "MANIPULATE",
      color: "#E4D234",
      book: "book-007",
      cover: "assets/images/books/book-007/cover-thumb-ko.webp?v=1.18",
      status: "coming",
      ko: { name: "피지컬 AI로 배우는 RoboCo 로봇팔과 작업 제어", robot: "4륜 이동 로봇팔 (4DOF + 집게)" },
      en: { name: "Physical AI with RoboCo: Robot Arms and Task Control", robot: "Four-wheel mobile robot arm (4 DOF + claw)" },
      files: { robot: { pending: true }, ko: { pending: true }, en: { pending: true } },
      page: { ko: "ko/books/book-007/", en: "ko/books/book-007/" }
    },
    {
      code: "QUAD-01",
      group: "roboco",
      capability: "WALK",
      color: "#F08300",
      book: "book-008",
      cover: "assets/images/books/book-008/cover-thumb-{lang}.webp?v=1.18",
      status: "available",
      version: "v3.5.0",
      ko: { name: "피지컬 AI로 배우는 RoboCo 구조와 보행 제어", robot: "12관절 4족 로봇 · 실습 모델 7종" },
      en: { name: "Learning Physical AI with RoboCo: Robot Structure and Gait Control", robot: "Twelve-joint quadruped · 7 practice models" },
      files: {
        robot: {
          workshop: "",
          note: { ko: "Steam Workshop 7종 · 주소 등록 예정", en: "7 models on Steam Workshop · links coming" }
        },
        ko: {
          href: "ko/books/book-008/downloads/Book_Q01_Robot_release_v3.5.0_kr.zip",
          bytes: 400046,
          sha256: "f8f09122a7b9df516400ce6bec4601ce7e232bf6e7e3a65eb6f270dc64322b24"
        },
        en: {
          href: "en/books/book-008/downloads/Book_Q01_Robot_release_v3.5.0_en.zip",
          bytes: 118752,
          sha256: "06954534149eb9df1d4578b5a9b3fe6aa14015192f501b5d6e9bd77e593e5e9f"
        }
      },
      page: { ko: "ko/books/book-008/", en: "en/books/book-008/" },
      guide: { ko: "ko/books/book-008/downloads/", en: "en/books/book-008/downloads/" },
      preview: "assets/images/books/book-008/robot/quad01-robot.webp"
    },
    {
      code: "QUAD-02",
      group: "roboco",
      capability: "DECIDE",
      color: "#F08300",
      book: "book-009",
      cover: "assets/images/books/book-009/cover-thumb-ko.webp?v=1.18",
      status: "coming",
      ko: { name: "피지컬 AI로 배우는 4족 로봇 자율보행과 AI", robot: "센서·판단을 더한 4족 로봇" },
      en: { name: "Physical AI with RoboCo: Autonomous Walking and AI", robot: "Quadruped with sensors and decision making" },
      files: { robot: { pending: true }, ko: { pending: true }, en: { pending: true } },
      page: { ko: "ko/books/book-009/", en: "ko/books/book-009/" }
    },
    {
      code: "QUAD-03",
      group: "roboco",
      capability: "WORK",
      color: "#F08300",
      book: "book-010",
      cover: "assets/images/books/book-010/cover-thumb-ko.webp?v=1.18",
      status: "coming",
      ko: { name: "피지컬 AI로 배우는 4족 로봇의 로봇팔과 작업 자동화", robot: "로봇팔을 단 4족 로봇" },
      en: { name: "Physical AI with RoboCo: A Quadruped's Robot Arm and Task Automation", robot: "Quadruped with a robot arm" },
      files: { robot: { pending: true }, ko: { pending: true }, en: { pending: true } },
      page: { ko: "ko/books/book-010/", en: "ko/books/book-010/" }
    },

    {
      code: "RP-TRANSFORM",
      group: "projects",
      icon: "transform",
      status: "planned",
      ko: { name: "변신 로봇", robot: "주행 형태와 보행 형태를 오가는 로봇" },
      en: { name: "Transforming robot", robot: "Switches between a driving form and a walking form" },
      files: { robot: { pending: true }, ko: { pending: true }, en: { pending: true } }
    },
    {
      code: "RP-ARM",
      group: "projects",
      icon: "arm",
      status: "planned",
      ko: { name: "로봇팔", robot: "고정형 다관절 로봇팔" },
      en: { name: "Robot arm", robot: "Fixed multi-joint robot arm" },
      files: { robot: { pending: true }, ko: { pending: true }, en: { pending: true } }
    },
    {
      code: "RP-DRONE",
      group: "projects",
      icon: "drone",
      status: "planned",
      ko: { name: "드론", robot: "여러 출력의 차이로 자세를 잡는 비행 로봇" },
      en: { name: "Drone", robot: "A flying robot that holds its attitude by balancing several outputs" },
      files: { robot: { pending: true }, ko: { pending: true }, en: { pending: true } }
    },
    {
      code: "RP-HEXAPOD",
      group: "projects",
      icon: "hexapod",
      status: "planned",
      ko: { name: "6족 로봇", robot: "다리 여섯 개를 두 무리로 나눠 걷는 로봇" },
      en: { name: "Hexapod", robot: "Six legs walking in two groups" },
      files: { robot: { pending: true }, ko: { pending: true }, en: { pending: true } }
    },
    {
      code: "RP-BIPED",
      group: "projects",
      icon: "biped",
      status: "planned",
      ko: { name: "2족 보행 로봇", robot: "두 다리로 균형을 잡으며 걷는 로봇" },
      en: { name: "Biped walking robot", robot: "Walks on two legs while keeping its balance" },
      files: { robot: { pending: true }, ko: { pending: true }, en: { pending: true } }
    }
  ]
};

/* Line icons for robot projects (48×48, stroke = currentColor). */
window.downloadIcons = {
  transform:
    '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="4" y="12" width="16" height="9" rx="2"/><circle cx="8" cy="25" r="3"/><circle cx="17" cy="25" r="3"/>' +
    '<path d="M22 14h5m-2-2 2 2-2 2M27 22h-5m2-2-2 2 2 2"/><rect x="31" y="10" width="13" height="8" rx="2"/><path d="M33 18l-2 8 2 6M42 18l2 8-2 6"/><path d="M4 38h40" stroke-dasharray="2 3"/></svg>',
  arm:
    '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="8" y="38" width="18" height="5" rx="1"/><path d="M17 38v-6"/><circle cx="17" cy="30" r="2.5"/>' +
    '<path d="M18.5 28 28 15"/><circle cx="29.5" cy="13.5" r="2.5"/><path d="M32 14.5 39 21"/><path d="M39 21l4-2M39 21l1 4"/></svg>',
  drone:
    '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M13 13l22 22M35 13 13 35"/><rect x="19" y="19" width="10" height="10" rx="2"/>' +
    '<ellipse cx="11" cy="11" rx="7" ry="2.5"/><ellipse cx="37" cy="11" rx="7" ry="2.5"/><ellipse cx="11" cy="37" rx="7" ry="2.5"/><ellipse cx="37" cy="37" rx="7" ry="2.5"/></svg>',
  hexapod:
    '<svg viewBox="0 0 48 48" aria-hidden="true"><ellipse cx="24" cy="24" rx="7" ry="11"/>' +
    '<path d="M17 17l-6-4-4 6M17 24h-7l-4 6M17 31l-6 4-2 7M31 17l6-4 4 6M31 24h7l4 6M31 31l6 4 2 7"/></svg>',
  biped:
    '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="18" y="4" width="12" height="9" rx="2"/><rect x="15" y="15" width="18" height="13" rx="2"/>' +
    '<path d="M15 18l-5 8M33 18l5 8M20 28l-2 8 1 7M28 28l2 8-1 7M15 43h7M26 43h7"/></svg>'
};
