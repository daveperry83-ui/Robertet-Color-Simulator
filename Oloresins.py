import React, { useState, useMemo } from "react";
import {
  Leaf,
  FlaskConical,
  Scale,
  Coins,
  TrendingDown,
  TrendingUp,
  Minus,
  Pencil,
  Info,
  Search,
} from "lucide-react";

/**
 * Oleoresin vs. natural spice — replacement & cost-in-use calculator.
 *
 * Replacement is computed on the basis of the key standardization marker
 * (piperine, volatile oil, curcumin, color value, Scoville heat units,
 * carnosic acid, etc.) defined for each oleoresin by the Food Chemicals
 * Codex (FCC) spice-oleoresin monograph, plus typical industry values.
 *
 *   Replacement factor  R   = marker in oleoresin / marker in natural spice
 *   Cost in use         CIU = oleoresin price / R   (per kg of spice equivalent)
 *   Savings                 = natural spice price − CIU
 *
 * All defaults are editable — always reconcile against your own CoA.
 */

// cat: "pungency" | "color" | "antioxidant" | "volatile" | "custom"
const PRODUCTS = [
  // Pungency / alkaloids
  { id: "black-pepper", name: "Black pepper",        marker: "Piperine",                   unit: "%",   nat: 5.0,   ol: 40,      cat: "pungency" },
  { id: "white-pepper", name: "White pepper",        marker: "Piperine",                   unit: "%",   nat: 6.0,   ol: 38,      cat: "pungency" },
  { id: "capsicum",     name: "Capsicum / chili",    marker: "Capsaicin (pungency)",       unit: "SHU", nat: 40000, ol: 1000000, cat: "pungency" },

  // Color
  { id: "paprika",      name: "Paprika",             marker: "Color value",                unit: "CU",  nat: 120,   ol: 40000,   cat: "color" },
  { id: "turmeric",     name: "Turmeric",            marker: "Curcumin",                   unit: "%",   nat: 3.5,   ol: 35,      cat: "color" },

  // Antioxidant
  { id: "rosemary-aox", name: "Rosemary (antioxidant)", marker: "Carnosic acid",           unit: "%",   nat: 2.0,   ol: 18,      cat: "antioxidant" },

  // Volatile oil / aroma
  { id: "ginger",       name: "Ginger",              marker: "Volatile oil (gingerols)",   unit: "%",   nat: 2.0,   ol: 26,      cat: "volatile" },
  { id: "cardamom",     name: "Cardamom",            marker: "Volatile oil",               unit: "%",   nat: 6.5,   ol: 60,      cat: "volatile" },
  { id: "clove",        name: "Clove",               marker: "Volatile oil (eugenol)",     unit: "%",   nat: 16,    ol: 80,      cat: "volatile" },
  { id: "nutmeg",       name: "Nutmeg",              marker: "Volatile oil",               unit: "%",   nat: 8.0,   ol: 30,      cat: "volatile" },
  { id: "mace",         name: "Mace",                marker: "Volatile oil",               unit: "%",   nat: 10,    ol: 30,      cat: "volatile" },
  { id: "cinnamon",     name: "Cinnamon / cassia",   marker: "Volatile oil (cinnamaldehyde)", unit: "%", nat: 1.5, ol: 25,      cat: "volatile" },
  { id: "allspice",     name: "Allspice / pimenta",  marker: "Volatile oil (eugenol)",     unit: "%",   nat: 4.0,   ol: 35,      cat: "volatile" },
  { id: "bay",          name: "Bay / laurel leaf",   marker: "Volatile oil",               unit: "%",   nat: 2.0,   ol: 15,      cat: "volatile" },
  { id: "cumin",        name: "Cumin",               marker: "Volatile oil",               unit: "%",   nat: 3.0,   ol: 20,      cat: "volatile" },
  { id: "coriander",    name: "Coriander",           marker: "Volatile oil",               unit: "%",   nat: 0.8,   ol: 6,       cat: "volatile" },
  { id: "caraway",      name: "Caraway",             marker: "Volatile oil",               unit: "%",   nat: 4.0,   ol: 15,      cat: "volatile" },
  { id: "fennel",       name: "Fennel",              marker: "Volatile oil",               unit: "%",   nat: 4.0,   ol: 12,      cat: "volatile" },
  { id: "anise",        name: "Anise",               marker: "Volatile oil (anethole)",    unit: "%",   nat: 2.5,   ol: 15,      cat: "volatile" },
  { id: "star-anise",   name: "Star anise",          marker: "Volatile oil (anethole)",    unit: "%",   nat: 8.0,   ol: 18,      cat: "volatile" },
  { id: "dill",         name: "Dill seed",           marker: "Volatile oil",               unit: "%",   nat: 3.0,   ol: 15,      cat: "volatile" },
  { id: "celery",       name: "Celery seed",         marker: "Volatile oil",               unit: "%",   nat: 2.5,   ol: 13,      cat: "volatile" },
  { id: "angelica",     name: "Angelica seed",       marker: "Volatile oil",               unit: "%",   nat: 1.0,   ol: 4,       cat: "volatile" },
  { id: "cubeb",        name: "Cubeb",               marker: "Volatile oil",               unit: "%",   nat: 12,    ol: 65,      cat: "volatile" },
  { id: "parsley-leaf", name: "Parsley leaf",        marker: "Volatile oil",               unit: "%",   nat: 0.2,   ol: 6,       cat: "volatile" },
  { id: "parsley-seed", name: "Parsley seed",        marker: "Volatile oil",               unit: "%",   nat: 3.0,   ol: 4,       cat: "volatile" },
  { id: "basil",        name: "Basil",               marker: "Volatile oil",               unit: "%",   nat: 1.0,   ol: 10,      cat: "volatile" },
  { id: "marjoram",     name: "Marjoram (sweet)",    marker: "Volatile oil",               unit: "%",   nat: 1.5,   ol: 13,      cat: "volatile" },
  { id: "oregano",      name: "Oregano / origanum",  marker: "Volatile oil (carvacrol)",   unit: "%",   nat: 4.0,   ol: 32,      cat: "volatile" },
  { id: "thyme",        name: "Thyme",               marker: "Volatile oil (thymol)",      unit: "%",   nat: 1.8,   ol: 8,       cat: "volatile" },
  { id: "sage",         name: "Sage",                marker: "Volatile oil",               unit: "%",   nat: 2.0,   ol: 12,      cat: "volatile" },
  { id: "rosemary-fl",  name: "Rosemary (flavor)",   marker: "Volatile oil",               unit: "%",   nat: 1.5,   ol: 12,      cat: "volatile" },
  { id: "fenugreek",    name: "Fenugreek",           marker: "Volatile oil / sotolon",     unit: "%",   nat: 0.3,   ol: 2,       cat: "volatile" },
  { id: "mustard",      name: "Mustard",             marker: "Volatile oil (allyl ITC)",   unit: "%",   nat: 0.8,   ol: 20,      cat: "volatile" },
  { id: "garlic",       name: "Garlic",              marker: "Volatile oil (sulfur cpds)", unit: "%",   nat: 0.3,   ol: 5,       cat: "volatile" },
  { id: "onion",        name: "Onion",               marker: "Volatile oil (sulfur cpds)", unit: "%",   nat: 0.1,   ol: 3,       cat: "volatile" },
  { id: "hop",          name: "Hop",                 marker: "Volatile oil / α-acids",     unit: "%",   nat: 1.0,   ol: 25,      cat: "volatile" },
  { id: "vanilla",      name: "Vanilla",             marker: "Vanillin",                   unit: "%",   nat: 2.0,   ol: 25,      cat: "volatile" },

  // Custom
  { id: "custom",       name: "Custom / other",      marker: "Marker",                     unit: "%",   nat: 0,     ol: 0,       cat: "custom" },
];

