// URL de l'API FastAPI
const API_BASE = "http://127.0.0.1:8000";

// Description des variables (pour garder la correspondance avec le backend)
const VARIABLES = [
  "model",
  "engine",
  "transmission",
  "drivetrain",
  "color",
  "interior",
  "pack",
];

// Labels lisibles (doivent être cohérents avec solver.py)
const LABELS = {
  model: {
    compact: "Compact Urbain",
    suv: "SUV Trail",
    sport_gt: "Coupé GT",
    luxury_sedan: "Berline Luxe",
  },
  engine: {
    petrol_1_6: "Essence 1.6L",
    petrol_2_0t: "Essence 2.0L Turbo",
    diesel_2_0: "Diesel 2.0L",
    hybrid_2_0: "Hybride 2.0L",
    electric_lr: "Électrique Long Range",
  },
  transmission: {
    manual: "Manuelle 6 rapports",
    auto8: "Auto 8 rapports",
  },
  drivetrain: {
    fwd: "Traction (FWD)",
    rwd: "Propulsion (RWD)",
    awd: "Transmission intégrale (AWD)",
  },
  color: {
    white: "Blanc Nacré",
    black: "Noir Onyx",
    red: "Rouge Carmin",
    blue: "Bleu Horizon",
    silver: "Gris Argent",
  },
  interior: {
    cloth: "Tissu",
    leather: "Cuir",
    alcantara: "Alcantara",
  },
  pack: {
    none: "Aucun pack",
    tech: "Pack Tech",
    premium: "Pack Premium",
    offroad: "Pack Offroad",
    performance: "Pack Performance",
  },
};

const form = document.getElementById("config-form");
const statusEl = document.getElementById("status");
const solutionEl = document.getElementById("solution");
const solveBtn = document.getElementById("solve-btn");
const resetBtn = document.getElementById("reset-btn");
const carBadge = document.getElementById("car-badge");
const carDetails = document.getElementById("car-details");
const BRANDS = {
  compact: "Civic",
  suv: "Trail-X",
  sport_gt: "Apex GT",
  luxury_sedan: "Aurora",
};
const PRESETS = {
  urban: {
    model: "compact",
    engine: "petrol_1_6",
    transmission: "manual",
    drivetrain: "fwd",
    color: "silver",
    interior: "cloth",
    pack: "tech",
  },
  trail: {
    model: "suv",
    engine: "diesel_2_0",
    transmission: "auto8",
    drivetrain: "awd",
    color: "black",
    interior: "leather",
    pack: "offroad",
  },
  gt: {
    model: "sport_gt",
    engine: "petrol_2_0t",
    transmission: "auto8",
    drivetrain: "rwd",
    color: "red",
    interior: "alcantara",
    pack: "performance",
  },
  lux: {
    model: "luxury_sedan",
    engine: "hybrid_2_0",
    transmission: "auto8",
    drivetrain: "awd",
    color: "blue",
    interior: "leather",
    pack: "premium",
  },
};

const ENGINE_SPECS = {
  petrol_1_6: { hp: 130, accel: 9.8, range: 650, price: 0 },
  petrol_2_0t: { hp: 210, accel: 6.7, range: 620, price: 5000 },
  diesel_2_0: { hp: 170, accel: 8.4, range: 900, price: 3000 },
  hybrid_2_0: { hp: 190, accel: 7.9, range: 850, price: 6000 },
  electric_lr: { hp: 320, accel: 4.8, range: 540, price: 12000 },
};

const MODEL_BASE = {
  compact: { price: 24000, hp: 0, accel: 0, range: 0 },
  suv: { price: 38000, hp: 10, accel: 0.3, range: -40 },
  sport_gt: { price: 55000, hp: 50, accel: -0.8, range: -50 },
  luxury_sedan: { price: 62000, hp: 20, accel: -0.2, range: -20 },
};

const PACK_EFFECT = {
  none: { price: 0, hp: 0, accel: 0, range: 0 },
  tech: { price: 1500, hp: 0, accel: 0, range: 0 },
  premium: { price: 4000, hp: 0, accel: 0, range: 0 },
  offroad: { price: 2000, hp: -5, accel: 0.4, range: -30 },
  performance: { price: 4500, hp: 40, accel: -0.6, range: -40 },
};

const DRIVE_EFFECT = {
  fwd: { price: 0, range: 0, accel: 0 },
  rwd: { price: 400, range: -5, accel: -0.05 },
  awd: { price: 1800, range: -30, accel: 0.15 },
};

// Initialise les selects avec des options vides (remplies après premier /propagate)
function initSelects() {
  VARIABLES.forEach((v) => {
    const select = document.getElementById(v);
    select.innerHTML = "";
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "-- (non spécifié) --";
    select.appendChild(opt);
  });
}

