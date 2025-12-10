document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector(".searchForm");
  if (!form) return;

  const tableFieldsData = JSON.parse(
    document.getElementById("table-fields-data").textContent,
  );

  const operatorMap = {
  exact: "Equals",
  iexact: "Equals (case-insensitive)",
  icontains: "Contains",
  gt: "Greater than (>)",
  gte: "Greater than or equal (>=)",
  lt: "Less than (<)",
  lte: "Less than or equal (<=)"
};

  const addFilterBtn = document.getElementById("add-filter-btn");
  const filterContainer = document.getElementById("filter-list-container");
  let filterRowCount = 0;

  addFilterBtn.addEventListener(
    "click",
    () => createFilterRow({}, false), // empty row
  );

  function createFilterRow(preset = {}, fromLoad = false) {
    filterRowCount++;

    const row = document.createElement("div");
    row.className = "filter-row";

    const groupSelect = document.createElement("select");
    groupSelect.name = `adv_group_${filterRowCount}`;
    groupSelect.innerHTML =
      `<option value="">-- Select Group --</option>` +
      Object.keys(tableFieldsData)
        .map((group) => `<option value="${group}">${group}</option>`)
        .join("");

    const fieldSelect = document.createElement("select");
    fieldSelect.name = `adv_field_${filterRowCount}`;
    fieldSelect.innerHTML = `<option value="">-- Select Field --</option>`;

    const opSelect = document.createElement("select");
    opSelect.name = `adv_op_${filterRowCount}`;
    
    opSelect.innerHTML =
  `<option value="">-- Operator --</option>` +
  Object.entries(operatorMap)
    .map(([val, label]) => `<option value="${val}">${label}</option>`)
    .join("");

	  // --- value input ---
    const valueInput = document.createElement("input");
    valueInput.type = "text";
    valueInput.name = `adv_val_${filterRowCount}`;
    valueInput.placeholder = "Value...";

    // --- remove button ---
    const removeBtn = document.createElement("button");
    removeBtn.type = "button";
    removeBtn.className = "remove-filter-btn";
    removeBtn.textContent = "X";
    removeBtn.onclick = () => row.remove();

    // When group changes → populate fields
    groupSelect.addEventListener("change", function () {
      const fields = tableFieldsData[this.value] || [];
      fieldSelect.innerHTML =
        `<option value="">-- Select Field --</option>` +
        fields
          .map((f) => `<option value="${f.name}">${f.label}</option>`)
          .join("");

      // If restoring, auto-select field after group is set
      if (fromLoad && preset.field) {
        fieldSelect.value = preset.field;
      }
    });

    // Append row now so we can fill fields dynamically later
    row.append(groupSelect, fieldSelect, opSelect, valueInput, removeBtn);
    filterContainer.appendChild(row);

    if (fromLoad) {
      if (preset.group) {
        groupSelect.value = preset.group;
        groupSelect.dispatchEvent(new Event("change"));
      }
      if (preset.op) opSelect.value = preset.op;
      if (preset.val) valueInput.value = preset.val;
    }
  }

  const params = new URLSearchParams(window.location.search);
  const existingFilters = [];

  params.forEach((value, key) => {
    const match = key.match(/^adv_(group|field|op|val)_(\d+)$/);
    if (!match) return;

    const [_, type, index] = match;

    if (!existingFilters[index]) existingFilters[index] = {};
    existingFilters[index][type] = value;
  });

  // Create rows in the correct order
  existingFilters.forEach((preset) => {
    if (preset) createFilterRow(preset, true);
  });

  form.addEventListener("submit", function () {
    sessionStorage.setItem("scrollToResults", "true");
  });
});

window.addEventListener("load", function () {
  if (sessionStorage.getItem("scrollToResults") === "true") {
    sessionStorage.removeItem("scrollToResults");

    const resultsSection = document.querySelector("#results");
    if (resultsSection) {
      document.documentElement.style.scrollBehavior = "auto";
      document.body.style.scrollBehavior = "auto";

      window.scrollTo({
        top: resultsSection.offsetTop,
        behavior: "auto",
      });
    }
  }
});
