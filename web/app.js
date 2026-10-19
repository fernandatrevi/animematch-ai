"use strict";

const state = { catalog: [], favorites: [] };
const $ = (selector) => document.querySelector(selector);
const form = $("#search-form");
const results = $("#results");
const message = $("#message");
const chips = $("#favorites");

function safeUrl(url) {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "https:" ? parsed.href : null;
  } catch { return null; }
}

function renderChips() {
  chips.replaceChildren();
  state.favorites.forEach((title) => {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.append(document.createTextNode(title));
    const remove = document.createElement("button");
    remove.type = "button";
    remove.setAttribute("aria-label", "Remove " + title);
    remove.textContent = "×";
    remove.addEventListener("click", () => {
      state.favorites = state.favorites.filter((item) => item !== title);
      renderChips();
    });
    chip.append(remove);
    chips.append(chip);
  });
}

function addFavorite() {
  const input = $("#favorite-search");
  const title = input.value.trim();
  const found = state.catalog.find((item) => item.title.toLowerCase() === title.toLowerCase());
  if (!found) {
    message.textContent = "Select an anime from the available catalog.";
    return;
  }
  if (!state.favorites.includes(found.title) && state.favorites.length < 10) {
    state.favorites.push(found.title);
    renderChips();
  }
  input.value = "";
  message.textContent = "";
}

function createCard(anime) {
  const card = document.createElement("article");
  card.className = "anime-card";
  const poster = document.createElement("div");
  poster.className = "poster";
  const imageUrl = safeUrl(anime.image_url);
  if (imageUrl) {
    const img = document.createElement("img");
    img.src = imageUrl;
    img.alt = anime.title + " cover art";
    img.loading = "lazy";
    img.addEventListener("error", () => {
      poster.replaceChildren();
      const placeholder = document.createElement("span");
      placeholder.className = "poster-placeholder";
      placeholder.textContent = "✦";
      poster.append(placeholder);
    });
    poster.append(img);
  } else {
    const placeholder = document.createElement("span");
    placeholder.className = "poster-placeholder";
    placeholder.textContent = "✦";
    poster.append(placeholder);
  }
  const content = document.createElement("div");
  content.className = "card-content";
  const title = document.createElement("h3");
  title.className = "card-title";
  title.textContent = anime.title;
  const genres = document.createElement("p");
  genres.className = "genres";
  genres.textContent = anime.genres || "Anime";
  const synopsis = document.createElement("p");
  synopsis.className = "synopsis";
  synopsis.textContent = anime.synopsis || "No synopsis available.";
  const meta = document.createElement("div");
  meta.className = "meta";
  const episodes = anime.episodes == null ? "Episodes unknown" : anime.episodes + " episodes";
  const score = anime.score == null ? "Unrated" : "★ " + Number(anime.score).toFixed(1);
  meta.textContent = episodes + "  ·  " + score;
  content.append(title, genres, synopsis, meta);
  const link = safeUrl(anime.url);
  if (link) {
    const a = document.createElement("a");
    a.href = link;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    a.className = "detail-link";
    a.textContent = "Explore anime ↗";
    content.append(a);
  }
  if (anime.explanation) {
    const details = document.createElement("details");
    details.className = "explanation";
    const summary = document.createElement("summary");
    summary.textContent = "Why this anime?";
    const body = document.createElement("div");
    body.className = "explanation-body";
    const keywords = anime.explanation.keywords || [];
    const genres = anime.explanation.genres || [];
    const explanationText = document.createElement("p");
    explanationText.textContent = keywords.length
      ? "This recommendation shares terms from your selected anime or description: " + keywords.join(", ") + "."
      : "This title was ranked using its synopsis and genres compared with your preferences.";
    body.append(explanationText);
    if (genres.length) {
      const genreText = document.createElement("p");
      genreText.textContent = "Genres: " + genres.join(", ") + ".";
      body.append(genreText);
    }
    const method = document.createElement("small");
    method.textContent = "Based on TF-IDF and cosine similarity, not a user rating.";
    body.append(method);
    details.append(summary, body);
    content.append(details);
  }
  card.append(poster, content);
  return card;
}

async function loadCatalog() {
  try {
    const response = await fetch("/api/catalog");
    if (!response.ok) throw new Error("Catalog request failed");
    const payload = await response.json();
    state.catalog = payload.items;
    const options = $("#anime-options");
    options.replaceChildren();
    state.catalog.forEach((anime) => {
      const option = document.createElement("option");
      option.value = anime.title;
      options.append(option);
    });
    const genreSelect = $("#genre-filter");
    const genreNames = new Set();
    state.catalog.forEach((anime) => {
      // AniList provides multi-word genres (e.g. "Slice of Life").
      const knownGenres = ["Action", "Adventure", "Comedy", "Drama", "Ecchi", "Fantasy", "Horror", "Mahou Shoujo", "Mecha", "Music", "Mystery", "Psychological", "Romance", "Sci-Fi", "Slice of Life", "Sports", "Supernatural", "Thriller"];
      knownGenres.forEach((genre) => {
        if ((anime.genres || "").split(" ").length && (" " + anime.genres + " ").toLowerCase().includes((" " + genre + " ").toLowerCase())) genreNames.add(genre);
      });
    });
    [...genreNames].sort().forEach((genre) => {
      const option = document.createElement("option");
      option.value = genre;
      option.textContent = genre;
      genreSelect.append(option);
    });
    $("#data-status").textContent = payload.count + " anime available · Source: " + payload.source;
  } catch {
    $("#data-status").textContent = "Unable to load the catalog. Please try refreshing.";
  }
}

async function findRecommendations(event) {
  event.preventDefault();
  const button = $("#submit-button");
  button.disabled = true;
  button.textContent = "Finding your anime...";
  message.textContent = "";
  results.replaceChildren();
  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        favorites: state.favorites,
        description: $("#description").value.trim(),
        max_episodes: $("#limit-episodes").checked ? Number($("#max-episodes").value) : null,
        genre: $("#genre-filter").value || null,
        min_score: $("#score-filter").value ? Number($("#score-filter").value) : null,
        limit: 9
      })
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "Unable to find recommendations.");
    $("#result-count").textContent = payload.items.length + " matches";
    if (!payload.items.length) message.textContent = "No matches found. Try changing your preferences or episode limit.";
    payload.items.forEach((anime) => results.append(createCard(anime)));
    if (payload.items.length) $("#recommendations").scrollIntoView({ behavior: "smooth" });
  } catch (error) {
    message.textContent = error.message || "Something went wrong.";
  } finally {
    button.disabled = false;
    button.innerHTML = 'Find my anime <span aria-hidden="true">→</span>';
  }
}

$("#add-favorite").addEventListener("click", addFavorite);
$("#favorite-search").addEventListener("keydown", (event) => {
  if (event.key === "Enter") { event.preventDefault(); addFavorite(); }
});
$("#limit-episodes").addEventListener("change", (event) => {
  $("#max-episodes").disabled = !event.target.checked;
});
form.addEventListener("submit", findRecommendations);
loadCatalog();
