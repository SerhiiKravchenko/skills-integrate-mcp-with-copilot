document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const signupMessage = document.getElementById("signup-message");
  const authMessage = document.getElementById("auth-message");
  const userInfo = document.getElementById("user-info");
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const logoutButton = document.getElementById("logout-button");

  function authHeader() {
    const token = localStorage.getItem("activityToken");
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  function displayMessage(element, text, type = "info") {
    element.textContent = text;
    element.className = type;
    element.classList.remove("hidden");
    setTimeout(() => {
      element.classList.add("hidden");
    }, 5000);
  }

  function updateUserInfo(user) {
    if (user) {
      userInfo.textContent = `Logged in as ${user.name} (${user.role})`;
      userInfo.className = "message info";
      userInfo.classList.remove("hidden");
      logoutButton.classList.remove("hidden");
      loginForm.classList.add("hidden");
      registerForm.classList.add("hidden");
      document.getElementById("email").value = user.email;
      document.getElementById("email").disabled = true;
    } else {
      userInfo.classList.add("hidden");
      logoutButton.classList.add("hidden");
      loginForm.classList.remove("hidden");
      registerForm.classList.remove("hidden");
      document.getElementById("email").disabled = false;
      document.getElementById("email").value = "";
    }
  }

  async function fetchUser() {
    const token = localStorage.getItem("activityToken");
    if (!token) {
      updateUserInfo(null);
      return;
    }

    try {
      const response = await fetch("/users/me", {
        headers: authHeader(),
      });

      if (!response.ok) {
        localStorage.removeItem("activityToken");
        updateUserInfo(null);
        return;
      }

      const user = await response.json();
      updateUserInfo(user);
    } catch (error) {
      console.error("Error checking user session:", error);
      updateUserInfo(null);
    }
  }

  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      activitiesList.innerHTML = "";
      activitySelect.innerHTML = "<option value=\"\">-- Select an activity --</option>";

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) =>
                      `<li><span class="participant-email">${email}</span><button class="delete-btn" data-activity="${name}" data-email="${email}">❌</button></li>`
                  )
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });

      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  async function handleUnregister(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const email = button.getAttribute("data-email");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
          headers: authHeader(),
        }
      );
      const result = await response.json();
      if (response.ok) {
        displayMessage(signupMessage, result.message, "success");
        fetchActivities();
      } else {
        displayMessage(signupMessage, result.detail || "An error occurred", "error");
      }
    } catch (error) {
      displayMessage(signupMessage, "Failed to unregister. Please try again.", "error");
      console.error("Error unregistering:", error);
    }
  }

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = document.getElementById("email").value;
    const activity = activitySelect.value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
          headers: authHeader(),
        }
      );
      const result = await response.json();
      if (response.ok) {
        displayMessage(signupMessage, result.message, "success");
        signupForm.reset();
        fetchActivities();
      } else {
        displayMessage(signupMessage, result.detail || "An error occurred", "error");
      }
    } catch (error) {
      displayMessage(signupMessage, "Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    try {
      const response = await fetch("/users/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });
      const result = await response.json();
      if (response.ok) {
        localStorage.setItem("activityToken", result.access_token);
        updateUserInfo(result.user);
        displayMessage(authMessage, "Login successful", "success");
      } else {
        displayMessage(authMessage, result.detail || "Unable to log in", "error");
      }
    } catch (error) {
      displayMessage(authMessage, "Failed to log in. Please try again.", "error");
      console.error("Login error:", error);
    }
  });

  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const name = document.getElementById("register-name").value;
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;

    try {
      const response = await fetch("/users/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name, email, password }),
      });
      const result = await response.json();
      if (response.ok) {
        displayMessage(authMessage, result.message, "success");
        registerForm.reset();
      } else {
        displayMessage(authMessage, result.detail || "Unable to register", "error");
      }
    } catch (error) {
      displayMessage(authMessage, "Failed to register. Please try again.", "error");
      console.error("Register error:", error);
    }
  });

  logoutButton.addEventListener("click", async () => {
    try {
      const response = await fetch("/users/logout", {
        method: "POST",
        headers: authHeader(),
      });
      if (response.ok) {
        localStorage.removeItem("activityToken");
        updateUserInfo(null);
        displayMessage(authMessage, "Logged out successfully", "info");
      }
    } catch (error) {
      console.error("Logout error:", error);
    }
  });

  fetchUser();
  fetchActivities();
});
