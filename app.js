(function () {
  const config = window.EBSIC_CONFIG || {};
  const form = document.getElementById("apply-form");
  const status = document.getElementById("form-status");
  const success = document.getElementById("form-success");
  const panel = document.getElementById("form-panel");
  if (!form) return;

  const email = (config.submitEmail || "").trim();

  function setStatus(message, kind) {
    if (!status) return;
    status.hidden = !message;
    status.textContent = message || "";
    status.classList.toggle("is-error", kind === "error");
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    setStatus("");

    if (!form.reportValidity()) {
      return;
    }

    const honey = form.querySelector('[name="_honey"]');
    if (honey && honey.value) {
      return;
    }

    if (!email) {
      setStatus(
        "Applications are not connected yet. Add submitEmail in config.js.",
        "error"
      );
      return;
    }

    const consent = form.querySelector('input[name="consent"]:checked');
    if (!consent || consent.value !== "Yes") {
      setStatus("Please consent to being contacted about membership.", "error");
      return;
    }

    const data = new FormData(form);
    const payload = {
      _subject: "EBS Investment Club application — " + (data.get("full_name") || ""),
      _template: "table",
      _captcha: "false",
      "Full name": data.get("full_name"),
      "Study group": data.get("study_group"),
      Email: data.get("email"),
      Phone: data.get("phone"),
      "Programme and year":
        (data.get("programme") || "") +
        (data.get("year") ? ", year " + data.get("year") : ""),
      LinkedIn: data.get("linkedin") || "",
      "How they heard about the club": data.get("heard"),
      "Investing experience": data.get("experience"),
      "Preferred team no. 1": data.get("team_1"),
      "Preferred team no. 2": data.get("team_2"),
      Introduction: data.get("introduction"),
      "Why EBS Investment Club": data.get("why_join"),
      Skillset: data.get("skillset"),
      Consent: data.get("consent"),
    };

    const button = form.querySelector('button[type="submit"]');
    const previous = button ? button.textContent : "";
    if (button) {
      button.disabled = true;
      button.textContent = "Sending…";
    }

    try {
      const response = await fetch(
        "https://formsubmit.co/ajax/" + encodeURIComponent(email),
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify(payload),
        }
      );
      const result = await response.json().catch(() => ({}));
      if (!response.ok || result.success === "false" || result.success === false) {
        throw new Error(result.message || "Could not send the application.");
      }

      form.hidden = true;
      if (panel) panel.classList.add("is-success");
      if (success) {
        success.hidden = false;
        success.focus();
      }
    } catch (err) {
      setStatus(
        err.message ||
          "Something went wrong. Please try again or email the club directly.",
        "error"
      );
    } finally {
      if (button) {
        button.disabled = false;
        button.textContent = previous;
      }
    }
  });
})();
