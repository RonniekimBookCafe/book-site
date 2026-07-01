const pageText = {
  ko: {
    subtitle: "출간 도서와 샘플 본문을 한국어로 확인하세요.",
    sectionTitle: "출간 도서",
    searchPlaceholder: "책 제목 또는 설명 검색",
    allCategory: "전체 카테고리",
    categories: {
      career: "커리어",
      education: "교육",
      essay: "에세이",
      tech: "기술"
    },
    sort: {
      featured: "추천순",
      newest: "최신순",
      oldest: "오래된순",
      title: "제목순"
    },
    countText: function (count) {
      return "총 " + count + "권";
    },
    empty: "검색 결과가 없습니다."
  },
  en: {
    subtitle: "Explore books and sample chapters in English.",
    sectionTitle: "Published Books",
    searchPlaceholder: "Search by title or description",
    allCategory: "All Categories",
    categories: {
      career: "Career",
      education: "Education",
      essay: "Essay",
      tech: "Technology"
    },
    sort: {
      featured: "Featured",
      newest: "Newest",
      oldest: "Oldest",
      title: "Title"
    },
    countText: function (count) {
      return count + " book" + (count === 1 ? "" : "s");
    },
    empty: "No books found."
  }
};

let currentLanguage = "ko";

const koButton = document.getElementById("lang-ko");
const enButton = document.getElementById("lang-en");

const siteSubtitle = document.getElementById("site-subtitle");
const sectionTitle = document.getElementById("section-title");
const bookGrid = document.getElementById("book-grid");

const bookSearch = document.getElementById("book-search");
const bookCategory = document.getElementById("book-category");
const bookSort = document.getElementById("book-sort");
const bookCount = document.getElementById("book-count");
const emptyMessage = document.getElementById("empty-message");

function updateToolText(lang) {
  const text = pageText[lang];

  bookSearch.placeholder = text.searchPlaceholder;

  bookCategory.innerHTML = `
    <option value="all">${text.allCategory}</option>
    <option value="career">${text.categories.career}</option>
    <option value="education">${text.categories.education}</option>
    <option value="essay">${text.categories.essay}</option>
    <option value="tech">${text.categories.tech}</option>
  `;

  bookSort.innerHTML = `
    <option value="featured">${text.sort.featured}</option>
    <option value="newest">${text.sort.newest}</option>
    <option value="oldest">${text.sort.oldest}</option>
    <option value="title">${text.sort.title}</option>
  `;

  emptyMessage.textContent = text.empty;
}

function getFilteredBooks() {
  const keyword = bookSearch.value.trim().toLowerCase();
  const category = bookCategory.value;
  const sort = bookSort.value;

  let result = booksData.filter((book) => {
    const data = book[currentLanguage];

    const matchesKeyword =
      !keyword ||
      data.title.toLowerCase().includes(keyword) ||
      data.description.toLowerCase().includes(keyword);

    const matchesCategory =
      category === "all" || book.category === category;

    return matchesKeyword && matchesCategory;
  });

  result.sort((a, b) => {
    const titleA = a[currentLanguage].title;
    const titleB = b[currentLanguage].title;

    if (sort === "newest") {
      return new Date(b.publishedAt) - new Date(a.publishedAt);
    }

    if (sort === "oldest") {
      return new Date(a.publishedAt) - new Date(b.publishedAt);
    }

    if (sort === "title") {
      return titleA.localeCompare(titleB);
    }

    return a.featured - b.featured;
  });

  return result;
}

function renderBooks() {
  const books = getFilteredBooks();
  const text = pageText[currentLanguage];

  bookGrid.innerHTML = "";
  bookCount.textContent = text.countText(books.length);
  emptyMessage.hidden = books.length !== 0;

  books.forEach((book) => {
    const data = book[currentLanguage];

    const article = document.createElement("article");
    article.className = "book-card compact-book-card";

    article.innerHTML = `
      <a class="book-cover-link" href="${data.link}">
        <img
          class="book-cover-thumb"
          src="${book.cover}"
          alt="${data.alt}"
        />
      </a>

      <h3>${data.title}</h3>
      <p>${data.description}</p>
      <a class="book-card-button" href="${data.link}">${data.button}</a>
    `;

    bookGrid.appendChild(article);
  });
}

function setLanguage(lang) {
  currentLanguage = lang;

  const selected = pageText[lang] || pageText.ko;

  document.documentElement.lang = lang;
  siteSubtitle.textContent = selected.subtitle;
  sectionTitle.textContent = selected.sectionTitle;

  koButton.classList.toggle("active", lang === "ko");
  enButton.classList.toggle("active", lang === "en");

  localStorage.setItem("siteLanguage", lang);

  updateToolText(lang);
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