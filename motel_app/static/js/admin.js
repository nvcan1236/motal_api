let statsForm = "chart"
const chartForm = document.getElementById("chart-form")
const tableForm = document.getElementById("table-form")
const switchButton = document.getElementById("switch-button")
console.log("aloooo")
const switchForm = function () {
    if (statsForm === "chart") {
        chartForm.classList.remove("d-none")
        tableForm.classList.add("d-none")
        switchButton.innerHtml = "Xem biểu đồ thống kê"
    } else {
        chartForm.classList.add("d-none")
        tableForm.classList.remove("d-none")
        switchButton.innerHtml = "Xem bảng báo cáo"
    }
}