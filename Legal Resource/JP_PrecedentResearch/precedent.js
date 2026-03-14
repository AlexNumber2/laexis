const API_CANDIDATES = (() => {
  if (window.__API_BASE__) return [window.__API_BASE__];

  const sameOrigin = `${location.protocol}//${location.host}/v1`;
  const cloudflareApi = "https://api.laexis.com/v1";
  const localApis = ["http://127.0.0.1:8000/v1", "http://localhost:8000/v1"];

  if (location.hostname.endsWith("laexis.com")) {
    return [sameOrigin, cloudflareApi, ...localApis];
  }
  return [...localApis, sameOrigin, cloudflareApi];
})();

const TAB_LABELS = {
  integrated: "Integrated Search",
  supreme: "Supreme Court",
  high: "High Courts",
  lower: "Lower Courts",
  administrative: "Administrative Cases",
  labor: "Labor Cases",
  ip: "IP Cases",
};

const el = (id) => document.getElementById(id);

const state = {
  apiBase: null,
  selectedDetailUrl: null,
  selectedItem: null,
  tab: "integrated",
};

function setLoading(isLoading) {
  el("loading").classList.toggle("active", isLoading);
  el("searchBtn").disabled = isLoading;
}

function setError(message) {
  const node = el("error");
  if (!message) {
    node.textContent = "";
    node.classList.remove("active");
    return;
  }
  node.textContent = message;
  node.classList.add("active");
}

function setAiLoading(isLoading) {
  el("aiLoading").classList.toggle("active", isLoading);
  document.querySelectorAll(".ai-btn").forEach((btn) => {
    btn.disabled = isLoading;
  });
}

function setAiError(message) {
  el("aiError").textContent = message || "";
}

function showResults(active) {
  el("results").classList.toggle("active", active);
}

function showDetail(active) {
  el("detail").classList.toggle("active", active);
}

function fillNumberSelect(selectEl, start, end) {
  selectEl.innerHTML = "";
  const blank = document.createElement("option");
  blank.value = "";
  blank.textContent = "Select";
  selectEl.appendChild(blank);
  for (let i = start; i <= end; i += 1) {
    const option = document.createElement("option");
    option.value = String(i);
    option.textContent = String(i);
    selectEl.appendChild(option);
  }
}

function applyJudgeDateMode(mode) {
  const disabled = mode !== "2";
  const row = el("dateToRow");
  row.style.opacity = disabled ? "0.55" : "1";
  ["judgeGengoTo", "judgeYearTo", "judgeMonthTo", "judgeDayTo"].forEach((id) => {
    const node = el(id);
    node.disabled = disabled;
    if (disabled) node.value = "";
  });
}

function currentFormPayload() {
  return {
    tab: state.tab,
    query1: el("query1").value.trim(),
    query2: el("query2").value.trim(),
    judgeDateMode: document.querySelector('input[name="judgeDateMode"]:checked')?.value || "",
    judgeGengoFrom: el("judgeGengoFrom").value,
    judgeYearFrom: el("judgeYearFrom").value,
    judgeMonthFrom: el("judgeMonthFrom").value,
    judgeDayFrom: el("judgeDayFrom").value,
    judgeGengoTo: el("judgeGengoTo").value,
    judgeYearTo: el("judgeYearTo").value,
    judgeMonthTo: el("judgeMonthTo").value,
    judgeDayTo: el("judgeDayTo").value,
    jikenGengo: el("jikenGengo").value,
    jikenYear: el("jikenYear").value.trim(),
    jikenCode: el("jikenCode").value.trim(),
    jikenNumber: el("jikenNumber").value.trim(),
    courtType: el("courtType").value,
    courtSection: el("courtSection").value,
    courtName: el("courtName").value.trim(),
    branchName: el("branchName").value.trim(),
    sort: el("sort").value,
    offset: el("offset").value.trim() || "0",
  };
}

function payloadToParams(payload) {
  const params = new URLSearchParams();
  Object.entries(payload).forEach(([key, value]) => {
    if (value === undefined || value === null) return;
    const normalized = String(value);
    if (!normalized) return;
    params.set(key, normalized);
  });
  return params;
}

function tabNote(tab) {
  if (tab === "integrated") {
    return "Phase 1 uses realtime proxy fetching with a lightweight cache.";
  }
  return `Phase 1 routes ${TAB_LABELS[tab]} to the matching court search page. Parsing is best-effort for this tab.`;
}

function setTab(tab) {
  state.tab = tab;
  document.querySelectorAll(".tab").forEach((button) => {
    const selected = button.dataset.tab === tab;
    button.setAttribute("aria-selected", selected ? "true" : "false");
  });
  el("phaseNote").textContent = tabNote(tab);
  setError("");
}

