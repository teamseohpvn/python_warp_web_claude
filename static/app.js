// ==========================================================================
// Claude Studio Hub - Main Application Script with Auth & Rate Limiting
// ==========================================================================

const state = {
  isAuthenticated: false,
  appInitialized: false,
  rateLimitCountdownInterval: null,
  activeCwd: "/root",
  activeTask: null,
  activeTaskId: null,
  taskTimerInterval: null,
  taskStartTime: null,
  eventSource: null,
  terminal: null,
  fitAddon: null,
  terminalWs: null,
  reports: [],
  selectedReport: null,
  showingRawReport: false,
  guides: {},
  activeGuideTool: "seo",
  isGuideOpen: false
};

// ==========================================================================
// 1. Initialization & Auth Lifecycle
// ==========================================================================
document.addEventListener("DOMContentLoaded", async () => {
  setupAuth();
  await checkAuthStatus();
});

async function checkAuthStatus() {
  try {
    const res = await fetch("/api/auth/status");
    const data = await res.json();

    if (data.authenticated) {
      state.isAuthenticated = true;
      hideLoginOverlay();
      if (!state.appInitialized) {
        await initApp();
      }
    } else {
      state.isAuthenticated = false;
      showLoginOverlay();
    }
  } catch (err) {
    console.error("Lỗi kiểm tra trạng thái xác thực:", err);
    showLoginOverlay();
  }
}

async function initApp() {
  state.appInitialized = true;
  setupTabs();
  await loadConfig();
  setupRunner();
  setupTerminal();
  setupReports();
  setupLogs();
  setupGuides();
}

function setupAuth() {
  const loginForm = document.getElementById("login-form");
  const pwdInput = document.getElementById("login-password");
  const togglePwdBtn = document.getElementById("btn-toggle-pwd");
  const logoutBtn = document.getElementById("btn-logout");

  // Toggle Password Visibility
  if (togglePwdBtn && pwdInput) {
    togglePwdBtn.addEventListener("click", () => {
      const isPwd = pwdInput.type === "password";
      pwdInput.type = isPwd ? "text" : "password";
      togglePwdBtn.textContent = isPwd ? "🔒" : "👁️";
    });
  }

  // Handle Login Submit
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const password = pwdInput.value.trim();
      if (!password) return;

      const submitBtn = document.getElementById("btn-submit-login");
      const errorMsg = document.getElementById("login-error-msg");

      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span>Đang xác thực...</span>`;
      errorMsg.style.display = "none";

      try {
        const res = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ password })
        });
        const result = await res.json();

        if (res.ok && result.success) {
          state.isAuthenticated = true;
          hideLoginOverlay();
          pwdInput.value = "";
          errorMsg.style.display = "none";
          if (!state.appInitialized) {
            await initApp();
          } else if (state.terminalWs && state.terminalWs.readyState !== WebSocket.OPEN) {
            connectTerminalWs();
          }
        } else {
          // Handle error (401 or 429)
          const errorDetail = result.detail || result.error || "Mật khẩu không chính xác";
          errorMsg.textContent = errorDetail;
          errorMsg.style.display = "block";

          if (res.status === 429) {
            // Rate limit exceeded: Extract countdown seconds if present
            const match = errorDetail.match(/(\d+)\s*giây/);
            let secondsLeft = match ? parseInt(match[1]) : 60;
            startRateLimitCountdown(secondsLeft);
          } else {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `<span>Mở Khóa Hệ Thống</span>`;
            pwdInput.focus();
            pwdInput.select();
          }
        }
      } catch (err) {
        errorMsg.textContent = "Lỗi kết nối tới máy chủ: " + err.message;
        errorMsg.style.display = "block";
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<span>Mở Khóa Hệ Thống</span>`;
      }
    });
  }

  // Handle Logout
  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      try {
        await fetch("/api/auth/logout", { method: "POST" });
      } catch (e) {}
      state.isAuthenticated = false;
      if (state.terminalWs) {
        try { state.terminalWs.close(); } catch (e) {}
      }
      showLoginOverlay();
    });
  }
}

