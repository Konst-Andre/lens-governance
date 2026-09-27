// smoke_local.mjs — локальний стенд lens-gh: справжній worker.js + підроблений GitHub у памʼяті.
// живе доки: живе lens-gh (tools/lens-gh/worker.js); запускається з smoke.sh (режим local), окремо не потрібен.
// Дім: lens-governance/tools/lens-gh/. Мережі не торкається: весь fetch воркера йде в підробку нижче.
// Підробка повторює те, на чому можна спіткнутися в житті: tarball = 302 на codeload з token у query,
// а заголовок Authorization на іншому домені відкидається (як у fetch за специфікацією); tar кладе все в теку-префікс.
import http from "node:http";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { Readable } from "node:stream";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.PORT || 8787);
const OUT = process.env.OUT || path.join(HERE, "smoke_out");
const LOG = path.join(OUT, "worker.log");
fs.mkdirSync(OUT, { recursive: true });
fs.writeFileSync(LOG, "");

// ---------- env воркера ----------
const ENV = { GH_TOKEN: "fake-gh-token", MCP_KEY: "localkey", OWNER: "Konst-Andre", TICKET_KEY: "local-ticket-key-0123456789abcdef0123456789" };
const ENV_FULL = { ...ENV };

// ---------- годинник (для простроченого квитка) ----------
let clockShift = 0;
const realNow = Date.now.bind(Date);
Date.now = () => realNow() + clockShift * 1000;

// ---------- лог воркера ----------
const realLog = console.log.bind(console);
console.log = (...a) => {
  const line = a.join(" ");
  if (line.startsWith("lens-gh t")) fs.appendFileSync(LOG, line + "\n");
  process.stderr.write("[worker] " + line + "\n");
};

// ---------- підроблений GitHub ----------
const gitSha = (buf) => crypto.createHash("sha1").update(Buffer.concat([Buffer.from("blob " + buf.length + "\0"), buf])).digest("hex");
function prng(seed, n) { // детермінований «xlsx»: повтор дає ті самі байти й той самий sha
  const out = Buffer.alloc(n); let x = seed >>> 0;
  for (let i = 0; i < n; i++) { x ^= x << 13; x >>>= 0; x ^= x >>> 17; x ^= x << 5; x >>>= 0; out[i] = x & 255; }
  return out;
}
const LINT = `import pathlib, sys
f = pathlib.Path(__file__).parent / "months/2026-09/route_pass2.xlsx"
if not f.is_file() or f.stat().st_size != 183000:
    print("lint FAIL"); sys.exit(1)
print("lint OK")
`;
const REPOS = {
  "Konst-Andre/routes-fake": {
    files: { "README.md": Buffer.from("fake routes\n"), "lint_repo.py": Buffer.from(LINT), "months/2026-09/route_pass2.xlsx": prng(20260927, 183000) },
  },
  "Konst-Andre/lens-target": { files: { "README.md": Buffer.from("target\n") } },
};
for (const [name, r] of Object.entries(REPOS)) {
  r.commit = crypto.createHash("sha1").update("commit:" + name).digest("hex");
  r.blobs = new Map();
  for (const buf of Object.values(r.files)) r.blobs.set(gitSha(buf), buf);
}
const CODELOAD_TOKEN = "codeload-" + crypto.randomBytes(6).toString("hex");
const seen = { codeloadAuthHeader: [], calls: [] };

function tarball(repoName) {
  const r = REPOS[repoName];
  const pre = repoName.replace("/", "-") + "-" + r.commit.slice(0, 7);
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "lgh-tar-"));
  for (const [p, buf] of Object.entries(r.files)) {
    fs.mkdirSync(path.join(tmp, pre, path.dirname(p)), { recursive: true });
    fs.writeFileSync(path.join(tmp, pre, p), buf);
  }
  const out = execFileSync("tar", ["czf", "-", "-C", tmp, pre]);
  fs.rmSync(tmp, { recursive: true, force: true });
  return out;
}

