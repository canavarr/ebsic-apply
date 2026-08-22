(function () {
  const url = ((window.EBSIC_CONFIG || {}).formUrl || "").trim();
  if (!url) return;
  document.querySelectorAll("[data-apply]").forEach((link) => {
    link.href = url;
  });
})();
