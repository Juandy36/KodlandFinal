// Asistente virtual: envia el mensaje a /enviar_mensaje y muestra la respuesta.
// Se usa textContent / createTextNode (nunca innerHTML) para evitar XSS.
(function () {
  "use strict";

  var form = document.getElementById("chat-form");
  var input = document.getElementById("user-message");
  var messages = document.getElementById("messages");
  var chatBox = document.getElementById("chat-box");
  if (!form || !input || !messages || !chatBox) return;

  var submitButton = form.querySelector('button[type="submit"]');

  function agregarMensaje(texto, autor, esError) {
    var div = document.createElement("div");
    div.className = autor === "usuario" ? "user-message" : "bot-message";
    if (esError) div.classList.add("is-error");

    // Prefijo solo para lectores de pantalla, para saber quien habla.
    var etiqueta = document.createElement("span");
    etiqueta.className = "visually-hidden";
    etiqueta.textContent = autor === "usuario" ? "Tú: " : "Asistente: ";

    div.appendChild(etiqueta);
    div.appendChild(document.createTextNode(texto));
    messages.appendChild(div);

    chatBox.scrollTop = chatBox.scrollHeight;
  }

  function textoRespuesta(respuesta) {
    // Algunas respuestas del backend son listas de opciones.
    if (Array.isArray(respuesta)) return respuesta.join("\n");
    return String(respuesta);
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();

    var mensaje = input.value.trim();
    if (mensaje === "") {
      input.focus();
      return;
    }

    agregarMensaje(mensaje, "usuario");
    input.value = "";
    input.focus();
    if (submitButton) submitButton.disabled = true;

    fetch("/enviar_mensaje", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: mensaje })
    })
      .then(function (response) {
        if (!response.ok) throw new Error("HTTP " + response.status);
        return response.json();
      })
      .then(function (data) {
        agregarMensaje(textoRespuesta(data.response), "bot");
      })
      .catch(function () {
        agregarMensaje("No se pudo contactar con el asistente. Revisa tu conexión e inténtalo de nuevo.", "bot", true);
      })
      .then(function () {
        if (submitButton) submitButton.disabled = false;
        input.focus();
      });
  });

  // Sugerencias rapidas: rellenan el campo y envian el formulario.
  var sugerencias = document.querySelectorAll("[data-mensaje]");
  Array.prototype.forEach.call(sugerencias, function (boton) {
    boton.addEventListener("click", function () {
      input.value = boton.getAttribute("data-mensaje");
      if (typeof form.requestSubmit === "function") {
        form.requestSubmit();
      } else {
        form.dispatchEvent(new Event("submit", { cancelable: true }));
      }
    });
  });
})();
