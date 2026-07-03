const booksData = [
  {
    id: "book-001",
    category: "career",
    publishedAt: "2026-06-12",
    featured: 1,
    cover: "./assets/images/books/book-001/cover-thumb.webp",

    ko: {
      title: "개발자는 회사를 얼마나 더 오래 다닐 수 있을까요?",
      description: "AI 시대 개발자의 생존 전략과 시장가치 재설계를 다룬 책입니다.",
      link: "./ko/books/book-001/",
      button: "책 보기",
      alt: "개발자는 회사를 얼마나 더 오래 다닐 수 있을까요? 책 표지"
    },

    en: {
      title: "How Long Will Developers Still Be Needed?",
      description: "A practical career survival guide for developers navigating AI, automation, and changing market value.",
      link: "./en/books/book-001/",
      button: "View Book",
      alt: "Book cover of How Long Will Developers Still Be Needed?"
    }
  },

  {
    id: "book-002",
    category: "arduino",
    publishedAt: "2021-02-28",
    featured: 2,
    cover: "./assets/images/books/book-002/cover-thumb.webp",

    ko: {
      title: "모두의 아두이노 환경 센서",
      description:
        "미세먼지, 온습도, 이산화탄소, 자외선, 포름알데히드, 방사선 등 18가지 환경 센서를 아두이노와 함께 실습하며 배우는 실전 입문서입니다.",
      link: "./ko/books/book-002/",
      button: "책 보기",
      alt: "모두의 아두이노 환경 센서 책 표지"
    },

    en: {
      title: "Arduino Environmental Sensors for Everyone",
      description:
        "Learn how to build practical environmental monitoring projects using Arduino and 18 different sensors, including particulate matter, CO₂, UV, temperature, humidity, radiation, and more.",
      link: "./en/books/book-002/",
      button: "View Book",
      alt: "Book cover of Arduino Environmental Sensors for Everyone"
    }
  }
];