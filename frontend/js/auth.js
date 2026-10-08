/**
 * CampusConnect - Authentication State & Session Management
 */

const AUTH_TOKEN_KEY = "cc_auth_token";
const AUTH_USER_KEY = "cc_auth_user";

const auth = {
  getToken() {
    return localStorage.getItem(AUTH_TOKEN_KEY);
  },

  setToken(token) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
  },

  getCurrentUser() {
    const raw = localStorage.getItem(AUTH_USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  },

  setCurrentUser(user) {
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
  },

  isAuthenticated() {
    return Boolean(this.getToken());
  },

  clearAuth() {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
  },

  logout() {
    this.clearAuth();
    showToast("You have been logged out successfully.", "info");
    setTimeout(() => {
      window.location.href = "index.html";
    }, 400);
  },

  requireAuth() {
    if (!this.isAuthenticated()) {
      window.location.href = "index.html";
      return false;
    }
    return true;
  },

  redirectIfAuthenticated() {
    if (this.isAuthenticated()) {
      window.location.href = "dashboard.html";
      return true;
    }
    return false;
  },

  /**
   * Initializes header/navbar user details if logged in
   */
  initNav() {
    const user = this.getCurrentUser();
    const navUserContainer = document.getElementById("nav-user-container");
    if (!navUserContainer) return;

    if (user && this.isAuthenticated()) {
      const initial = user.full_name ? user.full_name.charAt(0).toUpperCase() : "U";

      navUserContainer.innerHTML = `
        <div class="user-badge" title="${user.department || ""}">
          <span class="user-avatar-circle">${initial}</span>
          <span class="user-name">${user.full_name}</span>
        </div>
        <button id="logout-btn" class="btn btn-outline btn-sm" title="Log out of your account">
          Log Out
        </button>
      `;

      const logoutBtn = document.getElementById("logout-btn");
      if (logoutBtn) {
        logoutBtn.addEventListener("click", () => auth.logout());
      }
    } else {
      navUserContainer.innerHTML = `
        <a href="index.html" class="btn btn-primary btn-sm">Sign In</a>
      `;
    }
  },
};

// Handle Authentication Page (index.html) logic
document.addEventListener("DOMContentLoaded", () => {
  // Check if session expired query param is present
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("session_expired")) {
    showToast("Your session expired. Please log in again.", "info");
  }

  // Setup Navbar if present
  auth.initNav();

  // If on index.html login/register page
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const tabLoginBtn = document.getElementById("tab-login");
  const tabRegisterBtn = document.getElementById("tab-register");

  if (loginForm && registerForm) {
    // If student is already logged in, redirect them to dashboard
    if (auth.isAuthenticated()) {
      window.location.href = "dashboard.html";
      return;
    }

    // Tab switching
    if (tabLoginBtn && tabRegisterBtn) {
      tabLoginBtn.addEventListener("click", () => {
        tabLoginBtn.classList.add("active");
        tabRegisterBtn.classList.remove("active");
        loginForm.style.display = "block";
        registerForm.style.display = "none";
      });

      tabRegisterBtn.addEventListener("click", () => {
        tabRegisterBtn.classList.add("active");
        tabLoginBtn.classList.remove("active");
        registerForm.style.display = "block";
        loginForm.style.display = "none";
      });
    }

    // Login Form Submit
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = document.getElementById("login-email").value.trim();
      const password = document.getElementById("login-password").value;
      const submitBtn = document.getElementById("login-submit-btn");

      if (!email || !password) {
        showToast("Please enter both email and password.", "error");
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = "Signing In...";

      try {
        const response = await api.login({ email, password });
        auth.setToken(response.access_token);
        auth.setCurrentUser(response.user);

        showToast(`Welcome back, ${response.user.full_name}!`, "success");
        setTimeout(() => {
          window.location.href = "dashboard.html";
        }, 600);
      } catch (err) {
        showToast(err.message || "Failed to log in. Please check your credentials.", "error");
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Sign In";
      }
    });

    // Register Form Submit
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fullName = document.getElementById("reg-name").value.trim();
      const email = document.getElementById("reg-email").value.trim();
      const department = document.getElementById("reg-dept").value.trim();
      const password = document.getElementById("reg-password").value;
      const submitBtn = document.getElementById("reg-submit-btn");

      if (!fullName || !email || !department || !password) {
        showToast("All fields are required.", "error");
        return;
      }

      if (password.length < 6) {
        showToast("Password must be at least 6 characters long.", "error");
        return;
      }

      submitBtn.disabled = true;
      submitBtn.textContent = "Creating Account...";

      try {
        const response = await api.register({
          full_name: fullName,
          email,
          department,
          password,
        });

        auth.setToken(response.access_token);
        auth.setCurrentUser(response.user);

        showToast("Account created successfully! Redirecting...", "success");
        setTimeout(() => {
          window.location.href = "dashboard.html";
        }, 700);
      } catch (err) {
        showToast(err.message || "Registration failed. Please try again.", "error");
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Create Account";
      }
    });
  }
});

// Make accessible globally
window.auth = auth;
