const PRESETS = {
    "this-month": (today) => ({
        from: `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-01`,
        to: "",
    }),
    "last-month": (today) => {
        const last = new Date(today.getFullYear(), today.getMonth() - 1, 1);
        const next = new Date(today.getFullYear(), today.getMonth(), 1);
        const end = new Date(next.getFullYear(), next.getMonth(), 0);
        return {
            from: `${last.getFullYear()}-${String(last.getMonth() + 1).padStart(2, "0")}-01`,
            to: `${end.getFullYear()}-${String(end.getMonth() + 1).padStart(2, "0")}-${String(end.getDate()).padStart(2, "0")}`,
        };
    },
    "this-year": (today) => ({
        from: `${today.getFullYear()}-01-01`,
        to: `${today.getFullYear()}-12-31`,
    }),
    all: () => ({ from: "", to: "" }),
};

const state = {
    page: 1,
    totalPages: 1,
    category: "",
    preset: "all",
    from: "",
    to: "",
    editingId: null,
};

const summaryState = {
    preset: "this-month",
    from: "",
    to: "",
};

const elements = {
    balance: document.getElementById("balance"),
    list: document.getElementById("transaction-list"),
    empty: document.getElementById("empty-message"),
    filterCategory: document.getElementById("filter-category"),
    filterPreset: document.getElementById("filter-preset"),
    customRange: document.getElementById("custom-range"),
    filterFrom: document.getElementById("filter-from"),
    filterTo: document.getElementById("filter-to"),
    clearFilters: document.getElementById("clear-filters"),
    addButton: document.getElementById("add-transaction"),
    prevPage: document.getElementById("prev-page"),
    nextPage: document.getElementById("next-page"),
    pageInfo: document.getElementById("page-info"),
    summaryPreset: document.getElementById("summary-preset"),
    summaryCustomRange: document.getElementById("summary-custom-range"),
    summaryFrom: document.getElementById("summary-from"),
    summaryTo: document.getElementById("summary-to"),
    summaryList: document.getElementById("summary-list"),
    summaryTotal: document.getElementById("summary-total"),
    summaryEmpty: document.getElementById("summary-empty"),
    dialog: document.getElementById("transaction-dialog"),
    dialogTitle: document.getElementById("dialog-title"),
    form: document.getElementById("transaction-form"),
    formDescription: document.getElementById("form-description"),
    formAmount: document.getElementById("form-amount"),
    formCategory: document.getElementById("form-category"),
    formDate: document.getElementById("form-date"),
    formError: document.getElementById("form-error"),
    deleteButton: document.getElementById("delete-btn"),
    cancelButton: document.getElementById("cancel-btn"),
    saveButton: document.getElementById("save-btn"),
};

function queryUrl() {
    const params = new URLSearchParams();
    params.set("page", state.page);
    if (state.category) params.set("category", state.category);
    if (state.from) params.set("from", state.from);
    if (state.to) params.set("to", state.to);
    return `/api/transactions?${params.toString()}`;
}

function renderBalance(balance) {
    elements.balance.textContent = formatCents(balance);
    elements.balance.classList.toggle("negative", balance < 0);
}

function renderTransactions(data) {
    state.page = data.page;
    state.totalPages = data.total_pages;
    renderBalance(data.balance);

    elements.list.replaceChildren();
    for (const t of data.transactions) {
        const row = document.createElement("tr");

        const dateCell = document.createElement("td");
        dateCell.textContent = formatDate(t.date);
        const descCell = document.createElement("td");
        descCell.textContent = t.description;
        const catCell = document.createElement("td");
        const catBadge = document.createElement("span");
        catBadge.className = "badge";
        catBadge.textContent = t.category;
        catCell.appendChild(catBadge);
        const actionsCell = document.createElement("td");
        actionsCell.className = "actions-col";
        const editButton = document.createElement("button");
        editButton.type = "button";
        editButton.className = "btn-icon";
        editButton.title = "Edit transaction";
        editButton.setAttribute("aria-label", "Edit transaction");
        editButton.textContent = "\u270E";
        editButton.addEventListener("click", () => openDialog(t));
        actionsCell.appendChild(editButton);

        row.append(actionsCell, dateCell, descCell, catCell, buildAmountCell(t.amount, true));
        elements.list.appendChild(row);
    }

    elements.empty.classList.toggle("hidden", data.transactions.length > 0);
    elements.pageInfo.textContent = `${data.page} / ${data.total_pages}`;
    elements.prevPage.disabled = data.page <= 1;
    elements.nextPage.disabled = data.page >= data.total_pages;
}

function loadTransactions() {
    getJSON(queryUrl())
        .then(renderTransactions)
        .catch(() => {
            elements.list.replaceChildren();
            elements.empty.classList.remove("hidden");
        });
}

function applyPreset() {
    const range = PRESETS[state.preset](new Date());
    state.from = range.from;
    state.to = range.to;
}

function applySummaryPreset() {
    const range = PRESETS[summaryState.preset](new Date());
    summaryState.from = range.from;
    summaryState.to = range.to;
}

function summaryUrl() {
    const params = new URLSearchParams();
    if (summaryState.from) params.set("from", summaryState.from);
    if (summaryState.to) params.set("to", summaryState.to);
    return `/api/summary?${params.toString()}`;
}

function buildAmountCell(cents, negativeClass) {
    const cell = document.createElement("td");
    cell.className = "amount-col amount";
    cell.textContent = formatCents(cents);
    if (negativeClass) cell.classList.toggle("negative", cents < 0);
    return cell;
}