// Récupère les affectations courantes du formulaire
function getAssignments() {
  const data = {};
  VARIABLES.forEach((v) => {
    const value = document.getElementById(v).value;
    data[v] = value === "" ? null : value;
  });
  return data;
}

function pickColor(assignments) {
  const colorChoice = assignments.color;
  const colorMap = {
    white: "#e5e7eb",
    black: "#0f172a",
    red: "#ef4444",
    blue: "#2563eb",
    silver: "#cbd5e1",
  };
  return colorChoice && colorMap[colorChoice] ? colorMap[colorChoice] : "#38bdf8";
}

function pickAccent(assignments) {
  if (assignments.pack === "premium") return "#f59e0b";
  if (assignments.pack === "performance") return "#ef4444";
  if (assignments.pack === "offroad") return "#22c55e";
  if (assignments.model === "sport_gt") return "#ef4444";
  if (assignments.model === "luxury_sedan") return "#fbbf24";
  if (assignments.model === "suv") return "#22c55e";
  return "#38bdf8";
}

function rideSettings(assignments) {
  // Default
  let ride = "0px";
  let wheel = "52px";
  let offset = "58px";

  if (assignments.model === "suv" || assignments.pack === "offroad") {
    ride = "-4px";
    wheel = "58px";
    offset = "64px";
  }
  if (assignments.model === "sport_gt" || assignments.pack === "performance") {
    ride = "6px";
    wheel = "50px";
    offset = "56px";
  }
  if (assignments.model === "luxury_sedan") {
    wheel = "54px";
  }
  return { ride, wheel, offset };
}

function computeSpecs(assignments) {
  const engine = ENGINE_SPECS[assignments.engine];
  const model = MODEL_BASE[assignments.model];
  const pack = PACK_EFFECT[assignments.pack || "none"];
  const drive = DRIVE_EFFECT[assignments.drivetrain || "fwd"];

  if (!engine || !model) {
    return { hp: null, accel: null, range: null, price: null };
  }

  let hp = engine.hp + model.hp + pack.hp;
  let accel = engine.accel + model.accel + pack.accel + drive.accel;
  let range = engine.range + model.range + pack.range + drive.range;
  let price = model.price + engine.price + pack.price + drive.price;

  return { hp: Math.round(hp), accel: Math.max(accel, 3.5), range: Math.round(range), price };
}

