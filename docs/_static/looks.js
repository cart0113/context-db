/*
 * Look picker: a small panel for trying out styles for the docs.
 *
 * Temporary. The styles are in looks.css; see the note at the top of that file
 * for how to remove both. Picks are kept in this browser's localStorage and
 * set as data-cdb-* attributes on <html>.
 */
(function () {
  "use strict";

  var PICKS_KEY = "cdb-looks";
  var OPEN_KEY = "cdb-looks-open";

  // The first option of every group is the site as it is, and sets nothing.
  var GROUPS = [
    {
      id: "colors",
      label: "Colors",
      options: [
        ["current", "As it is", "#10b981, #06b6d4, #8b5cf6, #ec4899"],
        ["sunset", "Sunset", "#f59e0b, #f97316, #f43f5e, #a855f7"],
        ["ocean", "Ocean", "#14b8a6, #0ea5e9, #3b82f6, #6366f1"],
        ["candy", "Candy", "#ec4899, #d946ef, #8b5cf6, #38bdf8"],
        ["lime", "Lime", "#10b981, #22c55e, #84cc16, #eab308"],
        ["ink", "Ink", "#0f172a, #0f172a, #f43f5e"],
      ],
    },
    {
      id: "title",
      label: "Title (home page)",
      options: [
        ["current", "As it is"],
        ["flow", "Flow"],
        ["glow", "Glow"],
        ["marker", "Marker"],
        ["cursor", "Cursor"],
      ],
    },
    {
      id: "backdrop",
      label: "Backdrop",
      options: [
        ["current", "Plain"],
        ["aurora", "Aurora"],
        ["wash", "Wash"],
        ["dots", "Dots"],
        ["grid", "Grid"],
      ],
    },
    {
      id: "headings",
      label: "Section headings",
      options: [
        ["current", "Underline"],
        ["bar", "Bar"],
        ["text", "Gradient text"],
        ["hash", "Hash"],
        ["band", "Band"],
      ],
    },
    {
      id: "cards",
      label: "Command cards (home page)",
      options: [
        ["current", "Top stripe"],
        ["glow", "Glow"],
        ["fill", "Fill"],
        ["prompt", "Prompt"],
      ],
    },
    {
      id: "code",
      label: "Code blocks",
      options: [
        ["current", "Side stripe"],
        ["window", "Window"],
        ["dark", "Dark"],
        ["terminal", "Terminal"],
        ["gradient", "Gradient"],
      ],
    },
    {
      id: "header",
      label: "Header bar",
      options: [
        ["current", "Stripe"],
        ["flow", "Moving stripe"],
        ["glass", "Glass"],
        ["bold", "Bold"],
      ],
    },
    {
      id: "font",
      label: "Heading font",
      options: [
        ["current", "System"],
        ["grotesk", "Space Grotesk"],
        ["outfit", "Outfit"],
        ["serif", "Fraunces"],
        ["mono", "JetBrains Mono"],
      ],
    },
  ];

  // Extras are on or off, and any number can be on.
  var EXTRAS = [
    ["demo", "Terminal demo (home page)"],
    ["buttons", "Gradient button (home page)"],
    ["cmdcolor", "Command colors (Commands page)"],
    ["progress", "Scroll bar"],
    ["motion", "Scroll-in motion"],
  ];

  var PRESETS = [
    ["As it is", {}],
    [
      "Aurora",
      {
        title: "flow",
        backdrop: "aurora",
        headings: "bar",
        cards: "glow",
        code: "window",
        header: "glass",
        font: "grotesk",
        buttons: "on",
        progress: "on",
      },
    ],
    [
      "Sunset",
      {
        colors: "sunset",
        title: "glow",
        backdrop: "wash",
        headings: "text",
        cards: "fill",
        code: "gradient",
        header: "flow",
        font: "outfit",
        buttons: "on",
        motion: "on",
      },
    ],
    [
      "Ocean",
      {
        colors: "ocean",
        title: "flow",
        backdrop: "dots",
        headings: "bar",
        cards: "glow",
        code: "dark",
        header: "bold",
        font: "grotesk",
        cmdcolor: "on",
        progress: "on",
      },
    ],
    [
      "Candy",
      {
        colors: "candy",
        title: "marker",
        backdrop: "aurora",
        headings: "band",
        cards: "fill",
        code: "gradient",
        header: "glass",
        font: "outfit",
        buttons: "on",
        motion: "on",
      },
    ],
    [
      "Terminal",
      {
        colors: "lime",
        title: "cursor",
        backdrop: "grid",
        headings: "hash",
        cards: "prompt",
        code: "terminal",
        font: "mono",
        demo: "on",
        cmdcolor: "on",
      },
    ],
    [
      "Editorial",
      {
        colors: "ink",
        title: "marker",
        headings: "bar",
        code: "window",
        font: "serif",
        progress: "on",
      },
    ],
  ];

  var FONT_URLS = {
    grotesk: "Space+Grotesk:wght@500;700",
    outfit: "Outfit:wght@500;700;800",
    serif: "Fraunces:opsz,wght@9..144,600;9..144,800",
    mono: "JetBrains+Mono:wght@500;700;800",
  };

  var root = document.documentElement;
  var picks = read(PICKS_KEY, {});

  function read(key, fallback) {
    try {
      var value = JSON.parse(localStorage.getItem(key));
      return value === null ? fallback : value;
    } catch (error) {
      return fallback;
    }
  }

  function write(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      /* Private windows can refuse storage; the picks then last one page. */
    }
  }

  function picked(group) {
    return picks[group.id] || group.options[0][0];
  }

  function apply() {
    GROUPS.forEach(function (group) {
      var value = picked(group);
      if (value === group.options[0][0]) root.removeAttribute("data-cdb-" + group.id);
      else root.setAttribute("data-cdb-" + group.id, value);
    });
    EXTRAS.forEach(function (extra) {
      if (picks[extra[0]] === "on") root.setAttribute("data-cdb-" + extra[0], "on");
      else root.removeAttribute("data-cdb-" + extra[0]);
    });
    loadFont(picks.font);
  }

  function loadFont(font) {
    if (!FONT_URLS[font] || document.getElementById("cdb-font-" + font)) return;
    var link = document.createElement("link");
    link.id = "cdb-font-" + font;
    link.rel = "stylesheet";
    link.href = "https://fonts.googleapis.com/css2?family=" + FONT_URLS[font] + "&display=swap";
    document.head.appendChild(link);
  }

  // What to tell Claude: every pick that differs from the site as it is.
  function summary() {
    var parts = [];
    GROUPS.forEach(function (group) {
      if (picked(group) !== group.options[0][0]) parts.push(group.id + "=" + picked(group));
    });
    var extras = EXTRAS.filter(function (extra) {
      return picks[extra[0]] === "on";
    }).map(function (extra) {
      return extra[0];
    });
    if (extras.length) parts.push("extras=" + extras.join("+"));
    return parts.length ? parts.join(" ") : "as it is";
  }

  // This script is loaded in <head>, so the picks are in place before the
  // first paint.
  apply();

  // ── Behavior that some extras need ────────────────────────────────────────

  function trackScroll() {
    function update() {
      var range = root.scrollHeight - window.innerHeight;
      root.style.setProperty("--cdb-progress", range > 0 ? Math.min(1, window.scrollY / range) : 0);
    }
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    update();
  }

  function watchReveals() {
    var targets = document.querySelectorAll(
      ".bd-article h2, .bd-article .sd-col, .bd-article .sd-tab-set, .bd-article table, .cdb-demo"
    );
    if (!("IntersectionObserver" in window)) return;
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("cdb-in");
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px" }
    );
    targets.forEach(function (target) {
      target.classList.add("cdb-reveal");
      observer.observe(target);
    });
  }

  // ── The terminal demo ────────────────────────────────────────────────────

  var DEMO_TYPED = [
    "/context-db prompt",
    "",
    "Users report a bug here:",
    "",
    "https://issues.example.com/PAY-482",
    "",
    "It looks like it is in the new receipts database code.",
    "Can you investigate and propose a fix?",
  ].join("\n");

  var DEMO_STEPS = [
    ["Read", "wip/receipts-table.md", "the plan for the work in progress"],
    ["Read", "acme-payments-project/index.md", "one line for every file"],
    ["Read", "data-model/schema-conventions.md", "its description fits the task"],
    ["Skip", "11 other files", "nothing to do with receipts"],
  ];

  var demoTimer = null;

  function element(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function playDemo(body) {
    clearTimeout(demoTimer);
    body.textContent = "";
    body.appendChild(element("span", "cdb-demo__mark", "❯ "));
    var typed = body.appendChild(element("span"));
    var cursor = body.appendChild(element("span", "cdb-demo__cursor"));
    var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var typedCount = 0;
    var stepCount = 0;

    function addStep() {
      var step = DEMO_STEPS[stepCount++];
      var line = element("span", "cdb-demo__step" + (step[0] === "Skip" ? " is-skip" : ""));
      line.appendChild(element("b", "", "● " + step[0] + " "));
      line.appendChild(document.createTextNode(step[1] + "  "));
      line.appendChild(element("em", "", step[2]));
      body.appendChild(line);
    }

    function tick() {
      if (typedCount < DEMO_TYPED.length) {
        typedCount += 1;
        typed.textContent = DEMO_TYPED.slice(0, typedCount);
        demoTimer = setTimeout(tick, DEMO_TYPED[typedCount - 1] === "\n" ? 140 : 22);
      } else if (stepCount < DEMO_STEPS.length) {
        if (stepCount === 0) {
          cursor.remove();
          body.appendChild(document.createTextNode("\n\n"));
        }
        addStep();
        demoTimer = setTimeout(tick, 650);
      }
    }

    if (still) {
      typed.textContent = DEMO_TYPED;
      cursor.remove();
      body.appendChild(document.createTextNode("\n\n"));
      while (stepCount < DEMO_STEPS.length) addStep();
    } else {
      demoTimer = setTimeout(tick, 500);
    }
  }

  function syncDemo() {
    var existing = document.querySelector(".cdb-demo");
    var anchor = document.querySelector("section#context-db .hero-buttons");
    if (picks.demo !== "on" || !anchor) {
      clearTimeout(demoTimer);
      if (existing) existing.remove();
      return;
    }
    if (existing) return;

    var demo = element("div", "cdb-demo");
    var bar = demo.appendChild(element("div", "cdb-demo__bar"));
    bar.appendChild(element("i"));
    bar.appendChild(element("i"));
    bar.appendChild(element("i"));
    bar.appendChild(element("span", "", "claude"));
    var replay = bar.appendChild(element("button", "", "replay"));
    replay.type = "button";
    var body = demo.appendChild(element("div", "cdb-demo__body"));
    anchor.insertAdjacentElement("afterend", demo);
    replay.addEventListener("click", function () {
      playDemo(body);
    });
    playDemo(body);
  }

  // ── The panel ────────────────────────────────────────────────────────────

  function buildPanel() {
    var toggle = element("button", "cdb-looks-toggle", "Looks");
    toggle.type = "button";
    toggle.setAttribute("aria-expanded", "false");
    var panel = element("div", "cdb-looks");
    panel.hidden = true;
    var buttons = [];

    function chips(label) {
      panel.appendChild(element("div", "cdb-looks__label", label));
      return panel.appendChild(element("div", "cdb-looks__chips"));
    }

    function chip(parent, text, isOn, onClick) {
      var button = parent.appendChild(element("button", "", text));
      button.type = "button";
      button.addEventListener("click", function () {
        onClick();
        commit();
      });
      buttons.push([button, isOn]);
      return button;
    }

    function commit() {
      write(PICKS_KEY, picks);
      apply();
      syncDemo();
      refresh();
    }

    function refresh() {
      buttons.forEach(function (pair) {
        pair[0].setAttribute("aria-pressed", pair[1]() ? "true" : "false");
      });
      readout.textContent = summary();
    }

    var presetRow = chips("Whole looks");
    PRESETS.forEach(function (preset) {
      chip(
        presetRow,
        preset[0],
        function () {
          return JSON.stringify(picks, Object.keys(picks).sort()) ===
            JSON.stringify(preset[1], Object.keys(preset[1]).sort());
        },
        function () {
          picks = JSON.parse(JSON.stringify(preset[1]));
        }
      );
    });

    GROUPS.forEach(function (group) {
      var row = chips(group.label);
      group.options.forEach(function (option) {
        var button = chip(
          row,
          option[1],
          function () {
            return picked(group) === option[0];
          },
          function () {
            if (option[0] === group.options[0][0]) delete picks[group.id];
            else picks[group.id] = option[0];
          }
        );
        if (option[2]) {
          var dot = element("span", "cdb-looks__dot");
          dot.style.background = "linear-gradient(135deg, " + option[2] + ")";
          button.insertBefore(dot, button.firstChild);
        }
      });
    });

    var extraRow = chips("Extras (any number)");
    EXTRAS.forEach(function (extra) {
      chip(
        extraRow,
        extra[1],
        function () {
          return picks[extra[0]] === "on";
        },
        function () {
          if (picks[extra[0]] === "on") delete picks[extra[0]];
          else picks[extra[0]] = "on";
        }
      );
    });

    var foot = panel.appendChild(element("div", "cdb-looks__foot"));
    foot.appendChild(element("div", "cdb-looks__label", "Your picks, to tell Claude"));
    var readout = foot.appendChild(element("div", "cdb-looks__picks"));
    var actions = foot.appendChild(element("div", "cdb-looks__chips"));

    var copy = actions.appendChild(element("button", "", "Copy picks"));
    copy.type = "button";
    copy.addEventListener("click", function () {
      var text = "Looks: " + summary();
      var done = function () {
        copy.textContent = "Copied";
        setTimeout(function () {
          copy.textContent = "Copy picks";
        }, 1400);
      };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done, function () {});
      } else {
        // No clipboard on plain http: select the line so that Ctrl+C takes it.
        window.getSelection().selectAllChildren(readout);
      }
    });

    var shuffle = actions.appendChild(element("button", "", "Shuffle"));
    shuffle.type = "button";
    shuffle.addEventListener("click", function () {
      picks = {};
      GROUPS.forEach(function (group) {
        var option = group.options[Math.floor(Math.random() * group.options.length)];
        if (option[0] !== group.options[0][0]) picks[group.id] = option[0];
      });
      EXTRAS.forEach(function (extra) {
        if (Math.random() < 0.35) picks[extra[0]] = "on";
      });
      commit();
    });

    function setOpen(open) {
      panel.hidden = !open;
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      write(OPEN_KEY, open);
    }
    toggle.addEventListener("click", function () {
      setOpen(panel.hidden);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !panel.hidden) setOpen(false);
    });

    document.body.appendChild(panel);
    document.body.appendChild(toggle);
    refresh();
    setOpen(read(OPEN_KEY, false) === true);
  }

  document.addEventListener("DOMContentLoaded", function () {
    syncDemo();
    trackScroll();
    watchReveals();
    buildPanel();
  });
})();
