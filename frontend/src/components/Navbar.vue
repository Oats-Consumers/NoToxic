<template>
  <v-app-bar app dark color="#0E3A4F" elevation="6">
    <!-- Left: App title -->
    <v-btn text to="/" class="pl-2">
      <span class="text-h6 font-weight-bold white--text">Toxicity Ward ☣️</span>
    </v-btn>

    <v-spacer />

    <!-- ✅ Right-side when logged in -->
    <div v-if="loggedIn" class="d-flex align-center">
      <v-btn color="white" class="mr-2" @click="goToMyMatches">
        🎮 Check My Games
      </v-btn>
      <v-btn
        variant="text"
        density="compact"
        size="small"
        class="text-white"
        @click="logout"
      >
        Logout
      </v-btn>
    </div>

    <!-- ✅ Right-side when not logged in -->
    <v-btn v-else color="white" class="mr-4" @click="loginWithSteam">
      <v-avatar size="24" class="mr-2">
        <img
  src="https://upload.wikimedia.org/wikipedia/commons/8/83/Steam_icon_logo.svg"
  alt="Steam"
  height="24"
/>
      </v-avatar>
      Login with Steam
    </v-btn>
  </v-app-bar>
</template>


<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const loggedIn = ref(false)

onMounted(async () => {
  try {
    const res = await axios.get("http://127.0.0.1:5000/check-login", {
      withCredentials: true // ✅ send session cookie
    })
    if (res.data.loggedIn) {
      loggedIn.value = true
    }
  } catch (err) {
    loggedIn.value = false
  }
})

const logout = async () => {
  try {
    await axios.get("http://127.0.0.1:5000/logout", {
      withCredentials: true,
    })
    loggedIn.value = false
    window.location.href = "/" // optional: refresh or redirect
  } catch (e) {
    console.error("Logout failed:", e)
  }
}


const loginWithSteam = () => {
  window.location.href = "http://127.0.0.1:5000/login"
}

import { useRouter } from 'vue-router'
const router = useRouter()

const goToMyMatches = () => {
  window.location.href = '/my-matches'
}
</script>
