// Crea o deja como nueva la cuenta demo del Sprint 5, solo con la API pública.
//   node scripts/crear-demo.mjs           crea la cuenta (si no existe) y sus eventos
//   node scripts/crear-demo.mjs --ensayo  muestra qué haría, sin llamar a la API
// Las fechas salen de hoy. Solo toca demo@eventflow.com: no recibe otro correo.
// Si BACK no se define, usa la API de Render.

const BACK = process.env.BACK ?? "https://eventflow-back.onrender.com";
const EMAIL = "demo@eventflow.com";
const PASSWORD = "demo1234";
const NOMBRE = "Organizador Demo";
const ENSAYO = process.argv.includes("--ensayo");

// Estados de las gestiones.
const POR_HACER = "por hacer";
const EN_CURSO = "en curso";
const HECHA = "hecha";
const POSPUESTA = "pospuesta";

// Gestiones: [días desde hoy, título, horas, estado, nota]
const EVENTOS = [
  {
    nombre: "Boda de Laura y Andrés",
    tipo: "Boda",
    lugar: "Hacienda El Paraíso, Cali",
    cliente_nombre: "Laura Gómez",
    cliente_telefono: "300 555 1234",
    diasHastaEvento: 21,
    gestiones: [
      [-5, "Reservar el salón", 2, HECHA],
      [-3, "Enviar invitaciones", 1.5, HECHA],
      [-2, "Confirmar el catering", 2, POR_HACER],
      [0, "Llamar al fotógrafo", 1, POR_HACER],
      [0, "Probar el menú con los novios", 3, EN_CURSO],
      [2, "Contratar la banda", 2, POSPUESTA, "Esperando la cotización de la segunda banda"],
      [4, "Decoración floral", 3, POR_HACER],
      [20, "Ensayo general", 2, POR_HACER],
    ],
  },
  {
    nombre: "Lanzamiento Café Origen",
    tipo: "Corporativo",
    lugar: "Centro de Eventos Valle del Pacífico",
    cliente_nombre: "Café Origen S.A.S.",
    cliente_correo: "eventos@cafeorigen.co",
    diasHastaEvento: 10,
    gestiones: [
      [-1, "Imprimir volantes", 1, HECHA],
      // Mañana queda justo en el límite de 6 h: mover otra gestión a ese día da el conflicto.
      [1, "Buscar proveedor de sonido", 4, POR_HACER],
      [1, "Diseñar piezas gráficas", 2, POR_HACER],
      [3, "Confirmar lista de invitados", 1, POR_HACER],
    ],
  },
  {
    nombre: "Cumpleaños de Sofía",
    tipo: "Cumpleaños",
    lugar: "Salón social Conjunto Los Robles",
    cliente_nombre: "Marta Ruiz",
    cliente_telefono: "315 222 3344",
    cliente_correo: "marta.ruiz@correo.com",
    diasHastaEvento: 5,
    gestiones: [
      [-4, "Comprar la torta", 1, HECHA],
      [-2, "Contratar recreacionista", 1.5, HECHA],
    ],
  },
];

const pad = (n) => String(n).padStart(2, "0");
const fechaLocal = (dias) => {
  const d = new Date();
  d.setDate(d.getDate() + dias);
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
};

async function api(ruta, { metodo = "GET", cuerpo, token } = {}) {
  const res = await fetch(`${BACK}${ruta}`, {
    method: metodo,
    headers: {
      Accept: "application/json",
      ...(cuerpo ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: cuerpo ? JSON.stringify(cuerpo) : undefined,
  });
  const texto = await res.text();
  let datos = null;
  try { datos = texto ? JSON.parse(texto) : null; } catch { datos = texto; }
  return { status: res.status, datos };
}

// Pide la respuesta y para si no es la esperada, mostrando qué contestó la API.
async function pedir(ruta, opciones, esperados) {
  const r = await api(ruta, opciones);
  if (!esperados.includes(r.status)) {
    throw new Error(`${opciones?.metodo ?? "GET"} ${ruta} -> ${r.status} ${JSON.stringify(r.datos)}`);
  }
  return r.datos;
}

function resumen() {
  for (const e of EVENTOS) {
    console.log(`\n${e.nombre} (evento el ${fechaLocal(e.diasHastaEvento)})`);
    for (const [dias, titulo, horas, estado, nota] of e.gestiones) {
      console.log(`  ${fechaLocal(dias)}  ${horas} h  ${estado.padEnd(9)} ${titulo}${nota ? ` — ${nota}` : ""}`);
    }
  }
}

if (ENSAYO) {
  console.log(`Ensayo: no se llama a la API. Cuenta ${EMAIL}, servidor ${BACK}.`);
  resumen();
  process.exit(0);
}

// Render gratis duerme: el primer intento puede tardar.
console.log("Despertando la API...");
for (let i = 0; i < 6; i++) {
  try {
    const r = await api("/api/health/");
    if (r.status === 200) break;
  } catch { /* sigue intentando */ }
  if (i === 5) throw new Error("La API no respondió.");
  await new Promise((ok) => setTimeout(ok, 10000));
}

let sesion = await api("/api/login/", { metodo: "POST", cuerpo: { email: EMAIL, password: PASSWORD } });
let accion = "reiniciada";
if (sesion.status !== 200) {
  sesion = await api("/api/registro/", {
    metodo: "POST",
    cuerpo: { nombre: NOMBRE, email: EMAIL, password: PASSWORD },
  });
  if (sesion.status !== 201) {
    throw new Error(`No pude entrar ni crear la cuenta: ${sesion.status} ${JSON.stringify(sesion.datos)}`);
  }
  accion = "creada";
}
const token = sesion.datos.token;

// Se parte de cero para que la demo siempre se vea igual.
const existentes = await pedir("/api/eventos/", { token }, [200]);
const lista = Array.isArray(existentes) ? existentes : existentes?.results ?? [];
for (const e of lista) {
  await pedir(`/api/eventos/${e.id}/`, { metodo: "DELETE", token }, [200, 204]);
}

let total = 0;
for (const e of EVENTOS) {
  const { diasHastaEvento, gestiones, ...datos } = e;
  const evento = await pedir("/api/eventos/", {
    metodo: "POST",
    token,
    cuerpo: { cliente_telefono: "", cliente_correo: "", ...datos, fecha_hora: `${fechaLocal(diasHastaEvento)}T18:00:00` },
  }, [201]);
  for (const [dias, titulo, horas, estado, nota] of gestiones) {
    const gestion = await pedir(`/api/eventos/${evento.id}/subtareas/`, {
      metodo: "POST",
      token,
      cuerpo: { titulo, fecha_objetivo: fechaLocal(dias), horas_estimadas: horas },
    }, [201]);
    // Se crean "por hacer" y después cambian de estado, como lo hace la app.
    if (estado !== POR_HACER) {
      await pedir(`/api/subtareas/${gestion.id}/`, {
        metodo: "PATCH",
        token,
        cuerpo: { estado, ...(nota ? { nota } : {}) },
      }, [200]);
    }
    total++;
  }
}

console.log(`Cuenta demo ${accion}: ${EMAIL} / ${PASSWORD} (${EVENTOS.length} eventos, ${total} gestiones).`);
