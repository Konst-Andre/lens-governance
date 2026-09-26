// lens-gh — MCP-конектор «Lens GitHub» для claude.ai (Streamable HTTP, stateless, JSON).
// живе доки: Anthropic не поверне запис у GitHub із чату АБО конектор замінено іншим.
// Дім: Cloudflare Worker lens-gh (акаунт Konst). Канон коду — lens-governance/tools/lens-gh/ після першого успішного коміту.
// Секрети: MCP_KEY (ключ у URL), GH_TOKEN (fine-grained PAT). Змінні: OWNER, PROTECT (гілки через кому, куди запис заборонено).
// v1.1 (25.09.2026): expected_head обовʼязковий для запису в наявну гілку · gh_branch (list/create/delete) · gh_actions (workflows/runs/jobs/log/dispatch/rerun/cancel).
// Гілку за замовчуванням (main) видалити не можна ніколи — навіть якщо її нема в PROTECT.

const VERSION = "1.1.0";
const PROTOCOL_FALLBACK = "2025-06-18";
const GH = "https://api.github.com";

// ---------- утиліти ----------
function b64encode(text) {
  const bytes = new TextEncoder().encode(text);
  let bin = "";
  for (let i = 0; i < bytes.length; i += 32768) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 32768));
  return btoa(bin);
}
function b64decode(b64) {
  const bin = atob(String(b64).replace(/\s/g, ""));
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return new TextDecoder("utf-8", { fatal: false }).decode(bytes);
}
function safeEq(a, b) {
  a = String(a); b = String(b);
  if (a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}
function countOcc(hay, needle) {
  if (!needle) return 0;
  let n = 0, i = 0;
  while ((i = hay.indexOf(needle, i)) !== -1) { n++; i += needle.length; }
  return n;
}
class ToolError extends Error {}

// ---------- GitHub ----------
function gh(env) {
  const head = {
    "Authorization": "Bearer " + env.GH_TOKEN,
    // ⚠ Без User-Agent GitHub віддає 403, схожий на «поганий токен» (урок ae-edit).
    "User-Agent": "lens-gh-worker",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
  };
  async function call(method, path, body, accept) {
    const h = { ...head };
    if (accept) h.Accept = accept;
    if (body !== undefined) h["Content-Type"] = "application/json";
    const res = await fetch(GH + path, { method, headers: h, body: body === undefined ? undefined : JSON.stringify(body) });
    if (!res.ok) {
      let msg = "";
      try { msg = (await res.json()).message || ""; } catch (_) {}
      const e = new ToolError("GitHub " + res.status + " на " + method + " " + path + (msg ? ": " + msg : ""));
      e.status = res.status;
      throw e;
    }
    if (accept && accept.includes("raw")) return res.text();
    return res.status === 204 ? null : res.json();
  }
  return call;
}

function checkRepo(env, repo) {
  if (typeof repo !== "string" || !/^[\w.-]+\/[\w.-]+$/.test(repo)) throw new ToolError("repo має бути у формі власник/назва");
  const owner = repo.split("/")[0];
  if (owner.toLowerCase() !== String(env.OWNER || "Konst-Andre").toLowerCase())
    throw new ToolError("репо поза дозволеним власником: " + owner);
  return repo;
}
function checkPath(p) {
  if (typeof p !== "string" || !p || p.startsWith("/") || p.split("/").some((s) => s === ".." || s === ""))
    throw new ToolError("некоректний шлях: " + p);
  return p;
}
function enc(p) { return p.split("/").map(encodeURIComponent).join("/"); }

async function readFile(call, repo, path, ref) {
  const q = ref ? "?ref=" + encodeURIComponent(ref) : "";
  const meta = await call("GET", "/repos/" + repo + "/contents/" + enc(path) + q);
  if (Array.isArray(meta)) throw new ToolError(path + " — це тека; використай gh_list");
  let text;
  if (meta.encoding === "base64" && meta.content) text = b64decode(meta.content);
  else text = await call("GET", "/repos/" + repo + "/contents/" + enc(path) + q, undefined, "application/vnd.github.raw");
  return { text, sha: meta.sha, size: meta.size };
}

// ---------- інструменти ----------
const TOOLS = [
  {
    name: "gh_read",
    description: "Прочитати текстовий файл із репо Konst-Andre. Для великих файлів передавай start_line/end_line, щоб не тягнути весь файл.",
    inputSchema: {
      type: "object",
      properties: {
        repo: { type: "string", description: "власник/назва, напр. Konst-Andre/lens-governance" },
        path: { type: "string" },
        ref: { type: "string", description: "гілка, тег або sha; типово — гілка за замовчуванням" },
        start_line: { type: "integer", minimum: 1 },
        end_line: { type: "integer", minimum: 1 },
      },
      required: ["repo", "path"],
    },
  },
  {
    name: "gh_list",
    description: "Список файлів у теці репо (один рівень) або дерево всього репо (recursive=true).",
    inputSchema: {
      type: "object",
      properties: {
        repo: { type: "string" },
        path: { type: "string", description: "тека; порожньо = корінь" },
        ref: { type: "string" },
        recursive: { type: "boolean" },
      },
      required: ["repo"],
    },
  },
  {
    name: "gh_log",
    description: "Останні коміти гілки (sha, дата, перший рядок повідомлення).",
    inputSchema: {
      type: "object",
      properties: { repo: { type: "string" }, branch: { type: "string" }, n: { type: "integer", minimum: 1, maximum: 30 } },
      required: ["repo"],
    },
  },
  {
    name: "gh_commit",
    description:
      "Один коміт з кількох змін (один хід = один пуш). Кожна зміна — рівно одне: edits (заміни фрагментів, old має входити рівно 1 раз), content (повний текст — нові файли), content_base64 (бінарні), from (+move=true = git mv; можна з edits) або delete=true. " +
      "expected_head — sha голови гілки, на який розраховані правки (захист від перезапису); ОБОВʼЯЗКОВИЙ для запису в наявну гілку. dry_run=true — лише перевірка без запису. Запис у захищені гілки заборонено. Файли .github/workflows/* потребують дозволу токена Workflows.",
    inputSchema: {
      type: "object",
      properties: {
        repo: { type: "string" },
        branch: { type: "string" },
        message: { type: "string" },
        expected_head: { type: "string" },
        create_from: { type: "string", description: "якщо гілки нема — створити її від цієї гілки/sha" },
        dry_run: { type: "boolean" },
        changes: {
          type: "array",
          minItems: 1,
          maxItems: 40,
          items: {
            type: "object",
            properties: {
              path: { type: "string" },
              edits: {
                type: "array",
                items: { type: "object", properties: { old: { type: "string" }, new: { type: "string" } }, required: ["old", "new"] },
              },
              content: { type: "string" },
              content_base64: { type: "string", description: "бінарний файл (png тощо) у base64" },
              from: { type: "string", description: "скопіювати файл з цього шляху (можна з edits)" },
              move: { type: "boolean", description: "разом із from: видалити джерело (= git mv)" },
              delete: { type: "boolean" },
            },
            required: ["path"],
          },
        },
      },
      required: ["repo", "branch", "message", "changes"],
    },
  },
  {
    name: "gh_branch",
    description: "Гілки репо: list — список (імʼя · sha · захищена); create — нова гілка name від from (гілка або sha; типово гілка за замовчуванням); delete — видалити гілку name, потрібен expected_head (її sha). Гілку за замовчуванням і гілки з PROTECT видалити не можна.",
    inputSchema: {
      type: "object",
      properties: {
        repo: { type: "string" },
        action: { type: "string", enum: ["list", "create", "delete"] },
        name: { type: "string" },
        from: { type: "string" },
        expected_head: { type: "string" },
      },
      required: ["repo", "action"],
    },
  },
  {
    name: "gh_actions",
    description: "GitHub Actions: workflows — список workflow; runs — останні прогони (фільтр workflow = id або імʼя файлу, branch, n); jobs — джоби й кроки прогону run_id; log — хвіст логу джоба job_id (tail рядків, типово 80); dispatch — запустити workflow на ref з inputs; rerun — перезапустити run_id (failed_only=true — лише впалі джоби); cancel — скасувати run_id. Сам файл workflow пишеться через gh_commit у .github/workflows/.",
    inputSchema: {
      type: "object",
      properties: {
        repo: { type: "string" },
        action: { type: "string", enum: ["workflows", "runs", "jobs", "log", "dispatch", "rerun", "cancel"] },
        workflow: { type: "string", description: "id або імʼя файлу, напр. ci.yml" },
        branch: { type: "string" },
        n: { type: "integer", minimum: 1, maximum: 30 },
        run_id: { type: "integer" },
        job_id: { type: "integer" },
        tail: { type: "integer", minimum: 1, maximum: 400 },
        ref: { type: "string" },
        inputs: { type: "object" },
        failed_only: { type: "boolean" },
      },
      required: ["repo", "action"],
    },
  },
];

async function defaultBranch(call, repo) {
  return (await call("GET", "/repos/" + repo)).default_branch;
}
function checkBranchName(b) {
  b = String(b || "");
  if (!/^[\w./-]+$/.test(b) || b.includes("..") || b.startsWith("/") || b.endsWith("/")) throw new ToolError("некоректна гілка: " + b);
  return b;
}

async function toolBranch(env, a) {
  const call = gh(env);
  const repo = checkRepo(env, a.repo);
  if (a.action === "list") {
    const r = await call("GET", "/repos/" + repo + "/branches?per_page=100");
    const def = await defaultBranch(call, repo);
    return r.map((b) => b.name + " · " + b.commit.sha.slice(0, 7) + (b.name === def ? " · за замовчуванням" : "") + (b.protected ? " · protected (GitHub)" : "")).join("\n");
  }
  const name = checkBranchName(a.name);
  if (a.action === "create") {
    const from = a.from || (await defaultBranch(call, repo));
    const sha = /^[0-9a-f]{40}$/.test(from) ? from : (await call("GET", "/repos/" + repo + "/git/ref/heads/" + enc(checkBranchName(from)))).object.sha;
    await call("POST", "/repos/" + repo + "/git/refs", { ref: "refs/heads/" + name, sha });
    return "✅ гілка " + name + " створена від " + from + " · " + sha.slice(0, 7);
  }
  if (a.action === "delete") {
    const def = await defaultBranch(call, repo);
    const protect = String(env.PROTECT || "").split(",").map((s) => s.trim()).filter(Boolean);
    if (name === def) throw new ToolError("«" + name + "» — гілка за замовчуванням; видалення заборонено завжди");
    if (protect.includes(name)) throw new ToolError("гілка «" + name + "» захищена (PROTECT)");
    const head = (await call("GET", "/repos/" + repo + "/git/ref/heads/" + enc(name))).object.sha;
    if (!a.expected_head) throw new ToolError("для видалення передай expected_head = " + head.slice(0, 7));
    if (!head.startsWith(a.expected_head)) throw new ToolError("гілка зрушила: очікував " + a.expected_head + ", зараз " + head.slice(0, 7));
    await call("DELETE", "/repos/" + repo + "/git/refs/heads/" + enc(name));
    return "✅ гілку " + name + " видалено (була " + head.slice(0, 7) + ")";
  }
  throw new ToolError("action: list / create / delete");
}

function wfRef(w) {
  w = String(w || "");
  if (!/^[\w.-]+$/.test(w)) throw new ToolError("workflow — id або імʼя файлу (напр. ci.yml)");
  return encodeURIComponent(w);
}
function needId(v, what) {
  if (!Number.isInteger(v) || v <= 0) throw new ToolError("потрібен " + what);
  return v;
}

async function toolActions(env, a) {
  const call = gh(env);
  const repo = checkRepo(env, a.repo);
  const base = "/repos/" + repo + "/actions";
  switch (a.action) {
    case "workflows": {
      const r = await call("GET", base + "/workflows?per_page=100");
      if (!r.workflows.length) return "workflow нема";
      return r.workflows.map((w) => w.id + " · " + w.name + " · " + w.path + " · " + w.state).join("\n");
    }
    case "runs": {
      const q = "?per_page=" + (a.n || 10) + (a.branch ? "&branch=" + encodeURIComponent(a.branch) : "");
      const p = a.workflow ? base + "/workflows/" + wfRef(a.workflow) + "/runs" + q : base + "/runs" + q;
      const r = await call("GET", p);
      if (!r.workflow_runs.length) return "прогонів нема";
      return r.workflow_runs.map((x) => x.id + " · " + x.name + " · " + x.status + (x.conclusion ? "/" + x.conclusion : "") + " · " + x.head_branch + " · " + x.head_sha.slice(0, 7) + " · " + x.created_at + " · " + x.html_url).join("\n");
    }
    case "jobs": {
      const r = await call("GET", base + "/runs/" + needId(a.run_id, "run_id") + "/jobs?per_page=100");
      return r.jobs.map((j) => {
        const steps = (j.steps || []).map((s) => "   " + (s.conclusion === "failure" ? "✗ " : s.conclusion === "success" ? "✓ " : "· ") + s.number + ". " + s.name + " · " + (s.conclusion || s.status)).join("\n");
        return "job " + j.id + " · " + j.name + " · " + j.status + (j.conclusion ? "/" + j.conclusion : "") + (steps ? "\n" + steps : "");
      }).join("\n");
    }
    case "log": {
      const id = needId(a.job_id, "job_id");
      const res = await fetch(GH + base + "/jobs/" + id + "/logs", {
        headers: { "Authorization": "Bearer " + env.GH_TOKEN, "User-Agent": "lens-gh-worker", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28" },
        redirect: "manual",
      });
      let text;
      if (res.status === 302 || res.status === 301) {
        const loc = res.headers.get("Location");
        const r2 = await fetch(loc); // підписаний URL — без токена
        if (!r2.ok) throw new ToolError("лог недоступний: " + r2.status);
        text = await r2.text();
      } else if (res.ok) text = await res.text();
      else throw new ToolError("GitHub " + res.status + " на лог джоба " + id);
      const lines = text.split("\n");
      const n = a.tail || 80;
      return "job " + id + " · рядків " + lines.length + " · останні " + Math.min(n, lines.length) + "\n---\n" + lines.slice(-n).join("\n");
    }
    case "dispatch": {
      const ref = a.ref || (await defaultBranch(call, repo));
      await call("POST", base + "/workflows/" + wfRef(a.workflow) + "/dispatches", { ref, inputs: a.inputs || {} });
      return "✅ запущено " + a.workflow + " на " + ref + " — стан дивись через runs";
    }
    case "rerun": {
      const id = needId(a.run_id, "run_id");
      await call("POST", base + "/runs/" + id + (a.failed_only ? "/rerun-failed-jobs" : "/rerun"), {});
      return "✅ перезапуск " + id + (a.failed_only ? " (лише впалі джоби)" : "");
    }
    case "cancel": {
      const id = needId(a.run_id, "run_id");
      await call("POST", base + "/runs/" + id + "/cancel", {});
      return "✅ скасування " + id + " надіслано";
    }
  }
  throw new ToolError("action: workflows / runs / jobs / log / dispatch / rerun / cancel");
}

async function toolRead(env, a) {
  const call = gh(env);
  const repo = checkRepo(env, a.repo), path = checkPath(a.path);
  const f = await readFile(call, repo, path, a.ref);
  const lines = f.text.split("\n");
  const s = Math.max(1, a.start_line || 1), e = Math.min(lines.length, a.end_line || lines.length);
  const body = lines.slice(s - 1, e).join("\n");
  return `${repo}/${path} · sha ${f.sha} · ${f.size} байт · ${lines.length} рядків · показано ${s}–${e}\n---\n${body}`;
}

async function toolList(env, a) {
  const call = gh(env);
  const repo = checkRepo(env, a.repo);
  if (a.recursive) {
    const ref = a.ref || (await call("GET", "/repos/" + repo)).default_branch;
    const t = await call("GET", "/repos/" + repo + "/git/trees/" + encodeURIComponent(ref) + "?recursive=1");
    const pre = a.path ? a.path.replace(/\/$/, "") + "/" : "";
    const items = t.tree.filter((x) => x.type === "blob" && x.path.startsWith(pre)).map((x) => x.path + " · " + x.size);
    return `${repo} @ ${ref} · файлів: ${items.length}${t.truncated ? " (обрізано GitHub)" : ""}\n` + items.join("\n");
  }
  const p = a.path ? checkPath(a.path.replace(/\/$/, "")) : "";
  const q = a.ref ? "?ref=" + encodeURIComponent(a.ref) : "";
  const r = await call("GET", "/repos/" + repo + "/contents/" + (p ? enc(p) : "") + q);
  if (!Array.isArray(r)) throw new ToolError(p + " — це файл; використай gh_read");
  return r.map((x) => (x.type === "dir" ? x.name + "/" : x.name + " · " + x.size)).join("\n");
}

async function toolLog(env, a) {
  const call = gh(env);
  const repo = checkRepo(env, a.repo);
  const q = "?per_page=" + (a.n || 10) + (a.branch ? "&sha=" + encodeURIComponent(a.branch) : "");
  const r = await call("GET", "/repos/" + repo + "/commits" + q);
  return r.map((c) => c.sha.slice(0, 7) + " · " + c.commit.author.date + " · " + c.commit.message.split("\n")[0]).join("\n");
}

async function toolCommit(env, a) {
  const call = gh(env);
  const repo = checkRepo(env, a.repo);
  const branch = String(a.branch || "");
  if (!/^[\w./-]+$/.test(branch)) throw new ToolError("некоректна гілка");
  const protect = String(env.PROTECT || "").split(",").map((s) => s.trim()).filter(Boolean);
  if (protect.includes(branch)) throw new ToolError("гілка «" + branch + "» захищена від запису (змінна PROTECT)");
  if (!a.message || !String(a.message).trim()) throw new ToolError("порожнє повідомлення коміту");
  if (!Array.isArray(a.changes) || !a.changes.length) throw new ToolError("немає змін");
  const paths = new Set();
  for (const ch of a.changes) {
    checkPath(ch.path);
    if (paths.has(ch.path)) throw new ToolError("шлях двічі в одному коміті: " + ch.path);
    paths.add(ch.path);
    const modes = [!!ch.edits && !ch.from, typeof ch.content === "string", typeof ch.content_base64 === "string", !!ch.delete, !!ch.from].filter(Boolean).length;
    if (modes !== 1) throw new ToolError(ch.path + ": рівно одне з edits / content / content_base64 / from / delete");
    if (ch.from) checkPath(ch.from);
  }

  // голова гілки
  let head, created = false;
  try {
    head = (await call("GET", "/repos/" + repo + "/git/ref/heads/" + enc(branch))).object.sha;
  } catch (e) {
    if (e.status !== 404 || !a.create_from) throw e.status === 404 ? new ToolError("гілки «" + branch + "» нема; передай create_from") : e;
    const from = a.create_from;
    head = /^[0-9a-f]{40}$/.test(from) ? from : (await call("GET", "/repos/" + repo + "/git/ref/heads/" + enc(from))).object.sha;
    created = true;
  }
  if (!a.dry_run && !created && !a.expected_head)
    throw new ToolError("expected_head обовʼязковий для запису в наявну гілку «" + branch + "» (зараз голова " + head.slice(0, 7) + "). Звір і передай.");
  if (a.expected_head && !/^[0-9a-f]{7,40}$/.test(a.expected_head)) throw new ToolError("expected_head — sha від 7 hex-символів");
  if (a.expected_head && !head.startsWith(a.expected_head))
    throw new ToolError("гілка зрушила: очікував " + a.expected_head + ", зараз " + head.slice(0, 7) + ". Перечитай файли й повтори.");

  // застосувати зміни в пам'яті
  const report = [], tree = [];
  for (const ch of a.changes) {
    if (ch.delete) {
      tree.push({ path: ch.path, mode: "100644", type: "blob", sha: null });
      report.push("− " + ch.path);
      continue;
    }
    let text;
    if (typeof ch.content_base64 === "string") {
      if (a.dry_run) { report.push("+ " + ch.path + " (бінарний, " + Math.floor(ch.content_base64.length * 3 / 4) + " байт)"); continue; }
      const blob = await call("POST", "/repos/" + repo + "/git/blobs", { content: ch.content_base64.replace(/\s/g, ""), encoding: "base64" });
      tree.push({ path: ch.path, mode: "100644", type: "blob", sha: blob.sha });
      report.push("+ " + ch.path + " (бінарний)");
      continue;
    }
    if (ch.from) {
      const src = await readFile(call, repo, ch.from, head);
      if (ch.move) {
        if (paths.has(ch.from)) throw new ToolError(ch.from + ": джерело переносу змінюється в цьому ж коміті");
        tree.push({ path: ch.from, mode: "100644", type: "blob", sha: null });
      }
      if (!ch.edits) {
        tree.push({ path: ch.path, mode: "100644", type: "blob", sha: src.sha }); // той самий blob — годиться й для бінарних
        report.push((ch.move ? "→ " : "⧉ ") + ch.from + " → " + ch.path);
        continue;
      }
      text = src.text;
      ch.edits.forEach((ed, i) => {
        const n = countOcc(text, ed.old);
        if (n !== 1) throw new ToolError(ch.path + " правка #" + (i + 1) + ": фрагмент old знайдено " + n + " раз(и), треба рівно 1");
        text = text.replace(ed.old, () => ed.new);
      });
      report.push((ch.move ? "→ " : "⧉ ") + ch.from + " → " + ch.path + " (правок: " + ch.edits.length + ")");
    } else if (typeof ch.content === "string") {
      text = ch.content;
      report.push("+ " + ch.path + " (" + new TextEncoder().encode(text).length + " байт)");
    } else {
      const f = await readFile(call, repo, ch.path, head);
      text = f.text;
      ch.edits.forEach((ed, i) => {
        const n = countOcc(text, ed.old);
        if (n !== 1) throw new ToolError(ch.path + " правка #" + (i + 1) + ": фрагмент old знайдено " + n + " раз(и), треба рівно 1");
        text = text.replace(ed.old, () => ed.new);
      });
      report.push("~ " + ch.path + " (правок: " + ch.edits.length + ")");
    }
    tree.push({ path: ch.path, mode: "100644", type: "blob", content: text });
  }

  const summary = `${repo} · гілка ${branch}${created ? " (нова від " + a.create_from + ")" : ""} · база ${head.slice(0, 7)}\n` + report.join("\n");
  if (a.dry_run) return "DRY RUN — нічого не записано.\n" + summary;

  if (created) await call("POST", "/repos/" + repo + "/git/refs", { ref: "refs/heads/" + branch, sha: head });
  const baseTree = (await call("GET", "/repos/" + repo + "/git/commits/" + head)).tree.sha;
  const newTree = await call("POST", "/repos/" + repo + "/git/trees", { base_tree: baseTree, tree });
  const commit = await call("POST", "/repos/" + repo + "/git/commits", { message: String(a.message), tree: newTree.sha, parents: [head] });
  await call("PATCH", "/repos/" + repo + "/git/refs/heads/" + enc(branch), { sha: commit.sha, force: false });
  return `✅ коміт ${commit.sha.slice(0, 7)}\n${summary}\nhttps://github.com/${repo}/commit/${commit.sha}`;
}

const HANDLERS = { gh_read: toolRead, gh_list: toolList, gh_log: toolLog, gh_commit: toolCommit, gh_branch: toolBranch, gh_actions: toolActions };

// ---------- MCP (JSON-RPC) ----------
async function rpc(msg, env) {
  const { id, method, params } = msg || {};
  const isNote = id === undefined || id === null;
  const ok = (result) => ({ jsonrpc: "2.0", id, result });
  const err = (code, message) => ({ jsonrpc: "2.0", id: id ?? null, error: { code, message } });
  if (!msg || msg.jsonrpc !== "2.0" || typeof method !== "string") return err(-32600, "Invalid Request");
  if (isNote) return null; // notifications/initialized тощо
  switch (method) {
    case "initialize":
      return ok({
        protocolVersion: (params && params.protocolVersion) || PROTOCOL_FALLBACK,
        capabilities: { tools: { listChanged: false } },
        serverInfo: { name: "lens-gh", version: VERSION },
        instructions: "Запис у GitHub репо Konst-Andre. Кожен gh_commit — лише після явного «так» користувача. Спершу dry_run.",
      });
    case "ping":
      return ok({});
    case "tools/list":
      return ok({ tools: TOOLS });
    case "tools/call": {
      const name = params && params.name;
      const h = HANDLERS[name];
      if (!h) return err(-32602, "Unknown tool: " + name);
      try {
        const text = await h(env, (params && params.arguments) || {});
        return ok({ content: [{ type: "text", text }] });
      } catch (e) {
        const text = e instanceof ToolError ? e.message : "Внутрішня помилка: " + (e && e.message ? e.message : String(e));
        return ok({ content: [{ type: "text", text }], isError: true });
      }
    }
    default:
      return err(-32601, "Method not found: " + method);
  }
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json; charset=utf-8" } });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const m = url.pathname.match(/^\/mcp\/([^/]+)\/?$/);
    if (url.pathname === "/" && request.method === "GET") return new Response("lens-gh " + VERSION, { status: 200 });
    if (!m || !env.MCP_KEY || !safeEq(m[1], env.MCP_KEY)) return new Response("Not found", { status: 404 });
    if (!env.GH_TOKEN) return json({ jsonrpc: "2.0", id: null, error: { code: -32000, message: "GH_TOKEN не встановлено" } }, 500);
    if (request.method === "GET") return new Response("Method Not Allowed", { status: 405, headers: { Allow: "POST" } });
    if (request.method === "DELETE") return new Response(null, { status: 204 });
    if (request.method !== "POST") return new Response("Method Not Allowed", { status: 405 });
    let body;
    try { body = await request.json(); } catch (_) { return json({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } }, 400); }
    if (Array.isArray(body)) {
      const out = (await Promise.all(body.map((b) => rpc(b, env)))).filter(Boolean);
      return out.length ? json(out) : new Response(null, { status: 202 });
    }
    const r = await rpc(body, env);
    return r ? json(r) : new Response(null, { status: 202 });
  },
};
