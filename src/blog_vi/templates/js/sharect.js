document.addEventListener("DOMContentLoaded", function (event) {
    let sharectConfig = window['sharectConfig']

    Sharect.init()

    Sharect.config({
        ...sharectConfig
    }).init()
})