function startRateLimitCountdown(seconds) {
  const submitBtn = document.getElementById("btn-submit-login");
  const errorMsg = document.getElementById("login-error-msg");

  if (state.rateLimitCountdownInterval) {
    clearInterval(state.rateLimitCountdownInterval);
  }

  submitBtn.disabled = true;

  state.rateLimitCountdownInterval = setInterval(() => {
    seconds--;
    if (seconds <= 0) {
      clearInterval(state.rateLimitCountdownInterval);
      state.rateLimitCountdownInterval = null;
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<span>Mở Khóa Hệ Thống</span>`;
      errorMsg.textContent = "Bạn đã có thể thử nhập lại mật khẩu.";
      errorMsg.style.background = "rgba(16, 185, 129, 0.15)";
      errorMsg.style.borderColor = "rgba(16, 185, 129, 0.4)";
      errorMsg.style.color = "#6EE7B7";
    } else {
      submitBtn.innerHTML = `<span>Bị khóa: Thử lại sau ${seconds}s</span>`;
    }
  }, 1000);
}

function showLoginOverlay() {
  const overlay = document.getElementById("login-overlay");
  if (overlay) {
    overlay.classList.add("active");
    const pwdInput = document.getElementById("login-password");
    if (pwdInput) {
      setTimeout(() => pwdInput.focus(), 150);
    }
  }
}

function hideLoginOverlay() {
  const overlay = document.getElementById("login-overlay");
  if (overlay) {
    overlay.classList.remove("active");
  }
}

// Global fetch wrapper to catch 401 unauthorized
async function authFetch(url, options = {}) {
  const res = await fetch(url, options);
  if (res.status === 401) {
    state.isAuthenticated = false;
    showLoginOverlay();
    throw new Error("Yêu cầu xác thực mật khẩu");
  }
  return res;
}

// ==========================================================================
// 2. Tab Management
// ==========================================================================
function setupTabs() {
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.dataset.tab;
      tabButtons.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");

      // Auto-fit terminal if switching to terminal tab
      if (targetId === "tab-terminal") {
        setTimeout(() => {
          if (state.fitAddon) {
            try {
              state.fitAddon.fit();
              sendTerminalResize();
            } catch (e) {}
          }
        }, 100);
      } else if (targetId === "tab-reports") {
        loadReportsList();
      } else if (targetId === "tab-logs") {
        loadLogsList();
      }
    });
  });
}

// ==========================================================================
// 3. Configuration & Directory Selection
// ==========================================================================
async function loadConfig() {
  try {
    const res = await authFetch("/api/config");
    const data = await res.json();

    const cwdSelect = document.getElementById("cwd-select");
    cwdSelect.innerHTML = "";

    data.projects.forEach(p => {
      const opt = document.createElement("option");
      opt.value = p.path;
      opt.textContent = `${p.name} (${p.path})`;
      if (!p.exists) opt.textContent += " [Mới]";
      cwdSelect.appendChild(opt);
    });

    // Default to /root/site-dau-cong-nghiep if present, else first
    const preferred = data.projects.find(p => p.path.includes("site-dau-cong-nghiep")) || data.projects[0];
    if (preferred) {
      cwdSelect.value = preferred.path;
      state.activeCwd = preferred.path;
      const badge = document.getElementById("cwd-badge");
      badge.textContent = state.activeCwd.split("/").pop() || "Root";
    }

    cwdSelect.addEventListener("change", (e) => {
      state.activeCwd = e.target.value;
      const badge = document.getElementById("cwd-badge");
      badge.textContent = state.activeCwd.split("/").pop() || "Root";
    });

    state.guides = data.guides || {};
    renderPresets(data.presets);
  } catch (err) {
    console.error("Lỗi tải cấu hình:", err);
  }
}

// ==========================================================================
// 4. Presets & Command Runner
// ==========================================================================
function renderPresets(categories) {
  const container = document.getElementById("presets-container");
  container.innerHTML = "";

  categories.forEach(cat => {
    const catBlock = document.createElement("div");
    catBlock.className = "category-block";

    const catTitle = document.createElement("div");
    catTitle.className = "category-title";
    catTitle.innerHTML = `<span>⚡</span> <span>${cat.category}</span>`;
    catBlock.appendChild(catTitle);

    cat.items.forEach(item => {
      const card = document.createElement("div");
      card.className = "preset-card";
      card.dataset.itemId = item.id;

      let argsHtml = "";
      if (item.args && item.args.length > 0) {
        argsHtml = `<div class="preset-args">` + item.args.map(arg => `
          <div class="arg-field">
            <label>${arg.label}:</label>
            <input type="text" data-arg="${arg.name}" value="${arg.default || ''}" placeholder="${arg.placeholder || ''}" />
          </div>
        `).join("") + `</div>`;
      }

      card.innerHTML = `
        <div class="preset-header">
          <div class="preset-title">${item.title}</div>
        </div>
        <div class="preset-desc">${item.desc}</div>
        <div class="preset-cmd-preview"><code>${item.cmd}</code></div>
        ${argsHtml}
        <button class="btn btn-sm btn-primary btn-run-preset" style="width: 100%;">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
          <span>Thực hiện tác vụ</span>
        </button>
      `;

      // Handle Run Preset button
      const runBtn = card.querySelector(".btn-run-preset");
      runBtn.addEventListener("click", () => {
        let finalCmd = item.cmd;
        if (item.args && item.args.length > 0) {
          item.args.forEach(arg => {
            const input = card.querySelector(`input[data-arg="${arg.name}"]`);
            const val = input ? input.value.trim() : (arg.default || "");
            finalCmd = finalCmd.replace(`{${arg.name}}`, val);
          });
        }
        executeTask(finalCmd);
      });

      catBlock.appendChild(card);
    });

    container.appendChild(catBlock);
  });
}

function setupRunner() {
  const customInput = document.getElementById("custom-cmd-input");
  const runCustomBtn = document.getElementById("btn-run-custom");
  const clearBtn = document.getElementById("btn-clear-console");
  const copyBtn = document.getElementById("btn-copy-console");
  const cancelBtn = document.getElementById("btn-cancel-task");

  runCustomBtn.addEventListener("click", () => {
    const cmd = customInput.value.trim();
    if (cmd) executeTask(cmd);
  });

  customInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      const cmd = customInput.value.trim();
      if (cmd) executeTask(cmd);
    }
  });

  clearBtn.addEventListener("click", () => {
    const consoleOutput = document.getElementById("console-output");
    consoleOutput.innerHTML = '<div class="console-placeholder"><p>Màn hình đã xóa. Chọn một tác vụ để chạy tiếp.</p></div>';
  });

  copyBtn.addEventListener("click", () => {
    const consoleOutput = document.getElementById("console-output");
    navigator.clipboard.writeText(consoleOutput.innerText).then(() => {
      copyBtn.textContent = "Copied!";
      setTimeout(() => copyBtn.textContent = "Copy", 1500);
    });
  });

  cancelBtn.addEventListener("click", async () => {
    if (state.activeTaskId) {
      cancelBtn.disabled = true;
      cancelBtn.textContent = "Đang dừng...";
      await authFetch(`/api/tasks/${state.activeTaskId}/cancel`, { method: "POST" });
    }
  });
}

async function executeTask(cmd) {
  const consoleOutput = document.getElementById("console-output");
  const statusBadge = document.getElementById("task-status-badge");
  const cancelBtn = document.getElementById("btn-cancel-task");
  const taskInfo = document.getElementById("current-task-info");
  const logFileText = document.getElementById("current-log-file");
  const timerElem = document.getElementById("task-timer");

  // Close previous stream if open
  if (state.eventSource) {
    state.eventSource.close();
    state.eventSource = null;
  }

  // Clear previous output & set status
  consoleOutput.innerHTML = "";
  statusBadge.className = "badge badge-running";
  statusBadge.textContent = "RUNNING";
  cancelBtn.style.display = "inline-flex";
  cancelBtn.disabled = false;
  cancelBtn.textContent = "Dừng Task";
  taskInfo.textContent = `Lệnh: ${cmd} (CWD: ${state.activeCwd})`;

  // Start stopwatch
  state.taskStartTime = Date.now();
  if (state.taskTimerInterval) clearInterval(state.taskTimerInterval);
  state.taskTimerInterval = setInterval(() => {
    const elapsed = Math.floor((Date.now() - state.taskStartTime) / 1000);
    const mins = String(Math.floor(elapsed / 60)).padStart(2, '0');
    const secs = String(elapsed % 60).padStart(2, '0');
    timerElem.textContent = `${mins}:${secs}`;
  }, 1000);

  try {
    const res = await authFetch("/api/tasks/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cmd, cwd: state.activeCwd })
    });
    const result = await res.json();

    if (!result.success) {
      finishTask("failed", "Lỗi khởi chạy task: " + JSON.stringify(result));
      return;
    }

    const task = result.task;
    state.activeTaskId = task.task_id;
    logFileText.textContent = `Log: ${task.log_filename}`;

    // Connect SSE stream
    state.eventSource = new EventSource(`/api/tasks/${task.task_id}/stream`);

    state.eventSource.onmessage = (e) => {
      const line = e.data;
      appendConsoleOutput(line);

      if (line.includes("[FINISHED with exit code") || line.includes("[Task already finished")) {
        const isSuccess = line.includes("exit code 0");
        finishTask(isSuccess ? "completed" : "failed");
      }
    };

    state.eventSource.onerror = (e) => {
      if (statusBadge.textContent === "RUNNING") {
        finishTask("completed");
      }
    };

  } catch (err) {
    finishTask("failed", "Lỗi mạng hoặc server: " + err.message);
  }
}

function appendConsoleOutput(text) {
  const consoleOutput = document.getElementById("console-output");
  const autoScroll = document.getElementById("chk-autoscroll").checked;

  const span = document.createElement("div");
  span.textContent = text;
  consoleOutput.appendChild(span);

  if (autoScroll) {
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
  }
}

function finishTask(status, errorMsg) {
  const statusBadge = document.getElementById("task-status-badge");
  const cancelBtn = document.getElementById("btn-cancel-task");

  if (state.taskTimerInterval) {
    clearInterval(state.taskTimerInterval);
    state.taskTimerInterval = null;
  }

  if (state.eventSource) {
    state.eventSource.close();
    state.eventSource = null;
  }

  cancelBtn.style.display = "none";
  if (status === "completed") {
    statusBadge.className = "badge badge-completed";
    statusBadge.textContent = "FINISHED";
  } else {
    statusBadge.className = "badge badge-failed";
    statusBadge.textContent = "FAILED";
  }

  if (errorMsg) {
    appendConsoleOutput(`\n[ERROR]: ${errorMsg}`);
  }
}

// ==========================================================================
// 5. Interactive Terminal (xterm.js + PTY WebSocket)
// ==========================================================================
function setupTerminal() {
  const container = document.getElementById("terminal-container");

  state.terminal = new Terminal({
    cursorBlink: true,
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: 13,
    lineHeight: 1.25,
    rightClickSelectsWord: true,
    theme: {
      background: '#090D16',
      foreground: '#F1F5F9',
      cursor: '#E06D53',
      selection: 'rgba(224, 109, 83, 0.3)',
      black: '#000000',
      red: '#EF4444',
      green: '#10B981',
      yellow: '#F59E0B',
      blue: '#3B82F6',
      magenta: '#EC4899',
      cyan: '#06B6D4',
      white: '#FFFFFF'
    }
  });

  state.fitAddon = new FitAddon.FitAddon();
  state.terminal.loadAddon(state.fitAddon);
  state.terminal.open(container);
  state.fitAddon.fit();

  // Auto-copy on text selection
  state.terminal.onSelectionChange(() => {
    const selected = state.terminal.getSelection();
    if (selected && selected.trim().length > 0) {
      navigator.clipboard.writeText(selected).catch(() => {});
    }
  });

  connectTerminalWs();

  // Handle terminal keystroke input
  state.terminal.onData(data => {
    if (state.terminalWs && state.terminalWs.readyState === WebSocket.OPEN) {
      state.terminalWs.send(data);
    }
  });

  // Window resize handler
  window.addEventListener("resize", () => {
    if (state.fitAddon) {
      state.fitAddon.fit();
      sendTerminalResize();
    }
  });

  // Quick Action Buttons
  document.getElementById("btn-term-claude")?.addEventListener("click", () => sendToTerminal("claude\r"));
  document.getElementById("btn-term-seo-doc")?.addEventListener("click", () => sendToTerminal("/seo doctor\r"));
  document.getElementById("btn-term-seo-audit")?.addEventListener("click", () => sendToTerminal("/seo audit "));
  document.getElementById("btn-term-blog")?.addEventListener("click", () => sendToTerminal("/blog\r"));
  document.getElementById("btn-term-ads")?.addEventListener("click", () => sendToTerminal("/ads\r"));
  document.getElementById("btn-term-kwp")?.addEventListener("click", () => sendToTerminal("cd /projects/keywordpro && pnpm start\r"));
  document.getElementById("btn-term-ctrl-c")?.addEventListener("click", () => sendToTerminal("\x03"));
  document.getElementById("btn-term-clear")?.addEventListener("click", () => sendToTerminal("clear\r"));
  document.getElementById("btn-term-reconnect")?.addEventListener("click", () => connectTerminalWs());

  // Copy Text button handler
  const termCopyBtn = document.getElementById("btn-term-copy");
  if (termCopyBtn) {
    termCopyBtn.addEventListener("click", () => {
      let text = state.terminal.getSelection();
      if (!text) {
        const buffer = state.terminal.buffer.active;
        const lines = [];
        for (let i = 0; i < buffer.length; i++) {
          const line = buffer.getLine(i);
          if (line) lines.push(line.translateToString(true));
        }
        text = lines.join("\n").trim();
      }
      if (text) {
        navigator.clipboard.writeText(text).then(() => {
          const origHtml = termCopyBtn.innerHTML;
          termCopyBtn.innerHTML = "✅ Copied!";
          setTimeout(() => { termCopyBtn.innerHTML = origHtml; }, 1500);
        });
      }
    });
  }
}

function connectTerminalWs() {
  if (state.terminalWs) {
    try { state.terminalWs.close(); } catch (e) {}
  }

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/terminal?cwd=${encodeURIComponent(state.activeCwd)}`;

  state.terminal.writeln("\r\n\x1b[36m--- Đang kết nối tới phiên Terminal PTY... ---\x1b[0m\r\n");

  state.terminalWs = new WebSocket(wsUrl);
  state.terminalWs.binaryType = "arraybuffer";

  state.terminalWs.onopen = () => {
    state.terminal.writeln("\x1b[32m--- Kết nối thành công! Đang mở shell tại " + state.activeCwd + " ---\x1b[0m\r\n");
    sendTerminalResize();
  };

  state.terminalWs.onmessage = (event) => {
    if (event.data instanceof ArrayBuffer) {
      const decoder = new TextDecoder("utf-8");
      state.terminal.write(decoder.decode(event.data));
    } else {
      state.terminal.write(event.data);
    }
  };

  state.terminalWs.onclose = (event) => {
    if (event.code === 4001) {
      state.terminal.writeln("\r\n\x1b[31m--- Phiên làm việc chưa được xác thực mật khẩu. Vui lòng đăng nhập lại. ---\x1b[0m\r\n");
      showLoginOverlay();
    } else {
      state.terminal.writeln("\r\n\x1b[31m--- Phiên Terminal đã ngắt kết nối. Bấm 'Khởi động lại' để mở lại. ---\x1b[0m\r\n");
    }
  };

  state.terminalWs.onerror = (err) => {
    state.terminal.writeln("\r\n\x1b[31m--- Lỗi kết nối WebSocket Terminal. ---\x1b[0m\r\n");
  };
}

function sendTerminalResize() {
  if (state.terminal && state.terminalWs && state.terminalWs.readyState === WebSocket.OPEN) {
    const msg = JSON.stringify({
      type: "resize",
      cols: state.terminal.cols,
      rows: state.terminal.rows
    });
    state.terminalWs.send(msg);
  }
}

function sendToTerminal(str) {
  if (state.terminalWs && state.terminalWs.readyState === WebSocket.OPEN) {
    state.terminalWs.send(str);
  }
}

// ==========================================================================
// 6. Reports & Documents Viewer
// ==========================================================================
function setupReports() {
  document.getElementById("btn-refresh-reports").addEventListener("click", loadReportsList);

  document.getElementById("report-search").addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase();
    renderReportsList(state.reports.filter(r => r.name.toLowerCase().includes(q)));
  });

  const toggleRawBtn = document.getElementById("btn-toggle-raw");
  toggleRawBtn.addEventListener("click", () => {
    if (!state.selectedReport) return;
    state.showingRawReport = !state.showingRawReport;
    toggleRawBtn.textContent = state.showingRawReport ? "Xem Markdown Định Dạng" : "Xem Mã Markdown Thô";
    renderReportContent();
  });

  const copyReportBtn = document.getElementById("btn-copy-report");
  copyReportBtn.addEventListener("click", () => {
    if (state.selectedReport && state.selectedReport.content) {
      navigator.clipboard.writeText(state.selectedReport.content).then(() => {
        copyReportBtn.textContent = "Copied!";
        setTimeout(() => copyReportBtn.textContent = "Copy nội dung", 1500);
      });
    }
  });
}

async function loadReportsList() {
  try {
    const res = await authFetch("/api/reports");
    const data = await res.json();
    state.reports = data.reports || [];
    renderReportsList(state.reports);
  } catch (e) {
    console.error("Lỗi lấy danh sách báo cáo:", e);
  }
}

function renderReportsList(list) {
  const container = document.getElementById("reports-list");
  container.innerHTML = "";

  if (list.length === 0) {
    container.innerHTML = '<div style="padding:16px; color:#64748B; font-size:12px; text-align:center;">Không tìm thấy file báo cáo nào</div>';
    return;
  }

  list.forEach(item => {
    const div = document.createElement("div");
    div.className = "report-item";
    div.innerHTML = `
      <div class="report-item-title">${item.name}</div>
      <div class="report-item-meta">
        <span>${item.size_formatted}</span>
        <span>${item.modified}</span>
      </div>
    `;

    div.addEventListener("click", () => {
      document.querySelectorAll(".report-item").forEach(el => el.classList.remove("active"));
      div.classList.add("active");
      openReport(item.path);
    });

    container.appendChild(div);
  });
}

async function openReport(path) {
  const titleElem = document.getElementById("report-view-title");
  const pathElem = document.getElementById("report-view-path");
  const toggleRawBtn = document.getElementById("btn-toggle-raw");
  const copyReportBtn = document.getElementById("btn-copy-report");

  titleElem.textContent = "Đang tải...";
  pathElem.textContent = path;

  try {
    const res = await authFetch(`/api/reports/content?path=${encodeURIComponent(path)}`);
    const data = await res.json();

    state.selectedReport = data;
    state.showingRawReport = false;
    toggleRawBtn.style.display = "inline-flex";
    toggleRawBtn.textContent = "Xem Mã Markdown Thô";
    copyReportBtn.style.display = "inline-flex";

    titleElem.textContent = data.name;
    pathElem.textContent = `${data.path} (${data.size_formatted})`;

    renderReportContent();
  } catch (err) {
    titleElem.textContent = "Lỗi đọc file";
    document.getElementById("report-view-body").innerHTML = `<p style="color:#EF4444;">${err.message}</p>`;
  }
}

function renderReportContent() {
  const bodyElem = document.getElementById("report-view-body");
  if (!state.selectedReport) return;

  if (state.showingRawReport) {
    bodyElem.innerHTML = `<pre class="log-pre-viewer">${escapeHtml(state.selectedReport.content)}</pre>`;
  } else {
    // Render Markdown
    try {
      bodyElem.innerHTML = marked.parse(state.selectedReport.content);
    } catch (e) {
      bodyElem.innerHTML = `<pre class="log-pre-viewer">${escapeHtml(state.selectedReport.content)}</pre>`;
    }
  }
}

// ==========================================================================
// 7. Logs & Audit History
// ==========================================================================
function setupLogs() {
  document.getElementById("btn-refresh-logs").addEventListener("click", loadLogsList);

  document.getElementById("log-search-input").addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase();
    const rows = document.querySelectorAll("#logs-table-body tr");
    rows.forEach(row => {
      const text = row.innerText.toLowerCase();
      row.style.display = text.includes(q) ? "" : "none";
    });
  });

  document.getElementById("modal-close-btn").addEventListener("click", () => {
    document.getElementById("log-modal").classList.remove("active");
  });

  document.getElementById("log-modal").addEventListener("click", (e) => {
    if (e.target.id === "log-modal") {
      document.getElementById("log-modal").classList.remove("active");
    }
  });
}

