// ======= FILE UPLOAD PREVIEW =======
const fileInput = document.getElementById("file");
const preview = document.getElementById("preview");

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) {
    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";
  } else {
    preview.style.display = "none";
  }
});

// ======= CAMERA FUNCTIONALITY =======
const startCameraBtn = document.getElementById("start-camera");
const takePictureBtn = document.getElementById("take-picture");
const video = document.getElementById("camera");
const canvas = document.getElementById("snapshot");
const photo = document.getElementById("photo");
let stream;

startCameraBtn.addEventListener("click", async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    startCameraBtn.style.display = "none";
    takePictureBtn.style.display = "inline-block";
  } catch (err) {
    alert("Camera access denied or not available.");
    console.error(err);
  }
});

takePictureBtn.addEventListener("click", () => {
  const context = canvas.getContext("2d");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Stop the camera
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
  }

  // Convert canvas to image and show preview
  const dataUrl = canvas.toDataURL("image/png");
  photo.src = dataUrl;
  photo.style.display = "block";

  // Hide video and take picture button
  video.style.display = "none";
  takePictureBtn.style.display = "none";
});

// ======= BACKEND INTEGRATION =======
const uploadForm = document.getElementById("upload-form");
const recipesDiv = document.getElementById("recipes");
const loading = document.getElementById("loading");
const submitBtn = uploadForm.querySelector("button");

// Change this depending on your environment
const BACKEND_URL =
  window.location.hostname.includes("localhost") ||
  window.location.hostname.includes("127.0.0.1")
    ? "http://127.0.0.1:8000"
    : "https://smartchef-gw8c.onrender.com";
// const BACKEND_URL = "https://api.smartchefapp.tech"; // Production

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const file = fileInput.files[0];
  let blob;

  // Prefer camera photo if available
  if (photo.src && photo.style.display === "block") {
    const res = await fetch(photo.src);
    blob = await res.blob();
  } else if (file) {
    blob = file;
  } else {
    alert("Please upload or take a photo first!");
    return;
  }

  const formData = new FormData();
  formData.append("file", blob, "image.png");

  // Disable the button & show loader
  submitBtn.disabled = true;
  loading.style.display = "block";
  recipesDiv.innerHTML = "<p>Analyzing your image... please wait ⏳</p>";

  try {
    // 1️⃣ Upload image to backend for YOLO detection
    const uploadRes = await fetch(`${BACKEND_URL}/upload`, {
      method: "POST",
      body: formData,
    });
    const uploadData = await uploadRes.json();
    console.log("Detected labels:", uploadData.labels);

    // 2️⃣ Ask Gemini to generate a recipe
    const aiRes = await fetch(`${BACKEND_URL}/ai-recipe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: uploadData.labels }),
    });
    const aiData = await aiRes.json();

    // 3️⃣ Display result
    loading.style.display = "none";
    displayRecipe(aiData.recipe);
  } catch (err) {
    console.error(err);
    loading.style.display = "none";
    recipesDiv.innerHTML = "<p>⚠️ Error connecting to backend.</p>";
  } finally {
    // Re-enable the button
    submitBtn.disabled = false;
  }
});

function displayRecipe(recipe) {
  if (!recipe) {
    recipesDiv.innerHTML = "<p>❌ No recipe found.</p>";
    return;
  }

  recipesDiv.innerHTML = `
    <h3>${recipe.title}</h3>
    <h4>Ingredients:</h4>
    <ul>${recipe.ingredients.map((i) => `<li>${i}</li>`).join("")}</ul>
    <h4>Steps:</h4>
    <ol>${recipe.steps.map((s) => `<li>${s}</li>`).join("")}</ol>
  `;
}