const J = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: { "Content-Type": "application/json" } });
const B = (buf, type = "application/octet-stream") => new Response(buf, { status: 200, headers: { "Content-Type": type, "Content-Length": String(buf.length) } });
const NF = () => J({ message: "Not Found" }, 404);

async function fakeGitHub(url, init = {}) {
  const u = new URL(url);
  const method = (init.method || "GET").toUpperCase();
  const h = new Headers(init.headers || {});
  seen.calls.push(method + " " + u.host + u.pathname);
  if (u.host === "codeload.github.com") {
    seen.codeloadAuthHeader.push(h.has("authorization"));
    if (u.searchParams.get("token") !== CODELOAD_TOKEN) return NF();
    const m = u.pathname.match(/^\/([^/]+\/[^/]+)\/legacy\.tar\.gz\/([0-9a-f]{40})$/);
    if (!m || !REPOS[m[1]] || REPOS[m[1]].commit !== m[2]) return NF();
    return B(tarball(m[1]), "application/x-gzip");
  }
  if (u.host !== "api.github.com") return NF();
  if (h.get("authorization") !== "Bearer " + ENV.GH_TOKEN) return J({ message: "Bad credentials" }, 401);
  if (!h.get("user-agent")) return J({ message: "UA required" }, 403);
  const m = u.pathname.match(/^\/repos\/([^/]+\/[^/]+)(\/.*)?$/);
  if (!m || !REPOS[m[1]]) return NF();
  const name = m[1], r = REPOS[name], rest = m[2] || "";
  const ref = u.searchParams.get("ref");
  const refOk = (x) => x === "main" || x === r.commit;
  let mm;
  if (rest === "" && method === "GET") return J({ default_branch: "main" });
  if ((mm = rest.match(/^\/commits\/(.+)$/)) && method === "GET") {
    if (!refOk(decodeURIComponent(mm[1]))) return J({ message: "No commit found" }, 422);
    return (h.get("accept") || "").includes(".sha") ? new Response(r.commit) : J({ sha: r.commit });
  }
  if (rest === "/git/ref/heads/main") return J({ object: { sha: r.commit } });
  if ((mm = rest.match(/^\/tarball\/([0-9a-f]{40})$/)) && method === "GET") {
    if (mm[1] !== r.commit) return NF();
    return new Response(null, { status: 302, headers: { Location: `https://codeload.github.com/${name}/legacy.tar.gz/${mm[1]}?token=${CODELOAD_TOKEN}` } });
  }
  if ((mm = rest.match(/^\/contents\/?(.*)$/)) && method === "GET") {
    if (ref && !refOk(ref)) return NF();
    const p = decodeURIComponent(mm[1]);
    if (r.files[p]) return (h.get("accept") || "").includes("raw") ? B(r.files[p]) : J({ type: "file", name: path.basename(p), path: p, sha: gitSha(r.files[p]), size: r.files[p].length });
    const pre = p ? p + "/" : "";
    const kids = new Map();
    for (const [fp, buf] of Object.entries(r.files)) {
      if (!fp.startsWith(pre)) continue;
      const tail = fp.slice(pre.length), seg = tail.split("/")[0];
      if (tail.includes("/")) kids.set(seg, { type: "dir", name: seg, path: pre + seg, sha: "0".repeat(40), size: 0 });
      else kids.set(seg, { type: "file", name: seg, path: fp, sha: gitSha(buf), size: buf.length });
    }
    return kids.size ? J([...kids.values()]) : NF();
  }
  if (rest === "/git/blobs" && method === "POST") {
    let body;
    try { body = JSON.parse(Buffer.from(await new Response(init.body).arrayBuffer()).toString("utf8")); } catch (_) { return J({ message: "Problems parsing JSON" }, 400); }
    const c = String(body.content || "");
    if (body.encoding !== "base64" || c.length % 4 || !/^[A-Za-z0-9+/]*={0,2}$/.test(c)) return J({ message: "content is not valid Base64" }, 422);
    const buf = Buffer.from(c, "base64");
    const sha = gitSha(buf);
    r.blobs.set(sha, buf);
    return J({ sha, url: `https://api.github.com/repos/${name}/git/blobs/${sha}` }, 201);
  }
  if ((mm = rest.match(/^\/git\/blobs\/([0-9a-f]{40})$/)) && method === "GET") {
    const buf = r.blobs.get(mm[1]);
    return buf ? B(buf) : NF();
  }
  return NF();
}