const CATS = [
  { id: "pungency",    label: "Pungency / alkaloids" },
  { id: "color",       label: "Color" },
  { id: "antioxidant", label: "Antioxidant" },
  { id: "volatile",    label: "Volatile oil / aroma" },
  { id: "custom",      label: "Custom" },
];

const CURRENCIES = [
  { sym: "$",  label: "USD" },
  { sym: "€",  label: "EUR" },
  { sym: "$",  label: "MXN" },
  { sym: "$",  label: "COP" },
  { sym: "S/", label: "PEN" },
];

const num = (v) => {
  const n = parseFloat(String(v).replace(",", "."));
  return Number.isFinite(n) ? n : NaN;
};
const fmt = (n, d = 2) =>
  Number.isFinite(n)
    ? n.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d })
    : "—";

function Field({ label, suffix, value, onChange, placeholder, hint }) {
  return (
    <label className="block">
      <span className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-stone-500">
        {label}
        {hint && <span className="font-normal normal-case tracking-normal text-stone-400">· {hint}</span>}
      </span>
      <div className="mt-1.5 flex items-stretch overflow-hidden rounded-lg border border-stone-300 bg-white focus-within:border-amber-600 focus-within:ring-2 focus-within:ring-amber-600/20">
        <input
          inputMode="decimal"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full bg-transparent px-3 py-2.5 font-mono text-base text-stone-900 outline-none placeholder:text-stone-300"
        />
        {suffix && (
          <span className="flex select-none items-center border-l border-stone-200 bg-stone-50 px-3 font-mono text-sm text-stone-500">
            {suffix}
          </span>
        )}
      </div>
    </label>
  );
}

