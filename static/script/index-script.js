const classSelect = document.getElementById("select-class");
const batchSelect = document.getElementById("select-batch");


classSelect.addEventListener('change', function () {
    const selectedClass = this.value;

    batchSelect.innerHTML = "<option value='' class='options'>--Select a batch--</option>"

    if (selectedClass && batches[selectedClass]) {
        batches[selectedClass].forEach(element => {
            
            const option = document.createElement('option');
            option.value = element;
            option.textContent = element; 
            batchSelect.appendChild(option);

        });
    }
});
