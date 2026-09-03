/* مُكوّن خطة الاشتراك — data-driven بالكامل من #plan-matrix (نسخة Plan rows).
   ما في سعر ولا تركيبة ثابتة بالكود. */
(function () {
    "use strict";
    var root = document.getElementById("plan-builder");
    if (!root) return;

    var matrix = [];
    try { matrix = JSON.parse(document.getElementById("plan-matrix").textContent); } catch (e) { return; }
    if (!matrix.length) return;

    var goBase = root.dataset.goUrlBase || "/";
    var i18nEl = root.querySelector(".builder__i18n");
    var DAY = i18nEl.dataset.dayWord, MEAL_S = i18nEl.dataset.mealSingular, MEAL_P = i18nEl.dataset.mealPlural;

    var state = { type: null, meals: null, days: null };
    var STEPS = ["type", "meals", "days"];

    function combos(filter) {
        return matrix.filter(function (m) {
            return (filter.type == null || m.type === filter.type)
                && (filter.meals == null || m.meals === filter.meals)
                && (filter.days == null || m.days === filter.days);
        });
    }
    function distinct(list, key) {
        var seen = [], out = [];
        list.forEach(function (m) { if (seen.indexOf(m[key]) === -1) { seen.push(m[key]); out.push(m[key]); } });
        return out.sort(function (a, b) { return a - b; });
    }
    function mealsLabel(n) { return n + " " + (n === 1 ? MEAL_S : MEAL_P); }
    function daysLabel(n) { return n + " " + DAY; }

    function matchedPlan() {
        if (state.type == null || state.meals == null || state.days == null) return null;
        return combos(state)[0] || null;
    }

    // ---- render option pills for a step ----
    function renderOptions(step) {
        var wrap = root.querySelector('[data-options-for="' + step + '"]');
        if (!wrap) return;
        var opts;
        if (step === "meals") opts = distinct(combos({ type: state.type }), "meals");
        else opts = distinct(combos({ type: state.type, meals: state.meals }), "days");

        wrap.innerHTML = "";
        opts.forEach(function (val) {
            var b = document.createElement("button");
            b.type = "button";
            b.className = "builder-opt";
            b.setAttribute("role", "radio");
            b.setAttribute("aria-checked", String(state[step] === val));
            b.dataset.choice = step;
            b.dataset.value = String(val);
            b.textContent = step === "meals" ? mealsLabel(val) : daysLabel(val);
            if (state[step] === val) b.classList.add("is-selected");
            wrap.appendChild(b);
        });

        // اختيار تلقائي لو في خيار واحد بس
        if (opts.length === 1 && state[step] !== opts[0]) {
            select(step, opts[0], { silent: true });
        }
    }

    function stepEl(step) { return root.querySelector('.builder__step[data-step="' + step + '"]'); }

    function setStepEnabled(step, on) {
        var el = stepEl(step);
        if (!el) return;
        if (on) {
            el.hidden = false;
            // reflow ثم إزالة التعطيل لظهور ناعم
            void el.offsetWidth;
            el.removeAttribute("data-disabled");
        } else {
            el.setAttribute("data-disabled", "");
            el.hidden = true;
        }
    }

    // ---- progress indicator ----
    function renderProgress() {
        var current = state.type == null ? "type" : state.meals == null ? "meals" : "days";
        STEPS.forEach(function (step) {
            var li = root.querySelector('.builder__progress-step[data-progress="' + step + '"]');
            if (!li) return;
            li.classList.toggle("is-done", state[step] != null);
            li.classList.toggle("is-current", step === current && state[step] == null);
        });
    }

    // ---- selection + downstream invalidation ----
    function select(step, value, opts) {
        opts = opts || {};
        state[step] = value;

        // إلغاء الاختيارات اللاحقة إذا صارت غير صالحة
        var startIdx = STEPS.indexOf(step) + 1;
        for (var i = startIdx; i < STEPS.length; i++) {
            var later = STEPS[i];
            var valid = later === "meals"
                ? distinct(combos({ type: state.type }), "meals")
                : distinct(combos({ type: state.type, meals: state.meals }), "days");
            if (state[later] != null && valid.indexOf(state[later]) === -1) {
                state[later] = null;
            }
        }

        // حالة الاختيار البصرية بالخطوة الحالية (علامة الصح بالزاوية)
        root.querySelectorAll('[data-choice="' + step + '"]').forEach(function (btn) {
            var on = String(state[step]) === btn.dataset.value;
            btn.classList.toggle("is-selected", on);
            btn.setAttribute("aria-checked", String(on));
        });

        // تحديث الخطوات اللاحقة
        if (step === "type") { setStepEnabled("meals", true); renderOptions("meals"); }
        if (step === "type" || step === "meals") {
            var canDays = state.type != null && state.meals != null;
            setStepEnabled("days", canDays);
            if (canDays) renderOptions("days");
            else { var d = root.querySelector('[data-options-for="days"]'); if (d) d.innerHTML = ""; }
        }
        renderProgress();
        renderSummary();
    }

    // ---- summary + continue ----
    function renderSummary() {
        var empty = root.querySelector("[data-summary-empty]");
        var filled = root.querySelector("[data-summary-filled]");
        var cont = root.querySelector("[data-continue]");
        var plan = matchedPlan();
        var anySel = state.type != null;

        empty.hidden = anySel;
        filled.hidden = !anySel;

        if (anySel) {
            var typeName = (root.querySelector('[data-choice="type"][data-value="' + state.type + '"] .builder-opt__name') || {}).textContent || "—";
            root.querySelector("[data-sum-type]").textContent = typeName;

            var mealsRow = root.querySelector("[data-sum-meals-row]");
            mealsRow.hidden = state.meals == null;
            if (state.meals != null) root.querySelector("[data-sum-meals]").textContent = mealsLabel(state.meals);

            var daysRow = root.querySelector("[data-sum-days-row]");
            daysRow.hidden = state.days == null;
            if (state.days != null) root.querySelector("[data-sum-days]").textContent = daysLabel(state.days);

            var totalRow = root.querySelector("[data-sum-total-row]");
            totalRow.hidden = !plan;
            if (plan) root.querySelector("[data-sum-price]").textContent = Number(plan.price).toFixed(2);
        }

        var unavail = root.querySelector(".builder__unavailable");
        var noMatch = state.type != null && state.meals != null && state.days != null && !plan;
        unavail.hidden = !noMatch;

        if (plan) {
            cont.href = goBase + plan.id + "/?source=builder";
            cont.removeAttribute("aria-disabled");
            cont.removeAttribute("tabindex");
            cont.classList.remove("is-disabled");
        } else {
            cont.href = "#";
            cont.setAttribute("aria-disabled", "true");
            cont.setAttribute("tabindex", "-1");
            cont.classList.add("is-disabled");
        }
    }

    // ---- events ----
    root.addEventListener("click", function (e) {
        var btn = e.target.closest("[data-choice]");
        if (btn) {
            if (e.target.closest(".builder-opt__menu")) return;  // "شوف المنيو" رابط عادي
            select(btn.dataset.choice, isNaN(+btn.dataset.value) ? btn.dataset.value : +btn.dataset.value);
            btn.focus();
            return;
        }
        var cont = e.target.closest("[data-continue]");
        if (cont && cont.getAttribute("aria-disabled") === "true") e.preventDefault();
    });

    // كيبورد لمجموعات الراديو
    root.addEventListener("keydown", function (e) {
        var btn = e.target.closest('[data-choice]');
        if (!btn) return;
        var group = Array.prototype.slice.call(
            btn.closest("[role=radiogroup]").querySelectorAll('[data-choice]'));
        var i = group.indexOf(btn);
        if (["ArrowRight", "ArrowDown"].indexOf(e.key) > -1) { e.preventDefault(); (group[i + 1] || group[0]).focus(); }
        else if (["ArrowLeft", "ArrowUp"].indexOf(e.key) > -1) { e.preventDefault(); (group[i - 1] || group[group.length - 1]).focus(); }
        else if (e.key === " " || e.key === "Enter") { e.preventDefault(); btn.click(); }
    });

    renderProgress();
    renderSummary();
})();
