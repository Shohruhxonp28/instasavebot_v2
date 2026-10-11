/**
 * CLI wrapper for universalDownloader services to allow direct calling from Python
 * Usage: node cli.js <url> [platform]
 */

const { fetchBlueskyMedia } = require("./services/blueskyService");
const { fetchCapcutData } = require("./services/capcutService");
const { fetchDailymotionData } = require("./services/dailymotionService");
const { fetchDouyinVideoInfo } = require("./services/douyinService");
const facebookInsta = require("./services/facebookInstaService");
const { scrapeKuaishou } = require("./services/kuaishouService");
const { fetchLinkedinData } = require("./services/linkedinService");
const { fetchPinterestMedia } = require("./services/pinterestService");
const redditDownloader = require("./services/redditService");
const { fetchSnapchat } = require("./services/snapchatService");
const { fetchSoundcloudData } = require("./services/soundcloudService");
const { fetchSpotify } = require("./services/spotifyService");
const { fetchTerabox } = require("./services/teraboxService");
const threadsDownloader = require("./services/threadsService");
const { fetchTikTokData } = require("./services/tiktokService");
const { fetchTumblrData } = require("./services/tumblrService");
const { twitterDownloader } = require("./services/twitterService");
const { fetchYouTubeData } = require("./services/youtubeService");

function detectPlatform(url) {
  const lower = url.toLowerCase();
  if (lower.includes("threads.net")) return "threads";
  if (lower.includes("spotify.com") || lower.includes("open.spotify")) return "spotify";
  if (lower.includes("snapchat.com")) return "snapchat";
  if (lower.includes("capcut.com")) return "capcut";
  if (lower.includes("terabox") || lower.includes("1024tera") || lower.includes("terafileshare")) return "terabox";
  if (lower.includes("douyin.com")) return "douyin";
  if (lower.includes("kuaishou.com")) return "kuaishou";
  if (lower.includes("bsky.app") || lower.includes("bluesky")) return "bluesky";
  if (lower.includes("soundcloud.com")) return "soundcloud";
  if (lower.includes("reddit.com")) return "reddit";
  if (lower.includes("dailymotion.com")) return "dailymotion";
  if (lower.includes("tumblr.com")) return "tumblr";
  if (lower.includes("linkedin.com")) return "linkedin";
  if (lower.includes("pinterest.com") || lower.includes("pin.it")) return "pinterest";
  if (lower.includes("tiktok.com")) return "tiktok";
  if (lower.includes("twitter.com") || lower.includes("x.com")) return "twitter";
  if (lower.includes("instagram.com") || lower.includes("facebook.com") || lower.includes("fb.watch")) return "meta";
  if (lower.includes("youtube.com") || lower.includes("youtu.be")) return "youtube";
  return "unknown";
}

async function run() {
  const args = process.argv.slice(2);
  if (!args[0]) {
    console.error(JSON.stringify({ error: "Missing URL argument." }));
    process.exit(1);
  }

  const url = args[0];
  const platform = args[1] || detectPlatform(url);

  try {
    let result;
    switch (platform) {
      case "threads":
        result = await threadsDownloader(url);
        break;
      case "spotify":
        result = await fetchSpotify(url);
        break;
      case "snapchat":
        result = await fetchSnapchat(url);
        break;
      case "capcut":
        result = await fetchCapcutData(url);
        break;
      case "terabox":
        result = await fetchTerabox(url);
        break;
      case "douyin":
        result = await fetchDouyinVideoInfo(url);
        break;
      case "kuaishou":
        result = await scrapeKuaishou(url);
        break;
      case "bluesky":
        result = await fetchBlueskyMedia(url);
        break;
      case "soundcloud":
        result = await fetchSoundcloudData(url);
        break;
      case "reddit":
        result = await redditDownloader(url);
        break;
      case "dailymotion":
        result = await fetchDailymotionData(url);
        break;
      case "tumblr":
        result = await fetchTumblrData(url);
        break;
      case "linkedin":
        result = await fetchLinkedinData(url);
        break;
      case "pinterest":
        result = await fetchPinterestMedia(url);
        break;
      case "tiktok":
        result = await fetchTikTokData(url);
        break;
      case "twitter":
        result = await twitterDownloader(url);
        break;
      case "meta":
        result = await facebookInsta(url);
        break;
      case "youtube":
        result = await fetchYouTubeData(url);
        break;
      default:
        throw new Error(`Unsupported or unknown platform: ${platform}`);
    }

    console.log(JSON.stringify({ success: true, platform, data: result }));
  } catch (err) {
    console.error(JSON.stringify({ success: false, error: err.message || String(err) }));
    process.exit(1);
  }
}

run();