function renderSummary(data) {
    elements.summaryList.replaceChildren();
    elements.summaryTotal.replaceChildren();
    elements.summaryEmpty.classList.toggle("hidden", data.categories.length > 0);

    for (const item of data.categories) {
        const row = document.createElement("tr");
        const name = document.createElement("td");
        name.textContent = item.category;
        row.append(
            name,
            buildAmountCell(item.income),
            buildAmountCell(-item.expenses),
            buildAmountCell(item.net, true),
        );
        elements.summaryList.appendChild(row);
    }

    const totalRow = document.createElement("tr");
    const label = document.createElement("td");
    label.textContent = "Total";
    totalRow.append(
        label,
        buildAmountCell(data.total_income),
        buildAmountCell(-data.total_expenses),
        buildAmountCell(data.total_net, true),
    );
    elements.summaryTotal.appendChild(totalRow);
}

function loadSummary() {
    getJSON(summaryUrl())
        .then(renderSummary)
        .catch(() => {
            elements.summaryList.replaceChildren();
            elements.summaryTotal.replaceChildren();
            elements.summaryEmpty.classList.remove("hidden");
        });
}

function resetAndLoad() {
    state.page = 1;
    loadTransactions();
}

function populateCategorySelects(categories) {
    for (const category of categories) {
        elements.filterCategory.add(new Option(category, category));
        elements.formCategory.add(new Option(category, category));
    }
}

function openDialog(transaction) {
    elements.formError.classList.add("hidden");
    elements.form.reset();
    if (transaction) {
        state.editingId = transaction.id;
        elements.dialogTitle.textContent = "Edit Transaction";
        elements.formDescription.value = transaction.description;
        elements.formAmount.value = (Math.abs(transaction.amount) / 100).toFixed(2);
        elements.formCategory.value = transaction.category;
        elements.formDate.value = transaction.date;
        document.querySelector(
            `input[name="type"][value="${transaction.amount < 0 ? "expense" : "income"}"]`
        ).checked = true;
        elements.deleteButton.classList.remove("hidden");
    } else {
        state.editingId = null;
        elements.dialogTitle.textContent = "Add Transaction";
        elements.formDate.value = new Date().toISOString().slice(0, 10);
        elements.deleteButton.classList.add("hidden");
    }
    elements.dialog.showModal();
}

function closeDialog() {
    elements.dialog.close();
}

function formPayload() {
    const type = document.querySelector('input[name="type"]:checked').value;
    return {
        description: elements.formDescription.value,
        amount: parseFloat(elements.formAmount.value),
        type: type,
        category: elements.formCategory.value,
        date: elements.formDate.value,
    };
}

function showError(message) {
    elements.formError.textContent = message;
    elements.formError.classList.remove("hidden");
}

function saveTransaction(event) {
    event.preventDefault();
    const payload = formPayload();
    const url = state.editingId
        ? `/api/transactions/${state.editingId}`
        : "/api/transactions";
    const method = state.editingId ? "PUT" : "POST";

    sendJSON(url, method, payload)
        .then(() => {
            closeDialog();
            resetAndLoad();
        })
        .catch((error) => showError(error.message));
}

function deleteTransaction() {
    if (!confirm("Delete this transaction?")) return;

    sendJSON(`/api/transactions/${state.editingId}`, "DELETE")
        .then(() => {
            closeDialog();
            resetAndLoad();
        })
        .catch((error) => showError(error.message));
}

function bindEvents() {
    elements.filterCategory.addEventListener("change", () => {
        state.category = elements.filterCategory.value;
        resetAndLoad();
    });

    elements.filterPreset.addEventListener("change", () => {
        state.preset = elements.filterPreset.value;
        elements.customRange.classList.toggle("hidden", state.preset !== "custom");
        if (state.preset !== "custom") applyPreset();
        resetAndLoad();
    });

    for (const input of [elements.filterFrom, elements.filterTo]) {
        input.addEventListener("change", () => {
            state.from = elements.filterFrom.value;
            state.to = elements.filterTo.value;
            resetAndLoad();
        });
    }

    elements.clearFilters.addEventListener("click", () => {
        state.category = "";
        state.preset = "all";
        state.from = "";
        state.to = "";
        elements.filterCategory.value = "";
        elements.filterPreset.value = "all";
        elements.filterFrom.value = "";
        elements.filterTo.value = "";
        elements.customRange.classList.add("hidden");
        resetAndLoad();
    });

    elements.addButton.addEventListener("click", () => openDialog(null));
    elements.cancelButton.addEventListener("click", closeDialog);
    elements.deleteButton.addEventListener("click", deleteTransaction);
    elements.form.addEventListener("submit", saveTransaction);

    elements.prevPage.addEventListener("click", () => {
        if (state.page > 1) {
            state.page -= 1;
            loadTransactions();
        }
    });
    elements.nextPage.addEventListener("click", () => {
        if (state.page < state.totalPages) {
            state.page += 1;
            loadTransactions();
        }
    });

    elements.summaryPreset.addEventListener("change", () => {
        summaryState.preset = elements.summaryPreset.value;
        elements.summaryCustomRange.classList.toggle(
            "hidden", summaryState.preset !== "custom");
        if (summaryState.preset !== "custom") {
            applySummaryPreset();
            loadSummary();
        }
    });

    for (const input of [elements.summaryFrom, elements.summaryTo]) {
        input.addEventListener("change", () => {
            summaryState.from = elements.summaryFrom.value;
            summaryState.to = elements.summaryTo.value;
            loadSummary();
        });
    }
}

function init() {
    bindEvents();
    applyPreset();
    applySummaryPreset();
    getJSON("/api/categories")
        .then((categories) => populateCategorySelects(categories))
        .then(loadTransactions);
    loadSummary();
}

init();
