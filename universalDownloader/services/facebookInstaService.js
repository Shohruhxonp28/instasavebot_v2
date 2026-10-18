const fs = require("fs");
const path = require("path");

let snapsave;
try {
  snapsave = require("metadownloader");
} catch (err) {
  // Fix Node.js 24 strict assignment issue in metadownloader if encountered
  try {
    const metaPath = path.join(__dirname, "../node_modules/metadownloader/src/index.js");
    if (fs.existsSync(metaPath)) {
      let content = fs.readFileSync(metaPath, "utf8");
      if (content.includes("]=snapsave=")) {
        content = content.replace("]=snapsave=", "]=");
        fs.writeFileSync(metaPath, content, "utf8");
        delete require.cache[require.resolve("metadownloader")];
        snapsave = require("metadownloader");
      }
    }
  } catch (patchErr) {
    throw err;
  }
}

function normalizeMetaUrl(rawUrl) {
  if (!rawUrl) return rawUrl;
  let clean = rawUrl.trim();
  if (clean.startsWith("http://")) {
    clean = "https://" + clean.slice(7);
  }

  // Instagram normalization
  if (clean.includes("instagram.com")) {
    clean = clean.replace(/https?:\/\/(?:[a-zA-Z0-9_-]+\.)?instagram\.com/i, "https://www.instagram.com");
    clean = clean.replace(/\/reels\//i, "/reel/");
    try {
      const parsed = new URL(clean);
      clean = `${parsed.origin}${parsed.pathname}`;
    } catch (e) {}
  } else if (clean.includes("facebook.com") || clean.includes("fb.watch") || clean.includes("fb.com")) {
    clean = clean.replace(/https?:\/\/m\.facebook\.com/i, "https://www.facebook.com");
  }

  return clean;
}

async function facebookInsta(url) {
  try {
    if (!snapsave) {
      snapsave = require("metadownloader");
    }
    const normalizedUrl = normalizeMetaUrl(url);
    const result = await snapsave(normalizedUrl);
    return result;
  } catch (error) {
    throw new Error("Error fetching media: " + error.message);
  }
}

module.exports = facebookInsta;
