const pageText = {
  ko: {
    subtitle: "출간 도서와 샘플 본문을 한국어로 확인하세요.",
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
    upcomingLead: "CORE-01에 이어 센서, 로봇팔, 4족 보행, 자율보행 AI, 이동 조작으로 이어지는 다섯 권을 준비하고 있습니다.",
    empty: "검색 결과가 없습니다."
  },

  en: {
    subtitle: "Explore books and sample chapters in English.",
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
    upcomingLead: "After CORE-01, five more volumes cover sensors, robot arms, quadruped walking, autonom
ous AI, and mobile manipulation (Korean pages).",
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
    ? `<span class="book-status-badge${book.status === "upcoming" ? "" : " is-new"}">${data.badge}</span>
`
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

function setLanguage(lang) {
  currentLanguage = pageText[lang] ? lang : "ko";

  const selected = pageText[currentLanguage];

  document.documentElement.lang = currentLanguage;
  siteSubtitle.textContent = selected.subtitle;
  sectionTitle.textContent = selected.sectionTitle;

  koButton.classList.toggle("active", currentLanguage === "ko");
  enButton.classList.toggle("active", currentLanguage === "en");

  localStorage.setItem("siteLanguage", currentLanguage);

  updateToolText(currentLanguage);
  renderBooks();
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
