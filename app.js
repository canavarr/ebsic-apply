(function () {
  const url = ((window.EBSIC_CONFIG || {}).formUrl || "").trim();
  if (!url) return;
  document.querySelectorAll(".js-apply").forEach((link) => {
    link.href = url;
    link.target = "_blank";
    link.rel = "noreferrer";
  });
})();
