const openBtns = document.querySelectorAll(".open-modal");
const closeBtns = document.querySelectorAll(".close-modal");
const modal = document.querySelector("[data-modal]");
const confirmBtn = document.querySelector("[confirm-btn]");

var esp_to_delete = "";

openBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        modal.showModal();
        esp_to_delete = btn.parentElement.textContent;
        console.log(esp_to_delete);
    })
});

closeBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        modal.close();
    })
});

confirmBtn.addEventListener("click", () =>{
    console.log(esp_to_delete + " deleted");
    modal.close();
})