export default function App() {
  const [sel, setSel] = useState(PRODUCTS[0].id);
  const [query, setQuery] = useState("");
  const base = PRODUCTS.find((p) => p.id === sel);

  const [marker, setMarker] = useState(base.marker);
  const [unit, setUnit] = useState(base.unit);
  const [cNat, setCNat] = useState(String(base.nat || ""));
  const [cOl, setCOl] = useState("");

  const [currency, setCurrency] = useState(CURRENCIES[0]);
  const [pOl, setPOl] = useState("");
  const [pNat, setPNat] = useState("");
  const [target, setTarget] = useState("");

  function pick(id) {
    const p = PRODUCTS.find((x) => x.id === id);
    setSel(id);
    setMarker(p.marker);
    setUnit(p.unit);
    setCNat(p.nat ? String(p.nat) : "");
    setCOl("");
  }

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return PRODUCTS;
    return PRODUCTS.filter(
      (p) => p.name.toLowerCase().includes(q) || p.marker.toLowerCase().includes(q)
    );
  }, [query]);

  const c = useMemo(() => {
    const cn = num(cNat), co = num(cOl), po = num(pOl), pn = num(pNat), tg = num(target);
    const R = cn > 0 && co > 0 ? co / cn : NaN;          // kg natural spice per kg oleoresin
    const CIU = Number.isFinite(R) && po > 0 ? po / R : NaN;
    const saveKg = Number.isFinite(CIU) && pn > 0 ? pn - CIU : NaN;
    const savePct = Number.isFinite(saveKg) && pn > 0 ? (saveKg / pn) * 100 : NaN;
    const oleoNeed = Number.isFinite(R) && tg > 0 ? tg / R : NaN;
    const costOleo = Number.isFinite(oleoNeed) && po > 0 ? oleoNeed * po : NaN;
    const costNat = tg > 0 && pn > 0 ? tg * pn : NaN;
    const saveTotal = Number.isFinite(costOleo) && Number.isFinite(costNat) ? costNat - costOleo : NaN;
    return { R, CIU, saveKg, savePct, oleoNeed, costOleo, costNat, saveTotal };
  }, [cNat, cOl, pOl, pNat, target]);

  const m = currency.sym;
  const verdict =
    !Number.isFinite(c.saveKg) ? "none" : c.saveKg > 0.0001 ? "save" : c.saveKg < -0.0001 ? "over" : "even";

  return (
    <div className="min-h-screen bg-stone-100 px-4 py-6 text-stone-900 sm:px-6 sm:py-10">
      <div className="mx-auto max-w-2xl">
        {/* Header */}
        <header className="mb-6">
          <div className="flex items-center gap-2 text-amber-700">
            <FlaskConical className="h-5 w-5" strokeWidth={2.2} />
            <span className="text-xs font-bold uppercase tracking-[0.18em]">Oleoresins · Cost in use</span>
          </div>
          <h1 className="mt-2 text-3xl font-extrabold leading-tight tracking-tight sm:text-4xl">
            Oleoresin <span className="text-stone-400">vs.</span> natural spice replacement
          </h1>
          <p className="mt-2 text-sm leading-relaxed text-stone-600">
            Replacement factor on a marker basis, cost in use, and real savings — across the full set of
            commercial spice oleoresins.
          </p>
        </header>

        {/* Step 1 · Product */}
        <section className="mb-4 rounded-2xl border border-stone-200 bg-white p-4 shadow-sm sm:p-5">
          <div className="mb-3 flex items-center justify-between gap-3">
            <h2 className="flex items-center gap-2 text-sm font-bold uppercase tracking-wide text-stone-700">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-stone-900 text-xs font-bold text-white">1</span>
              <Leaf className="h-4 w-4 text-amber-700" /> Oleoresin
            </h2>
            <div className="relative w-40 sm:w-56">
              <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-stone-400" />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search…"
                className="w-full rounded-lg border border-stone-300 bg-white py-1.5 pl-8 pr-2 text-sm outline-none focus:border-amber-600 focus:ring-2 focus:ring-amber-600/20"
              />
            </div>
          </div>

          <div className="space-y-3">
            {CATS.map((cat) => {
              const items = filtered.filter((p) => p.cat === cat.id);
              if (!items.length) return null;
              return (
                <div key={cat.id}>
                  <div className="mb-1.5 text-[10px] font-bold uppercase tracking-[0.14em] text-stone-400">
                    {cat.label}
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {items.map((p) => {
                      const active = p.id === sel;
                      return (
                        <button
                          key={p.id}
                          onClick={() => pick(p.id)}
                          className={
                            "rounded-full border px-3 py-1.5 text-sm font-medium transition focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-600/40 " +
                            (active
                              ? "border-stone-900 bg-stone-900 text-white"
                              : "border-stone-300 bg-white text-stone-600 hover:border-amber-600 hover:text-stone-900")
                          }
                        >
                          {p.name}
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
            {!filtered.length && (
              <p className="py-2 text-sm text-stone-400">No oleoresin matches “{query}”.</p>
            )}
          </div>
        </section>

        {/* Step 2 · Marker concentration */}
        <section className="mb-4 rounded-2xl border border-stone-200 bg-white p-4 shadow-sm sm:p-5">
          <div className="mb-3 flex items-center gap-2">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-stone-900 text-xs font-bold text-white">2</span>
            <h2 className="flex items-center gap-1.5 text-sm font-bold uppercase tracking-wide text-stone-700">
              <Scale className="h-4 w-4 text-amber-700" /> Marker concentration
            </h2>
          </div>

          <div className="mb-4 flex flex-wrap items-end gap-3">
            <label className="grow">
              <span className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-stone-500">
                <Pencil className="h-3 w-3" /> Parameter that governs replacement
              </span>
              <input
                value={marker}
                onChange={(e) => setMarker(e.target.value)}
                className="mt-1.5 w-full rounded-lg border border-stone-300 bg-white px-3 py-2.5 text-base outline-none focus:border-amber-600 focus:ring-2 focus:ring-amber-600/20"
              />
            </label>
            <label className="w-24">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-stone-500">Unit</span>
              <input
                value={unit}
                onChange={(e) => setUnit(e.target.value)}
                className="mt-1.5 w-full rounded-lg border border-stone-300 bg-white px-3 py-2.5 text-center font-mono text-base outline-none focus:border-amber-600 focus:ring-2 focus:ring-amber-600/20"
              />
            </label>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Field label="In the natural spice" hint="reference, editable" suffix={unit} value={cNat} onChange={setCNat} placeholder="0.0" />
            <Field label="In the oleoresin" hint="from your CoA" suffix={unit} value={cOl} onChange={setCOl} placeholder="0.0" />
          </div>

          <p className="mt-3 flex items-start gap-1.5 text-xs leading-relaxed text-stone-500">
            <Info className="mt-0.5 h-3.5 w-3.5 shrink-0 text-stone-400" />
            Natural-spice values are typical industry references; oleoresin defaults follow the FCC spice-oleoresin
            monograph. Adjust both to your own standard or Certificate of Analysis (CoA). For color and pungency,
            keep the same method on both sides.
          </p>
        </section>

        {/* Readout · Replacement factor */}
        <section className="mb-4 overflow-hidden rounded-2xl bg-stone-900 text-white shadow-md">
          <div className="border-b border-white/10 px-5 py-3">
            <span className="text-[11px] font-semibold uppercase tracking-[0.18em] text-amber-400">Replacement factor</span>
          </div>
          <div className="px-5 py-6 text-center">
            {Number.isFinite(c.R) ? (
              <>
                <div className="font-mono text-5xl font-bold leading-none text-amber-400 sm:text-6xl">
                  {fmt(c.R, c.R >= 100 ? 0 : 1)}×
                </div>
                <p className="mt-3 font-mono text-sm text-stone-300">
                  1 kg oleoresin <span className="text-amber-400">⟶</span> {fmt(c.R, c.R >= 100 ? 0 : 2)} kg {base.name.toLowerCase()}
                </p>
                <p className="mt-1 text-xs text-stone-500">basis: {marker.toLowerCase()}</p>
              </>
            ) : (
              <p className="py-4 font-mono text-sm text-stone-500">Enter both concentrations to see the factor</p>
            )}
          </div>
        </section>

        {/* Step 3 · Prices */}
        <section className="mb-4 rounded-2xl border border-stone-200 bg-white p-4 shadow-sm sm:p-5">
          <div className="mb-3 flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-stone-900 text-xs font-bold text-white">3</span>
              <h2 className="flex items-center gap-1.5 text-sm font-bold uppercase tracking-wide text-stone-700">
                <Coins className="h-4 w-4 text-amber-700" /> Price per kg
              </h2>
            </div>
            <div className="flex flex-wrap gap-1">
              {CURRENCIES.map((cu) => (
                <button
                  key={cu.label}
                  onClick={() => setCurrency(cu)}
                  className={
                    "rounded-md px-2 py-1 text-xs font-semibold transition " +
                    (currency.label === cu.label ? "bg-amber-700 text-white" : "bg-stone-100 text-stone-500 hover:bg-stone-200")
                  }
                >
                  {cu.label}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Field label="Oleoresin price" suffix={`${m}/kg`} value={pOl} onChange={setPOl} placeholder="0.00" />
            <Field label="Natural spice price" suffix={`${m}/kg`} value={pNat} onChange={setPNat} placeholder="0.00" />
          </div>
        </section>

        {/* Cost results */}
        <section className="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
          <div className="rounded-2xl border border-stone-200 bg-white p-5 shadow-sm">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-stone-500">Oleoresin cost in use</span>
            <p className="mt-1 text-xs text-stone-400">per kg of spice equivalent</p>
            <div className="mt-3 font-mono text-3xl font-bold text-stone-900">
              {Number.isFinite(c.CIU) ? `${m} ${fmt(c.CIU)}` : "—"}
            </div>
          </div>

          <div
            className={
              "rounded-2xl border p-5 shadow-sm " +
              (verdict === "save" ? "border-emerald-200 bg-emerald-50" : verdict === "over" ? "border-red-200 bg-red-50" : "border-stone-200 bg-white")
            }
          >
            <span className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-stone-500">
              {verdict === "save" ? (
                <TrendingDown className="h-4 w-4 text-emerald-700" />
              ) : verdict === "over" ? (
                <TrendingUp className="h-4 w-4 text-red-700" />
              ) : (
                <Minus className="h-4 w-4 text-stone-400" />
              )}
              {verdict === "over" ? "Extra cost" : "Savings"} per kg
            </span>
            <p className="mt-1 text-xs text-stone-400">vs. buying the natural spice</p>
            <div
              className={
                "mt-3 font-mono text-3xl font-bold " +
                (verdict === "save" ? "text-emerald-700" : verdict === "over" ? "text-red-700" : "text-stone-900")
              }
            >
              {Number.isFinite(c.saveKg) ? `${m} ${fmt(Math.abs(c.saveKg))}` : "—"}
            </div>
            {Number.isFinite(c.savePct) && (
              <div
                className={
                  "mt-1 font-mono text-sm font-semibold " +
                  (verdict === "save" ? "text-emerald-600" : verdict === "over" ? "text-red-600" : "text-stone-500")
                }
              >
                {c.savePct >= 0 ? "" : "−"}
                {fmt(Math.abs(c.savePct), 1)}%
              </div>
            )}
          </div>
        </section>

        {/* Batch (optional) */}
        <section className="rounded-2xl border border-dashed border-stone-300 bg-white p-4 shadow-sm sm:p-5">
          <h2 className="mb-3 text-sm font-bold uppercase tracking-wide text-stone-700">
            Batch calculation <span className="font-normal normal-case tracking-normal text-stone-400">(optional)</span>
          </h2>
          <div className="max-w-xs">
            <Field label="Natural spice to replace" suffix="kg" value={target} onChange={setTarget} placeholder="0" />
          </div>
          {Number.isFinite(c.oleoNeed) && (
            <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div className="rounded-xl bg-stone-50 p-3">
                <span className="text-[11px] uppercase tracking-wider text-stone-500">Oleoresin needed</span>
                <div className="mt-1 font-mono text-xl font-bold text-stone-900">{fmt(c.oleoNeed)} kg</div>
              </div>
              <div className="rounded-xl bg-stone-50 p-3">
                <span className="text-[11px] uppercase tracking-wider text-stone-500">Cost with oleoresin</span>
                <div className="mt-1 font-mono text-xl font-bold text-stone-900">
                  {Number.isFinite(c.costOleo) ? `${m} ${fmt(c.costOleo)}` : "—"}
                </div>
              </div>
              <div className="rounded-xl bg-stone-50 p-3">
                <span className="text-[11px] uppercase tracking-wider text-stone-500">Total savings</span>
                <div
                  className={
                    "mt-1 font-mono text-xl font-bold " +
                    (Number.isFinite(c.saveTotal) && c.saveTotal >= 0 ? "text-emerald-700" : "text-red-700")
                  }
                >
                  {Number.isFinite(c.saveTotal) ? `${m} ${fmt(c.saveTotal)}` : "—"}
                </div>
              </div>
            </div>
          )}
        </section>

        <footer className="mt-6 text-center text-xs leading-relaxed text-stone-400">
          Replacement is computed by marker equivalence. Standardization parameters follow the Food Chemicals Codex
          (FCC) spice-oleoresin monograph. Real sensory substitution may require formulation adjustments (volatiles,
          matrix, carrier). Always verify against your CoA.
        </footer>
      </div>
    </div>
  );
}
