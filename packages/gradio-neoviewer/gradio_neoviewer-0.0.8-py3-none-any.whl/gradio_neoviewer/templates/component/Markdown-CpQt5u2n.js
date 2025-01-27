import { k as ae, B as Re, M as Le, b as Me, p as U, c as ie, f as Ne } from "./Index-BzP9AfWt.js";
const {
  SvelteComponent: ze,
  append_hydration: Be,
  attr: E,
  children: le,
  claim_svg_element: se,
  detach: X,
  init: De,
  insert_hydration: He,
  noop: Z,
  safe_not_equal: Se,
  svg_element: oe
} = window.__gradio__svelte__internal;
function Ae(r) {
  let e, t;
  return {
    c() {
      e = oe("svg"), t = oe("polyline"), this.h();
    },
    l(n) {
      e = se(n, "svg", {
        xmlns: !0,
        viewBox: !0,
        fill: !0,
        stroke: !0,
        "aria-hidden": !0,
        "stroke-width": !0,
        "stroke-linecap": !0,
        "stroke-linejoin": !0
      });
      var a = le(e);
      t = se(a, "polyline", { points: !0 }), le(t).forEach(X), a.forEach(X), this.h();
    },
    h() {
      E(t, "points", "20 6 9 17 4 12"), E(e, "xmlns", "http://www.w3.org/2000/svg"), E(e, "viewBox", "2 0 20 20"), E(e, "fill", "none"), E(e, "stroke", "currentColor"), E(e, "aria-hidden", "true"), E(e, "stroke-width", "2"), E(e, "stroke-linecap", "round"), E(e, "stroke-linejoin", "round");
    },
    m(n, a) {
      He(n, e, a), Be(e, t);
    },
    p: Z,
    i: Z,
    o: Z,
    d(n) {
      n && X(e);
    }
  };
}
class Ie extends ze {
  constructor(e) {
    super(), De(this, e, null, Ae, Se, {});
  }
}
const {
  SvelteComponent: qe,
  append_hydration: ce,
  attr: C,
  children: K,
  claim_svg_element: F,
  detach: S,
  init: Pe,
  insert_hydration: Ve,
  noop: Y,
  safe_not_equal: je,
  svg_element: W
} = window.__gradio__svelte__internal;
function Ue(r) {
  let e, t, n;
  return {
    c() {
      e = W("svg"), t = W("path"), n = W("path"), this.h();
    },
    l(a) {
      e = F(a, "svg", {
        xmlns: !0,
        viewBox: !0,
        color: !0,
        "aria-hidden": !0
      });
      var i = K(e);
      t = F(i, "path", { fill: !0, d: !0 }), K(t).forEach(S), n = F(i, "path", { fill: !0, d: !0 }), K(n).forEach(S), i.forEach(S), this.h();
    },
    h() {
      C(t, "fill", "currentColor"), C(t, "d", "M28 10v18H10V10h18m0-2H10a2 2 0 0 0-2 2v18a2 2 0 0 0 2 2h18a2 2 0 0 0 2-2V10a2 2 0 0 0-2-2Z"), C(n, "fill", "currentColor"), C(n, "d", "M4 18H2V4a2 2 0 0 1 2-2h14v2H4Z"), C(e, "xmlns", "http://www.w3.org/2000/svg"), C(e, "viewBox", "0 0 33 33"), C(e, "color", "currentColor"), C(e, "aria-hidden", "true");
    },
    m(a, i) {
      Ve(a, e, i), ce(e, t), ce(e, n);
    },
    p: Y,
    i: Y,
    o: Y,
    d(a) {
      a && S(e);
    }
  };
}
class Xe extends qe {
  constructor(e) {
    super(), Pe(this, e, null, Ue, je, {});
  }
}
function Ze(r) {
  r.addEventListener("click", e);
  async function e(t) {
    const n = t.composedPath(), [a] = n.filter(
      (i) => (i == null ? void 0 : i.tagName) === "BUTTON" && i.classList.contains("copy_code_button")
    );
    if (a) {
      let i = function(d) {
        d.style.opacity = "1", setTimeout(() => {
          d.style.opacity = "0";
        }, 2e3);
      };
      t.stopImmediatePropagation();
      const l = a.parentElement.innerText.trim(), s = Array.from(
        a.children
      )[1];
      await Ke(l) && i(s);
    }
  }
  return {
    destroy() {
      r.removeEventListener("click", e);
    }
  };
}
async function Ke(r) {
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
var Fe = function(e, t, n) {
  for (var a = n, i = 0, l = e.length; a < t.length; ) {
    var s = t[a];
    if (i <= 0 && t.slice(a, a + l) === e)
      return a;
    s === "\\" ? a++ : s === "{" ? i++ : s === "}" && i--, a++;
  }
  return -1;
}, Ye = function(e) {
  return e.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&");
}, We = /^\\begin{/, Ge = function(e, t) {
  for (var n, a = [], i = new RegExp("(" + t.map((d) => Ye(d.left)).join("|") + ")"); n = e.search(i), n !== -1; ) {
    n > 0 && (a.push({
      type: "text",
      data: e.slice(0, n)
    }), e = e.slice(n));
    var l = t.findIndex((d) => e.startsWith(d.left));
    if (n = Fe(t[l].right, e, t[l].left.length), n === -1)
      break;
    var s = e.slice(0, n + t[l].right.length), o = We.test(s) ? s : e.slice(t[l].left.length, n);
    a.push({
      type: "math",
      data: o,
      rawData: s,
      display: t[l].display
    }), e = e.slice(n + t[l].right.length);
  }
  return e !== "" && a.push({
    type: "text",
    data: e
  }), a;
}, Je = function(e, t) {
  var n = Ge(e, t.delimiters);
  if (n.length === 1 && n[0].type === "text")
    return null;
  for (var a = document.createDocumentFragment(), i = 0; i < n.length; i++)
    if (n[i].type === "text")
      a.appendChild(document.createTextNode(n[i].data));
    else {
      var l = document.createElement("span"), s = n[i].data;
      t.displayMode = n[i].display;
      try {
        t.preProcess && (s = t.preProcess(s)), ae.render(s, l, t);
      } catch (o) {
        if (!(o instanceof ae.ParseError))
          throw o;
        t.errorCallback("KaTeX auto-render: Failed to parse `" + n[i].data + "` with ", o), a.appendChild(document.createTextNode(n[i].rawData));
        continue;
      }
      a.appendChild(l);
    }
  return a;
}, Qe = function r(e, t) {
  for (var n = 0; n < e.childNodes.length; n++) {
    var a = e.childNodes[n];
    if (a.nodeType === 3) {
      for (var i = a.textContent, l = a.nextSibling, s = 0; l && l.nodeType === Node.TEXT_NODE; )
        i += l.textContent, l = l.nextSibling, s++;
      var o = Je(i, t);
      if (o) {
        for (var d = 0; d < s; d++)
          a.nextSibling.remove();
        n += o.childNodes.length - 1, e.replaceChild(o, a);
      } else
        n += s;
    } else a.nodeType === 1 && function() {
      var h = " " + a.className + " ", c = t.ignoredTags.indexOf(a.nodeName.toLowerCase()) === -1 && t.ignoredClasses.every((_) => h.indexOf(" " + _ + " ") === -1);
      c && r(a, t);
    }();
  }
}, $e = function(e, t) {
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
  ], n.ignoredTags = n.ignoredTags || ["script", "noscript", "style", "textarea", "pre", "code", "option"], n.ignoredClasses = n.ignoredClasses || [], n.errorCallback = n.errorCallback || console.error, n.macros = n.macros || {}, Qe(e, n);
};
function et(r) {
  if (typeof r == "function" && (r = {
    highlight: r
  }), !r || typeof r.highlight != "function")
    throw new Error("Must provide highlight function");
  return typeof r.langPrefix != "string" && (r.langPrefix = "language-"), typeof r.emptyLangClass != "string" && (r.emptyLangClass = ""), {
    async: !!r.async,
    walkTokens(e) {
      if (e.type !== "code")
        return;
      const t = ue(e.lang);
      if (r.async)
        return Promise.resolve(r.highlight(e.text, t, e.lang || "")).then(fe(e));
      const n = r.highlight(e.text, t, e.lang || "");
      if (n instanceof Promise)
        throw new Error("markedHighlight is not set to async but the highlight function is async. Set the async option to true on markedHighlight to await the async highlight function.");
      fe(e)(n);
    },
    useNewRenderer: !0,
    renderer: {
      code(e, t, n) {
        typeof e == "object" && (n = e.escaped, t = e.lang, e = e.text);
        const a = ue(t), i = a ? r.langPrefix + de(a) : r.emptyLangClass, l = i ? ` class="${i}"` : "";
        return e = e.replace(/\n$/, ""), `<pre><code${l}>${n ? e : de(e, !0)}
</code></pre>`;
      }
    }
  };
}
function ue(r) {
  return (r || "").match(/\S*/)[0];
}
function fe(r) {
  return (e) => {
    typeof e == "string" && e !== r.text && (r.escaped = !0, r.text = e);
  };
}
const be = /[&<>"']/, tt = new RegExp(be.source, "g"), ke = /[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/, nt = new RegExp(ke.source, "g"), rt = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;"
}, he = (r) => rt[r];
function de(r, e) {
  if (e) {
    if (be.test(r))
      return r.replace(tt, he);
  } else if (ke.test(r))
    return r.replace(nt, he);
  return r;
}
const at = '<svg class="md-link-icon" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true" fill="currentColor"><path d="m7.775 3.275 1.25-1.25a3.5 3.5 0 1 1 4.95 4.95l-2.5 2.5a3.5 3.5 0 0 1-4.95 0 .751.751 0 0 1 .018-1.042.751.751 0 0 1 1.042-.018 1.998 1.998 0 0 0 2.83 0l2.5-2.5a2.002 2.002 0 0 0-2.83-2.83l-1.25 1.25a.751.751 0 0 1-1.042-.018.751.751 0 0 1-.018-1.042Zm-4.69 9.64a1.998 1.998 0 0 0 2.83 0l1.25-1.25a.751.751 0 0 1 1.042.018.751.751 0 0 1 .018 1.042l-1.25 1.25a3.5 3.5 0 1 1-4.95-4.95l2.5-2.5a3.5 3.5 0 0 1 4.95 0 .751.751 0 0 1-.018 1.042.751.751 0 0 1-1.042.018 1.998 1.998 0 0 0-2.83 0l-2.5 2.5a1.998 1.998 0 0 0 0 2.83Z"></path></svg>', it = `<svg
xmlns="http://www.w3.org/2000/svg"
width="100%"
height="100%"
viewBox="0 0 32 32"
><path
  fill="currentColor"
  d="M28 10v18H10V10h18m0-2H10a2 2 0 0 0-2 2v18a2 2 0 0 0 2 2h18a2 2 0 0 0 2-2V10a2 2 0 0 0-2-2Z"
/><path fill="currentColor" d="M4 18H2V4a2 2 0 0 1 2-2h14v2H4Z" /></svg>`, lt = `<svg
xmlns="http://www.w3.org/2000/svg"
width="100%"
height="100%"
viewBox="0 0 24 24"
fill="none"
stroke="currentColor"
stroke-width="3"
stroke-linecap="round"
stroke-linejoin="round"><polyline points="20 6 9 17 4 12" /></svg>`, _e = `<button title="copy" class="copy_code_button">
<span class="copy-text">${it}</span>
<span class="check">${lt}</span>
</button>`, xe = /[&<>"']/, st = new RegExp(xe.source, "g"), Ee = /[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/, ot = new RegExp(Ee.source, "g"), ct = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;"
}, ge = (r) => ct[r] || "";
function G(r, e) {
  if (e) {
    if (xe.test(r))
      return r.replace(st, ge);
  } else if (Ee.test(r))
    return r.replace(ot, ge);
  return r;
}
function ut(r) {
  const e = r.map((t) => ({
    start: new RegExp(t.left.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&")),
    end: new RegExp(t.right.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&"))
  }));
  return {
    name: "latex",
    level: "block",
    start(t) {
      for (const n of e) {
        const a = t.match(n.start);
        if (a)
          return a.index;
      }
      return -1;
    },
    tokenizer(t, n) {
      for (const a of e) {
        const i = new RegExp(
          `${a.start.source}([\\s\\S]+?)${a.end.source}`
        ).exec(t);
        if (i)
          return {
            type: "latex",
            raw: i[0],
            text: i[1].trim()
          };
      }
    },
    renderer(t) {
      return `<div class="latex-block">${t.text}</div>`;
    }
  };
}
const ft = {
  code(r, e, t) {
    var a;
    const n = ((a = (e ?? "").match(/\S*/)) == null ? void 0 : a[0]) ?? "";
    return r = r.replace(/\n$/, "") + `
`, n ? '<div class="code_wrap">' + _e + '<pre><code class="language-' + G(n) + '">' + (t ? r : G(r, !0)) + `</code></pre></div>
` : '<div class="code_wrap">' + _e + "<pre><code>" + (t ? r : G(r, !0)) + `</code></pre></div>
`;
  }
}, ht = new Re();
function dt({
  header_links: r,
  line_breaks: e,
  latex_delimiters: t
}) {
  const n = new Le();
  n.use(
    {
      gfm: !0,
      pedantic: !1,
      breaks: e
    },
    et({
      highlight: (i, l) => U.languages[l] ? U.highlight(i, U.languages[l], l) : i
    }),
    { renderer: ft }
  ), r && (n.use(Me()), n.use({
    extensions: [
      {
        name: "heading",
        level: "block",
        renderer(i) {
          const l = i.raw.toLowerCase().trim().replace(/<[!\/a-z].*?>/gi, ""), s = "h" + ht.slug(l), o = i.depth, d = this.parser.parseInline(i.tokens);
          return `<h${o} id="${s}"><a class="md-header-anchor" href="#${s}">${at}</a>${d}</h${o}>
`;
        }
      }
    ]
  }));
  const a = ut(t);
  return n.use({
    extensions: [a]
  }), n;
}
const {
  HtmlTagHydration: _t,
  SvelteComponent: gt,
  attr: mt,
  binding_callbacks: pt,
  children: vt,
  claim_element: wt,
  claim_html_tag: yt,
  detach: me,
  element: bt,
  init: kt,
  insert_hydration: xt,
  noop: pe,
  safe_not_equal: Et,
  toggle_class: A
} = window.__gradio__svelte__internal, { afterUpdate: Ct } = window.__gradio__svelte__internal;
function Tt(r) {
  let e, t;
  return {
    c() {
      e = bt("span"), t = new _t(!1), this.h();
    },
    l(n) {
      e = wt(n, "SPAN", { class: !0 });
      var a = vt(e);
      t = yt(a, !1), a.forEach(me), this.h();
    },
    h() {
      t.a = null, mt(e, "class", "md svelte-91qfmi"), A(
        e,
        "chatbot",
        /*chatbot*/
        r[0]
      ), A(
        e,
        "prose",
        /*render_markdown*/
        r[1]
      );
    },
    m(n, a) {
      xt(n, e, a), t.m(
        /*html*/
        r[3],
        e
      ), r[9](e);
    },
    p(n, [a]) {
      a & /*html*/
      8 && t.p(
        /*html*/
        n[3]
      ), a & /*chatbot*/
      1 && A(
        e,
        "chatbot",
        /*chatbot*/
        n[0]
      ), a & /*render_markdown*/
      2 && A(
        e,
        "prose",
        /*render_markdown*/
        n[1]
      );
    },
    i: pe,
    o: pe,
    d(n) {
      n && me(e), r[9](null);
    }
  };
}
function ve(r) {
  return r.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
function Ot(r, e, t) {
  var n = this && this.__awaiter || function(f, g, m, u) {
    function M(v) {
      return v instanceof m ? v : new m(function(y) {
        y(v);
      });
    }
    return new (m || (m = Promise))(function(v, y) {
      function B(x) {
        try {
          k(u.next(x));
        } catch (D) {
          y(D);
        }
      }
      function b(x) {
        try {
          k(u.throw(x));
        } catch (D) {
          y(D);
        }
      }
      function k(x) {
        x.done ? v(x.value) : M(x.value).then(B, b);
      }
      k((u = u.apply(f, g || [])).next());
    });
  };
  let { chatbot: a = !0 } = e, { message: i } = e, { sanitize_html: l = !0 } = e, { latex_delimiters: s = [] } = e, { render_markdown: o = !0 } = e, { line_breaks: d = !0 } = e, { header_links: h = !1 } = e, c, _;
  const w = dt({
    header_links: h,
    line_breaks: d,
    latex_delimiters: s
  }), H = (f) => {
    try {
      return !!f && new URL(f, location.href).origin !== location.origin;
    } catch {
      return !1;
    }
  };
  ie.addHook("afterSanitizeAttributes", function(f) {
    "target" in f && H(f.getAttribute("href")) && (f.setAttribute("target", "_blank"), f.setAttribute("rel", "noopener noreferrer"));
  });
  function N(f) {
    let g = f;
    if (o) {
      const m = [];
      s.forEach((u, M) => {
        const v = ve(u.left), y = ve(u.right), B = new RegExp(`${v}([\\s\\S]+?)${y}`, "g");
        g = g.replace(B, (b, k) => (m.push(b), `%%%LATEX_BLOCK_${m.length - 1}%%%`));
      }), g = w.parse(g), g = g.replace(/%%%LATEX_BLOCK_(\d+)%%%/g, (u, M) => m[parseInt(M, 10)]);
    }
    return l && (g = ie.sanitize(g)), g;
  }
  function z(f) {
    return n(this, void 0, void 0, function* () {
      s.length > 0 && f && s.some((m) => f.includes(m.left) && f.includes(m.right)) && $e(c, {
        delimiters: s,
        throwOnError: !1
      });
    });
  }
  Ct(() => n(void 0, void 0, void 0, function* () {
    c && document.body.contains(c) ? yield z(i) : console.error("Element is not in the DOM");
  }));
  function P(f) {
    pt[f ? "unshift" : "push"](() => {
      c = f, t(2, c);
    });
  }
  return r.$$set = (f) => {
    "chatbot" in f && t(0, a = f.chatbot), "message" in f && t(4, i = f.message), "sanitize_html" in f && t(5, l = f.sanitize_html), "latex_delimiters" in f && t(6, s = f.latex_delimiters), "render_markdown" in f && t(1, o = f.render_markdown), "line_breaks" in f && t(7, d = f.line_breaks), "header_links" in f && t(8, h = f.header_links);
  }, r.$$.update = () => {
    r.$$.dirty & /*message*/
    16 && (i && i.trim() ? t(3, _ = N(i)) : t(3, _ = ""));
  }, [
    a,
    o,
    c,
    _,
    i,
    l,
    s,
    d,
    h,
    P
  ];
}
class Rt extends gt {
  constructor(e) {
    super(), kt(this, e, Ot, Tt, Et, {
      chatbot: 0,
      message: 4,
      sanitize_html: 5,
      latex_delimiters: 6,
      render_markdown: 1,
      line_breaks: 7,
      header_links: 8
    });
  }
}
const {
  SvelteComponent: Lt,
  action_destroyer: Mt,
  add_render_callback: Nt,
  append_hydration: zt,
  attr: p,
  check_outros: Ce,
  children: J,
  claim_component: Q,
  claim_element: $,
  claim_space: Bt,
  create_component: ee,
  create_in_transition: Dt,
  destroy_component: te,
  detach: L,
  element: ne,
  empty: we,
  group_outros: Te,
  init: Ht,
  insert_hydration: q,
  listen: St,
  mount_component: re,
  noop: Oe,
  safe_not_equal: At,
  space: It,
  toggle_class: I,
  transition_in: T,
  transition_out: R
} = window.__gradio__svelte__internal, { createEventDispatcher: qt } = window.__gradio__svelte__internal;
function ye(r) {
  let e, t, n, a;
  const i = [Vt, Pt], l = [];
  function s(o, d) {
    return (
      /*copied*/
      o[11] ? 0 : 1
    );
  }
  return e = s(r), t = l[e] = i[e](r), {
    c() {
      t.c(), n = we();
    },
    l(o) {
      t.l(o), n = we();
    },
    m(o, d) {
      l[e].m(o, d), q(o, n, d), a = !0;
    },
    p(o, d) {
      let h = e;
      e = s(o), e === h ? l[e].p(o, d) : (Te(), R(l[h], 1, 1, () => {
        l[h] = null;
      }), Ce(), t = l[e], t ? t.p(o, d) : (t = l[e] = i[e](o), t.c()), T(t, 1), t.m(n.parentNode, n));
    },
    i(o) {
      a || (T(t), a = !0);
    },
    o(o) {
      R(t), a = !1;
    },
    d(o) {
      o && L(n), l[e].d(o);
    }
  };
}
function Pt(r) {
  let e, t, n, a, i;
  return t = new Xe({}), {
    c() {
      e = ne("button"), ee(t.$$.fragment), this.h();
    },
    l(l) {
      e = $(l, "BUTTON", {
        "aria-label": !0,
        "aria-roledescription": !0,
        class: !0
      });
      var s = J(e);
      Q(t.$$.fragment, s), s.forEach(L), this.h();
    },
    h() {
      p(e, "aria-label", "Copy"), p(e, "aria-roledescription", "Copy text"), p(e, "class", "svelte-1sn7l5u");
    },
    m(l, s) {
      q(l, e, s), re(t, e, null), n = !0, a || (i = St(
        e,
        "click",
        /*handle_copy*/
        r[13]
      ), a = !0);
    },
    p: Oe,
    i(l) {
      n || (T(t.$$.fragment, l), n = !0);
    },
    o(l) {
      R(t.$$.fragment, l), n = !1;
    },
    d(l) {
      l && L(e), te(t), a = !1, i();
    }
  };
}
function Vt(r) {
  let e, t, n, a;
  return t = new Ie({}), {
    c() {
      e = ne("button"), ee(t.$$.fragment), this.h();
    },
    l(i) {
      e = $(i, "BUTTON", {
        "aria-label": !0,
        "aria-roledescription": !0,
        class: !0
      });
      var l = J(e);
      Q(t.$$.fragment, l), l.forEach(L), this.h();
    },
    h() {
      p(e, "aria-label", "Copied"), p(e, "aria-roledescription", "Text copied"), p(e, "class", "svelte-1sn7l5u");
    },
    m(i, l) {
      q(i, e, l), re(t, e, null), a = !0;
    },
    p: Oe,
    i(i) {
      a || (T(t.$$.fragment, i), i && (n || Nt(() => {
        n = Dt(e, Ne, { duration: 300 }), n.start();
      })), a = !0);
    },
    o(i) {
      R(t.$$.fragment, i), a = !1;
    },
    d(i) {
      i && L(e), te(t);
    }
  };
}
function jt(r) {
  let e, t, n, a, i, l, s, o, d, h = (
    /*show_copy_button*/
    r[10] && ye(r)
  );
  return n = new Rt({
    props: {
      message: (
        /*value*/
        r[2]
      ),
      latex_delimiters: (
        /*latex_delimiters*/
        r[7]
      ),
      sanitize_html: (
        /*sanitize_html*/
        r[5]
      ),
      line_breaks: (
        /*line_breaks*/
        r[6]
      ),
      chatbot: !1,
      header_links: (
        /*header_links*/
        r[8]
      )
    }
  }), {
    c() {
      e = ne("div"), h && h.c(), t = It(), ee(n.$$.fragment), this.h();
    },
    l(c) {
      e = $(c, "DIV", {
        class: !0,
        "data-testid": !0,
        dir: !0,
        style: !0
      });
      var _ = J(e);
      h && h.l(_), t = Bt(_), Q(n.$$.fragment, _), _.forEach(L), this.h();
    },
    h() {
      p(e, "class", a = "prose " + /*elem_classes*/
      r[0].join(" ") + " svelte-1sn7l5u"), p(e, "data-testid", "markdown"), p(e, "dir", i = /*rtl*/
      r[4] ? "rtl" : "ltr"), p(e, "style", l = /*height*/
      r[9] ? `max-height: ${/*css_units*/
      r[12](
        /*height*/
        r[9]
      )}; overflow-y: auto;` : ""), I(
        e,
        "min",
        /*min_height*/
        r[3]
      ), I(e, "hide", !/*visible*/
      r[1]);
    },
    m(c, _) {
      q(c, e, _), h && h.m(e, null), zt(e, t), re(n, e, null), s = !0, o || (d = Mt(Ze.call(null, e)), o = !0);
    },
    p(c, [_]) {
      /*show_copy_button*/
      c[10] ? h ? (h.p(c, _), _ & /*show_copy_button*/
      1024 && T(h, 1)) : (h = ye(c), h.c(), T(h, 1), h.m(e, t)) : h && (Te(), R(h, 1, 1, () => {
        h = null;
      }), Ce());
      const w = {};
      _ & /*value*/
      4 && (w.message = /*value*/
      c[2]), _ & /*latex_delimiters*/
      128 && (w.latex_delimiters = /*latex_delimiters*/
      c[7]), _ & /*sanitize_html*/
      32 && (w.sanitize_html = /*sanitize_html*/
      c[5]), _ & /*line_breaks*/
      64 && (w.line_breaks = /*line_breaks*/
      c[6]), _ & /*header_links*/
      256 && (w.header_links = /*header_links*/
      c[8]), n.$set(w), (!s || _ & /*elem_classes*/
      1 && a !== (a = "prose " + /*elem_classes*/
      c[0].join(" ") + " svelte-1sn7l5u")) && p(e, "class", a), (!s || _ & /*rtl*/
      16 && i !== (i = /*rtl*/
      c[4] ? "rtl" : "ltr")) && p(e, "dir", i), (!s || _ & /*height*/
      512 && l !== (l = /*height*/
      c[9] ? `max-height: ${/*css_units*/
      c[12](
        /*height*/
        c[9]
      )}; overflow-y: auto;` : "")) && p(e, "style", l), (!s || _ & /*elem_classes, min_height*/
      9) && I(
        e,
        "min",
        /*min_height*/
        c[3]
      ), (!s || _ & /*elem_classes, visible*/
      3) && I(e, "hide", !/*visible*/
      c[1]);
    },
    i(c) {
      s || (T(h), T(n.$$.fragment, c), s = !0);
    },
    o(c) {
      R(h), R(n.$$.fragment, c), s = !1;
    },
    d(c) {
      c && L(e), h && h.d(), te(n), o = !1, d();
    }
  };
}
function Ut(r, e, t) {
  var n = this && this.__awaiter || function(u, M, v, y) {
    function B(b) {
      return b instanceof v ? b : new v(function(k) {
        k(b);
      });
    }
    return new (v || (v = Promise))(function(b, k) {
      function x(O) {
        try {
          V(y.next(O));
        } catch (j) {
          k(j);
        }
      }
      function D(O) {
        try {
          V(y.throw(O));
        } catch (j) {
          k(j);
        }
      }
      function V(O) {
        O.done ? b(O.value) : B(O.value).then(x, D);
      }
      V((y = y.apply(u, M || [])).next());
    });
  };
  let { elem_classes: a = [] } = e, { visible: i = !0 } = e, { value: l } = e, { min_height: s = !1 } = e, { rtl: o = !1 } = e, { sanitize_html: d = !0 } = e, { line_breaks: h = !1 } = e, { latex_delimiters: c = [
    {
      left: "$$",
      right: "$$",
      display: !0
    }
  ] } = e, { header_links: _ = !1 } = e, { height: w = void 0 } = e, { show_copy_button: H = !1 } = e, N = !1, z;
  const P = qt(), f = (u) => typeof u == "number" ? u + "px" : u;
  function g() {
    return n(this, void 0, void 0, function* () {
      "clipboard" in navigator && (yield navigator.clipboard.writeText(l), m());
    });
  }
  function m() {
    t(11, N = !0), z && clearTimeout(z), z = setTimeout(
      () => {
        t(11, N = !1);
      },
      1e3
    );
  }
  return r.$$set = (u) => {
    "elem_classes" in u && t(0, a = u.elem_classes), "visible" in u && t(1, i = u.visible), "value" in u && t(2, l = u.value), "min_height" in u && t(3, s = u.min_height), "rtl" in u && t(4, o = u.rtl), "sanitize_html" in u && t(5, d = u.sanitize_html), "line_breaks" in u && t(6, h = u.line_breaks), "latex_delimiters" in u && t(7, c = u.latex_delimiters), "header_links" in u && t(8, _ = u.header_links), "height" in u && t(9, w = u.height), "show_copy_button" in u && t(10, H = u.show_copy_button);
  }, r.$$.update = () => {
    r.$$.dirty & /*value*/
    4 && P("change");
  }, [
    a,
    i,
    l,
    s,
    o,
    d,
    h,
    c,
    _,
    w,
    H,
    N,
    f,
    g
  ];
}
class Zt extends Lt {
  constructor(e) {
    super(), Ht(this, e, Ut, jt, At, {
      elem_classes: 0,
      visible: 1,
      value: 2,
      min_height: 3,
      rtl: 4,
      sanitize_html: 5,
      line_breaks: 6,
      latex_delimiters: 7,
      header_links: 8,
      height: 9,
      show_copy_button: 10
    });
  }
}
export {
  Zt as default
};
