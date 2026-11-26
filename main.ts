// news-image-20261125 entrypoint.
//
// Copies the pre-rendered front page (entry.png, drawn by
// tools/make_image.py) into the directory make.fun expects, then
// self-checks the copy: it must exist, start with the PNG magic bytes,
// and be exactly 1024 x 1024 pixels. Prints OK on success.
//
// Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, readFileSync, statSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const EXPECTED_WIDTH = 1024;
const EXPECTED_HEIGHT = 1024;

function fail(message) {
  console.error(`FAIL: ${message}`);
  process.exit(1);
}

function main() {
  const outDir = process.env.MAKEFUN_OUTPUT_DIR;
  if (!outDir) {
    fail("MAKEFUN_OUTPUT_DIR is not set");
  }

  const here = resolve(fileURLToPath(new URL(".", import.meta.url)));
  const source = join(here, "entry.png");
  const target = join(resolve(outDir), "entry.png");

  if (!existsSync(source)) {
    fail(`entry.png not found at ${source} (run tools/make_image.py first)`);
  }

  copyFileSync(source, target);

  if (!existsSync(target)) {
    fail(`copy failed: ${target} does not exist`);
  }

  const bytes = readFileSync(target);
  if (bytes.length < 33 || !bytes.subarray(0, 8).equals(PNG_MAGIC)) {
    fail(`${target} is not a PNG file`);
  }

  // PNG header: width is a big-endian uint32 at offset 16, height at 20.
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width !== EXPECTED_WIDTH || height !== EXPECTED_HEIGHT) {
    fail(
      `expected ${EXPECTED_WIDTH}x${EXPECTED_HEIGHT}, got ${width}x${height}`,
    );
  }

  // The copy must be byte-identical to the source image.
  const sourceBytes = readFileSync(source);
  if (!bytes.equals(sourceBytes)) {
    fail("copied entry.png differs from the source entry.png");
  }

  const size = statSync(target).size;
  console.log(
    `OK: entry.png (${width}x${height}, ${size} bytes) -> ${target}`,
  );
}

main();
