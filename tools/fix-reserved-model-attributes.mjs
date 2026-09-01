import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";

const modelsDirectory = "/home/ubuntu/AI-Smart-Engineer-Enterprise/apps/api/src/db/models";
const oldDeclaration = "metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)";
const newDeclaration = "metadata_payload: Mapped[dict | None] = mapped_column(\"metadata\", JSON, nullable=True)";
let updated = 0;

for (const entry of await readdir(modelsDirectory)) {
  if (!entry.endsWith(".py")) continue;
  const target = path.join(modelsDirectory, entry);
  const source = await readFile(target, "utf8");
  if (!source.includes(oldDeclaration)) continue;
  await writeFile(target, source.replaceAll(oldDeclaration, newDeclaration), "utf8");
  updated += 1;
}

console.log(`Updated reserved metadata declarations in ${updated} model files.`);
