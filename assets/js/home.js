const pageText = {
  ko: {
    subtitle: "출간 도서와 샘플 본문을 한국어로 확인하세요.",
    sectionTitle: "출간 도서"
  },
  en: {
    subtitle: "Explore books and sample chapters in English.",
    sectionTitle: "Published Books"
  }
};

const koButton = document.getElementById("lang-ko");
const enButton = document.getElementById("lang-en");
const siteSubtitle = document.getElementById("site-subtitle");
const sectionTitle = document.getElementById("section-title");
const bookGrid = document.getElementById("book-grid");

function renderBooks(lang) {
  bookGrid.innerHTML = "";

  booksData.forEach((book) => {
    const data = book[lang];

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
  const selected = pageText[lang] || pageText.ko;

  document.documentElement.lang = lang;
  siteSubtitle.textContent = selected.subtitle;
  sectionTitle.textContent = selected.sectionTitle;

  koButton.classList.toggle("active", lang === "ko");
  enButton.classList.toggle("active", lang === "en");

  localStorage.setItem("siteLanguage", lang);
  renderBooks(lang);
}

koButton.addEventListener("click", function () {
  setLanguage("ko");
});

enButton.addEventListener("click", function () {
  setLanguage("en");
});

const savedLanguage = localStorage.getItem("siteLanguage");
const browserLanguage = navigator.language || navigator.userLanguage;
const initialLanguage =
  savedLanguage ||
  (browserLanguage && browserLanguage.toLowerCase().startsWith("ko") ? "ko" : "en");

setLanguage(initialLanguage);