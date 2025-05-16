<template>
  <v-app-bar app dark color="#0E3A4F" elevation="6">
    <!-- Left: App title -->
    <v-btn text to="/" class="pl-2">
      <span class="text-h6 font-weight-bold white--text">Toxicity Ward ☣️</span>
    </v-btn>

    <v-spacer />

    <!-- ✅ Right-side when logged in -->
    <div v-if="false">
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
    </div>
  </v-app-bar>
</template>


<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const API_BASE = import.meta.env.VITE_API_BASE

const loggedIn = ref(false)

onMounted(async () => {
  try {
    const res = await axios.get(`${API_BASE}/check-login`, {
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
    await axios.get(`${API_BASE}/logout`, {
      withCredentials: true,
    })
    loggedIn.value = false
    window.location.href = "/" // optional: refresh or redirect
  } catch (e) {
    console.error("Logout failed:", e)
  }
}


const loginWithSteam = () => {
  window.location.href = `${API_BASE}/login`
}

import { useRouter } from 'vue-router'
const router = useRouter()

const goToMyMatches = () => {
  window.location.href = '/my-matches'
}
</script>
