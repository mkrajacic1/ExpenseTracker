const euroFormat = new Intl.NumberFormat("de-DE", {
    style: "currency",
    currency: "EUR",
});

function formatCents(cents) {
    return euroFormat.format(cents / 100);
}

function formatDate(iso) {
    const [year, month, day] = iso.split("-");
    return `${day}.${month}.${year}`;
}

function getJSON(url) {
    return fetch(url).then((response) => {
        if (!response.ok) {
            throw new Error(`Request failed: ${response.status}`);
        }
        return response.json();
    });
}

function sendJSON(url, method, body) {
    return fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    }).then((response) => {
        if (!response.ok) {
            return response.json().then((data) => {
                throw new Error(data.error || "Request failed");
            });
        }
        return response;
    });
}
