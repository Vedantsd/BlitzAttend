const inputs = document.querySelectorAll(".pass-input");
const usernameInput = document.getElementById("username");
const errorMessage = document.getElementById("errorMessage");
const loading = document.getElementById("loading");

inputs.forEach((input, index) => {
    input.addEventListener("input", (e) => {
        const value = e.target.value;

        if (!/^[0-9]$/.test(value)) {
            e.target.value = "";
            return;
        }

        if (value && index < inputs.length - 1) {
            inputs[index + 1].focus();
        }

        if (value && index === inputs.length - 1) {
            submitForm();
        }
    });

    input.addEventListener("keydown", (e) => {
        if (e.key === "Backspace" && !input.value && index > 0) {
            inputs[index - 1].focus();
        }
    });

    input.addEventListener("paste", (e) => {
        e.preventDefault();
        const pastedData = e.clipboardData.getData("text");
        const digits = pastedData.replace(/\D/g, "").slice(0, 4);
        
        digits.split("").forEach((digit, i) => {
            if (inputs[i]) {
                inputs[i].value = digit;
            }
        });

        if (digits.length === 4) {
            submitForm();
        } else if (inputs[digits.length]) {
            inputs[digits.length].focus();
        }
    });
});

async function submitForm() {
    const username = usernameInput.value.trim();
    const pin = Array.from(inputs).map(input => input.value).join("");

    if (!username) {
        showError("Please enter your username");
        usernameInput.focus();
        return;
    }

    if (pin.length !== 4) {
        showError("Please enter complete 4-digit PIN");
        return;
    }

    errorMessage.classList.remove("show");
    loading.classList.add("show");

    try {
        const response = await fetch("/validate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                username: username,
                pin: pin
            })
        });

        const data = await response.json();
        console.log(data.redirect);
        if (response.ok && data.success) {
            
            window.location.href = data.redirect;
        } else {
            loading.classList.remove("show");
            showError(data.message || "Invalid username or PIN");
            clearPIN();
        }
    } catch (error) {
        loading.classList.remove("show");
        showError("Connection error. Please try again.");
        clearPIN();
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add("show");
}

function clearPIN() {
    inputs.forEach(input => input.value = "");
    inputs[0].focus();
}

window.addEventListener("load", () => {
    usernameInput.focus();
});
