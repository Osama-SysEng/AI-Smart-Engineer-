#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const args = process.argv.slice(2);
const value = (flag, fallback) => {
  const index = args.indexOf(flag);
  return index === -1 ? fallback : args[index + 1];
};
const root = path.resolve(value("--root", "."));
const output = path.resolve(value("--output", "reports/security/secret-heuristic.json"));
const ignoredDirectories = new Set([".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", "reports"]);
const ignoredFiles = new Set([".env", ".env.local", ".env.production"]);
const patterns = [
  { id: "private-key", expression: /-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/ },
  { id: "generic-secret-assignment", expression: /(?:secret|password|token|api[_-]?key)\s*[:=]\s*["'][^"'\s]{12,}["']/i },
  { id: "aws-access-key", expression: /AKIA[0-9A-Z]{16}/ },
];
const findings = [];

function scan(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (!ignoredDirectories.has(entry.name)) scan(path.join(directory, entry.name));
      continue;
    }
    if (!entry.isFile() || ignoredFiles.has(entry.name)) continue;
    const file = path.join(directory, entry.name);
    const relative = path.relative(root, file);
    if (fs.statSync(file).size > 1_000_000) continue;
    const text = fs.readFileSync(file, "utf8");
    text.split(/\r?\n/).forEach((line, index) => {
      for (const pattern of patterns) {
        if (pattern.expression.test(line)) findings.push({ rule: pattern.id, file: relative, line: index + 1 });
      }
    });
  }
}

scan(root);
fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, JSON.stringify({ scanner: "local-secret-heuristic", findings }, null, 2));
console.log(JSON.stringify({ findings: findings.length }));
process.exitCode = findings.length ? 1 : 0;
