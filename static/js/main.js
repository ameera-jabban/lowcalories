// يسجل حدث "Lead" بـ Meta Pixel لحظة ما حدا يضغط زر واتساب (قبل ما يتنقل)
// آمن حتى لو الـ Pixel مو مفعّل (fbq غير معرّفة) — ما بيكسر شي
function fbqLead() {
    if (typeof fbq === "function") {
        fbq("track", "Lead");
    }
}

(function () {
    "use strict";

    /* ---------- هيدر لاصق: تأثير blur/ظل تدريجي عند التمرير ---------- */
    var header = document.getElementById("site-header");
    if (header) {
        var onScroll = function () {
            header.classList.toggle("header--scrolled", window.scrollY > 12);
        };
        onScroll();
        window.addEventListener("scroll", onScroll, { passive: true });
    }

    /* ---------- القائمة الكبيرة (overlay) — نفس التجربة على كل المقاسات ---------- */
    var toggle = document.getElementById("nav-toggle");
    var panel = document.getElementById("nav-panel");
    var panelMenu = document.getElementById("nav-panel-menu");
    var closeBtn = document.getElementById("nav-close");
    if (toggle && panel && panelMenu) {
        var lastFocused = null;
        var FOCUSABLE = 'a[href], button:not([disabled]), input, [tabindex]:not([tabindex="-1"])';

        var isOpen = function () { return panel.classList.contains("is-open"); };

        var openPanel = function () {
            lastFocused = document.activeElement;
            panel.hidden = false;
            requestAnimationFrame(function () { panel.classList.add("is-open"); });
            toggle.setAttribute("aria-expanded", "true");
            toggle.setAttribute("aria-label", toggle.dataset.labelClose || "إغلاق القائمة");
            document.body.classList.add("nav-open");
            document.addEventListener("keydown", onKey, true);
            window.setTimeout(function () { (closeBtn || panelMenu).focus(); }, 60);
        };

        var closePanel = function (refocus) {
            panel.classList.remove("is-open");
            toggle.setAttribute("aria-expanded", "false");
            toggle.setAttribute("aria-label", toggle.dataset.labelOpen || "افتح القائمة");
            document.body.classList.remove("nav-open");
            document.removeEventListener("keydown", onKey, true);
            window.setTimeout(function () { if (!isOpen()) panel.hidden = true; }, 420);
            if (refocus !== false && lastFocused && lastFocused.focus) lastFocused.focus();
        };

        function onKey(e) {
            if (e.key === "Escape") { e.preventDefault(); closePanel(); return; }
            if (e.key !== "Tab") return;
            var nodes = Array.prototype.filter.call(
                panelMenu.querySelectorAll(FOCUSABLE),
                function (el) { return el.offsetParent !== null; }
            );
            if (!nodes.length) return;
            var first = nodes[0], last = nodes[nodes.length - 1];
            if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
            else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
        }

        toggle.addEventListener("click", function () { isOpen() ? closePanel() : openPanel(); });
        if (closeBtn) closeBtn.addEventListener("click", function () { closePanel(); });
        panel.querySelectorAll("[data-nav-close]").forEach(function (el) {
            el.addEventListener("click", function (e) {
                // النقر داخل بطاقة العرض (البرومو) ما يغلق — روابطها تشتغل عادي
                if (e.target.closest(".nav-panel__promo")) return;
                closePanel();
            });
        });
        // اختيار وجهة تنقّل → إغلاق فوري (بدون إعادة تركيز — الصفحة رح تتغير)
        panel.querySelectorAll("[data-nav-close-link]").forEach(function (el) {
            el.addEventListener("click", function () { closePanel(false); });
        });
    }

    /* ---------- قائمة اللغة (أيقونة الكرة الأرضية بالنافبار) ---------- */
    var langWrap = document.querySelector("[data-lang-menu]");
    var langToggle = document.getElementById("lang-toggle");
    if (langWrap && langToggle) {
        var closeLang = function () { langWrap.classList.remove("is-open"); langToggle.setAttribute("aria-expanded", "false"); };
        langToggle.addEventListener("click", function (e) {
            e.stopPropagation();
            var open = langWrap.classList.toggle("is-open");
            langToggle.setAttribute("aria-expanded", String(open));
        });
        document.addEventListener("click", function (e) { if (!langWrap.contains(e.target)) closeLang(); });
        document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeLang(); });
    }

    /* ---------- قوائم منسدلة بالنافبار الأفقي (ديسكتوب) ---------- */
    var dropdowns = Array.prototype.slice.call(document.querySelectorAll("[data-nav-dropdown]"));
    dropdowns.forEach(function (dd) {
        var trigger = dd.querySelector(".primary-nav__trigger");
        if (!trigger) return;
        var closeDd = function () { dd.classList.remove("is-open"); trigger.setAttribute("aria-expanded", "false"); };
        var openDd = function () {
            dropdowns.forEach(function (o) { if (o !== dd) { o.classList.remove("is-open"); var t = o.querySelector(".primary-nav__trigger"); if (t) t.setAttribute("aria-expanded", "false"); } });
            dd.classList.add("is-open"); trigger.setAttribute("aria-expanded", "true");
        };
        trigger.addEventListener("click", function (e) {
            e.stopPropagation();
            dd.classList.contains("is-open") ? closeDd() : openDd();
        });
    });
    document.addEventListener("click", function () {
        dropdowns.forEach(function (dd) {
            dd.classList.remove("is-open");
            var t = dd.querySelector(".primary-nav__trigger");
            if (t) t.setAttribute("aria-expanded", "false");
        });
    });
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") dropdowns.forEach(function (dd) {
            dd.classList.remove("is-open");
            var t = dd.querySelector(".primary-nav__trigger");
            if (t) t.setAttribute("aria-expanded", "false");
        });
    });
})();

