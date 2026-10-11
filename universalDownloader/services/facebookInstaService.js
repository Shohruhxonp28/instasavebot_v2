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

async function facebookInsta(url) {
  try {
    if (!snapsave) {
      snapsave = require("metadownloader");
    }
    const result = await snapsave(url);
    return result;
  } catch (error) {
    throw new Error("Error fetching media: " + error.message);
  }
}

module.exports = facebookInsta;