async function loadLogsList() {
  try {
    const res = await authFetch("/api/logs");
    const data = await res.json();
    const tbody = document.getElementById("logs-table-body");
    tbody.innerHTML = "";

    if (!data.logs || data.logs.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#64748B; padding:20px;">Chưa có log nào được ghi</td></tr>';
      return;
    }

    data.logs.forEach(log => {
      const tr = document.createElement("tr");

      const badgeType = log.type === "task"
        ? '<span class="badge badge-task">Task Run</span>'
        : '<span class="badge badge-terminal">Terminal PTY</span>';

      tr.innerHTML = `
        <td><strong style="color:#FFF;">${log.filename}</strong></td>
        <td>${badgeType}</td>
        <td style="color:#94A3B8;">${log.modified}</td>
        <td style="font-family:monospace;">${log.size_formatted}</td>
        <td style="text-align: right;">
          <button class="btn btn-sm btn-secondary btn-view-log" data-fn="${log.filename}">Xem</button>
          <a class="btn btn-sm btn-primary" href="/api/logs/${encodeURIComponent(log.filename)}/download" download>Tải</a>
          <button class="btn btn-sm btn-danger btn-del-log" data-fn="${log.filename}">Xóa</button>
        </td>
      `;

      tr.querySelector(".btn-view-log").addEventListener("click", () => openLogModal(log.filename));
      tr.querySelector(".btn-del-log").addEventListener("click", async () => {
        if (confirm(`Bạn có chắc muốn xóa file log: ${log.filename}?`)) {
          await authFetch(`/api/logs/${encodeURIComponent(log.filename)}`, { method: "DELETE" });
          loadLogsList();
        }
      });

      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Lỗi tải logs:", err);
  }
}

async function openLogModal(filename) {
  const modal = document.getElementById("log-modal");
  const title = document.getElementById("modal-log-title");
  const meta = document.getElementById("modal-log-meta");
  const content = document.getElementById("modal-log-content");
  const downloadBtn = document.getElementById("modal-download-btn");

  title.textContent = `File: ${filename}`;
  meta.textContent = "Đang tải dữ liệu...";
  content.textContent = "Đang đọc log...";
  downloadBtn.href = `/api/logs/${encodeURIComponent(filename)}/download`;
  modal.classList.add("active");

  try {
    const res = await authFetch(`/api/logs/${encodeURIComponent(filename)}`);
    const data = await res.json();

    meta.textContent = `Dung lượng: ${data.size} | Dòng: ${data.total_lines} | Cập nhật: ${data.modified}`;
    content.textContent = data.content || "(Log rỗng)";
  } catch (e) {
    content.textContent = "Lỗi khi đọc file log: " + e.message;
  }
}

function escapeHtml(text) {
  if (!text) return "";
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function escapeAttr(text) {
  if (!text) return "";
  return String(text).replace(/"/g, "&quot;");
}

// ==========================================================================
// 8. Tool Guides & Right 25% Sidebar Manager
// ==========================================================================
function setupGuides() {
  const guideMenuBtn = document.getElementById("btn-guide-menu");
  const guideDropdown = document.getElementById("guide-dropdown");
  const guideMenuContainer = document.querySelector(".guide-menu-container");
  const guideSidebar = document.getElementById("guide-sidebar");
  const closeGuideBtn = document.getElementById("btn-close-guide");
  const toggleGuidePill = document.getElementById("btn-toggle-guide-panel");
  const searchInput = document.getElementById("guide-search-input");
  const clearSearchBtn = document.getElementById("btn-clear-guide-search");
  const guidePills = document.querySelectorAll(".guide-pill");
  const dropdownItems = document.querySelectorAll(".guide-dropdown-item");

  // Toggle Dropdown Menu in Navbar
  if (guideMenuBtn && guideDropdown) {
    guideMenuBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const isOpen = guideDropdown.style.display === "block";
      guideDropdown.style.display = isOpen ? "none" : "block";
      guideMenuContainer?.classList.toggle("open", !isOpen);
    });

    document.addEventListener("click", (e) => {
      if (!guideMenuContainer?.contains(e.target)) {
        guideDropdown.style.display = "none";
        guideMenuContainer?.classList.remove("open");
      }
    });
  }

  // Handle clicking items in the Navbar Dropdown
  dropdownItems.forEach(item => {
    item.addEventListener("click", () => {
      const toolId = item.dataset.tool;
      if (guideDropdown) guideDropdown.style.display = "none";
      guideMenuContainer?.classList.remove("open");
      openGuideSidebar(toolId);
    });
  });

  // Handle Toggle Button on Tabs Header
  if (toggleGuidePill) {
    toggleGuidePill.addEventListener("click", () => {
      if (state.isGuideOpen) {
        closeGuideSidebar();
      } else {
        openGuideSidebar(state.activeGuideTool || "seo");
      }
    });
  }

  // Handle Close Button inside Sidebar
  if (closeGuideBtn) {
    closeGuideBtn.addEventListener("click", () => {
      closeGuideSidebar();
    });
  }

  // Handle Sidebar Tool Switcher Pills
  guidePills.forEach(pill => {
    pill.addEventListener("click", () => {
      const toolId = pill.dataset.tool;
      switchGuideTool(toolId);
    });
  });

  // Handle Search Input in Sidebar
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      const query = e.target.value.trim().toLowerCase();
      if (clearSearchBtn) clearSearchBtn.style.display = query ? "block" : "none";
      renderFilteredGuideCommands(query);
    });
  }

  if (clearSearchBtn && searchInput) {
    clearSearchBtn.addEventListener("click", () => {
      searchInput.value = "";
      clearSearchBtn.style.display = "none";
      renderFilteredGuideCommands("");
      searchInput.focus();
    });
  }
}