/* ---------- زر التمرير للأسفل بالهيرو ---------- */
(function () {
    "use strict";
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    document.querySelectorAll("[data-scroll-to]").forEach(function (link) {
        link.addEventListener("click", function (e) {
            var id = (link.getAttribute("href") || "").replace(/^.*#/, "#");
            var target = id && id.length > 1 ? document.querySelector(id) : null;
            if (!target) return;   // ما في قسم → نخلي الرابط عادي
            e.preventDefault();
            target.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
        });
    });
    // احترام تقليل الحركة: نوقف فيديو الهيرو ونعرض الـ poster
    if (reduce) {
        document.querySelectorAll("[data-hero-video]").forEach(function (v) {
            try { v.removeAttribute("autoplay"); v.pause(); } catch (e) {}
        });
    }
})();

/* ---------- عنوان الـ Hero المتغيّر ---------- */
(function () {
    "use strict";
    var rotator = document.querySelector(".hero__rotator");
    if (!rotator) return;
    var items = rotator.querySelectorAll(".hero__rotator-item");
    if (items.length < 2) return;
    var i = 0;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    setInterval(function () {
        items[i].classList.remove("is-active");
        i = (i + 1) % items.length;
        items[i].classList.add("is-active");
    }, 2200);
})();

/* ---------- كاروسيل التقييمات ---------- */
(function () {
    "use strict";
    document.querySelectorAll("[data-carousel]").forEach(function (root) {
        var track = root.querySelector("[data-carousel-track]");
        var prev = root.querySelector("[data-carousel-prev]");
        var next = root.querySelector("[data-carousel-next]");
        if (!track) return;
        var slides = Array.prototype.slice.call(track.querySelectorAll(".carousel__slide"));
        if (!slides.length) return;
        var idx = 0;
        var loop = root.hasAttribute("data-carousel-loop");
        var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

        function isRTL() { return getComputedStyle(track).direction === "rtl"; }

        function scrollByDir(dir) {
            // تمرير أفقي داخل المسار فقط — أبداً scrollIntoView (يمنع قفزة الصفحة
            // عمودياً) وأبداً .focus() (ما نسرق تركيز لوحة المفاتيح). dir موجب = التالي.
            var step = Math.max(240, track.clientWidth * 0.85);
            var delta = step * dir * (isRTL() ? -1 : 1);
            var atEnd = !canScroll(dir);
            if (atEnd && loop) { track.scrollTo({ left: isRTL() ? 0 : (track.scrollWidth), behavior: reduceMotion ? "auto" : "smooth" }); }
            else track.scrollBy({ left: delta, behavior: reduceMotion ? "auto" : "smooth" });
            window.setTimeout(syncNav, 350);
        }

        function canScroll(dir) {
            // dir موجب = "التالي": في LTR يعني scrollLeft يزيد، في RTL يقل (سالب)
            var max = track.scrollWidth - track.clientWidth;
            var sl = Math.abs(track.scrollLeft);
            return dir > 0 ? sl < max - 2 : sl > 2;
        }

        function syncNav() {
            if (loop) return;
            if (prev) prev.disabled = !canScroll(-1);
            if (next) next.disabled = !canScroll(1);
        }

        // مزامنة idx مع أقرب شريحة عند السحب اليدوي (بدون سرقة تركيز)
        track.addEventListener("scroll", function () {
            var mid = track.scrollLeft + track.clientWidth / 2;
            var best = 0, bestD = Infinity;
            slides.forEach(function (s, k) {
                var c = Math.abs(s.offsetLeft + s.offsetWidth / 2 - mid);
                if (c < bestD) { bestD = c; best = k; }
            });
            idx = best;
            syncNav();
        }, { passive: true });

        // ضغط الأسهم: التركيز يبقى على الزر المضغوط (ما ننقله للشريحة)
        if (prev) prev.addEventListener("click", function () { scrollByDir(-1); });
        if (next) next.addEventListener("click", function () { scrollByDir(1); });
        syncNav();

        // تقدّم تلقائي — opt-in فقط عبر data-carousel-autoplay، ويتوقف عند التفاعل
        var timer = null;
        var autoplay = root.hasAttribute("data-carousel-autoplay");
        function start() {
            if (timer || !autoplay || slides.length < 2 || reduceMotion) return;
            timer = setInterval(function () { scrollByDir(loop ? 1 : (idx >= slides.length - 1 ? -idx : 1)); }, 6000);
        }
        function stop() { clearInterval(timer); timer = null; }
        if (autoplay) {
            ["mouseenter", "touchstart", "focusin"].forEach(function (e) { root.addEventListener(e, stop, { passive: true }); });
            ["mouseleave", "touchend", "focusout"].forEach(function (e) { root.addEventListener(e, start, { passive: true }); });
            document.addEventListener("visibilitychange", function () { document.hidden ? stop() : start(); });
            start();
        }
    });
})();

/* ---------- منع الإرسال المزدوج للفورم (data-once) ---------- */
(function () {
    "use strict";
    document.querySelectorAll("form").forEach(function (form) {
        var btn = form.querySelector("[data-once]");
        if (!btn) return;
        form.addEventListener("submit", function () {
            window.setTimeout(function () { btn.disabled = true; btn.classList.add("is-busy"); }, 0);
        });
    });
})();

/* ---------- تبويبات أيام المنيو الأسبوعي ---------- */
(function () {
    "use strict";
    var tabs = document.querySelector("[data-day-tabs]");
    if (!tabs) return;
    var btns = Array.prototype.slice.call(tabs.querySelectorAll('[role="tab"]'));
    btns.forEach(function (btn) {
        btn.addEventListener("click", function () {
            btns.forEach(function (b) {
                var on = b === btn;
                b.classList.toggle("is-active", on);
                b.setAttribute("aria-selected", String(on));
                var panel = document.getElementById(b.getAttribute("aria-controls"));
                if (panel) panel.hidden = !on;
            });
        });
        btn.addEventListener("keydown", function (e) {
            var i = btns.indexOf(btn);
            if (["ArrowRight", "ArrowDown"].indexOf(e.key) > -1) { e.preventDefault(); (btns[i + 1] || btns[0]).focus(); }
            else if (["ArrowLeft", "ArrowUp"].indexOf(e.key) > -1) { e.preventDefault(); (btns[i - 1] || btns[btns.length - 1]).focus(); }
        });
    });
})();

/* ---------- نسخ للحافظة (كود/رابط الإحالة) — بدون alert ---------- */
(function () {
    "use strict";
    document.querySelectorAll("[data-copy]").forEach(function (btn) {
        var label = btn.querySelector("span");
        var original = label ? label.textContent : "";
        btn.addEventListener("click", function () {
            var text = btn.getAttribute("data-copy") || "";
            var done = function () {
                btn.classList.add("is-copied");
                if (label) label.textContent = btn.getAttribute("data-copied") || original;
                window.setTimeout(function () {
                    btn.classList.remove("is-copied");
                    if (label) label.textContent = original;
                }, 1800);
            };
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(done).catch(fallback);
            } else { fallback(); }
            function fallback() {
                var t = document.createElement("textarea");
                t.value = text; t.style.position = "fixed"; t.style.opacity = "0";
                document.body.appendChild(t); t.select();
                try { document.execCommand("copy"); done(); } catch (e) {}
                document.body.removeChild(t);
            }
        });
    });
})();

/* ---------- أكورديون الأسئلة الشائعة ---------- */
(function () {
    "use strict";
    document.querySelectorAll("[data-accordion]").forEach(function (acc) {
        var multi = acc.hasAttribute("data-accordion-multi");
        var triggers = acc.querySelectorAll(".accordion__trigger");
        triggers.forEach(function (btn) {
            btn.addEventListener("click", function () {
                var expanded = btn.getAttribute("aria-expanded") === "true";
                if (!multi) {
                    // بند واحد مفتوح كل مرة (allowMultipleOpen = false)
                    triggers.forEach(function (other) {
                        if (other === btn) return;
                        other.setAttribute("aria-expanded", "false");
                        var p = document.getElementById(other.getAttribute("aria-controls"));
                        if (p) p.hidden = true;
                    });
                }
                btn.setAttribute("aria-expanded", expanded ? "false" : "true");
                var panel = document.getElementById(btn.getAttribute("aria-controls"));
                if (panel) panel.hidden = expanded;
            });
        });
    });
})();
