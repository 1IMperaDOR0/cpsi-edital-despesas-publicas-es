// Alterna entre tema claro e escuro e guarda a escolha no navegador.
// O tema inicial é aplicado por um script no <head> (ver app.py).
(function () {
  var STORAGE_KEY = "cpsi-theme";

  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {
      // Sem localStorage (janela anônima, bloqueio): o tema vale só para esta visita.
    }
  }

  // Delegação de evento: o botão é criado pelo React depois que este script carrega.
  document.addEventListener("click", function (event) {
    var button = event.target.closest && event.target.closest("#theme-toggle");
    if (!button) return;
    applyTheme(currentTheme() === "dark" ? "light" : "dark");
  });
})();
