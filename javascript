// ======= FILE UPLOAD PREVIEW =======
const fileInput = document.getElementById('file');
const preview = document.getElementById('preview');

fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];
  if (file) {
    preview.src = URL.createObjectURL(file);
    preview.style.display = 'block';
  } else {
    preview.style.display = 'none';
  }
});

// ======= CAMERA FUNCTIONALITY =======
const startCameraBtn = document.getElementById('start-camera');
const takePictureBtn = document.getElementById('take-picture');
const video = document.getElementById('camera');
const canvas = document.getElementById('snapshot');
const photo = document.getElementById('photo');
let stream;

// Start the camera
startCameraBtn.addEventListener('click', async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    startCameraBtn.style.display = 'none';
    takePictureBtn.style.display = 'inline-block';
  } catch (err) {
    alert("Camera access denied or not available.");
    console.error(err);
  }
});

// Take a picture
takePictureBtn.addEventListener('click', () => {
  const context = canvas.getContext('2d');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Stop the camera
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
  }

  // Convert canvas to image and show preview
  const dataUrl = canvas.toDataURL('image/png');
  photo.src = dataUrl;
  photo.style.display = 'block';

  // Hide video and take picture button
  video.style.display = 'none';
  takePictureBtn.style.display = 'none';
});
