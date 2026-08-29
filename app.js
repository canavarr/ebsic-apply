(function () {
  const config = window.EBSIC_CONFIG || {};
  const formUrl = (config.formUrl || "").trim();
  const substackUrl = (config.substackUrl || "").trim().replace(/\/$/, "");

  if (formUrl) {
    document.querySelectorAll(".js-apply").forEach((link) => {
      link.href = formUrl;
      link.target = "_blank";
      link.rel = "noreferrer";
    });
  }

  const form = document.getElementById("newsletter-form");
  if (!form || !substackUrl) return;

  const emailInput = document.getElementById("newsletter-email");
  const honeypot = form.querySelector(".newsletter-honeypot");
  const status = document.getElementById("newsletter-status");
  const subscribeBase = substackUrl + "/subscribe";

  form.action = subscribeBase;

  function showStatus(message, kind) {
    if (!status) return;
    status.hidden = !message;
    status.textContent = message || "";
    if (kind) status.setAttribute("data-kind", kind);
    else status.removeAttribute("data-kind");
  }

  form.addEventListener("submit", (event) => {
    if (honeypot && honeypot.value) {
      event.preventDefault();
      return;
    }

    const email = ((emailInput && emailInput.value) || "").trim();
    if (!email || !emailInput.checkValidity()) {
      event.preventDefault();
      showStatus("Enter a valid email address.", "error");
      if (emailInput) emailInput.focus();
      return;
    }

    event.preventDefault();
    const url = subscribeBase + "?email=" + encodeURIComponent(email);
    window.open(url, "_blank", "noopener,noreferrer");
    showStatus("Confirm the email Substack sends you.", "ok");
    form.reset();
  });
})();
