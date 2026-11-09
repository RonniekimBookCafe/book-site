/* Ronnie Kim Books — 1:1 문의 (v1.25).
   Sends the form to the Google Apps Script web app in contact-config.js. The script e-mails the author;
   the author's "Reply" goes to the reader. Fields: see the form in /ko|en/contact/index.html. */
(function () {
  var body = document.body;
  var lang = body.getAttribute("data-lang") === "en" ? "en" : "ko";
  var cfg = window.contactConfig || {};
  var endpoint = (cfg.endpoint || "").trim();
  var started = Date.now();
  var $ = function (id) { return document.getElementById(id); };
  var form = $("contact-form");

  var T = {
    ko: {
      notReady: "문의 접수를 준비하고 있습니다. 곧 이 페이지에서 바로 보낼 수 있습니다.",
      sending: "보내는 중…",
      send: "문의 보내기",
      fix: "입력 내용을 확인해 주세요.",
      tooFast: "조금 천천히 작성한 뒤 다시 보내 주세요.",
      rate: "방금 문의를 보내셨습니다. 1분 뒤에 다시 보내 주세요.",
      quota: "오늘 받을 수 있는 문의가 가득 찼습니다. 내일 다시 보내 주세요.",
      server: "전송 중 문제가 생겼습니다. 잠시 뒤 다시 보내 주세요.",
      network: "인터넷 연결을 확인한 뒤 다시 보내 주세요.",
      doneTitle: "문의가 접수되었습니다",
      doneBody: function (email) { return "저자가 확인한 뒤 " + email + " 로 답장을 보내 드립니다. 답장이 보이지 않으면 스팸함도 확인해 주세요."; },
      doneId: "접수 번호",
      doneUnconfirmed: "전송했습니다. 이 브라우저에서는 접수 확인을 받지 못했으니, 며칠 안에 답장이 없으면 다시 보내 주세요.",
      again: "다른 문의 보내기",
      count: function (n) { return n.toLocaleString("ko-KR") + " / 3,000"; }
    },
    en: {
      notReady: "The contact form is being set up. You will be able to send messages from this page soon.",
      sending: "Sending…",
      send: "Send message",
      fix: "Please check the highlighted fields.",
      tooFast: "Please take a moment and send it again.",
      rate: "You just sent a message. Please wait a minute before sending another.",
      quota: "Today's message limit has been reached. Please try again tomorrow.",
      server: "Something went wrong while sending. Please try again shortly.",
      network: "Check your internet connection and try again.",
      doneTitle: "Your message has been sent",
      doneBody: function (email) { return "The author will reply to " + email + ". If you don't see it, check your spam folder."; },
      doneId: "Reference",
      doneUnconfirmed: "Sent. This browser could not confirm receipt, so if you don't hear back in a few days, please send it again.",
      again: "Send another message",
      count: function (n) { return n.toLocaleString("en-US") + " / 3,000"; }
    }
  }[lang];

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  /* books select */
  var books = (window.booksData || []).filter(function (b) { return b[lang]; });
  books.sort(function (a, b) {
    var ua = a.status === "upcoming", ub = b.status === "upcoming";
    if (ua !== ub) return ua ? 1 : -1;
    if (a.series && b.series && a.seriesOrder && b.seriesOrder && ua) return a.seriesOrder - b.seriesOrder;
    return (b.publishedAt || "").localeCompare(a.publishedAt || "");
  });
  function bookLabel(b) {
    var title = b[lang].title;
    if (b.seriesCode && title.indexOf(b.seriesCode) === -1) return b.seriesCode + " · " + title;
    return title;
  }
  var bookSel = $("f-book");
  books.forEach(function (b) {
    var o = document.createElement("option");
    o.value = b.id;
    o.textContent = bookLabel(b);
    bookSel.appendChild(o);
  });

  /* prefill from the URL: ?book=book-008&type=practice */
  var qs = new URLSearchParams(location.search);
  if (qs.get("book") && books.some(function (b) { return b.id === qs.get("book"); })) bookSel.value = qs.get("book");
  if (qs.get("type")) $("f-type").value = qs.get("type");

  /* practice setup fields appear for code/file issues */
  function toggleEnv() {
    $("env").hidden = $("f-type").value !== "practice";
  }
  $("f-type").addEventListener("change", toggleEnv);
  toggleEnv();

  /* character counter */
  function count() {
    $("f-count").textContent = T.count($("f-message").value.length);
  }
  $("f-message").addEventListener("input", count);
  count();

  $("retention").textContent = (cfg.retention && cfg.retention[lang]) || (lang === "ko" ? "답변 완료 후 1년" : "one year after the reply");

  /* not configured yet */
  var notice = $("form-notice");
  function showNotice(msg, kind) {
    notice.textContent = msg;
    notice.className = "form-notice" + (kind ? " is-" + kind : "");
    notice.hidden = !msg;
  }
  if (!endpoint) {
    showNotice(T.notReady, "info");
    $("f-submit").disabled = true;
  }

  /* validation */
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  function check() {
    var bad = [];
    var rules = {
      type: !!$("f-type").value,
      name: !!$("f-name").value.trim(),
      email: EMAIL_RE.test($("f-email").value.trim()),
      subject: !!$("f-subject").value.trim(),
      message: $("f-message").value.trim().length >= 5,
      consent: $("f-consent").checked
    };
    Object.keys(rules).forEach(function (k) {
      var ok = rules[k];
      var input = $("f-" + k);
      $("e-" + k).hidden = ok;
      input.setAttribute("aria-invalid", ok ? "false" : "true");
      if (!ok) bad.push(input);
    });
    return bad;
  }

  function payload() {
    var b = books.filter(function (x) { return x.id === bookSel.value; })[0];
    return {
      type: $("f-type").value,
      bookId: b ? b.id : "",
      bookCode: b && b.seriesCode ? b.seriesCode : "",
      book: b ? bookLabel(b) : "",
      name: $("f-name").value.trim(),
      email: $("f-email").value.trim(),
      subject: $("f-subject").value.trim(),
      message: $("f-message").value.trim(),
      envVersion: $("env").hidden ? "" : $("f-ver").value.trim(),
      envChapter: $("env").hidden ? "" : $("f-ch").value.trim(),
      envOs: $("env").hidden ? "" : $("f-os").value.trim(),
      envLog: $("env").hidden ? "" : $("f-log").value.trim(),
      consent: $("f-consent").checked,
      website: $("f-website").value,
      started: started,
      lang: lang,
      page: location.pathname
    };
  }

  function showSent(data, id, confirmed) {
    form.hidden = true;
    document.querySelector(".contact-aside").hidden = true;
    var box = $("sent");
    box.innerHTML = '<h2>' + T.doneTitle + "</h2>" +
      "<p>" + esc(confirmed ? T.doneBody(data.email) : T.doneUnconfirmed) + "</p>" +
      (id ? '<p class="sent-id">' + T.doneId + ": <strong>" + esc(id) + "</strong></p>" : "") +
      '<dl><dt>' + esc(document.querySelector('label[for="f-subject"]').firstChild.textContent.trim()) + "</dt><dd>" + esc(data.subject) + "</dd></dl>" +
      '<button type="button" class="btn is-ghost" id="again">' + T.again + "</button>";
    box.hidden = false;
    box.focus();
    $("again").addEventListener("click", function () {
      form.reset();
      bookSel.value = qs.get("book") || "";
      toggleEnv();
      count();
      started = Date.now();
      box.hidden = true;
      form.hidden = false;
      document.querySelector(".contact-aside").hidden = false;
      showNotice("");
      $("f-type").focus();
    });
  }

  function errorMessage(code) {
    return { too_fast: T.tooFast, rate_limited: T.rate, quota: T.quota, invalid: T.fix }[code] || T.server;
  }

  function setBusy(busy) {
    $("f-submit").disabled = busy;
    $("f-submit").textContent = busy ? T.sending : T.send;
    form.setAttribute("aria-busy", busy ? "true" : "false");
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!endpoint) return;
    var bad = check();
    if (bad.length) {
      showNotice(T.fix, "error");
      bad[0].focus();
      return;
    }
    var data = payload();
    showNotice("");
    setBusy(true);
    // text/plain avoids a CORS preflight, which Apps Script web apps do not answer.
    fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "text/plain;charset=utf-8" },
      body: JSON.stringify(data),
      redirect: "follow"
    })
      .then(function (res) { return res.json(); })
      .then(function (r) {
        setBusy(false);
        if (r && r.ok) {
          showSent(data, r.id === "IGNORED" ? "" : r.id, true);
        } else {
          showNotice(errorMessage(r && r.code), "error");
          if (r && r.code === "invalid" && r.field && $("f-" + r.field)) $("f-" + r.field).focus();
        }
      })
      .catch(function () {
        // Some browsers block reading the reply across origins. Send once more without reading it;
        // the script still receives it, but the page cannot confirm.
        fetch(endpoint, { method: "POST", mode: "no-cors", headers: { "Content-Type": "text/plain;charset=utf-8" }, body: JSON.stringify(data) })
          .then(function () {
            setBusy(false);
            showSent(data, "", false);
          })
          .catch(function () {
            setBusy(false);
            showNotice(T.network, "error");
          });
      });
  });

  /* clear a field's error as soon as it is fixed */
  ["type", "name", "email", "subject", "message", "consent"].forEach(function (k) {
    var el = $("f-" + k);
    el.addEventListener(k === "consent" || k === "type" ? "change" : "input", function () {
      if (el.getAttribute("aria-invalid") === "true") check();
    });
  });
})();
