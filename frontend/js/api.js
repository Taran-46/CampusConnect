/**
 * CampusConnect - Central API Service & Fetch Utility
 */

const API_BASE_URL = (function () {
  // If hosted on FastAPI itself (port 8000), use relative path, otherwise point to default backend port
  if (window.location.origin.includes(":8000")) {
    return "/api";
  }
  return "http://127.0.0.1:8000/api";
})();

/**
 * Toast Notification System
 * Displays temporary alert messages on the top right
 */
function showToast(message, type = "info") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  const iconSpan = document.createElement("span");
  if (type === "success") iconSpan.textContent = "✓";
  else if (type === "error") iconSpan.textContent = "✕";
  else iconSpan.textContent = "ℹ";

  const msgSpan = document.createElement("span");
  msgSpan.textContent = message;

  toast.appendChild(iconSpan);
  toast.appendChild(msgSpan);
  container.appendChild(toast);

  // Auto remove after 3.5 seconds
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 250);
  }, 3500);
}

/**
 * Core HTTP Request Wrapper
 */
async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    "Accept": "application/json",
    ...options.headers,
  };

  // Attach JWT Bearer token if student is authenticated
  const token = localStorage.getItem("cc_auth_token");
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Ensure Content-Type is set for JSON payloads
  if (options.body && typeof options.body === "string" && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle 401 Unauthorized (expired or invalid token)
    if (response.status === 401) {
      // Clear token only if we're not attempting to login
      if (!endpoint.includes("/login")) {
        localStorage.removeItem("cc_auth_token");
        localStorage.removeItem("cc_auth_user");
        if (!window.location.pathname.endsWith("index.html") && window.location.pathname !== "/") {
          window.location.href = "index.html?session_expired=1";
          return;
        }
      }
    }

    const contentType = response.headers.get("content-type");
    let data = null;
    if (contentType && contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      let errorMessage = "An unexpected error occurred.";
      if (data && typeof data === "object") {
        if (data.detail) {
          if (Array.isArray(data.detail)) {
            // Pydantic validation error array
            errorMessage = data.detail.map((err) => `${err.loc ? err.loc.join(" -> ") : ""}: ${err.msg}`).join("; ");
          } else {
            errorMessage = data.detail;
          }
        } else if (data.message) {
          errorMessage = data.message;
        }
      } else if (typeof data === "string" && data.trim()) {
        errorMessage = data;
      }
      throw new Error(errorMessage);
    }

    return data;
  } catch (error) {
    console.error(`API Fetch Error [${options.method || "GET"} ${endpoint}]:`, error);
    throw error;
  }
}

/**
 * High-Level API Module
 */
const api = {
  // Auth API
  async register(userData) {
    return await apiFetch("/register", {
      method: "POST",
      body: JSON.stringify(userData),
    });
  },

  async login(credentials) {
    return await apiFetch("/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
  },

  async getMe() {
    return await apiFetch("/me", {
      method: "GET",
    });
  },

  // Issues API
  async getIssues(filters = {}) {
    const queryParams = new URLSearchParams();
    if (filters.category) queryParams.append("category", filters.category);
    if (filters.status) queryParams.append("status", filters.status);
    if (filters.userId) queryParams.append("user_id", filters.userId);
    if (filters.search) queryParams.append("search", filters.search);

    const qs = queryParams.toString();
    const endpoint = `/issues${qs ? `?${qs}` : ""}`;
    return await apiFetch(endpoint, {
      method: "GET",
    });
  },

  async getIssue(id) {
    return await apiFetch(`/issues/${id}`, {
      method: "GET",
    });
  },

  async createIssue(issueData) {
    return await apiFetch("/issues", {
      method: "POST",
      body: JSON.stringify(issueData),
    });
  },

  async updateIssueStatus(id, newStatus) {
    return await apiFetch(`/issues/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status: newStatus }),
    });
  },

  async deleteIssue(id) {
    return await apiFetch(`/issues/${id}`, {
      method: "DELETE",
    });
  },
};

// Make accessible globally
window.api = api;
window.showToast = showToast;
