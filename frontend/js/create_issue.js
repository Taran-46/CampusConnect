/**
 * CampusConnect - Create Issue Form Submission Handler
 */

document.addEventListener("DOMContentLoaded", () => {
  // Ensure student is authenticated
  if (!auth.requireAuth()) return;

  const issueForm = document.getElementById("create-issue-form");
  const titleInput = document.getElementById("issue-title");
  const categorySelect = document.getElementById("issue-category");
  const descTextarea = document.getElementById("issue-description");
  const charCounter = document.getElementById("char-counter");
  const submitBtn = document.getElementById("submit-issue-btn");

  if (!issueForm) return;

  // Simple Character Counter for Viva demonstration
  if (descTextarea && charCounter) {
    descTextarea.addEventListener("input", () => {
      const currentLength = descTextarea.value.length;
      charCounter.textContent = `${currentLength} / 3000`;
      if (currentLength > 2900) {
        charCounter.style.color = "var(--danger-500, #ef4444)";
      } else {
        charCounter.style.color = "var(--slate-500)";
      }
    });
  }

  issueForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const title = titleInput.value.trim();
    const category = categorySelect.value;
    const description = descTextarea.value.trim();

    // Client-side validations
    if (!title || !category || !description) {
      showToast("Please fill in all required fields.", "error");
      return;
    }

    if (title.length < 3) {
      showToast("Title must be at least 3 characters long.", "error");
      titleInput.focus();
      return;
    }

    if (description.length < 5) {
      showToast("Description must be at least 5 characters long.", "error");
      descTextarea.focus();
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting Issue...";

    try {
      const created = await api.createIssue({
        title,
        category,
        description,
      });

      showToast("Issue submitted successfully!", "success");
      setTimeout(() => {
        // Redirect to detail page of the new issue
        window.location.href = `issue-detail.html?id=${created.id}`;
      }, 700);
    } catch (err) {
      showToast(err.message || "Failed to submit issue. Please try again.", "error");
      submitBtn.disabled = false;
      submitBtn.textContent = "Submit Issue";
    }
  });
});
