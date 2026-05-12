import { execFileSync } from "node:child_process";
import { existsSync } from "node:fs";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { dirname, join, resolve } from "node:path";

const args = parseArgs(process.argv.slice(2));

if (!args.input || !args.output) {
  throw new Error("Usage: node scripts/svg-to-png.mjs --input input.svg --output output.png");
}

const inputPath = resolve(args.input);
const outputPath = resolve(args.output);
const width = Number(args.width ?? 1400);
const height = Number(args.height ?? 920);
const puppeteerConfig = args.puppeteerConfigFile
  ? JSON.parse(await readFile(resolve(args.puppeteerConfigFile), "utf8"))
  : {};

const puppeteer = await loadPuppeteer();
const browser = await puppeteer.launch(puppeteerConfig);

try {
  const svg = await readFile(inputPath, "utf8");
  const page = await browser.newPage();
  await page.setViewport({ width, height, deviceScaleFactor: 1 });
  await page.setContent(
    `<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <style>
      html, body { margin: 0; padding: 0; width: ${width}px; height: ${height}px; background: white; }
      svg { display: block; }
    </style>
  </head>
  <body>${svg}</body>
</html>`,
    { waitUntil: "networkidle0" },
  );
  const bytes = await page.screenshot({
    type: "png",
    clip: { x: 0, y: 0, width, height },
  });
  await mkdir(dirname(outputPath), { recursive: true });
  await writeFile(outputPath, bytes);
} finally {
  await browser.close();
}

function parseArgs(values) {
  const parsed = {};
  for (let index = 0; index < values.length; index += 1) {
    const value = values[index];
    if (!value.startsWith("--")) {
      continue;
    }
    const key = value.slice(2).replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
    parsed[key] = values[index + 1];
    index += 1;
  }
  return parsed;
}

async function loadPuppeteer() {
  try {
    return await import("puppeteer");
  } catch {
    // Fall through to Mermaid CLI's dependency tree.
  }

  const candidates = [];
  if (process.env.APPDATA) {
    candidates.push(join(process.env.APPDATA, "npm", "node_modules", "@mermaid-js", "mermaid-cli", "node_modules"));
  }

  try {
    const npmRoot = execFileSync("npm", ["root", "-g"], { encoding: "utf8" }).trim();
    candidates.push(join(npmRoot, "@mermaid-js", "mermaid-cli", "node_modules"));
  } catch {
    // npm may not be available in every environment.
  }

  for (const nodeModulesPath of candidates) {
    const packagePath = join(nodeModulesPath, "puppeteer", "package.json");
    if (!existsSync(packagePath)) {
      continue;
    }
    const requireFromMermaidCli = createRequire(packagePath);
    return requireFromMermaidCli("puppeteer");
  }

  throw new Error(
    "Puppeteer was not found. Install @mermaid-js/mermaid-cli or make puppeteer available to Node.js.",
  );
}