function openGuideSidebar(toolId) {
  const guideSidebar = document.getElementById("guide-sidebar");
  const toggleGuidePill = document.getElementById("btn-toggle-guide-panel");
  const activeBadge = document.getElementById("guide-active-badge");

  state.isGuideOpen = true;
  state.activeGuideTool = toolId || "seo";

  if (guideSidebar) {
    guideSidebar.style.display = "flex";
  }

  if (toggleGuidePill) {
    toggleGuidePill.classList.add("active");
  }
  if (activeBadge) {
    activeBadge.style.display = "inline-block";
    activeBadge.textContent = (toolId || "seo").toUpperCase();
  }

  switchGuideTool(state.activeGuideTool);

  // Trigger terminal resize when layout width changes (100% -> 75%)
  setTimeout(() => {
    if (state.fitAddon) {
      try {
        state.fitAddon.fit();
        sendTerminalResize();
      } catch (e) {}
    }
  }, 260);
}

function closeGuideSidebar() {
  const guideSidebar = document.getElementById("guide-sidebar");
  const toggleGuidePill = document.getElementById("btn-toggle-guide-panel");
  const activeBadge = document.getElementById("guide-active-badge");

  state.isGuideOpen = false;

  if (guideSidebar) {
    guideSidebar.style.display = "none";
  }
  if (toggleGuidePill) {
    toggleGuidePill.classList.remove("active");
  }
  if (activeBadge) {
    activeBadge.style.display = "none";
  }

  // Trigger terminal resize when layout width returns to 100%
  setTimeout(() => {
    if (state.fitAddon) {
      try {
        state.fitAddon.fit();
        sendTerminalResize();
      } catch (e) {}
    }
  }, 260);
}

