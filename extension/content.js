// Store selected text
let selectedText = "";

// Handle text selection
document.addEventListener("mouseup", () => {
  const text = window.getSelection().toString().trim();
  if (text.length >= 10) {
    // Only store if text is long enough
    selectedText = text;
    chrome.storage.local.set({ selectedText: text });
  }
});

// Clear stored text when clicking outside
document.addEventListener("mousedown", (e) => {
  if (e.target.tagName !== "INPUT" && e.target.tagName !== "TEXTAREA") {
    chrome.storage.local.remove(["selectedText"]);
  }
});

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getSelection") {
    sendResponse({ text: selectedText });
  }
  return true;
});
