function togglePreview(btn) {
  const businessId = btn.dataset.biz;
  const container = document.getElementById("preview-" + businessId);
  const iframe = document.getElementById("iframe-" + businessId);
  const loading = document.getElementById("loading-" + businessId);
  const status = document.getElementById("status-" + businessId);
  const previewUrl = btn.dataset.previewUrl || iframe.dataset.previewUrl;

  // Toggle visibility
  const opening = container.style.display !== "block";
  container.style.display = opening ? "block" : "none";

  // Update button text
  btn.textContent = opening ? "Hide PDF" : "Show PDF";

  if (opening) {
    iframe.classList.remove("loaded");
    status.style.display = "none";
    loading.style.display = "block";

    // Lazy load only the first time
    if (iframe.src === "about:blank") {
      iframe.src = previewUrl;
      setupPreviewTimeout(iframe);
    } else {
      // already loaded once — just show it again
      setTimeout(() => {
        loading.style.display = "none";
        iframe.classList.add("loaded");
      }, 500);
    }
  }
}

function onIframeLoad(iframe) {
  const businessId = iframe.id.replace("iframe-", "");
  const loading = document.getElementById("loading-" + businessId);

  // Smooth fade in
  setTimeout(() => {
    loading.style.display = "none";
    iframe.classList.add("loaded");
  }, 500);
}

function onIframeError(iframe) {
  const businessId = iframe.id.replace("iframe-", "");
  const loading = document.getElementById("loading-" + businessId);
  const status = document.getElementById("status-" + businessId);

  loading.style.display = "none";
  status.textContent =
    "Failed to load PDF preview. Please try downloading the PDF instead.";
  status.className = "preview-status error";
  status.style.display = "block";
}

function setupPreviewTimeout(iframe, timeoutMs = 10000) {
  const businessId = iframe.id.replace("iframe-", "");

  setTimeout(() => {
    const currentIframe = document.getElementById("iframe-" + businessId);
    const loading = document.getElementById("loading-" + businessId);
    const status = document.getElementById("status-" + businessId);

    if (
      loading.style.display !== "none" &&
      !currentIframe.classList.contains("loaded")
    ) {
      loading.style.display = "none";
      status.textContent =
        "Preview loading is taking longer than expected. The PDF might be large or slow to load.";
      status.className = "preview-status info";
      status.style.display = "block";
    }
  }, timeoutMs);
}
