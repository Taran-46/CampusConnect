/**
 * CampusConnect - Dashboard Controller & Issue Rendering
 */

document.addEventListener("DOMContentLoaded", () => {
  // Ensure student is logged in
  if (!auth.requireAuth()) return;

  const issuesContainer = document.getElementById("issues-container");
  const categoryFilter = document.getElementById("filter-category");
  const statusFilter = document.getElementById("filter-status");
  const searchInput = document.getElementById("filter-search");
  const resetBtn = document.getElementById("filter-reset");

  // Summary Metrics Elements
  const totalCountEl = document.getElementById("stat-total");
  const openCountEl = document.getElementById("stat-open");
  const progressCountEl = document.getElementById("stat-progress");
  const resolvedCountEl = document.getElementById("stat-resolved");

  let allIssues = [];
  let searchTimeout = null;

  /**
   * Format ISO date string into readable local timestamp
   */
  function formatDate(isoString) {
    if (!isoString) return "";
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return isoString;
    }
  }

  /**
   * Helper to construct safe badge CSS class names
   */
  function getCategoryBadgeClass(category) {
    const slug = category.toLowerCase().replace(/[^a-z0-9]/g, "-");
    return `badge-category-${slug}`;
  }

  function getStatusBadgeClass(status) {
    const slug = status.toLowerCase().replace(/\s+/g, "-");
    return `badge-status-${slug}`;
  }

  /**
   * Render issue cards safely into DOM using textContent to prevent XSS
   */
  function renderIssues(issues) {
    issuesContainer.innerHTML = "";

    if (!issues || issues.length === 0) {
      issuesContainer.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">📋</div>
          <h3>No Issues Found</h3>
          <p>No campus issues match your current filter criteria. Try adjusting your filters or report a new issue.</p>
          <a href="create-issue.html" class="btn btn-primary btn-sm">+ Report New Issue</a>
        </div>
      `;
      return;
    }

    issues.forEach((issue) => {
      const card = document.createElement("article");
      card.className = "issue-card";
      card.setAttribute("role", "button");
      card.setAttribute("tabindex", "0");
      card.title = `View details for #${issue.id}: ${issue.title}`;

      // Card Header
      const header = document.createElement("div");
      header.className = "issue-card-header";

      const categoryBadge = document.createElement("span");
      categoryBadge.className = `badge ${getCategoryBadgeClass(issue.category)}`;
      categoryBadge.textContent = issue.category;

      const statusBadge = document.createElement("span");
      statusBadge.className = `badge ${getStatusBadgeClass(issue.status)}`;
      statusBadge.textContent = issue.status;

      header.appendChild(categoryBadge);
      header.appendChild(statusBadge);

      // Card Title
      const title = document.createElement("h3");
      title.className = "issue-card-title";
      title.textContent = issue.title;

      // Card Description
      const desc = document.createElement("p");
      desc.className = "issue-card-desc";
      desc.textContent = issue.description;

      // Card Footer (Submitter & Timestamp)
      const footer = document.createElement("div");
      footer.className = "issue-card-footer";

      const submitterSpan = document.createElement("span");
      submitterSpan.className = "issue-meta-user";
      submitterSpan.textContent = `👤 ${issue.submitted_by_name || "Student"}`;
      if (issue.submitted_by_department) {
        submitterSpan.title = issue.submitted_by_department;
      }

      const dateSpan = document.createElement("span");
      dateSpan.className = "issue-meta-date";
      dateSpan.textContent = formatDate(issue.created_at);

      footer.appendChild(submitterSpan);
      footer.appendChild(dateSpan);

      // Assemble Card
      card.appendChild(header);
      card.appendChild(title);
      card.appendChild(desc);
      card.appendChild(footer);

      // Card Click & Keyboard Navigation
      const navigateToDetail = () => {
        window.location.href = `issue-detail.html?id=${issue.id}`;
      };
      card.addEventListener("click", navigateToDetail);
      card.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          navigateToDetail();
        }
      });

      issuesContainer.appendChild(card);
    });
  }

  /**
   * Update Summary Statistics Counters
   */
  function updateStatistics(issues) {
    if (!totalCountEl) return;

    let total = issues.length;
    let open = 0;
    let inProgress = 0;
    let resolved = 0;

    issues.forEach((i) => {
      if (i.status === "Open") open++;
      else if (i.status === "In Progress") inProgress++;
      else if (i.status === "Resolved") resolved++;
    });

    totalCountEl.textContent = total;
    openCountEl.textContent = open;
    progressCountEl.textContent = inProgress;
    resolvedCountEl.textContent = resolved;
  }

  /**
   * Fetch issues from API based on active UI filter selections
   */
  async function loadIssues() {
    issuesContainer.innerHTML = `
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>Loading campus issues...</p>
      </div>
    `;

    try {
      const filters = {
        category: categoryFilter.value || undefined,
        status: statusFilter.value || undefined,
        search: searchInput.value.trim() || undefined,
      };

      const issues = await api.getIssues(filters);
      allIssues = issues;

      // Update metrics based on initial full fetch or current filtered set
      if (!categoryFilter.value && !statusFilter.value && !searchInput.value.trim()) {
        updateStatistics(issues);
      }

      renderIssues(issues);
    } catch (err) {
      issuesContainer.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">⚠️</div>
          <h3>Failed to Load Issues</h3>
          <p>${err.message || "Please make sure the backend server is running at http://127.0.0.1:8000"}</p>
          <button id="retry-btn" class="btn btn-outline btn-sm">Try Again</button>
        </div>
      `;
      const retryBtn = document.getElementById("retry-btn");
      if (retryBtn) retryBtn.addEventListener("click", loadIssues);
    }
  }

  // Event Listeners for Filters
  if (categoryFilter) {
    categoryFilter.addEventListener("change", loadIssues);
  }

  if (statusFilter) {
    statusFilter.addEventListener("change", loadIssues);
  }

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(loadIssues, 300);
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener("click", () => {
      categoryFilter.value = "";
      statusFilter.value = "";
      searchInput.value = "";
      loadIssues();
    });
  }

  // Initial Load
  loadIssues();
});
