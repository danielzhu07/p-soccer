(function () {
  const form = document.getElementById("upload-form");
  const fileInput = document.getElementById("file-input");
  const fileNameEl = document.getElementById("file-name");
  const submitBtn = document.getElementById("submit-btn");
  const statusSection = document.getElementById("status-section");
  const statusText = document.getElementById("status-text");
  const resultSection = document.getElementById("result-section");
  const statsDisplay = document.getElementById("stats-display");
  const downloadLink = document.getElementById("download-link");
  const errorSection = document.getElementById("error-section");
  const errorText = document.getElementById("error-text");

  fileInput.addEventListener("change", function () {
    const file = fileInput.files[0];
    fileNameEl.textContent = file ? file.name : "No file chosen";
    submitBtn.disabled = !file;
  });

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    const file = fileInput.files[0];
    if (!file) return;

    resultSection.classList.add("hidden");
    errorSection.classList.add("hidden");
    statusSection.classList.remove("hidden");
    statusText.textContent = "Uploading…";
    submitBtn.disabled = true;

    const formData = new FormData();
    formData.append("file", file);

    let jobId;
    try {
      const res = await fetch("/jobs", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "Upload failed");
      }
      const data = await res.json();
      jobId = data.job_id;
    } catch (err) {
      statusSection.classList.add("hidden");
      errorText.textContent = err.message || "Upload failed";
      errorSection.classList.remove("hidden");
      submitBtn.disabled = false;
      return;
    }

    statusText.textContent = "Processing…";
    pollJob(jobId);
  });

  function pollJob(jobId) {
    const interval = setInterval(async () => {
      try {
        const res = await fetch("/jobs/" + jobId);
        if (!res.ok) return;
        const job = await res.json();

        if (job.status === "completed") {
          clearInterval(interval);
          statusSection.classList.add("hidden");
          statsDisplay.textContent = JSON.stringify(job.stats || {}, null, 2);
          downloadLink.href = "/jobs/" + jobId + "/video";
          downloadLink.download = "p-soccer-" + jobId.slice(0, 8) + ".mp4";
          resultSection.classList.remove("hidden");
          submitBtn.disabled = false;
          return;
        }

        if (job.status === "failed") {
          clearInterval(interval);
          statusSection.classList.add("hidden");
          errorText.textContent = job.error || "Processing failed";
          errorSection.classList.remove("hidden");
          submitBtn.disabled = false;
        }
      } catch (_) {
        // keep polling
      }
    }, 1500);
  }
})();