function resetForm() {
  el("query1").value = "";
  el("query2").value = "";
  el("query2Row").style.display = "none";
  el("toggleQuery2").setAttribute("aria-expanded", "false");
  el("toggleQuery2").textContent = "+ Additional keyword";

  document.querySelector('input[name="judgeDateMode"][value="1"]').checked = true;
  applyJudgeDateMode("1");

  ["judgeGengoFrom", "judgeYearFrom", "judgeMonthFrom", "judgeDayFrom"].forEach((id) => (el(id).value = ""));
  ["judgeGengoTo", "judgeYearTo", "judgeMonthTo", "judgeDayTo"].forEach((id) => (el(id).value = ""));
  ["jikenGengo", "jikenYear", "jikenCode", "jikenNumber"].forEach((id) => (el(id).value = ""));
  ["courtType", "courtSection", "courtName", "branchName"].forEach((id) => (el(id).value = ""));

  el("sort").value = "1";
  el("offset").value = "0";
  setError("");
}

async function resolveApiBase() {
  if (state.apiBase) return state.apiBase;

  for (const candidate of API_CANDIDATES) {
    try {
      const response = await fetch(`${candidate}/health`, { method: "GET" });
      if (response.ok) {
        state.apiBase = candidate;
        el("backendHint").textContent = candidate;
        return candidate;
      }
    } catch (_error) {
      // Keep checking.
    }
  }

  const fallback = API_CANDIDATES[0];
  el("backendHint").textContent = fallback;
  throw new Error(
    "API is unreachable. Start the backend, configure window.__API_BASE__, or route /v1 or api.laexis.com to the FastAPI service."
  );
}

async function fetchJson(path, options) {
  const base = await resolveApiBase();
  let response;
  try {
    response = await fetch(`${base}${path}`, options);
  } catch (_networkError) {
    throw new Error(`Cannot reach API at ${base}. Check backend status, Cloudflare routing, or CORS.`);
  }
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return response.json();
}

function renderResultItem(item) {
  const wrapper = document.createElement("div");
  wrapper.className = "result-item";

  const left = document.createElement("div");
  const title = document.createElement("div");
  title.className = "result-title";
  title.textContent = item.title || item.section || "(no title)";

  const meta = document.createElement("div");
  meta.className = "result-meta";
  meta.textContent = (item.meta || []).join(" | ");

  left.appendChild(title);
  left.appendChild(meta);

  if (item.tags && item.tags.length) {
    const pills = document.createElement("div");
    pills.className = "pills";
    item.tags.slice(0, 6).forEach((tag) => {
      const pill = document.createElement("span");
      pill.className = "pill";
      pill.textContent = tag;
      pills.appendChild(pill);
    });
    left.appendChild(pills);
  }

  const right = document.createElement("div");
  right.className = "actions";

  const detailButton = document.createElement("button");
  detailButton.className = "action-btn";
  detailButton.type = "button";
  detailButton.textContent = "Select";

  const pdfButton = document.createElement("a");
  pdfButton.className = "action-btn";
  pdfButton.textContent = "PDF";
  pdfButton.href = item.pdf_url || "#";
  pdfButton.target = "_blank";
  pdfButton.rel = "noopener noreferrer";
  if (!item.pdf_url) pdfButton.style.display = "none";

  right.appendChild(detailButton);
  right.appendChild(pdfButton);
  wrapper.appendChild(left);
  wrapper.appendChild(right);

  detailButton.addEventListener("click", (event) => {
    event.preventDefault();
    selectCase(item);
  });
  wrapper.addEventListener("click", () => selectCase(item));

  return wrapper;
}

async function handleSearch() {
  setError("");
  showDetail(false);

  const payload = currentFormPayload();
  if (!payload.query1 && !payload.query2) {
    setError("Please enter at least one keyword.");
    return;
  }

  setLoading(true);
  try {
    const params = payloadToParams(payload);
    const data = await fetchJson(`/search/cases?${params.toString()}`);
    el("resultCount").textContent = data.count_text || `${data.total || 0} results`;

    const list = el("resultList");
    list.innerHTML = "";
    (data.results || []).forEach((item) => list.appendChild(renderResultItem(item)));

    showResults(true);
    if (!data.results || data.results.length === 0) {
      setError("No results. Try a different keyword.");
    }
  } catch (error) {
    setError(error?.message || String(error));
    showResults(false);
  } finally {
    setLoading(false);
  }
}

