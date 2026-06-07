document.addEventListener('DOMContentLoaded', function () {

  // ========== SESSION TIMER ==========
  const timerEl = document.getElementById('sessionTimer');
  let segundosRestantes = 30 * 60;

  if (timerEl) {
    setInterval(function () {
      segundosRestantes--;
      if (segundosRestantes < 0) segundosRestantes = 0;
      const min = Math.floor(segundosRestantes / 60);
      const seg = segundosRestantes % 60;
      timerEl.textContent = '⏱ Sesión expira en ' + String(min).padStart(2, '0') + ':' + String(seg).padStart(2, '0');
      if (segundosRestantes < 300) {
        timerEl.style.background = 'rgba(198,40,40,0.3)';
      }
      if (segundosRestantes === 0) {
        mostrarReAuth();
      }
    }, 1000);
  }

  function mostrarReAuth() {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.id = 'reauthOverlay';
    overlay.innerHTML =
      '<div class="modal-card" onclick="event.stopPropagation()">' +
        '<h3>🔐 Su sesión ha expirado</h3>' +
        '<p style="margin-bottom:16px;font-size:0.9rem">Ingrese su código MFA para re-autenticarse.</p>' +
        '<div class="mfa-inputs">' +
          '<input type="text" maxlength="1" class="mfa-box reauth-box">' +
          '<input type="text" maxlength="1" class="mfa-box reauth-box">' +
          '<input type="text" maxlength="1" class="mfa-box reauth-box">' +
          '<input type="text" maxlength="1" class="mfa-box reauth-box">' +
          '<input type="text" maxlength="1" class="mfa-box reauth-box">' +
          '<input type="text" maxlength="1" class="mfa-box reauth-box">' +
        '</div>' +
        '<div style="margin-top:16px;text-align:center">' +
          '<button class="btn btn-primary" onclick="reautenticar()">Re-autenticar</button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(overlay);
  }

  window.reautenticar = function () {
    const boxes = document.querySelectorAll('.reauth-box');
    let code = '';
    boxes.forEach(function (b) { code += b.value; });
    if (code.length === 6) {
      segundosRestantes = 30 * 60;
      document.getElementById('reauthOverlay').remove();
    } else {
      alert('Ingrese los 6 dígitos del código MFA.');
    }
  };

  // Auto-advance MFA inputs
  document.querySelectorAll('.mfa-box').forEach(function (input, idx) {
    input.addEventListener('input', function () {
      const allBoxes = document.querySelectorAll('.mfa-box');
      if (this.value && idx < allBoxes.length - 1) {
        allBoxes[idx + 1].focus();
      }
    });
  });

  // ========== NOTIFICATIONS PANEL ==========
  window.toggleNotifications = function () {
    const panel = document.getElementById('notifPanel');
    const overlay = document.getElementById('notifOverlay');
    if (panel) {
      panel.classList.toggle('open');
      overlay.style.display = panel.classList.contains('open') ? 'block' : 'none';
    }
  };

  // ========== LIVE TIMESTAMP ==========
  const tsEl = document.getElementById('liveTimestamp');
  if (tsEl) {
    function actualizarTimestamp() {
      const ahora = new Date();
      const utc5 = new Date(ahora.getTime() - 5 * 60 * 60 * 1000);
      const h = String(utc5.getUTCHours()).padStart(2, '0');
      const m = String(utc5.getUTCMinutes()).padStart(2, '0');
      const s = String(utc5.getUTCSeconds()).padStart(2, '0');
      tsEl.textContent = h + ':' + m + ':' + s + ' UTC-5';
    }
    actualizarTimestamp();
    setInterval(actualizarTimestamp, 1000);
  }
});
