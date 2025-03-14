// Create context menu item
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "fact-check",
    title: "Kiểm tra thông tin",
    contexts: ["selection"],
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "fact-check" && info.selectionText) {
    // Store the selected text
    chrome.storage.local.set({ selectedText: info.selectionText }, () => {
      // Open popup with stored text
      chrome.windows.create({
        url: "popup.html",
        type: "popup",
        width: 600,
        height: 600,
      });
    });
  }
});

// Handle extension icon clicks
chrome.action.onClicked.addListener((tab) => {
  // Query the active tab for selected text
  chrome.tabs.sendMessage(tab.id, { action: "getSelection" }, (response) => {
    if (chrome.runtime.lastError) {
      console.error(chrome.runtime.lastError);
      return;
    }

    if (response && response.text) {
      // Store the selected text
      chrome.storage.local.set({ selectedText: response.text }, () => {
        // Open popup with stored text
        chrome.windows.create({
          url: "popup.html",
          type: "popup",
          width: 600,
          height: 600,
        });
      });
    } else {
      // Open popup anyway, it will show error if no text is selected
      chrome.windows.create({
        url: "popup.html",
        type: "popup",
        width: 600,
        height: 600,
      });
    }
  });
});
