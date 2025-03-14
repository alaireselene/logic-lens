// Elements
const loadingEl = document.getElementById("loading");
const errorEl = document.getElementById("error");
const errorMessageEl = document.getElementById("error-message");
const resultsEl = document.getElementById("results");
const totalScoreEl = document.getElementById("total-score");
const sentimentBadgeEl = document.getElementById("sentiment-badge");
const criteriaListEl = document.getElementById("criteria-list");

// State management
let currentText = "";

// Show/hide UI states
function showLoading() {
  loadingEl.classList.remove("hidden");
  errorEl.classList.add("hidden");
  resultsEl.classList.add("hidden");
}

function showError(message) {
  loadingEl.classList.add("hidden");
  errorEl.classList.remove("hidden");
  resultsEl.classList.add("hidden");
  errorMessageEl.textContent = message;
}

function showResults() {
  loadingEl.classList.add("hidden");
  errorEl.classList.add("hidden");
  resultsEl.classList.remove("hidden");
}

// Create result card for a criterion
function createCriterionCard(criterion) {
  const resultClass =
    criterion.result === "Đúng"
      ? "result-true"
      : criterion.result === "Sai"
      ? "result-false"
      : "result-review";

  const card = document.createElement("div");
  card.className = "criterion-card";
  card.innerHTML = `
        <div class="criterion-header">
            <span class="criterion-name">${criterion.name}</span>
            <div class="flex items-center gap-2">
                <span class="criterion-result ${resultClass}">${criterion.result}</span>
                <span class="criterion-points">${criterion.points} điểm</span>
            </div>
        </div>
        <p class="text-gray-600">${criterion.explanation}</p>
    `;
  return card;
}

// Update UI with fact check results
function updateResults(data) {
  // Calculate total score
  const totalScore = data.criteria.reduce(
    (sum, criterion) => sum + criterion.points,
    0
  );
  totalScoreEl.textContent = `${totalScore}/20`;

  // Set sentiment badge
  const sentimentClass =
    data.sentiment === "Tiêu cực"
      ? "sentiment-negative"
      : data.sentiment === "Tích cực"
      ? "sentiment-positive"
      : "sentiment-neutral";
  sentimentBadgeEl.className = `sentiment-badge ${sentimentClass}`;
  sentimentBadgeEl.textContent = data.sentiment;

  // Clear and update criteria list
  criteriaListEl.innerHTML = "";
  data.criteria.forEach((criterion) => {
    criteriaListEl.appendChild(createCriterionCard(criterion));
  });

  showResults();
}

// Handle fact checking
async function checkFacts(text) {
  if (!text || text.length < 10) {
    showError("Vui lòng chọn đoạn văn bản dài hơn để phân tích.");
    return;
  }

  showLoading();

  try {
    const response = await fetch("http://localhost:8000/api/fact-check", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    const data = await response.json();
    updateResults(data);
  } catch (error) {
    console.error("Error:", error);
    showError("Có lỗi xảy ra khi phân tích văn bản. Vui lòng thử lại sau.");
  }
}

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "checkText") {
    currentText = request.text;
    checkFacts(currentText);
  }
});

// On popup load, check for stored text
document.addEventListener("DOMContentLoaded", () => {
  chrome.storage.local.get(["selectedText"], function (result) {
    if (result.selectedText) {
      currentText = result.selectedText;
      checkFacts(currentText);
    } else {
      showError("Vui lòng chọn đoạn văn bản để phân tích.");
    }
  });
});
