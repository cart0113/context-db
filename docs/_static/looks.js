/*
 * Look picker: a small panel for trying out style ideas for the docs.
 *
 * Temporary. The styles are in looks.css; see the note at the top of that file
 * for how to remove both. Picks are kept in this browser's localStorage and
 * set as data-cdb-* attributes on <html>.
 */
(function () {
  "use strict";

  var PICKS_KEY = "cdb-looks-2";
  var OPEN_KEY = "cdb-looks-open";

  // The first option of every group is the site as it is, and sets nothing.
  var GROUPS = [
    {
      id: "headings",
      label: "Section headings",
      options: [
        ["current", "Underline"],
        ["slash", "Slash"],
        ["chevron", "Chevron"],
      ],
    },
    {
      id: "cards",
      label: "Command cards (home page)",
      options: [
        ["current", "Plain"],
        ["stripe", "Top stripe"],
        ["window", "Window"],
        ["spotlight", "Spotlight"],
      ],
    },
  ];

  // Extras are on or off, and any number can be on.
  var EXTRAS = [
    ["typed", "Typed title (home page)"],
    ["brandslash", "Slash in the header"],
    ["drift", "Drifting backdrop"],
    ["pointer", "Pointer glow"],
    ["pillnav", "Pill nav"],
    ["mononav", "Mono nav"],
    ["codeglow", "Code glow"],
  ];

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

  function element(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  // ── Behavior that two of the ideas need ──────────────────────────────────

  // Pointer glow: one element behind the page, moved with the pointer.
  function syncPointerGlow() {
    var glow = document.querySelector(".cdb-pointer-glow");
    if (picks.pointer !== "on") {
      if (glow) glow.remove();
      return;
    }
    if (!glow) document.body.appendChild(element("div", "cdb-pointer-glow"));
  }

  // The pointer's position, for the glow and for the Spotlight cards.
  function trackPointer() {
    var waiting = false;
    window.addEventListener(
      "pointermove",
      function (event) {
        if (waiting) return;
        waiting = true;
        requestAnimationFrame(function () {
          waiting = false;
          var glow = document.querySelector(".cdb-pointer-glow");
          if (glow) {
            glow.style.setProperty("--cdb-mx", event.clientX + "px");
            glow.style.setProperty("--cdb-my", event.clientY + "px");
          }
          var card = event.target.closest && event.target.closest(".command-card");
          if (card) {
            var box = card.getBoundingClientRect();
            card.style.setProperty("--cdb-cx", event.clientX - box.left + "px");
            card.style.setProperty("--cdb-cy", event.clientY - box.top + "px");
          }
        });
      },
      { passive: true }
    );
    document.querySelectorAll(".command-card").forEach(function (card) {
      card.addEventListener("pointerleave", function () {
        card.style.removeProperty("--cdb-cx");
        card.style.removeProperty("--cdb-cy");
      });
    });
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
    }

    function commit() {
      write(PICKS_KEY, picks);
      apply();
      syncPointerGlow();
      refresh();
    }

    function refresh() {
      buttons.forEach(function (pair) {
        pair[0].setAttribute("aria-pressed", pair[1]() ? "true" : "false");
      });
      readout.textContent = summary();
    }

    GROUPS.forEach(function (group) {
      var row = chips(group.label);
      group.options.forEach(function (option) {
        chip(
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

    panel.appendChild(element("div", "cdb-looks__label", "Your picks, to tell Claude"));
    var readout = panel.appendChild(element("div", "cdb-looks__picks"));
    var actions = panel.appendChild(element("div", "cdb-looks__chips"));

    var copy = actions.appendChild(element("button", "", "Copy picks"));
    copy.type = "button";
    copy.addEventListener("click", function () {
      var text = "Looks: " + summary();
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function () {
          copy.textContent = "Copied";
          setTimeout(function () {
            copy.textContent = "Copy picks";
          }, 1400);
        });
      } else {
        // No clipboard on plain http: select the line so that Ctrl+C takes it.
        window.getSelection().selectAllChildren(readout);
      }
    });

    var clear = actions.appendChild(element("button", "", "All off"));
    clear.type = "button";
    clear.addEventListener("click", function () {
      picks = {};
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
    syncPointerGlow();
    trackPointer();
    buildPanel();
  });
})();
