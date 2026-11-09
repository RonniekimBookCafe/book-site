/*
 * 1:1 문의 설정 (v1.25)
 *
 * endpoint: Google Apps Script 웹 앱 주소. 「1on1_문의_AppsScript_설치안내.md」 5단계에서 복사한 주소를
 *           따옴표 안에 붙여 넣고, ?v= 값을 올려 다시 배포하세요. 예:
 *           endpoint: "https://script.google.com/macros/s/AKfycb.../exec",
 *           비어 있으면 문의 페이지에 "준비 중" 안내가 나오고 전송 버튼이 꺼집니다.
 * retention: 개인정보 안내에 표시하는 보유 기간 (개인정보 처리방침 페이지와 맞춥니다).
 */
window.contactConfig = {
  endpoint: "https://script.google.com/macros/s/AKfycbyVShOHhHvQ9I37oofl1Dn6VW-1pxVgyyBz_lCEX1JNpR20H5ZX1wR9mMlMPklnFMQT/exec",
  retention: { ko: "답변 완료 후 1년", en: "one year after the reply" }
};
