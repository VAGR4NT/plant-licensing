document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector(".searchForm");
  if (!form) return;

  const tableFieldsData = JSON.parse(document.getElementById('table-fields-data').textContent); 
  
  const operators = [
    "exact",
    "iexact",
    "icontains",
    "gt",
    "gte",
    "lt",
    "lte",
  ];

  console.log(tableFieldsData);
  const addFilterBtn = document.getElementById('add-filter-btn');
  const filterContainer = document.getElementById('filter-list-container');
  let filterRowCount = 0;
  addFilterBtn.addEventListener('click', createFilterRow);
  function createFilterRow() {
      filterRowCount++;
      const row = document.createElement('div');
      row.className = 'filter-row';
      const groupSelect = document.createElement('select');
      groupSelect.name = `adv_group_${filterRowCount}`;
      groupSelect.innerHTML = `<option value="">-- Select Group --</option>` + 
          Object.keys(tableFieldsData).map(group => `<option value="${group}">${group}</option>`).join('');
      const fieldSelect = document.createElement('select');
      fieldSelect.name = `adv_field_${filterRowCount}`;
      fieldSelect.innerHTML = `<option value="">-- Select Field --</option>`;

      const opSelect = document.createElement('select');
      opSelect.name = `adv_op_${filterRowCount}`;
      opSelect.innerHTML = `<option value="">-- Operator --</option>` +
          operators.map(op => `<option value="${op}">${op}</option>`).join('');

      const valueInput = document.createElement('input');
      valueInput.type = 'text';
      valueInput.name = `adv_val_${filterRowCount}`;
      valueInput.placeholder = 'Value...';

      const removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.className = 'remove-filter-btn';
      removeBtn.textContent = 'X';
      removeBtn.onclick = () => row.remove();
      groupSelect.addEventListener('change', function() {
          const selectedGroup = this.value;
          const fields = tableFieldsData[selectedGroup] || [];
          fieldSelect.innerHTML = `<option value="">-- Select Field --</option>` +
              fields.map(field => `<option value="${field.name}">${field.label}</option>`).join('');
      });
      row.append(groupSelect, fieldSelect, opSelect, valueInput, removeBtn);
      filterContainer.appendChild(row);

  }

  // Before form submission, mark that we should scroll after reload
  form.addEventListener("submit", function () {
    sessionStorage.setItem("scrollToResults", "true");
  });
});

window.addEventListener("load", function () {
  // Check if we should scroll after reload
  if (sessionStorage.getItem("scrollToResults") === "true") {
    sessionStorage.removeItem("scrollToResults"); // reset the flag

    const resultsSection = document.querySelector("#results");
    if (resultsSection) {
      // Disable all smooth scrolling and jump instantly
      document.documentElement.style.scrollBehavior = "auto";
      document.body.style.scrollBehavior = "auto";

      // Force an immediate scroll to the results section
      window.scrollTo({
        top: resultsSection.offsetTop,
        behavior: "auto",
      });
    }
  }
});


