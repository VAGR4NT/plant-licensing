document.addEventListener("DOMContentLoaded", () => {
  const fieldset = document.getElementById("master-form-fieldset");
  const editButton = document.getElementById("edit-button");
  const saveButton = document.getElementById("save-button");
  const cancelButton = document.getElementById("cancel-button");

  // All input/select/textarea fields
  const inputs = fieldset.querySelectorAll("input, select, textarea");

  // All labels inside the form
  const labels = fieldset.querySelectorAll("label");

  // --- STORE ORIGINAL VALUES ---
  const originalValues = {};
  inputs.forEach((input) => {
    originalValues[input.name] = input.value;
  });

  // Label appearance functions
  const setLabelsDisabled = () => {
    labels.forEach((label) => {
      label.style.color = "#777";
      label.style.fontWeight = "600";
    });
  };

  const setLabelsEnabled = () => {
    labels.forEach((label) => {
      label.style.color = "";
      label.style.fontWeight = "";
    });
  };

  // Initialize labels as disabled
  setLabelsDisabled();

  // --- EDIT ---
  editButton.addEventListener("click", () => {
    fieldset.disabled = false;
    setLabelsEnabled();

    editButton.style.display = "none";
    saveButton.style.display = "inline-block";
    cancelButton.style.display = "inline-block";
  });

  // --- CANCEL ---
  cancelButton.addEventListener("click", () => {
    // Disable form again
    fieldset.disabled = true;
    setLabelsDisabled();

    // Restore original values
    inputs.forEach((input) => {
      if (originalValues.hasOwnProperty(input.name)) {
        input.value = originalValues[input.name];
      }
    });

    editButton.style.display = "inline-block";
    saveButton.style.display = "none";
    cancelButton.style.display = "none";
  });
});
