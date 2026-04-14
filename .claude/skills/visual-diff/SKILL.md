---
name: visual-diff
description: >
  Run visual regression comparison for UI components. Use when developing new
  ws-ai-ui components or ws-ai-ui-wrapper wrappers — e.g. "compare visuals",
  "visual diff", "check design match", "screenshot compare".
paths:
  - "libs/ws-ai-ui/src/components/**/*"
  - "libs/ws-ai-ui-wrapper/src/components/**/*"
  - "libs/ws-components/src/lib/**/*.stories.*"
---

# Visual Diff — Component DesignBoard Comparison

Compare rendered Storybook DesignBoard stories against Figma design specs and
against the legacy ws-components implementation using Playwright screenshots
and pixelmatch pixel-level diffing.

## Prerequisites

- `@playwright/test` installed (monorepo devDep)
- `pixelmatch` + `pngjs` installed (monorepo devDep)
- Figma Desktop app running with the design file open (for Figma MCP screenshots)

## What This Skill Does

Two comparisons, run in sequence:

| # | Compare A | Compare B | Purpose |
|---|-----------|-----------|---------|
| 1 | **ws-ai-ui DesignBoard** (Storybook) | **Figma spec** (MCP screenshot) | Does our component match the design? |
| 2 | **ws-components original DesignBoard** | **ws-ai-ui-wrapper DesignBoard** | Does the wrapper reproduce the original? |

## Step 1 — Identify the Component

Ask the user which component to compare, or infer from the current file context.
Determine:

- **Component name** (e.g. `Button`, `Checkbox`, `Badge`)
- **Figma node ID** — read from the component's `.figma.tsx` Code Connect file:
  ```bash
  grep -o 'node-id=[0-9:-]*' libs/ws-ai-ui/src/components/ui/<component>.figma.tsx
  ```
- **Storybook story IDs**:
  - ws-ai-ui: `atoms-<component>--design-board`
  - ws-components original: `atoms-<component>--design-board`
  - ws-components wrapper: `atoms-<component>-wrapper--design-board`

## Step 2 — Start Storybook Instances

```bash
# ws-ai-ui Storybook (for comparison 1)
npx nx run ws-ai-ui:storybook --port 6007 &
# ws-components Storybook (for comparison 2)
npx nx run ws-components:storybook --port 6008 &

# Wait for both to be ready
for port in 6007 6008; do
  for i in $(seq 1 60); do
    curl -s "http://localhost:$port" > /dev/null 2>&1 && break
    sleep 3
  done
done
```

## Step 3 — Capture Screenshots

Use `@playwright/test`'s `chromium` to capture full-page screenshots of each
DesignBoard story at 1440px viewport width.

```javascript
const { chromium } = require('@playwright/test');

async function captureStory(port, storyId, outputPath) {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const url = `http://localhost:${port}/iframe.html?id=${storyId}&viewMode=story`;
  await page.goto(url, { timeout: 90000, waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: outputPath, fullPage: true });
  await browser.close();
}
```

For the **Figma screenshot**, use the Figma Desktop MCP:

```
mcp__figma-desktop__get_screenshot(nodeId: "<figma-node-id>")
```

Save the result to `/tmp/visual-diff/figma-<component>.png`.

## Step 4 — Run pixelmatch

```javascript
const fs = require('fs');
const { PNG } = require('pngjs');
const pixelmatch = require('pixelmatch');

function compareImages(imgPathA, imgPathB, diffOutputPath) {
  const imgA = PNG.sync.read(fs.readFileSync(imgPathA));
  const imgB = PNG.sync.read(fs.readFileSync(imgPathB));

  // Resize to the larger canvas so both fit
  const width = Math.max(imgA.width, imgB.width);
  const height = Math.max(imgA.height, imgB.height);

  // Create padded versions on a white background
  function padImage(img, w, h) {
    const padded = new PNG({ width: w, height: h });
    // Fill white
    for (let i = 0; i < padded.data.length; i += 4) {
      padded.data[i] = 255;
      padded.data[i + 1] = 255;
      padded.data[i + 2] = 255;
      padded.data[i + 3] = 255;
    }
    PNG.bitblt(img, padded, 0, 0, img.width, img.height, 0, 0);
    return padded;
  }

  const a = padImage(imgA, width, height);
  const b = padImage(imgB, width, height);
  const diff = new PNG({ width, height });

  const mismatchedPixels = pixelmatch(
    a.data, b.data, diff.data,
    width, height,
    { threshold: 0.15 }   // Allow small anti-aliasing differences
  );

  fs.writeFileSync(diffOutputPath, PNG.sync.write(diff));

  const totalPixels = width * height;
  const matchPercent = ((1 - mismatchedPixels / totalPixels) * 100).toFixed(2);

  return { mismatchedPixels, totalPixels, matchPercent, width, height };
}
```

## Step 5 — Report Results

Print a table:

```
## Visual Diff Results — <Component>

| Comparison | Match % | Mismatched px | Diff image |
|------------|---------|---------------|------------|
| ws-ai-ui DesignBoard vs Figma | 94.2% | 12,340 | /tmp/visual-diff/diff-figma.png |
| Original DesignBoard vs Wrapper | 87.5% | 28,901 | /tmp/visual-diff/diff-wrapper.png |
```

Then **read the diff images** using the Read tool so the user can see highlighted
differences visually.

**Thresholds:**
- **> 95%** match: PASS — minor anti-aliasing or font rendering differences
- **80–95%**: WARN — layout or spacing issues, review the diff image
- **< 80%**: FAIL — significant visual regression, investigate

## Step 6 — Clean Up

```bash
kill $(lsof -ti:6007) 2>/dev/null
kill $(lsof -ti:6008) 2>/dev/null
```

## Notes

- Figma MCP (`mcp__figma-desktop__get_screenshot`) requires the Figma Desktop
  app to be running. If unavailable, skip comparison 1 and report it as skipped.
- The wrapper comparison (comparison 2) requires ws-ai-ui CSS to be loaded in
  ws-components Storybook — ensure `preview.js` has the `WithWsAiUiTheme`
  decorator and `ws-ai-ui-styles.css` import.
- Screenshots are saved to `/tmp/visual-diff/` — create the directory if needed.
