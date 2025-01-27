import { k as ne, A as ve, c as pe, f as we } from "./Index-cnwSUJS7.js";
var ke = function(e, t, n) {
  for (var a = n, i = 0, l = e.length; a < t.length; ) {
    var f = t[a];
    if (i <= 0 && t.slice(a, a + l) === e)
      return a;
    f === "\\" ? a++ : f === "{" ? i++ : f === "}" && i--, a++;
  }
  return -1;
}, Ee = function(e) {
  return e.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&");
}, Te = /^\\begin{/, Ce = function(e, t) {
  for (var n, a = [], i = new RegExp("(" + t.map((_) => Ee(_.left)).join("|") + ")"); n = e.search(i), n !== -1; ) {
    n > 0 && (a.push({
      type: "text",
      data: e.slice(0, n)
    }), e = e.slice(n));
    var l = t.findIndex((_) => e.startsWith(_.left));
    if (n = ke(t[l].right, e, t[l].left.length), n === -1)
      break;
    var f = e.slice(0, n + t[l].right.length), o = Te.test(f) ? f : e.slice(t[l].left.length, n);
    a.push({
      type: "math",
      data: o,
      rawData: f,
      display: t[l].display
    }), e = e.slice(n + t[l].right.length);
  }
  return e !== "" && a.push({
    type: "text",
    data: e
  }), a;
}, xe = function(e, t) {
  var n = Ce(e, t.delimiters);
  if (n.length === 1 && n[0].type === "text")
    return null;
  for (var a = document.createDocumentFragment(), i = 0; i < n.length; i++)
    if (n[i].type === "text")
      a.appendChild(document.createTextNode(n[i].data));
    else {
      var l = document.createElement("span"), f = n[i].data;
      t.displayMode = n[i].display;
      try {
        t.preProcess && (f = t.preProcess(f)), ne.render(f, l, t);
      } catch (o) {
        if (!(o instanceof ne.ParseError))
          throw o;
        t.errorCallback("KaTeX auto-render: Failed to parse `" + n[i].data + "` with ", o), a.appendChild(document.createTextNode(n[i].rawData));
        continue;
      }
      a.appendChild(l);
    }
  return a;
}, Le = function r(e, t) {
  for (var n = 0; n < e.childNodes.length; n++) {
    var a = e.childNodes[n];
    if (a.nodeType === 3) {
      for (var i = a.textContent, l = a.nextSibling, f = 0; l && l.nodeType === Node.TEXT_NODE; )
        i += l.textContent, l = l.nextSibling, f++;
      var o = xe(i, t);
      if (o) {
        for (var _ = 0; _ < f; _++)
          a.nextSibling.remove();
        n += o.childNodes.length - 1, e.replaceChild(o, a);
      } else
        n += f;
    } else a.nodeType === 1 && function() {
      var d = " " + a.className + " ", c = t.ignoredTags.indexOf(a.nodeName.toLowerCase()) === -1 && t.ignoredClasses.every((u) => d.indexOf(" " + u + " ") === -1);
      c && r(a, t);
    }();
  }
}, Me = function(e, t) {
  if (!e)
    throw new Error("No element provided to render");
  var n = {};
  for (var a in t)
    t.hasOwnProperty(a) && (n[a] = t[a]);
  n.delimiters = n.delimiters || [
    {
      left: "$$",
      right: "$$",
      display: !0
    },
    {
      left: "\\(",
      right: "\\)",
      display: !1
    },
    // LaTeX uses $…$, but it ruins the display of normal `$` in text:
    // {left: "$", right: "$", display: false},
    // $ must come after $$
    // Render AMS environments even if outside $$…$$ delimiters.
    {
      left: "\\begin{equation}",
      right: "\\end{equation}",
      display: !0
    },
    {
      left: "\\begin{align}",
      right: "\\end{align}",
      display: !0
    },
    {
      left: "\\begin{alignat}",
      right: "\\end{alignat}",
      display: !0
    },
    {
      left: "\\begin{gather}",
      right: "\\end{gather}",
      display: !0
    },
    {
      left: "\\begin{CD}",
      right: "\\end{CD}",
      display: !0
    },
    {
      left: "\\[",
      right: "\\]",
      display: !0
    }
  ], n.ignoredTags = n.ignoredTags || ["script", "noscript", "style", "textarea", "pre", "code", "option"], n.ignoredClasses = n.ignoredClasses || [], n.errorCallback = n.errorCallback || console.error, n.macros = n.macros || {}, Le(e, n);
};
const Oe = (r, e) => {
  try {
    return !!r && new URL(r).origin !== new URL(e).origin;
  } catch {
    return !1;
  }
};
function ae(r, e) {
  const t = new ve(), n = new DOMParser().parseFromString(r, "text/html");
  return _e(n.body, "A", (a) => {
    a instanceof HTMLElement && "target" in a && Oe(a.getAttribute("href"), e) && (a.setAttribute("target", "_blank"), a.setAttribute("rel", "noopener noreferrer"));
  }), t.sanitize(n).body.innerHTML;
}
function _e(r, e, t) {
  r && (r.nodeName === e || typeof e == "function") && t(r);
  const n = (r == null ? void 0 : r.childNodes) || [];
  for (let a = 0; a < n.length; a++)
    _e(n[a], e, t);
}
const {
  HtmlTagHydration: ze,
  SvelteComponent: Ae,
  attr: De,
  binding_callbacks: Ne,
  children: Se,
  claim_element: Be,
  claim_html_tag: qe,
  detach: re,
  element: Re,
  init: He,
  insert_hydration: Ie,
  noop: ie,
  safe_not_equal: Ue,
  toggle_class: R
} = window.__gradio__svelte__internal, { afterUpdate: Ve } = window.__gradio__svelte__internal;
function je(r) {
  let e, t;
  return {
    c() {
      e = Re("span"), t = new ze(!1), this.h();
    },
    l(n) {
      e = Be(n, "SPAN", { class: !0 });
      var a = Se(e);
      t = qe(a, !1), a.forEach(re), this.h();
    },
    h() {
      t.a = null, De(e, "class", "md svelte-1m32c2s"), R(
        e,
        "chatbot",
        /*chatbot*/
        r[0]
      ), R(
        e,
        "prose",
        /*render_markdown*/
        r[1]
      );
    },
    m(n, a) {
      Ie(n, e, a), t.m(
        /*html*/
        r[3],
        e
      ), r[10](e);
    },
    p(n, [a]) {
      a & /*html*/
      8 && t.p(
        /*html*/
        n[3]
      ), a & /*chatbot*/
      1 && R(
        e,
        "chatbot",
        /*chatbot*/
        n[0]
      ), a & /*render_markdown*/
      2 && R(
        e,
        "prose",
        /*render_markdown*/
        n[1]
      );
    },
    i: ie,
    o: ie,
    d(n) {
      n && re(e), r[10](null);
    }
  };
}
function le(r) {
  return r.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
function Pe(r, e, t) {
  var n = this && this.__awaiter || function(h, b, g, w) {
    function s(E) {
      return E instanceof g ? E : new g(function(p) {
        p(E);
      });
    }
    return new (g || (g = Promise))(function(E, p) {
      function C(v) {
        try {
          k(w.next(v));
        } catch (S) {
          p(S);
        }
      }
      function N(v) {
        try {
          k(w.throw(v));
        } catch (S) {
          p(S);
        }
      }
      function k(v) {
        v.done ? E(v.value) : s(v.value).then(C, N);
      }
      k((w = w.apply(h, b || [])).next());
    });
  };
  let { chatbot: a = !0 } = e, { message: i } = e, { sanitize_html: l = !0 } = e, { latex_delimiters: f = [] } = e, { render_markdown: o = !0 } = e, { line_breaks: _ = !0 } = e, { header_links: d = !1 } = e, { root: c } = e, u, m;
  const B = pe({
    header_links: d,
    line_breaks: _,
    latex_delimiters: f
  });
  function q(h) {
    let b = h;
    if (o) {
      const g = [];
      f.forEach((w, s) => {
        const E = le(w.left), p = le(w.right), C = new RegExp(`${E}([\\s\\S]+?)${p}`, "g");
        b = b.replace(C, (N, k) => (g.push(N), `%%%LATEX_BLOCK_${g.length - 1}%%%`));
      }), b = B.parse(b), b = b.replace(/%%%LATEX_BLOCK_(\d+)%%%/g, (w, s) => g[parseInt(s, 10)]);
    }
    return l && ae && (b = ae(b, c)), b;
  }
  function A(h) {
    return n(this, void 0, void 0, function* () {
      f.length > 0 && h && f.some((g) => h.includes(g.left) && h.includes(g.right)) && Me(u, {
        delimiters: f,
        throwOnError: !1
      });
    });
  }
  Ve(() => n(void 0, void 0, void 0, function* () {
    u && document.body.contains(u) ? yield A(i) : console.error("Element is not in the DOM");
  }));
  function D(h) {
    Ne[h ? "unshift" : "push"](() => {
      u = h, t(2, u);
    });
  }
  return r.$$set = (h) => {
    "chatbot" in h && t(0, a = h.chatbot), "message" in h && t(4, i = h.message), "sanitize_html" in h && t(5, l = h.sanitize_html), "latex_delimiters" in h && t(6, f = h.latex_delimiters), "render_markdown" in h && t(1, o = h.render_markdown), "line_breaks" in h && t(7, _ = h.line_breaks), "header_links" in h && t(8, d = h.header_links), "root" in h && t(9, c = h.root);
  }, r.$$.update = () => {
    r.$$.dirty & /*message*/
    16 && (i && i.trim() ? t(3, m = q(i)) : t(3, m = ""));
  }, [
    a,
    o,
    u,
    m,
    i,
    l,
    f,
    _,
    d,
    c,
    D
  ];
}
class Xe extends Ae {
  constructor(e) {
    super(), He(this, e, Pe, je, Ue, {
      chatbot: 0,
      message: 4,
      sanitize_html: 5,
      latex_delimiters: 6,
      render_markdown: 1,
      line_breaks: 7,
      header_links: 8,
      root: 9
    });
  }
}
const Fe = [
  { color: "red", primary: 600, secondary: 100 },
  { color: "green", primary: 600, secondary: 100 },
  { color: "blue", primary: 600, secondary: 100 },
  { color: "yellow", primary: 500, secondary: 100 },
  { color: "purple", primary: 600, secondary: 100 },
  { color: "teal", primary: 600, secondary: 100 },
  { color: "orange", primary: 600, secondary: 100 },
  { color: "cyan", primary: 600, secondary: 100 },
  { color: "lime", primary: 500, secondary: 100 },
  { color: "pink", primary: 600, secondary: 100 }
], fe = {
  inherit: "inherit",
  current: "currentColor",
  transparent: "transparent",
  black: "#000",
  white: "#fff",
  slate: {
    50: "#f8fafc",
    100: "#f1f5f9",
    200: "#e2e8f0",
    300: "#cbd5e1",
    400: "#94a3b8",
    500: "#64748b",
    600: "#475569",
    700: "#334155",
    800: "#1e293b",
    900: "#0f172a",
    950: "#020617"
  },
  gray: {
    50: "#f9fafb",
    100: "#f3f4f6",
    200: "#e5e7eb",
    300: "#d1d5db",
    400: "#9ca3af",
    500: "#6b7280",
    600: "#4b5563",
    700: "#374151",
    800: "#1f2937",
    900: "#111827",
    950: "#030712"
  },
  zinc: {
    50: "#fafafa",
    100: "#f4f4f5",
    200: "#e4e4e7",
    300: "#d4d4d8",
    400: "#a1a1aa",
    500: "#71717a",
    600: "#52525b",
    700: "#3f3f46",
    800: "#27272a",
    900: "#18181b",
    950: "#09090b"
  },
  neutral: {
    50: "#fafafa",
    100: "#f5f5f5",
    200: "#e5e5e5",
    300: "#d4d4d4",
    400: "#a3a3a3",
    500: "#737373",
    600: "#525252",
    700: "#404040",
    800: "#262626",
    900: "#171717",
    950: "#0a0a0a"
  },
  stone: {
    50: "#fafaf9",
    100: "#f5f5f4",
    200: "#e7e5e4",
    300: "#d6d3d1",
    400: "#a8a29e",
    500: "#78716c",
    600: "#57534e",
    700: "#44403c",
    800: "#292524",
    900: "#1c1917",
    950: "#0c0a09"
  },
  red: {
    50: "#fef2f2",
    100: "#fee2e2",
    200: "#fecaca",
    300: "#fca5a5",
    400: "#f87171",
    500: "#ef4444",
    600: "#dc2626",
    700: "#b91c1c",
    800: "#991b1b",
    900: "#7f1d1d",
    950: "#450a0a"
  },
  orange: {
    50: "#fff7ed",
    100: "#ffedd5",
    200: "#fed7aa",
    300: "#fdba74",
    400: "#fb923c",
    500: "#f97316",
    600: "#ea580c",
    700: "#c2410c",
    800: "#9a3412",
    900: "#7c2d12",
    950: "#431407"
  },
  amber: {
    50: "#fffbeb",
    100: "#fef3c7",
    200: "#fde68a",
    300: "#fcd34d",
    400: "#fbbf24",
    500: "#f59e0b",
    600: "#d97706",
    700: "#b45309",
    800: "#92400e",
    900: "#78350f",
    950: "#451a03"
  },
  yellow: {
    50: "#fefce8",
    100: "#fef9c3",
    200: "#fef08a",
    300: "#fde047",
    400: "#facc15",
    500: "#eab308",
    600: "#ca8a04",
    700: "#a16207",
    800: "#854d0e",
    900: "#713f12",
    950: "#422006"
  },
  lime: {
    50: "#f7fee7",
    100: "#ecfccb",
    200: "#d9f99d",
    300: "#bef264",
    400: "#a3e635",
    500: "#84cc16",
    600: "#65a30d",
    700: "#4d7c0f",
    800: "#3f6212",
    900: "#365314",
    950: "#1a2e05"
  },
  green: {
    50: "#f0fdf4",
    100: "#dcfce7",
    200: "#bbf7d0",
    300: "#86efac",
    400: "#4ade80",
    500: "#22c55e",
    600: "#16a34a",
    700: "#15803d",
    800: "#166534",
    900: "#14532d",
    950: "#052e16"
  },
  emerald: {
    50: "#ecfdf5",
    100: "#d1fae5",
    200: "#a7f3d0",
    300: "#6ee7b7",
    400: "#34d399",
    500: "#10b981",
    600: "#059669",
    700: "#047857",
    800: "#065f46",
    900: "#064e3b",
    950: "#022c22"
  },
  teal: {
    50: "#f0fdfa",
    100: "#ccfbf1",
    200: "#99f6e4",
    300: "#5eead4",
    400: "#2dd4bf",
    500: "#14b8a6",
    600: "#0d9488",
    700: "#0f766e",
    800: "#115e59",
    900: "#134e4a",
    950: "#042f2e"
  },
  cyan: {
    50: "#ecfeff",
    100: "#cffafe",
    200: "#a5f3fc",
    300: "#67e8f9",
    400: "#22d3ee",
    500: "#06b6d4",
    600: "#0891b2",
    700: "#0e7490",
    800: "#155e75",
    900: "#164e63",
    950: "#083344"
  },
  sky: {
    50: "#f0f9ff",
    100: "#e0f2fe",
    200: "#bae6fd",
    300: "#7dd3fc",
    400: "#38bdf8",
    500: "#0ea5e9",
    600: "#0284c7",
    700: "#0369a1",
    800: "#075985",
    900: "#0c4a6e",
    950: "#082f49"
  },
  blue: {
    50: "#eff6ff",
    100: "#dbeafe",
    200: "#bfdbfe",
    300: "#93c5fd",
    400: "#60a5fa",
    500: "#3b82f6",
    600: "#2563eb",
    700: "#1d4ed8",
    800: "#1e40af",
    900: "#1e3a8a",
    950: "#172554"
  },
  indigo: {
    50: "#eef2ff",
    100: "#e0e7ff",
    200: "#c7d2fe",
    300: "#a5b4fc",
    400: "#818cf8",
    500: "#6366f1",
    600: "#4f46e5",
    700: "#4338ca",
    800: "#3730a3",
    900: "#312e81",
    950: "#1e1b4b"
  },
  violet: {
    50: "#f5f3ff",
    100: "#ede9fe",
    200: "#ddd6fe",
    300: "#c4b5fd",
    400: "#a78bfa",
    500: "#8b5cf6",
    600: "#7c3aed",
    700: "#6d28d9",
    800: "#5b21b6",
    900: "#4c1d95",
    950: "#2e1065"
  },
  purple: {
    50: "#faf5ff",
    100: "#f3e8ff",
    200: "#e9d5ff",
    300: "#d8b4fe",
    400: "#c084fc",
    500: "#a855f7",
    600: "#9333ea",
    700: "#7e22ce",
    800: "#6b21a8",
    900: "#581c87",
    950: "#3b0764"
  },
  fuchsia: {
    50: "#fdf4ff",
    100: "#fae8ff",
    200: "#f5d0fe",
    300: "#f0abfc",
    400: "#e879f9",
    500: "#d946ef",
    600: "#c026d3",
    700: "#a21caf",
    800: "#86198f",
    900: "#701a75",
    950: "#4a044e"
  },
  pink: {
    50: "#fdf2f8",
    100: "#fce7f3",
    200: "#fbcfe8",
    300: "#f9a8d4",
    400: "#f472b6",
    500: "#ec4899",
    600: "#db2777",
    700: "#be185d",
    800: "#9d174d",
    900: "#831843",
    950: "#500724"
  },
  rose: {
    50: "#fff1f2",
    100: "#ffe4e6",
    200: "#fecdd3",
    300: "#fda4af",
    400: "#fb7185",
    500: "#f43f5e",
    600: "#e11d48",
    700: "#be123c",
    800: "#9f1239",
    900: "#881337",
    950: "#4c0519"
  }
};
Fe.reduce(
  (r, { color: e, primary: t, secondary: n }) => ({
    ...r,
    [e]: {
      primary: fe[e][t],
      secondary: fe[e][n]
    }
  }),
  {}
);
function Ke(r) {
  r.addEventListener("click", e);
  async function e(t) {
    const n = t.composedPath(), [a] = n.filter(
      (i) => (i == null ? void 0 : i.tagName) === "BUTTON" && i.classList.contains("copy_code_button")
    );
    if (a) {
      let i = function(_) {
        _.style.opacity = "1", setTimeout(() => {
          _.style.opacity = "0";
        }, 2e3);
      };
      t.stopImmediatePropagation();
      const l = a.parentElement.innerText.trim(), f = Array.from(
        a.children
      )[1];
      await Ze(l) && i(f);
    }
  }
  return {
    destroy() {
      r.removeEventListener("click", e);
    }
  };
}
async function Ze(r) {
  let e = !1;
  if ("clipboard" in navigator)
    await navigator.clipboard.writeText(r), e = !0;
  else {
    const t = document.createElement("textarea");
    t.value = r, t.style.position = "absolute", t.style.left = "-999999px", document.body.prepend(t), t.select();
    try {
      document.execCommand("copy"), e = !0;
    } catch (n) {
      console.error(n), e = !1;
    } finally {
      t.remove();
    }
  }
  return e;
}
const {
  SvelteComponent: We,
  append_hydration: Ge,
  attr: T,
  children: oe,
  claim_svg_element: ce,
  detach: P,
  init: Je,
  insert_hydration: Qe,
  noop: X,
  safe_not_equal: Ye,
  svg_element: se
} = window.__gradio__svelte__internal;
function $e(r) {
  let e, t;
  return {
    c() {
      e = se("svg"), t = se("polyline"), this.h();
    },
    l(n) {
      e = ce(n, "svg", {
        xmlns: !0,
        viewBox: !0,
        fill: !0,
        stroke: !0,
        "aria-hidden": !0,
        "stroke-width": !0,
        "stroke-linecap": !0,
        "stroke-linejoin": !0
      });
      var a = oe(e);
      t = ce(a, "polyline", { points: !0 }), oe(t).forEach(P), a.forEach(P), this.h();
    },
    h() {
      T(t, "points", "20 6 9 17 4 12"), T(e, "xmlns", "http://www.w3.org/2000/svg"), T(e, "viewBox", "2 0 20 20"), T(e, "fill", "none"), T(e, "stroke", "currentColor"), T(e, "aria-hidden", "true"), T(e, "stroke-width", "2"), T(e, "stroke-linecap", "round"), T(e, "stroke-linejoin", "round");
    },
    m(n, a) {
      Qe(n, e, a), Ge(e, t);
    },
    p: X,
    i: X,
    o: X,
    d(n) {
      n && P(e);
    }
  };
}
class et extends We {
  constructor(e) {
    super(), Je(this, e, null, $e, Ye, {});
  }
}
const {
  SvelteComponent: tt,
  append_hydration: de,
  attr: x,
  children: F,
  claim_svg_element: K,
  detach: H,
  init: nt,
  insert_hydration: at,
  noop: Z,
  safe_not_equal: rt,
  svg_element: W
} = window.__gradio__svelte__internal;
function it(r) {
  let e, t, n;
  return {
    c() {
      e = W("svg"), t = W("path"), n = W("path"), this.h();
    },
    l(a) {
      e = K(a, "svg", {
        xmlns: !0,
        viewBox: !0,
        color: !0,
        "aria-hidden": !0
      });
      var i = F(e);
      t = K(i, "path", { fill: !0, d: !0 }), F(t).forEach(H), n = K(i, "path", { fill: !0, d: !0 }), F(n).forEach(H), i.forEach(H), this.h();
    },
    h() {
      x(t, "fill", "currentColor"), x(t, "d", "M28 10v18H10V10h18m0-2H10a2 2 0 0 0-2 2v18a2 2 0 0 0 2 2h18a2 2 0 0 0 2-2V10a2 2 0 0 0-2-2Z"), x(n, "fill", "currentColor"), x(n, "d", "M4 18H2V4a2 2 0 0 1 2-2h14v2H4Z"), x(e, "xmlns", "http://www.w3.org/2000/svg"), x(e, "viewBox", "0 0 33 33"), x(e, "color", "currentColor"), x(e, "aria-hidden", "true");
    },
    m(a, i) {
      at(a, e, i), de(e, t), de(e, n);
    },
    p: Z,
    i: Z,
    o: Z,
    d(a) {
      a && H(e);
    }
  };
}
class lt extends tt {
  constructor(e) {
    super(), nt(this, e, null, it, rt, {});
  }
}
const {
  SvelteComponent: ft,
  action_destroyer: ot,
  add_render_callback: ct,
  append_hydration: st,
  attr: y,
  check_outros: me,
  children: G,
  claim_component: J,
  claim_element: Q,
  claim_space: dt,
  create_component: Y,
  create_in_transition: ut,
  destroy_component: $,
  detach: z,
  element: ee,
  empty: ue,
  group_outros: be,
  init: ht,
  insert_hydration: U,
  listen: _t,
  mount_component: te,
  noop: ge,
  safe_not_equal: mt,
  space: bt,
  toggle_class: I,
  transition_in: L,
  transition_out: O
} = window.__gradio__svelte__internal, { createEventDispatcher: gt } = window.__gradio__svelte__internal;
function he(r) {
  let e, t, n, a;
  const i = [vt, yt], l = [];
  function f(o, _) {
    return (
      /*copied*/
      o[12] ? 0 : 1
    );
  }
  return e = f(r), t = l[e] = i[e](r), {
    c() {
      t.c(), n = ue();
    },
    l(o) {
      t.l(o), n = ue();
    },
    m(o, _) {
      l[e].m(o, _), U(o, n, _), a = !0;
    },
    p(o, _) {
      let d = e;
      e = f(o), e === d ? l[e].p(o, _) : (be(), O(l[d], 1, 1, () => {
        l[d] = null;
      }), me(), t = l[e], t ? t.p(o, _) : (t = l[e] = i[e](o), t.c()), L(t, 1), t.m(n.parentNode, n));
    },
    i(o) {
      a || (L(t), a = !0);
    },
    o(o) {
      O(t), a = !1;
    },
    d(o) {
      o && z(n), l[e].d(o);
    }
  };
}
function yt(r) {
  let e, t, n, a, i;
  return t = new lt({}), {
    c() {
      e = ee("button"), Y(t.$$.fragment), this.h();
    },
    l(l) {
      e = Q(l, "BUTTON", {
        "aria-label": !0,
        "aria-roledescription": !0,
        class: !0
      });
      var f = G(e);
      J(t.$$.fragment, f), f.forEach(z), this.h();
    },
    h() {
      y(e, "aria-label", "Copy"), y(e, "aria-roledescription", "Copy text"), y(e, "class", "svelte-1sn7l5u");
    },
    m(l, f) {
      U(l, e, f), te(t, e, null), n = !0, a || (i = _t(
        e,
        "click",
        /*handle_copy*/
        r[14]
      ), a = !0);
    },
    p: ge,
    i(l) {
      n || (L(t.$$.fragment, l), n = !0);
    },
    o(l) {
      O(t.$$.fragment, l), n = !1;
    },
    d(l) {
      l && z(e), $(t), a = !1, i();
    }
  };
}
function vt(r) {
  let e, t, n, a;
  return t = new et({}), {
    c() {
      e = ee("button"), Y(t.$$.fragment), this.h();
    },
    l(i) {
      e = Q(i, "BUTTON", {
        "aria-label": !0,
        "aria-roledescription": !0,
        class: !0
      });
      var l = G(e);
      J(t.$$.fragment, l), l.forEach(z), this.h();
    },
    h() {
      y(e, "aria-label", "Copied"), y(e, "aria-roledescription", "Text copied"), y(e, "class", "svelte-1sn7l5u");
    },
    m(i, l) {
      U(i, e, l), te(t, e, null), a = !0;
    },
    p: ge,
    i(i) {
      a || (L(t.$$.fragment, i), i && (n || ct(() => {
        n = ut(e, we, { duration: 300 }), n.start();
      })), a = !0);
    },
    o(i) {
      O(t.$$.fragment, i), a = !1;
    },
    d(i) {
      i && z(e), $(t);
    }
  };
}
function pt(r) {
  let e, t, n, a, i, l, f, o, _, d = (
    /*show_copy_button*/
    r[11] && he(r)
  );
  return n = new Xe({
    props: {
      message: (
        /*value*/
        r[2]
      ),
      latex_delimiters: (
        /*latex_delimiters*/
        r[8]
      ),
      sanitize_html: (
        /*sanitize_html*/
        r[5]
      ),
      line_breaks: (
        /*line_breaks*/
        r[7]
      ),
      chatbot: !1,
      header_links: (
        /*header_links*/
        r[9]
      ),
      root: (
        /*root*/
        r[6]
      )
    }
  }), {
    c() {
      e = ee("div"), d && d.c(), t = bt(), Y(n.$$.fragment), this.h();
    },
    l(c) {
      e = Q(c, "DIV", {
        class: !0,
        "data-testid": !0,
        dir: !0,
        style: !0
      });
      var u = G(e);
      d && d.l(u), t = dt(u), J(n.$$.fragment, u), u.forEach(z), this.h();
    },
    h() {
      y(e, "class", a = "prose " + /*elem_classes*/
      r[0].join(" ") + " svelte-1sn7l5u"), y(e, "data-testid", "markdown"), y(e, "dir", i = /*rtl*/
      r[4] ? "rtl" : "ltr"), y(e, "style", l = /*height*/
      r[10] ? `max-height: ${/*css_units*/
      r[13](
        /*height*/
        r[10]
      )}; overflow-y: auto;` : ""), I(
        e,
        "min",
        /*min_height*/
        r[3]
      ), I(e, "hide", !/*visible*/
      r[1]);
    },
    m(c, u) {
      U(c, e, u), d && d.m(e, null), st(e, t), te(n, e, null), f = !0, o || (_ = ot(Ke.call(null, e)), o = !0);
    },
    p(c, [u]) {
      /*show_copy_button*/
      c[11] ? d ? (d.p(c, u), u & /*show_copy_button*/
      2048 && L(d, 1)) : (d = he(c), d.c(), L(d, 1), d.m(e, t)) : d && (be(), O(d, 1, 1, () => {
        d = null;
      }), me());
      const m = {};
      u & /*value*/
      4 && (m.message = /*value*/
      c[2]), u & /*latex_delimiters*/
      256 && (m.latex_delimiters = /*latex_delimiters*/
      c[8]), u & /*sanitize_html*/
      32 && (m.sanitize_html = /*sanitize_html*/
      c[5]), u & /*line_breaks*/
      128 && (m.line_breaks = /*line_breaks*/
      c[7]), u & /*header_links*/
      512 && (m.header_links = /*header_links*/
      c[9]), u & /*root*/
      64 && (m.root = /*root*/
      c[6]), n.$set(m), (!f || u & /*elem_classes*/
      1 && a !== (a = "prose " + /*elem_classes*/
      c[0].join(" ") + " svelte-1sn7l5u")) && y(e, "class", a), (!f || u & /*rtl*/
      16 && i !== (i = /*rtl*/
      c[4] ? "rtl" : "ltr")) && y(e, "dir", i), (!f || u & /*height*/
      1024 && l !== (l = /*height*/
      c[10] ? `max-height: ${/*css_units*/
      c[13](
        /*height*/
        c[10]
      )}; overflow-y: auto;` : "")) && y(e, "style", l), (!f || u & /*elem_classes, min_height*/
      9) && I(
        e,
        "min",
        /*min_height*/
        c[3]
      ), (!f || u & /*elem_classes, visible*/
      3) && I(e, "hide", !/*visible*/
      c[1]);
    },
    i(c) {
      f || (L(d), L(n.$$.fragment, c), f = !0);
    },
    o(c) {
      O(d), O(n.$$.fragment, c), f = !1;
    },
    d(c) {
      c && z(e), d && d.d(), $(n), o = !1, _();
    }
  };
}
function wt(r, e, t) {
  var n = this && this.__awaiter || function(s, E, p, C) {
    function N(k) {
      return k instanceof p ? k : new p(function(v) {
        v(k);
      });
    }
    return new (p || (p = Promise))(function(k, v) {
      function S(M) {
        try {
          V(C.next(M));
        } catch (j) {
          v(j);
        }
      }
      function ye(M) {
        try {
          V(C.throw(M));
        } catch (j) {
          v(j);
        }
      }
      function V(M) {
        M.done ? k(M.value) : N(M.value).then(S, ye);
      }
      V((C = C.apply(s, E || [])).next());
    });
  };
  let { elem_classes: a = [] } = e, { visible: i = !0 } = e, { value: l } = e, { min_height: f = !1 } = e, { rtl: o = !1 } = e, { sanitize_html: _ = !0 } = e, { root: d } = e, { line_breaks: c = !1 } = e, { latex_delimiters: u = [
    {
      left: "$$",
      right: "$$",
      display: !0
    }
  ] } = e, { header_links: m = !1 } = e, { height: B = void 0 } = e, { show_copy_button: q = !1 } = e, A = !1, D;
  const h = gt(), b = (s) => typeof s == "number" ? s + "px" : s;
  function g() {
    return n(this, void 0, void 0, function* () {
      "clipboard" in navigator && (yield navigator.clipboard.writeText(l), w());
    });
  }
  function w() {
    t(12, A = !0), D && clearTimeout(D), D = setTimeout(
      () => {
        t(12, A = !1);
      },
      1e3
    );
  }
  return r.$$set = (s) => {
    "elem_classes" in s && t(0, a = s.elem_classes), "visible" in s && t(1, i = s.visible), "value" in s && t(2, l = s.value), "min_height" in s && t(3, f = s.min_height), "rtl" in s && t(4, o = s.rtl), "sanitize_html" in s && t(5, _ = s.sanitize_html), "root" in s && t(6, d = s.root), "line_breaks" in s && t(7, c = s.line_breaks), "latex_delimiters" in s && t(8, u = s.latex_delimiters), "header_links" in s && t(9, m = s.header_links), "height" in s && t(10, B = s.height), "show_copy_button" in s && t(11, q = s.show_copy_button);
  }, r.$$.update = () => {
    r.$$.dirty & /*value*/
    4 && h("change");
  }, [
    a,
    i,
    l,
    f,
    o,
    _,
    d,
    c,
    u,
    m,
    B,
    q,
    A,
    b,
    g
  ];
}
class Et extends ft {
  constructor(e) {
    super(), ht(this, e, wt, pt, mt, {
      elem_classes: 0,
      visible: 1,
      value: 2,
      min_height: 3,
      rtl: 4,
      sanitize_html: 5,
      root: 6,
      line_breaks: 7,
      latex_delimiters: 8,
      header_links: 9,
      height: 10,
      show_copy_button: 11
    });
  }
}
export {
  Et as default
};
