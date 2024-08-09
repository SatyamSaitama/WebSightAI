<script setup>
import { ref, nextTick } from 'vue';
import axios from '../axios';

// Define refs to hold the generated HTML, loading state, and the content container
const generatedHTML = ref('');
const isLoading = ref(false);
const contentRef = ref(null);
const copyButtonRef = ref(null);

// Function to handle the search button click and Enter key press
const handleSearch = async () => {
  const input = document.getElementById('floatingInput').value;

  // Show loading indicator
  isLoading.value = true;

  try {
    const response = await axios.post('generate', {
      prompt: input
    });
    // Store the actual HTML content
    generatedHTML.value = response.data.response;

    // Create a Blob URL for iframe source
    const file = new Blob([generatedHTML.value], { type: 'text/html' });
    const fileURL = URL.createObjectURL(file);

    // Wait for DOM updates to complete and then scroll to the content
    await nextTick();
    contentRef.value.scrollIntoView({ behavior: 'smooth' });

    // Set the iframe source to the Blob URL
    contentRef.value.querySelector('iframe').src = fileURL;
  } catch (error) {
    console.error('Error generating HTML:', error);
  } finally {
    // Hide loading indicator
    isLoading.value = false;
  }
};

// Function to handle the Enter key press
const handleKeyPress = (event) => {
  if (event.key === 'Enter') {
    handleSearch();
  }
};

// Function to copy the generated HTML to the clipboard
const copyHTML = () => {
  // Use the actual HTML content instead of Blob URL
  navigator.clipboard.writeText(generatedHTML.value)
    .then(() => {
      copyButtonRef.value.textContent = 'Copied!';
      setTimeout(() => {
        copyButtonRef.value.textContent = 'Copy';
      }, 2000);
    })
    .catch(err => console.error('Failed to copy text: ', err));
};
</script>

<template>
  <div class="container my-5">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="input-group mb-3">
          <input
            type="text"
            id="floatingInput"
            class="form-control form-control-lg"
            placeholder="Create Magic ..."
            @keypress="handleKeyPress"
          />
          <button type="button" class="btn btn-lg btn-gradient-primary" @click="handleSearch">
            <span class="material-symbols-outlined">search</span>
          </button>
        </div>

        <!-- Loading indicator -->
        <div v-if="isLoading" class="text-center my-5">
          <div class="spinner-border text-gradient-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        

        <!-- Section to render the generated HTML -->
        <div ref="contentRef" v-if="generatedHTML" class="iframe-container">
          <iframe
            frameborder="0"
            class="iframe-content"
          ></iframe>
          <button
            ref="copyButtonRef"
            class="btn btn-gradient-danger btn-sm copy-button"
            @click="copyHTML"
          >
            Copy
          </button>
        </div>
        <!-- Embedded iframe section -->
        <div class="iframe-section mb-4">
          <iframe
            src="https://huggingface.co/datasets/HuggingFaceM4/WebSight/embed/viewer/v0.2/train?row=50"
            frameborder="0"
            width="100%"
            height="560px"
          ></iframe>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.form-control:focus {
  outline: none;
  box-shadow: none;
}
.form-control-lg {
  font-size: 1.25rem;
  padding: 0.5rem 1rem;
}

.btn-lg {
  font-size: 1.25rem;
  padding: 0.5rem 1rem;
}

.btn-gradient-primary {
  background-image: linear-gradient(to right, #007bff, #00c851);
  color: #fff;
  border: none;
}

.btn-gradient-danger {
  background-image: linear-gradient(to right, #dc3545, #ff6b6b);
  color: #fff;
  border: none;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.spinner-border.text-gradient-primary {
  background-image: linear-gradient(to right, #007bff, #00c851);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.iframe-section {
  margin-bottom: 1.5rem;
}

.iframe-container {
  position: relative;
  background-color: #f8f9fa;
  padding: 2rem;
  border-radius: 0.5rem;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.iframe-content {
  width: 100%;
  height: 500px;
}

.copy-button {
  position: absolute;
  top: 0px;
  right: 10px;
}
</style>