// fetch за специфікацією: іде за редиректом, на інший origin не несе Authorization
async function fakeFetch(input, init = {}) {
  let url = typeof input === "string" ? input : input.url;
  let hdrs = new Headers(init.headers || {});
  for (let hop = 0; hop < 5; hop++) {
    const res = await fakeGitHub(url, { ...init, headers: hdrs });
    if (![301, 302, 307, 308].includes(res.status) || init.redirect === "manual") return res;
    const next = new URL(res.headers.get("Location"), url);
    if (next.origin !== new URL(url).origin) { hdrs = new Headers(hdrs); hdrs.delete("authorization"); }
    url = next.toString();
  }
  throw new Error("too many redirects");
}
globalThis.fetch = fakeFetch;

// ---------- воркер ----------
const src = fs.readFileSync(path.join(HERE, "worker.js"));
const tmpMod = path.join(os.tmpdir(), "lens-gh-worker-" + crypto.createHash("md5").update(src).digest("hex") + ".mjs");
fs.writeFileSync(tmpMod, src);
const worker = (await import(tmpMod)).default;

// підпис квитка — незалежна реалізація формату (base64url(JSON).base64url(HMAC-SHA256)) для підроблених квитків
const b64u = (b) => Buffer.from(b).toString("base64url");
function signLocal(payload) {
  const body = b64u(JSON.stringify(payload));
  return body + "." + b64u(crypto.createHmac("sha256", ENV.TICKET_KEY).update(body).digest());
}

// ---------- HTTP ----------
const server = http.createServer(async (req, res) => {
  try {
    const u = new URL(req.url, "http://127.0.0.1:" + PORT);
    if (u.pathname.startsWith("/__")) {
      let out = {};
      if (u.pathname === "/__clock") { clockShift = Number(u.searchParams.get("shift") || 0); out = { clockShift }; }
      else if (u.pathname === "/__sign") { const chunks = []; for await (const c of req) chunks.push(c); out = { ticket: signLocal(JSON.parse(Buffer.concat(chunks).toString())) }; }
      else if (u.pathname === "/__env") { const drop = u.searchParams.get("drop"); for (const k of Object.keys(ENV)) delete ENV[k]; Object.assign(ENV, ENV_FULL); if (drop) delete ENV[drop]; out = { keys: Object.keys(ENV) }; }
      else if (u.pathname === "/__gh") out = { codeloadAuthHeader: seen.codeloadAuthHeader, calls: seen.calls.length, now: Math.floor(Date.now() / 1000) };
      res.writeHead(200, { "Content-Type": "application/json" });
      return res.end(JSON.stringify(out));
    }
    const hasBody = !["GET", "HEAD"].includes(req.method);
    const request = new Request(u.toString(), { method: req.method, headers: req.headers, body: hasBody ? Readable.toWeb(req) : undefined, duplex: "half" });
    const r = await worker.fetch(request, { ...ENV });
    const headers = {};
    r.headers.forEach((v, k) => { headers[k] = v; });
    res.writeHead(r.status, headers);
    if (r.body) Readable.fromWeb(r.body).pipe(res); else res.end();
  } catch (e) {
    process.stderr.write("[harness] " + (e && e.stack || e) + "\n");
    res.writeHead(500); res.end("harness error");
  }
});
server.listen(PORT, "127.0.0.1", () => realLog("ready " + PORT));