async function selectCase(item) {
  state.selectedDetailUrl = item.detail_url;
  state.selectedItem = item;
  setAiError("");
  el("aiResult").style.display = "none";

  showDetail(true);
  el("detailLink").href = item.detail_url;
  el("detailMeta").textContent = (item.meta || []).join(" | ");
  el("detailText").textContent = "Loading detail...";

  try {
    const params = new URLSearchParams();
    params.set("detail_url", item.detail_url);
    const data = await fetchJson(`/cases/detail?${params.toString()}`);

    el("detailMeta").textContent = [data.case_number, data.judgment_date, data.court_name, data.case_title]
      .filter(Boolean)
      .join(" | ");

    if (data.pdf_url) {
      el("pdfLink").href = data.pdf_url;
      el("pdfLink").style.display = "inline-flex";
    } else {
      el("pdfLink").style.display = "none";
    }

    el("detailText").textContent = data.preview_text || data.raw_text || "(no text extracted)";
  } catch (error) {
    el("detailText").textContent = "";
    setAiError(error?.message || String(error));
  }
}

async function summarize(mode) {
  if (!state.selectedDetailUrl) {
    setAiError("Please select a precedent first.");
    return;
  }

  setAiError("");
  setAiLoading(true);
  try {
    const data = await fetchJson("/cases/summarize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ detail_url: state.selectedDetailUrl, mode }),
    });

    el("sumDate").textContent = data.judgment_date || "Not clearly stated";
    el("sumFacts").textContent = data.case_facts || "Not clearly stated";
    el("sumReason").textContent = data.judge_reasoning || "Not clearly stated";
    el("sumHolding").textContent = data.final_holding || "Not clearly stated";
    el("aiResult").style.display = "block";
  } catch (error) {
    setAiError(error?.message || String(error));
  } finally {
    setAiLoading(false);
  }
}

async function loadMeta() {
  try {
    const data = await fetchJson("/meta/courts");
    const typeSelect = el("courtType");
    const sectionSelect = el("courtSection");
    const courtList = el("courtNameList");
    const branchList = el("branchNameList");

    if (Array.isArray(data.courtTypes)) {
      data.courtTypes.forEach((item) => {
        const option = document.createElement("option");
        option.value = String(item.id);
        option.textContent = item.name;
        typeSelect.appendChild(option);
      });
    }

    if (Array.isArray(data.courtSections)) {
      data.courtSections.forEach((item) => {
        const option = document.createElement("option");
        option.value = String(item.id);
        option.textContent = item.name;
        sectionSelect.appendChild(option);
      });
    }

    if (Array.isArray(data.courts)) {
      const seen = new Set();
      data.courts.forEach((item) => {
        if (!item?.name || seen.has(item.name)) return;
        seen.add(item.name);
        const option = document.createElement("option");
        option.value = item.name;
        courtList.appendChild(option);
      });
    }

    if (Array.isArray(data.branches)) {
      const seen = new Set();
      data.branches.forEach((item) => {
        if (!item?.name || seen.has(item.name)) return;
        seen.add(item.name);
        const option = document.createElement("option");
        option.value = item.name;
        branchList.appendChild(option);
      });
    }
  } catch (error) {
    setError(error?.message || String(error));
  }
}

document.getElementById("searchForm").addEventListener("submit", (event) => {
  event.preventDefault();
  handleSearch();
});

document.querySelectorAll(".ai-btn").forEach((button) => {
  button.addEventListener("click", () => summarize(button.dataset.mode || "summary_zh"));
});

document.querySelectorAll('input[name="judgeDateMode"]').forEach((radio) => {
  radio.addEventListener("change", () => applyJudgeDateMode(radio.value));
});

el("toggleQuery2").addEventListener("click", () => {
  const row = el("query2Row");
  const expanded = el("toggleQuery2").getAttribute("aria-expanded") === "true";
  const next = !expanded;
  el("toggleQuery2").setAttribute("aria-expanded", next ? "true" : "false");
  row.style.display = next ? "block" : "none";
  el("toggleQuery2").textContent = next ? "- Additional keyword" : "+ Additional keyword";
});

el("clearBtn").addEventListener("click", resetForm);

document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => setTab(button.dataset.tab || "integrated"));
});

fillNumberSelect(el("judgeYearFrom"), 1, 100);
fillNumberSelect(el("judgeYearTo"), 1, 100);
fillNumberSelect(el("judgeMonthFrom"), 1, 12);
fillNumberSelect(el("judgeMonthTo"), 1, 12);
fillNumberSelect(el("judgeDayFrom"), 1, 31);
fillNumberSelect(el("judgeDayTo"), 1, 31);
applyJudgeDateMode(document.querySelector('input[name="judgeDateMode"]:checked')?.value || "1");
setTab("integrated");

resolveApiBase()
  .then(() => loadMeta())
  .catch((error) => {
    setError(error?.message || String(error));
  });