function fmt(value, suffix) {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${value}${suffix}`;
}

function fmtPrice(value) {
  if (!value) return "—";
  return `€${(value / 1000).toFixed(1)}k`;
}

function updateSpecs(assignments) {
  const { hp, accel, range, price } = computeSpecs(assignments);
  document.getElementById("spec-power").textContent = fmt(hp, " ch");
  document.getElementById("spec-accel").textContent = fmt(accel ? accel.toFixed(1) : null, " s");
  document.getElementById("spec-range").textContent = fmt(range, " km");
  document.getElementById("spec-price").textContent = fmtPrice(price);
}

function labelFor(varName, value) {
  const varLabels = LABELS[varName];
  if (!varLabels) return value || "";
  return varLabels[value] || value || "";
}

function updateCarPreview(assignments) {
  const preview = document.querySelector(".car-preview");
  if (!preview) return;
  const bodyColor = pickColor(assignments);
  const accentColor = pickAccent(assignments);
  const { ride, wheel, offset } = rideSettings(assignments);
  preview.style.setProperty("--car-color", bodyColor);
  preview.style.setProperty("--car-accent", accentColor);
  preview.style.setProperty("--car-ride", ride);
  preview.style.setProperty("--car-wheel", wheel);
  preview.style.setProperty("--car-wheel-offset", offset);

  const texts = [];
  if (assignments.model) texts.push(labelFor("model", assignments.model));
  if (assignments.engine) texts.push(labelFor("engine", assignments.engine));
  if (assignments.transmission) texts.push(labelFor("transmission", assignments.transmission));
  if (assignments.drivetrain) texts.push(labelFor("drivetrain", assignments.drivetrain));
  if (assignments.pack) texts.push(labelFor("pack", assignments.pack));

  carBadge.textContent = texts.length ? texts.join(" • ") : "Sélectionnez des options";

  const detailParts = [];
  if (assignments.model) detailParts.push(BRANDS[assignments.model] || assignments.model);
  if (assignments.color) detailParts.push(`Couleur ${labelFor("color", assignments.color)}`);
  if (assignments.interior) detailParts.push(`Intérieur ${labelFor("interior", assignments.interior)}`);
  if (assignments.pack) detailParts.push(`Pack ${labelFor("pack", assignments.pack)}`);

  carDetails.textContent =
    detailParts.length > 0
      ? detailParts.join(" • ")
      : "Le visuel s'adapte à vos choix (couleur, modèle, moteur, pack).";

  updateSpecs(assignments);
}

// Met à jour les options des selects en fonction des domaines renvoyés
function updateSelects(domains, valid, assignments = {}) {
  VARIABLES.forEach((v) => {
    const select = document.getElementById(v);
    const previousValue = select.value || "";
    const allowed = new Set(domains[v] || []);
    const currentAssignment = assignments[v] ?? "";

    // Nettoyer et reconstruire le select
    select.innerHTML = "";

    // option vide
    const emptyOpt = document.createElement("option");
    emptyOpt.value = "";
    emptyOpt.textContent = "-- (non spécifié) --";
    select.appendChild(emptyOpt);

    const labels = LABELS[v];
    if (!labels) return;

    Object.entries(labels).forEach(([value, label]) => {
      const opt = document.createElement("option");
      opt.value = value;
      opt.textContent = label;

      if (!allowed.has(value)) {
        opt.disabled = true;
        opt.classList.add("disabled-option");
      }

      select.appendChild(opt);
    });

    // Remettre la valeur de l'utilisateur si présente, sinon conserver l'ancienne valide
    if (currentAssignment && allowed.has(currentAssignment)) {
      select.value = currentAssignment;
    } else if (previousValue && allowed.has(previousValue)) {
      select.value = previousValue;
    } else {
      select.value = "";
    }
  });

  if (!valid) {
    statusEl.textContent =
      "⚠️ Les choix actuels sont incompatibles (aucune configuration possible).";
    statusEl.className = "status error";
  } else {
    statusEl.textContent =
      "✔️ Configuration partielle compatible. Choisissez d'autres options ou cliquez sur 'Trouver une configuration complète'.";
    statusEl.className = "status ok";
  }

  updateCarPreview(assignments);
}

// Appel API /propagate
async function propagate() {
  const assignments = getAssignments();

  // Toute modification annule la solution précédente
  solutionEl.textContent = "";

  try {
    const res = await fetch(`${API_BASE}/propagate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ assignments }),
    });

    if (!res.ok) {
      statusEl.textContent = "Erreur lors de la propagation";
      statusEl.className = "status error";
      return;
    }

    const data = await res.json();
    updateSelects(data.domains, data.valid, assignments);
  } catch (err) {
    console.error(err);
    statusEl.textContent = "Impossible de contacter l'API (backend lancé ?)";
    statusEl.className = "status error";
  }
}

// Appel API /solve
async function solve() {
  const assignments = getAssignments();

  try {
    const res = await fetch(`${API_BASE}/solve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ assignments }),
    });

    if (!res.ok) {
      solutionEl.textContent = "Erreur lors de la résolution.";
      return;
    }

    const data = await res.json();
    if (data.status === "INFEASIBLE" || !data.configuration) {
      solutionEl.textContent =
        "Aucune configuration complète n'est possible avec ces choix.";
      return;
    }

    // Affichage lisible
    const config = data.configuration;
    const lines = ["Configuration trouvée :"];
    VARIABLES.forEach((v) => {
      const value = config[v];
      const label =
        LABELS[v] && LABELS[v][value]
          ? LABELS[v][value]
          : value;
      lines.push(`- ${v} : ${label} (${value})`);
    });

    solutionEl.textContent = lines.join("\n");
  } catch (err) {
    console.error(err);
    solutionEl.textContent =
      "Erreur de communication avec l'API (vérifiez que le backend tourne).";
  }
}

function resetForm() {
  VARIABLES.forEach((v) => {
    const select = document.getElementById(v);
    if (select) select.value = "";
  });
  solutionEl.textContent = "";
  statusEl.textContent = "Sélectionnez des options pour démarrer.";
  statusEl.className = "status";
  updateCarPreview({});
  propagate();
}

function applyPreset(name) {
  const preset = PRESETS[name];
  if (!preset) return;
  VARIABLES.forEach((v) => {
    const select = document.getElementById(v);
    if (!select) return;
    select.value = preset[v] ?? "";
  });
  solutionEl.textContent = "";
  statusEl.textContent = "Preset appliqué, vérification des contraintes...";
  statusEl.className = "status ok";
  propagate();
}

// Écouteurs
VARIABLES.forEach((v) => {
  document.getElementById(v).addEventListener("change", propagate);
});

solveBtn.addEventListener("click", solve);
resetBtn.addEventListener("click", resetForm);
document.querySelectorAll(".preset-card").forEach((el) => {
  el.addEventListener("click", () => applyPreset(el.dataset.preset));
});

// Initialisation
initSelects();
propagate();