function switchGuideTool(toolId) {
  state.activeGuideTool = toolId;
  const toolData = state.guides ? state.guides[toolId] : null;
  if (!toolData) return;

  // Update Pills
  document.querySelectorAll(".guide-pill").forEach(p => {
    p.classList.toggle("active", p.dataset.tool === toolId);
  });

  // Update Dropdown Items
  document.querySelectorAll(".guide-dropdown-item").forEach(d => {
    d.classList.toggle("active", d.dataset.tool === toolId);
  });

  // Update Header
  const toolIcon = document.getElementById("guide-tool-icon");
  const toolName = document.getElementById("guide-tool-name");
  const toolBadge = document.getElementById("guide-tool-badge");
  const toolSummary = document.getElementById("guide-tool-summary");

  if (toolIcon) toolIcon.textContent = toolData.icon || "📖";
  if (toolName) toolName.textContent = toolData.name || "Tool Guide";
  if (toolBadge) toolBadge.textContent = toolData.badge || `${toolData.commands?.length || 0} Commands`;
  if (toolSummary) {
    toolSummary.innerHTML = `<strong>${toolData.name}:</strong> ${toolData.summary || ''}`;
  }

  // Clear search and render commands
  const searchInput = document.getElementById("guide-search-input");
  if (searchInput) searchInput.value = "";
  const clearSearchBtn = document.getElementById("btn-clear-guide-search");
  if (clearSearchBtn) clearSearchBtn.style.display = "none";

  renderFilteredGuideCommands("");
}

