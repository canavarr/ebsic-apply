(function () {
  const config = window.EBSIC_CONFIG || {};
  const mount = document.getElementById("form-mount");
  const openLink = document.getElementById("form-open-link");
  if (!mount) return;

  const raw = (config.formEmbedUrl || "").trim();

  function toEmbedUrl(url) {
    try {
      const parsed = new URL(url);
      if (!parsed.searchParams.has("embed")) {
        parsed.searchParams.set("embed", "true");
      }
      return parsed.toString();
    } catch (err) {
      return url;
    }
  }

  if (!raw) {
    mount.hidden = false;
    return;
  }

  const src = toEmbedUrl(raw);
  const height = Number(config.formHeight) || 2800;

  mount.replaceChildren();
  mount.hidden = false;
  mount.classList.add("is-live");

  const frame = document.createElement("iframe");
  frame.title = "EBS Investment Club membership application";
  frame.src = src;
  frame.width = "100%";
  frame.height = String(height);
  frame.setAttribute("allowfullscreen", "");
  frame.setAttribute("webkitallowfullscreen", "");
  frame.setAttribute("mozallowfullscreen", "");
  frame.setAttribute("msallowfullscreen", "");
  frame.setAttribute("loading", "lazy");
  mount.appendChild(frame);

  if (openLink) {
    openLink.hidden = false;
    openLink.href = src.replace(/[?&]embed=true/, "") || src;
  }
})();
