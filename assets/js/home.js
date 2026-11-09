const pageText = {
  ko: {
    subtitle: "책을 읽고, 실습 로봇 파일과 소스 코드를 받아 직접 실행해 보세요. 커리어·아두이노·교육·로봇·피지컬 AI 책을 한곳에 모았습니다.",
    sectionTitle: "출간 도서",
    searchPlaceholder: "책 제목 또는 설명 검색",
    allCategory: "전체 카테고리",
    categories: {
      career: "커리어",
      arduino: "아두이노",
      education: "교육",
      essay: "에세이",
      tech: "기술",
      robotics: "로봇·피지컬 AI"
    },
    sort: {
      newest: "최신순",
      featured: "추천순",
      oldest: "오래된순",
      title: "제목순"
    },
    countText: function (count) {
      return "총 " + count + "권";
    },
    upcomingTitle: "출간 예정 · 피지컬 AI로 배우는 RoboCo 시리즈",
    channelsLabel: "공식 채널",
    youtube: "공식 YouTube",
    youtubeDesc: "실습 실행 영상 · 책 QR 영상",
    blog: "공식 네이버 블로그",
    blogDesc: "집필 노트 · 업데이트 · 정오표 소식",
    spotlightBadge: "신간",
    spotlightView: "책 보기",
    spotlightBuy: "구매하기",
    spotlightVideo: "걷는 영상 보기",
    upcomingLead: "CORE-01과 QUAD-01에 이어 센서, 로봇팔, 자율보행 AI, 이동 조작으로 이어지는 네 권을 준비하고 있습니다.",
    empty: "검색 결과가 없습니다."
  },

  en: {
    subtitle: "Read the books, then download the robot files and source code and run them yourself. Career, Arduino, education, and robotics & physical AI books in one place.",
    sectionTitle: "Published Books",
    searchPlaceholder: "Search by title or description",
    allCategory: "All Categories",
    categories: {
      career: "Career",
      arduino: "Arduino",
      education: "Education",
      essay: "Essay",
      tech: "Technology",
      robotics: "Robotics & Physical AI"
    },
    sort: {
      newest: "Newest",
      featured: "Featured",
      oldest: "Oldest",
      title: "Title"
    },
    countText: function (count) {
      return count + " book" + (count === 1 ? "" : "s");
    },
    upcomingTitle: "Coming soon · Physical AI with RoboCo series",
    channelsLabel: "Official channels",
    youtube: "YouTube",
    youtubeDesc: "Practice run videos · videos from the book's QR codes",
    blog: "Naver Blog (Korean)",
    blogDesc: "Writing notes, updates, and errata news",
    spotlightBadge: "New release",
    spotlightView: "View book",
    spotlightBuy: "Buy",
    spotlightVideo: "Watch it walk",
    upcomingLead: "After CORE-01 and QUAD-01, four more volumes cover sensors, robot arms, autonomous AI, and mobile manipulation (Korean pages).",
    empty: "No books found."
  }
};

let currentLanguage = "ko";

const koButton = document.getElementById("lang-ko");
const enButton = document.getElementById("lang-en");

const siteSubtitle = document.getElementById("site-subtitle");
const sectionTitle = document.getElementById("section-title");
const bookGrid = document.getElementById("book-grid");
const upcomingSection = document.getElementById("upcoming-section");
const upcomingGrid = document.getElementById("upcoming-grid");
const upcomingTitle = document.getElementById("upcoming-title");
const upcomingLead = document.getElementById("upcoming-lead");

const bookSearch = document.getElementById("book-search");
const bookCategory = document.getElementById("book-category");
const bookSort = document.getElementById("book-sort");
const bookCount = document.getElementById("book-count");
const emptyMessage = document.getElementById("empty-message");

function getBooksData() {
  return Array.isArray(window.booksData) ? window.booksData : [];
}

function updateToolText(lang) {
  const text = pageText[lang] || pageText.ko;

  bookSearch.placeholder = text.searchPlaceholder;

  bookCategory.innerHTML = `
    <option value="all">${text.allCategory}</option>
    <option value="career">${text.categories.career}</option>
    <option value="arduino">${text.categories.arduino}</option>
    <option value="education">${text.categories.education}</option>
    <option value="essay">${text.categories.essay}</option>
    <option value="tech">${text.categories.tech}</option>
    <option value="robotics">${text.categories.robotics}</option>
  `;

  const selectedSort = bookSort.value || "newest";

  bookSort.innerHTML = `
    <option value="newest">${text.sort.newest}</option>
    <option value="featured">${text.sort.featured}</option>
    <option value="oldest">${text.sort.oldest}</option>
    <option value="title">${text.sort.title}</option>
  `;

  bookSort.value = selectedSort;

  emptyMessage.textContent = text.empty;
}

function getFilteredBooks() {
  const keyword = bookSearch.value.trim().toLowerCase();
  const category = bookCategory.value;
  const sort = bookSort.value;

  const result = getBooksData().filter(function (book) 
{
    const data = book[currentLanguage];

    if (!data) {
      return false;
    }

    const matchesKeyword =
      !keyword ||
      data.title.toLowerCase().includes(keyword) ||
      data.description.toLowerCase().includes(keyword);

    const matchesCategory =
      category === "all" || book.category === category;

    return matchesKeyword && matchesCategory;
  });

  // Upcoming books have no publishedAt yet; treat them as the newest.
  function sortTime(book) {
    const time = book.publishedAt ? new Date(book.publishedAt).getTime() : NaN;
    return isNaN(time) ? Number.MAX_SAFE_INTEGER : time;
  }

  result.sort(function (a, b) {
    const titleA = a[currentLanguage].title;
    const titleB = b[currentLanguage].title;

    if (sort === "newest") {
      return sortTime(b) - sortTime(a);
    }

    if (sort === "oldest") {
      return sortTime(a) - sortTime(b);
    }

    if (sort === "title") {
      return titleA.localeCompare(titleB);
    }

    return a.featured - b.featured;
  });

  return result;
}