function renderFilteredGuideCommands(query) {
  const listContainer = document.getElementById("guide-commands-list");
  if (!listContainer) return;

  const toolData = state.guides ? state.guides[state.activeGuideTool] : null;
  if (!toolData || !toolData.commands) {
    listContainer.innerHTML = `<div class="guide-empty-state">Đang tải dữ liệu lệnh...</div>`;
    return;
  }

  let commands = toolData.commands;
  if (query) {
    commands = commands.filter(c =>
      c.cmd.toLowerCase().includes(query) ||
      (c.desc && c.desc.toLowerCase().includes(query)) ||
      (c.category && c.category.toLowerCase().includes(query))
    );
  }

  if (commands.length === 0) {
    listContainer.innerHTML = `
      <div class="guide-empty-state">
        <p>🔍 Không tìm thấy lệnh nào khớp với: "<strong>${escapeHtml(query)}</strong>"</p>
        <p><small>Thử tìm từ khóa khác như "audit", "schema", "serp", "crawl"...</small></p>
      </div>
    `;
    return;
  }

  listContainer.innerHTML = commands.map((c, idx) => {
    return `
      <div class="guide-cmd-card" data-cmd-idx="${idx}">
        <div class="guide-cmd-meta">
          <span class="guide-cmd-cat">${c.category || 'Chung'}</span>
          <div class="guide-cmd-actions">
            <button class="btn-cmd-action btn-insert" title="Chèn câu lệnh này vào ô nhập lệnh hoặc Terminal" data-cmd="${escapeAttr(c.cmd)}">
              <span>⚡ Chèn</span>
            </button>
            <button class="btn-cmd-action btn-copy" title="Sao chép câu lệnh" data-cmd="${escapeAttr(c.cmd)}">
              <span>📋 Copy</span>
            </button>
          </div>
        </div>
        <div class="guide-cmd-syntax">
          <code>${formatCmdSyntax(c.cmd)}</code>
        </div>
        <div class="guide-cmd-desc">${escapeHtml(c.desc)}</div>
        ${c.example && c.example !== c.cmd ? `<div class="guide-cmd-example">Ví dụ: <code>${escapeHtml(c.example)}</code></div>` : ''}
      </div>
    `;
  }).join("");

  // Attach event handlers to buttons in cards
  listContainer.querySelectorAll(".btn-copy").forEach(btn => {
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      const cmd = btn.dataset.cmd;
      try {
        await navigator.clipboard.writeText(cmd);
        const originalHtml = btn.innerHTML;
        btn.innerHTML = `<span>✓ Đã chép</span>`;
        btn.style.borderColor = "var(--accent-emerald)";
        btn.style.color = "var(--accent-emerald)";
        setTimeout(() => {
          btn.innerHTML = originalHtml;
          btn.style.borderColor = "";
          btn.style.color = "";
        }, 1500);
      } catch (err) {
        console.error("Copy failed:", err);
      }
    });
  });

  listContainer.querySelectorAll(".btn-insert").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const cmd = btn.dataset.cmd;

      // Check active tab
      const activeTabBtn = document.querySelector(".tab-btn.active");
      const activeTab = activeTabBtn ? activeTabBtn.dataset.tab : "tab-runner";

      if (activeTab === "tab-terminal") {
        sendToTerminal(cmd);
      } else {
        // Default to command runner input
        const customInput = document.getElementById("custom-cmd-input");
        if (customInput) {
          customInput.value = cmd;
          customInput.focus();
          customInput.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      }

      const originalHtml = btn.innerHTML;
      btn.innerHTML = `<span>✓ Đã chèn</span>`;
      btn.style.borderColor = "var(--accent-emerald)";
      setTimeout(() => {
        btn.innerHTML = originalHtml;
        btn.style.borderColor = "";
      }, 1500);
    });
  });
}

function formatCmdSyntax(cmd) {
  const parts = escapeHtml(cmd).split(" ");
  if (parts.length === 0) return cmd;
  const prefix = parts[0];
  const rest = parts.slice(1).join(" ");
  return `<span class="cmd-prefix">${prefix}</span> ${rest}`;
}
