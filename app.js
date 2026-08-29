(function () {
  const config = window.EBSIC_CONFIG || {};
  const formUrl = (config.formUrl || "").trim();
  const supabaseUrl = (config.supabaseUrl || "").trim().replace(/\/$/, "");
  const supabaseAnonKey = (config.supabaseAnonKey || "").trim();

  const registerUrl = (config.eventRegisterUrl || "").trim();

  if (formUrl) {
    document.querySelectorAll(".js-apply").forEach((link) => {
      link.href = formUrl;
      link.target = "_blank";
      link.rel = "noreferrer";
    });
  }

  if (registerUrl) {
    document.querySelectorAll(".js-register").forEach((link) => {
      link.href = registerUrl;
      link.target = "_blank";
      link.rel = "noreferrer";
    });
  }

  const topbar = document.querySelector(".topbar");
  const navToggle = document.querySelector(".nav-toggle");
  if (topbar && navToggle) {
    navToggle.addEventListener("click", () => {
      const open = topbar.classList.toggle("nav-open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  const form = document.getElementById("newsletter-form");
  if (!form) return;

  const emailInput = document.getElementById("newsletter-email");
  const honeypot = form.querySelector(".newsletter-honeypot");
  const status = document.getElementById("newsletter-status");
  const submitBtn = form.querySelector(".newsletter-join");

  function showStatus(message, kind) {
    if (!status) return;
    status.hidden = !message;
    status.textContent = message || "";
    if (kind) status.setAttribute("data-kind", kind);
    else status.removeAttribute("data-kind");
  }

  function isDuplicateError(payload, httpStatus) {
    if (httpStatus === 409) return true;
    const code = payload && payload.code;
    return code === "23505";
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (honeypot && honeypot.value) return;

    const email = ((emailInput && emailInput.value) || "").trim().toLowerCase();
    if (!email || !emailInput.checkValidity()) {
      showStatus("Enter a valid email address.", "error");
      if (emailInput) emailInput.focus();
      return;
    }

    if (!supabaseUrl || !supabaseAnonKey) {
      showStatus("Newsletter signup is not configured yet.", "error");
      return;
    }

    if (submitBtn) submitBtn.disabled = true;
    showStatus("Saving…", "ok");

    try {
      const response = await fetch(supabaseUrl + "/rest/v1/newsletter_signups", {
        method: "POST",
        headers: {
          apikey: supabaseAnonKey,
          Authorization: "Bearer " + supabaseAnonKey,
          "Content-Type": "application/json",
          Prefer: "return=minimal",
        },
        body: JSON.stringify({ email: email }),
      });

      let payload = null;
      const text = await response.text();
      if (text) {
        try {
          payload = JSON.parse(text);
        } catch (err) {
          payload = null;
        }
      }

      if (response.ok) {
        showStatus("You’re on the list.", "ok");
        form.reset();
        return;
      }

      if (isDuplicateError(payload, response.status)) {
        showStatus("You’re already on the list.", "ok");
        form.reset();
        return;
      }

      const code = payload && payload.code;
      if (code === "PGRST205") {
        showStatus("List is not set up yet. Run the SQL in the README.", "error");
        return;
      }

      if (response.status === 401 || response.status === 403) {
        showStatus("Subscribe is blocked. Check the table policy in Supabase.", "error");
        return;
      }

      showStatus("Could not subscribe. Try again.", "error");
    } catch (err) {
      showStatus("Could not subscribe. Try again.", "error");
    } finally {
      if (submitBtn) submitBtn.disabled = false;
    }
  });
})();