function createCard(book) {
  const data = book[currentLanguage];

  const article = document.createElement("article");
  article.className = "book-card compact-book-card" + (book.status === "upcoming" ? " is-upcoming" : "");

  const badge = data.badge
    ? `<span class="book-status-badge${book.status === "upcoming" ? "" : " is-new"}">${data.badge}</span>`
    : "";

  article.innerHTML = `
    ${badge}
    <a class="book-cover-link" href="${data.link}">
      <img
        class="book-cover-thumb"
        src="${data.cover}"
        alt="${data.alt}"
        loading="lazy"
      />
    </a>

    <h3>${data.title}</h3>
    <p>${data.description}</p>
    <a class="book-card-button" href="${data.link}">${data.button}</a>
  `;

  return article;
}

function renderBooks() {
  const books = getFilteredBooks();
  const text = pageText[currentLanguage] || pageText.ko;

  const published = books.filter(function (book) {
    return book.status !== "upcoming";
  });

  // Upcoming books keep series order (CORE-02 → QUAD-03) in their own row.
  const upcoming = books
    .filter(function (book) {
      return book.status === "upcoming";
    })
    .sort(function (a, b) {
      return (a.seriesOrder || 0) - (b.seriesOrder || 0);
    });

  bookGrid.innerHTML = "";
  bookCount.textContent = text.countText(published.length);
  emptyMessage.hidden = books.length !== 0;

  published.forEach(function (book) {
    bookGrid.appendChild(createCard(book));
  });

  if (upcomingSection) {
    upcomingGrid.innerHTML = "";
    upcomingTitle.textContent = text.upcomingTitle;
    upcomingLead.textContent = text.upcomingLead;
    upcomingSection.hidden = upcoming.length === 0;

    upcoming.forEach(function (book) {
      upcomingGrid.appendChild(createCard(book));
    });
  }
}


// New-release spotlight: books with `spotlight` data are shown first, above the book grid.
function renderSpotlight() {
  const section = document.getElementById("spotlight");
  if (!section) return;
  const text = pageText[currentLanguage] || pageText.ko;
  const book = getBooksData().find(function (b) {
    return b.spotlight && b[currentLanguage];
  });
  if (!book) {
    section.hidden = true;
    return;
  }
  const data = book[currentLanguage];
  const extra = book.spotlight[currentLanguage] || {};
  section.style.setProperty("--spot", book.spotlight.color || "#ff8a34");
  section.innerHTML = `
    <a class="spotlight-cover" href="${data.link}"><img src="${data.coverLarge || data.cover}" alt="${data.alt}" width="420" height="622" /></a>
    <div>
      <p class="spotlight-badges"><span class="is-new">${text.spotlightBadge}</span><span class="is-code">${book.seriesCode} · ${extra.capability || ""}</span></p>
      <h2 id="spotlight-title">${extra.title || data.title}</h2>
      <p class="spotlight-lead">${extra.lead || ""}</p>
      <p class="spotlight-desc">${data.description}</p>
      <div class="spotlight-cta">
        <a class="primary" href="${data.link}buy.html">${text.spotlightBuy}</a>
        <a href="${data.link}">${text.spotlightView}</a>
        <a href="${data.link}learn/">${text.spotlightVideo} ↗</a>
      </div>
    </div>
  `;
  section.hidden = false;
}

function setLanguage(lang) {
  currentLanguage = pageText[lang] ? lang : "ko";

  const selected = pageText[currentLanguage];

  document.documentElement.lang = currentLanguage;
  siteSubtitle.textContent = selected.subtitle;

  const channelsLabel = document.getElementById("channels-label");
  if (channelsLabel) {
    channelsLabel.textContent = selected.channelsLabel;
    document.getElementById("channel-youtube").textContent = selected.youtube;
    document.getElementById("channel-youtube-desc").textContent = selected.youtubeDesc;
    document.getElementById("channel-blog").textContent = selected.blog;
    document.getElementById("channel-blog-desc").textContent = selected.blogDesc;
  }
  sectionTitle.textContent = selected.sectionTitle;

  koButton.classList.toggle("active", currentLanguage === "ko");
  enButton.classList.toggle("active", currentLanguage === "en");

  localStorage.setItem("siteLanguage", currentLanguage);

  updateToolText(currentLanguage);
  renderSpotlight();
  renderBooks();
  if (typeof window.renderHomeHub === "function") {
    window.renderHomeHub(currentLanguage);
  }
}

koButton.addEventListener("click", function () {
  setLanguage("ko");
});

enButton.addEventListener("click", function () {
  setLanguage("en");
});

bookSearch.addEventListener("input", renderBooks);
bookCategory.addEventListener("change", renderBooks);
bookSort.addEventListener("change", renderBooks);

const savedLanguage = localStorage.getItem("siteLanguage");
const browserLanguage = navigator.language || navigator.userLanguage;

const initialLanguage =
  savedLanguage ||
  (browserLanguage && browserLanguage.toLowerCase().startsWith("ko") ? "ko" : "en");

setLanguage(initialLanguage);
