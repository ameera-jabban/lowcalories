/* كود خصم صفحة الخطط — تحقّق عبر endpoint خفيف ثم حساب السعر المخفّض محلياً.
   ⚠️ عرض استرشادي فقط؛ الخصم الفعلي يطبّقه الفريق على واتساب. */
(function () {
  "use strict";
  document.addEventListener("DOMContentLoaded", function () {
    var box = document.getElementById("discount-box");
    if (!box) return;

    var input = document.getElementById("discount-input");
    var btn = document.getElementById("discount-apply");
    var msg = document.getElementById("discount-msg");
    var urlTemplate = box.dataset.validateUrl; // .../validate-code/CODE/

    function money(n) { return n.toFixed(2); }

    // كل بطاقة خطة = .mcard المعتمدة داخل .plans-grid
    function cards() { return document.querySelectorAll(".plans-grid .mcard"); }

    function reset() {
      cards().forEach(function (card) {
        var priceEl = card.querySelector(".mcard__price");
        if (!priceEl || !priceEl.dataset.price) return;
        card.querySelector(".mcard__price-now").textContent = money(parseFloat(priceEl.dataset.price));
        var oldEl = card.querySelector(".mcard__price-was");
        oldEl.hidden = true;
        oldEl.textContent = "";
        var link = card.querySelector(".mcard__cta");
        if (link) link.href = link.dataset.base;
      });
    }

    function apply(code, pct) {
      cards().forEach(function (card) {
        var priceEl = card.querySelector(".mcard__price");
        if (!priceEl || !priceEl.dataset.price) return;
        var base = parseFloat(priceEl.dataset.price);
        card.querySelector(".mcard__price-now").textContent = money(base * (1 - pct / 100));
        var oldEl = card.querySelector(".mcard__price-was");
        oldEl.textContent = money(base);
        oldEl.hidden = false;
        var link = card.querySelector(".mcard__cta");
        if (link) link.href = link.dataset.base + "&code=" + encodeURIComponent(code);
      });
    }

    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") { e.preventDefault(); btn.click(); }
    });

    btn.addEventListener("click", function () {
      var code = input.value.trim();
      msg.textContent = "";
      msg.className = "discount-msg";
      if (!code) { reset(); return; }

      fetch(urlTemplate.replace(/CODE\/$/, encodeURIComponent(code) + "/"), {
        headers: { "X-Requested-With": "XMLHttpRequest" }
      })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          if (data.valid) {
            apply(data.code, data.discount_percent);
            msg.textContent = "−" + data.discount_percent + "%";
            msg.classList.add("discount-msg--ok");
          } else {
            reset();
            msg.textContent = data.error || box.dataset.msgInvalid || "";
            msg.classList.add("discount-msg--err");
          }
        })
        .catch(function () {
          reset();
          msg.textContent = box.dataset.msgError || "";
          msg.classList.add("discount-msg--err");
        });
    });
  });
})();
