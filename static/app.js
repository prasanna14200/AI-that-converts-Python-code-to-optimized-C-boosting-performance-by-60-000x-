const source = document.querySelector("#source");
const output = document.querySelector("#output");
const statusBox = document.querySelector("#status");
const convertButton = document.querySelector("#convert");

const sample = `def total_even_squares(limit):
    total = 0
    for number in range(limit):
        if number % 2 == 0:
            total += number * number
    return total

print(total_even_squares(10))`;

function setStatus(message, kind = "idle") {
  statusBox.textContent = message;
  statusBox.dataset.kind = kind;
}

async function convertCode() {
  const code = source.value.trim();
  output.value = "";
  setStatus("Converting", "busy");
  convertButton.disabled = true;

  try {
    const response = await fetch("/api/convert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });
    const data = await response.json();

    if (!response.ok) {
      setStatus(data.error || "Conversion failed", "error");
      return;
    }

    output.value = data.cpp_code || "";
    setStatus(`${data.direction} with ${data.model}`, "success");
  } catch (error) {
    setStatus(`Request failed: ${error.message}`, "error");
  } finally {
    convertButton.disabled = false;
  }
}

function downloadOutput() {
  if (!output.value.trim()) {
    setStatus("No generated C++ to download", "error");
    return;
  }

  const blob = new Blob([output.value], { type: "text/x-c++src" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "converted.cpp";
  link.click();
  URL.revokeObjectURL(url);
  setStatus("Download prepared", "success");
}

document.querySelector("#loadSample").addEventListener("click", () => {
  source.value = sample;
  setStatus("Sample loaded");
});

document.querySelector("#clear").addEventListener("click", () => {
  source.value = "";
  output.value = "";
  setStatus("Ready");
});

document.querySelector("#copy").addEventListener("click", async () => {
  if (!output.value.trim()) {
    setStatus("No generated C++ to copy", "error");
    return;
  }
  await navigator.clipboard.writeText(output.value);
  setStatus("Copied", "success");
});

document.querySelector("#download").addEventListener("click", downloadOutput);
convertButton.addEventListener("click", convertCode);
